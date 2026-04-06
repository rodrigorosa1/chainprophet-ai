from pathlib import Path

import joblib

import lightgbm as lgb
import pandas as pd


class MlModelService:
    def __init__(self, model_dir: str = "storage/models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def _normalize_model_key(self, ticker: str, horizon_hours: int, suffix: str) -> str:
        safe_ticker = ticker.lower().replace("-", "_")
        return f"{safe_ticker}_{horizon_hours}h_{suffix}.pkl"

    def train_direction_model(
        self,
        ticker: str,
        horizon_hours: int,
        features: pd.DataFrame,
        target: pd.Series,
    ):
        model = lgb.LGBMClassifier(
            n_estimators=400,
            learning_rate=0.03,
            max_depth=6,
            num_leaves=31,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
        )

        model.fit(features, target)
        self.save_model(
            model,
            self._normalize_model_key(ticker, horizon_hours, "direction"),
        )
        return model

    def train_return_model(
        self,
        ticker: str,
        horizon_hours: int,
        features: pd.DataFrame,
        target: pd.Series,
    ):
        model = lgb.LGBMRegressor(
            n_estimators=500,
            learning_rate=0.03,
            max_depth=6,
            num_leaves=31,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
        )

        model.fit(features, target)
        self.save_model(
            model,
            self._normalize_model_key(ticker, horizon_hours, "return"),
        )
        return model

    def train_quantile_model(
        self,
        ticker: str,
        horizon_hours: int,
        features: pd.DataFrame,
        target: pd.Series,
        alpha: float,
        suffix: str,
    ):
        model = lgb.LGBMRegressor(
            objective="quantile",
            alpha=alpha,
            n_estimators=500,
            learning_rate=0.03,
            max_depth=6,
            num_leaves=31,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
        )

        model.fit(features, target)
        self.save_model(
            model,
            self._normalize_model_key(ticker, horizon_hours, suffix),
        )
        return model

    def save_model(self, model, model_name: str):
        file_path = self.model_dir / model_name
        joblib.dump(model, file_path)

    def load_model(self, ticker: str, horizon_hours: int, suffix: str):
        file_path = self.model_dir / self._normalize_model_key(
            ticker, horizon_hours, suffix
        )

        if not file_path.exists():
            raise FileNotFoundError(f"Model file not found: {file_path}")

        return joblib.load(file_path)

    def model_exists(self, ticker: str, horizon_hours: int, suffix: str) -> bool:
        file_path = self.model_dir / self._normalize_model_key(
            ticker, horizon_hours, suffix
        )
        return file_path.exists()

    def has_complete_model_set(self, ticker: str, horizon_hours: int) -> bool:
        required_suffixes = ["direction", "return", "q15", "q85"]
        return all(
            self.model_exists(ticker, horizon_hours, suffix)
            for suffix in required_suffixes
        )
