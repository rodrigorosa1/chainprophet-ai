import numpy as np
import pandas as pd


class SignalEngineService:
    def robust_zscore(self, x: pd.Series):
        x = x.dropna()
        if x.empty:
            return x, pd.Series(dtype=float)

        med = x.median()
        mad = (x - med).abs().median()

        if mad == 0 or np.isnan(mad):
            std = x.std()
            if std == 0 or np.isnan(std):
                return x, pd.Series([0.0] * len(x), index=x.index)
            z = (x - x.mean()) / std
            return x, z

        z = 0.6745 * (x - med) / mad
        return x, z

    def detect_anomaly_score(
        self, close_series: pd.Series, lookback_hours: int = 24 * 14
    ) -> float:
        close = close_series.dropna().tail(lookback_hours)
        if len(close) < 24:
            return 0.0

        returns = close.pct_change().dropna()
        _, z = self.robust_zscore(returns)

        recent = z.tail(24).abs()
        return float(np.clip(recent.mean() if not recent.empty else 0.0, 0.0, 10.0))

    def calculate_rsi(self, close_series: pd.Series, period: int = 14):
        delta = close_series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))

        return rsi.fillna(50)

    def calculate_volatility(self, close_series: pd.Series, window: int = 24) -> float:
        returns = close_series.pct_change().dropna()
        if returns.empty:
            return 0.0

        rolling_vol = returns.rolling(window=window).std()
        latest_vol = (
            rolling_vol.iloc[-1] if not rolling_vol.dropna().empty else returns.std()
        )

        if pd.isna(latest_vol):
            return 0.0

        return float(latest_vol)

    def calculate_trend_strength(
        self, close_series: pd.Series, short_window: int = 12, long_window: int = 48
    ) -> dict:
        close = close_series.dropna()

        if len(close) < long_window:
            return {"direction": "neutral", "strength": 0.0}

        ma_short = close.rolling(window=short_window).mean().iloc[-1]
        ma_long = close.rolling(window=long_window).mean().iloc[-1]

        if pd.isna(ma_short) or pd.isna(ma_long) or ma_long == 0:
            return {"direction": "neutral", "strength": 0.0}

        diff_ratio = float((ma_short - ma_long) / ma_long)

        if diff_ratio > 0:
            direction = "up"
        elif diff_ratio < 0:
            direction = "down"
        else:
            direction = "neutral"

        return {"direction": direction, "strength": abs(diff_ratio)}

    def calculate_volume_signal(
        self, data: pd.DataFrame, volume_window: int = 24
    ) -> dict:
        if "Volume" not in data.columns:
            return {
                "relative_volume": 1.0,
                "direction_confirmation": 0.0,
                "trend": "neutral",
            }

        volume = data["Volume"].dropna()
        close = data["Close"].dropna()

        if len(volume) < volume_window + 2 or len(close) < 2:
            return {
                "relative_volume": 1.0,
                "direction_confirmation": 0.0,
                "trend": "neutral",
            }

        current_volume = float(volume.iloc[-1])
        avg_volume = float(volume.tail(volume_window).mean())
        relative_volume = current_volume / avg_volume if avg_volume > 0 else 1.0

        latest_return = float(close.pct_change().iloc[-1])

        if latest_return > 0 and relative_volume >= 1.15:
            return {
                "relative_volume": round(relative_volume, 4),
                "direction_confirmation": 1.0,
                "trend": "bullish_confirmation",
            }
        if latest_return < 0 and relative_volume >= 1.15:
            return {
                "relative_volume": round(relative_volume, 4),
                "direction_confirmation": -1.0,
                "trend": "bearish_confirmation",
            }
        if latest_return > 0 and relative_volume < 0.9:
            return {
                "relative_volume": round(relative_volume, 4),
                "direction_confirmation": -0.5,
                "trend": "weak_bullish",
            }
        if latest_return < 0 and relative_volume < 0.9:
            return {
                "relative_volume": round(relative_volume, 4),
                "direction_confirmation": 0.5,
                "trend": "weak_bearish",
            }

        return {
            "relative_volume": round(relative_volume, 4),
            "direction_confirmation": 0.0,
            "trend": "neutral",
        }

    def detect_market_regime(
        self, volatility: float, trend: dict, rsi_value: float
    ) -> dict:
        trend_direction = trend.get("direction", "neutral")
        trend_strength = trend.get("strength", 0.0)

        high_vol = volatility >= 0.02
        strong_trend = trend_strength >= 0.01

        if trend_direction == "up" and strong_trend and high_vol:
            regime = "high_volatility_bullish"
        elif trend_direction == "down" and strong_trend and high_vol:
            regime = "high_volatility_bearish"
        elif trend_direction == "up" and strong_trend:
            regime = "bullish"
        elif trend_direction == "down" and strong_trend:
            regime = "bearish"
        else:
            regime = "sideways"

        regime_score = 0.0
        if regime == "bullish":
            regime_score = 0.8
        elif regime == "bearish":
            regime_score = -0.8
        elif regime == "high_volatility_bullish":
            regime_score = 0.4
        elif regime == "high_volatility_bearish":
            regime_score = -0.4

        if rsi_value > 75:
            regime_score -= 0.2
        elif rsi_value < 25:
            regime_score += 0.2

        return {"name": regime, "score": float(regime_score)}
