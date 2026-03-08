import numpy as np
import pandas as pd
from prophet import Prophet


class BacktestService:
    def _build_prophet_model(self):
        return Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            changepoint_prior_scale=0.15,
        )

    def _score_backtest_quality(
        self, mape_percent: float, directional_accuracy_percent: float
    ) -> float:
        if mape_percent is None:
            return 50.0

        mape_score = max(0.0, 100.0 - min(mape_percent * 10.0, 100.0))
        direction_score = max(0.0, min(directional_accuracy_percent, 100.0))

        quality = (mape_score * 0.65) + (direction_score * 0.35)
        return round(float(quality), 2)

    def run(
        self,
        df: pd.DataFrame,
        horizon_hours: int = 24,
        windows: int = 3,
        min_train_points: int = 24 * 14,
        step_hours: int = 12,
    ) -> dict:
        if len(df) < (min_train_points + horizon_hours + 1):
            return {
                "windows_used": 0,
                "horizon_hours": horizon_hours,
                "mae": None,
                "rmse": None,
                "mape_percent": None,
                "directional_accuracy_percent": None,
                "quality_score_percent": 50.0,
            }

        results = []

        last_possible_cutoff = len(df) - horizon_hours
        cutoffs = []

        current_cutoff = last_possible_cutoff
        while current_cutoff >= min_train_points and len(cutoffs) < windows:
            cutoffs.append(current_cutoff)
            current_cutoff -= step_hours

        cutoffs = sorted(cutoffs)

        for cutoff in cutoffs:
            train_df = df.iloc[:cutoff].copy()
            actual_df = df.iloc[cutoff : cutoff + horizon_hours].copy()

            if len(actual_df) < horizon_hours:
                continue

            try:
                model = self._build_prophet_model()
                model.fit(train_df)

                future = model.make_future_dataframe(periods=horizon_hours, freq="h")
                forecast = model.predict(future)

                pred_df = forecast[["ds", "yhat"]].tail(horizon_hours).copy()
                merged = actual_df.merge(pred_df, on="ds", how="inner")

                if merged.empty:
                    continue

                merged["ae"] = (merged["y"] - merged["yhat"]).abs()
                merged["se"] = (merged["y"] - merged["yhat"]) ** 2
                merged["ape"] = np.where(
                    merged["y"] != 0, merged["ae"] / merged["y"].abs(), np.nan
                )

                actual_diff = merged["y"].diff()
                pred_diff = merged["yhat"].diff()

                direction_mask = actual_diff.notna() & pred_diff.notna()
                if direction_mask.any():
                    direction_hits = (
                        np.sign(actual_diff[direction_mask])
                        == np.sign(pred_diff[direction_mask])
                    ).mean() * 100.0
                else:
                    direction_hits = np.nan

                results.append(
                    {
                        "mae": float(merged["ae"].mean()),
                        "rmse": float(np.sqrt(merged["se"].mean())),
                        "mape_percent": float(np.nanmean(merged["ape"]) * 100.0),
                        "directional_accuracy_percent": (
                            float(direction_hits)
                            if not np.isnan(direction_hits)
                            else np.nan
                        ),
                    }
                )
            except Exception:
                continue

        if not results:
            return {
                "windows_used": 0,
                "horizon_hours": horizon_hours,
                "mae": None,
                "rmse": None,
                "mape_percent": None,
                "directional_accuracy_percent": None,
                "quality_score_percent": 50.0,
            }

        mae = float(np.nanmean([r["mae"] for r in results]))
        rmse = float(np.nanmean([r["rmse"] for r in results]))
        mape_percent = float(np.nanmean([r["mape_percent"] for r in results]))
        directional_accuracy_percent = float(
            np.nanmean([r["directional_accuracy_percent"] for r in results])
        )

        quality_score = self._score_backtest_quality(
            mape_percent, directional_accuracy_percent
        )

        return {
            "windows_used": len(results),
            "horizon_hours": horizon_hours,
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "mape_percent": round(mape_percent, 4),
            "directional_accuracy_percent": round(directional_accuracy_percent, 2),
            "quality_score_percent": quality_score,
        }
