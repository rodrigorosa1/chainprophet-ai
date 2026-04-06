import numpy as np
import pandas as pd


class FeatureEngineeringService:
    def build_features(self, data: pd.DataFrame, horizon_hours: int) -> pd.DataFrame:
        df = data.copy()

        if df.empty:
            raise ValueError("Empty dataframe received for feature engineering.")

        df = df.rename(columns=str.lower)

        required_columns = {"close", "high", "low"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        if "volume" not in df.columns:
            df["volume"] = 0.0

        df["return_1h"] = df["close"].pct_change(1)
        df["return_2h"] = df["close"].pct_change(2)
        df["return_3h"] = df["close"].pct_change(3)
        df["return_6h"] = df["close"].pct_change(6)
        df["return_12h"] = df["close"].pct_change(12)
        df["return_24h"] = df["close"].pct_change(24)
        df["return_48h"] = df["close"].pct_change(48)

        df["volatility_6h"] = df["return_1h"].rolling(6).std()
        df["volatility_12h"] = df["return_1h"].rolling(12).std()
        df["volatility_24h"] = df["return_1h"].rolling(24).std()
        df["volatility_48h"] = df["return_1h"].rolling(48).std()

        df["ema_6"] = df["close"].ewm(span=6, adjust=False).mean()
        df["ema_12"] = df["close"].ewm(span=12, adjust=False).mean()
        df["ema_24"] = df["close"].ewm(span=24, adjust=False).mean()
        df["ema_48"] = df["close"].ewm(span=48, adjust=False).mean()

        df["ema_gap_6"] = (df["close"] / df["ema_6"]) - 1.0
        df["ema_gap_12"] = (df["close"] / df["ema_12"]) - 1.0
        df["ema_gap_24"] = (df["close"] / df["ema_24"]) - 1.0
        df["ema_gap_48"] = (df["close"] / df["ema_48"]) - 1.0

        df["volume_mean_24"] = df["volume"].rolling(24).mean()
        df["relative_volume_24"] = np.where(
            df["volume_mean_24"] > 0,
            df["volume"] / df["volume_mean_24"],
            1.0,
        )

        df["high_low_range"] = np.where(
            df["close"] > 0,
            (df["high"] - df["low"]) / df["close"],
            0.0,
        )

        index_dt = pd.to_datetime(df.index)
        if getattr(index_dt, "tz", None) is not None:
            index_dt = index_dt.tz_localize(None)

        df["hour"] = index_dt.hour
        df["day_of_week"] = index_dt.dayofweek
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
        df["is_london_us_overlap"] = df["hour"].between(12, 16).astype(int)

        df[f"target_return_{horizon_hours}h"] = (
            df["close"].shift(-horizon_hours) / df["close"]
        ) - 1.0

        df[f"target_direction_{horizon_hours}h"] = (
            df[f"target_return_{horizon_hours}h"] > 0
        ).astype(int)

        df = df.replace([np.inf, -np.inf], np.nan).dropna()

        return df

    def get_feature_columns(self) -> list[str]:
        return [
            "return_1h",
            "return_2h",
            "return_3h",
            "return_6h",
            "return_12h",
            "return_24h",
            "return_48h",
            "volatility_6h",
            "volatility_12h",
            "volatility_24h",
            "volatility_48h",
            "ema_gap_6",
            "ema_gap_12",
            "ema_gap_24",
            "ema_gap_48",
            "relative_volume_24",
            "high_low_range",
            "hour",
            "day_of_week",
            "is_weekend",
            "is_london_us_overlap",
        ]
