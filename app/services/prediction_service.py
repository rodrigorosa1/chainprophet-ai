import yfinance as yf
import pandas as pd
import numpy as np
from prophet import Prophet


def _build_prophet_model():
    model = Prophet(
        daily_seasonality=True, weekly_seasonality=True, changepoint_prior_scale=0.15
    )
    return model


def _get_sentiment_analyzer():
    try:
        from transformers import pipeline

        clf = pipeline("text-classification", model="ProsusAI/finbert", top_k=None)
        return ("finbert", clf)
    except Exception:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

            return ("vader", SentimentIntensityAnalyzer())
        except Exception:
            return (None, None)


def _sentiment_score(texts, analyzer_kind, analyzer):
    if not texts:
        return 0.0

    texts = [t for t in texts if isinstance(t, str) and t.strip()][:30]

    if analyzer_kind == "finbert":
        scores = []
        for t in texts:
            out = analyzer(t)
            best = max(out, key=lambda x: x["score"])
            label = best["label"].lower()
            score = best["score"]

            if "positive" in label:
                scores.append(float(score))
            elif "negative" in label:
                scores.append(float(-score))
            else:
                scores.append(0.0)

        return float(np.mean(scores)) if scores else 0.0

    if analyzer_kind == "vader":
        scores = [float(analyzer.polarity_scores(t)["compound"]) for t in texts]
        return float(np.mean(scores)) if scores else 0.0

    return 0.0


def _robust_zscore(x: pd.Series):
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


def _detect_anomaly_score(close_series: pd.Series, lookback_hours: int = 24 * 14):
    close = close_series.dropna().tail(lookback_hours)
    if len(close) < 24:
        return 0.0

    returns = close.pct_change().dropna()
    _, z = _robust_zscore(returns)

    recent = z.tail(24).abs()
    return float(np.clip(recent.mean() if not recent.empty else 0.0, 0.0, 10.0))


def _fetch_yahoo_news_titles(ticker_obj, max_items: int = 20):
    try:
        news = getattr(ticker_obj, "news", None) or []
        titles = []

        for n in news[:max_items]:
            title = n.get("title") or ""
            if title.strip():
                titles.append(title.strip())

        return titles
    except Exception:
        return []


def _get_asset_info(ticker_obj, ticker_symbol):
    try:
        info = ticker_obj.info

        name = info.get("shortName") or info.get("longName") or ticker_symbol
        code = info.get("symbol")

        if code and "-" in code:
            code = code.split("-")[0]

        return {"name": name, "symbol": ticker_symbol, "code": code or ticker_symbol}
    except Exception:
        code = ticker_symbol.split("-")[0] if "-" in ticker_symbol else ticker_symbol
        return {"name": ticker_symbol, "symbol": ticker_symbol, "code": code}


def _calculate_rsi(close_series: pd.Series, period: int = 14):
    delta = close_series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    return rsi.fillna(50)


def _calculate_volatility(close_series: pd.Series, window: int = 24):
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


def _calculate_trend_strength(
    close_series: pd.Series, short_window: int = 12, long_window: int = 48
):
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


def _calculate_volume_signal(data: pd.DataFrame, volume_window: int = 24):
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
        direction_confirmation = 1.0
        trend = "bullish_confirmation"
    elif latest_return < 0 and relative_volume >= 1.15:
        direction_confirmation = -1.0
        trend = "bearish_confirmation"
    elif latest_return > 0 and relative_volume < 0.9:
        direction_confirmation = -0.5
        trend = "weak_bullish"
    elif latest_return < 0 and relative_volume < 0.9:
        direction_confirmation = 0.5
        trend = "weak_bearish"
    else:
        direction_confirmation = 0.0
        trend = "neutral"

    return {
        "relative_volume": float(round(relative_volume, 4)),
        "direction_confirmation": float(direction_confirmation),
        "trend": trend,
    }


def _detect_market_regime(volatility: float, trend: dict, rsi_value: float):
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


def _score_backtest_quality(mape_percent: float, directional_accuracy_percent: float):
    if mape_percent is None:
        return 50.0

    mape_score = max(0.0, 100.0 - min(mape_percent * 10.0, 100.0))
    direction_score = max(0.0, min(directional_accuracy_percent, 100.0))

    quality = (mape_score * 0.65) + (direction_score * 0.35)
    return round(float(quality), 2)


def _run_backtest(
    df: pd.DataFrame,
    horizon_hours: int = 24,
    windows: int = 3,
    min_train_points: int = 24 * 14,
    step_hours: int = 12,
):
    """
    Backtest walk-forward do modelo base Prophet.
    Observação: o backtest é do núcleo estatístico; sentimento/notícias não entram aqui
    para evitar vazamento temporal.
    """
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
            model = _build_prophet_model()
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

    quality_score = _score_backtest_quality(
        mape_percent=mape_percent,
        directional_accuracy_percent=directional_accuracy_percent,
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


def _calculate_confidence(
    row,
    anomaly_score: float,
    sentiment_avg: float,
    volatility: float,
    rsi_value: float,
    trend: dict,
    volume_signal: dict,
    market_regime: dict,
    backtest: dict,
):
    estimated_price = float(row["yhat_adj"])
    lower = float(row["yhat_lower_adj"])
    upper = float(row["yhat_upper_adj"])

    if estimated_price <= 0:
        return 0.0

    interval_width_ratio = (upper - lower) / estimated_price
    relative_volume = volume_signal.get("relative_volume", 1.0)
    direction_confirmation = volume_signal.get("direction_confirmation", 0.0)
    regime_name = market_regime.get("name", "sideways")
    backtest_quality = float(backtest.get("quality_score_percent", 50.0) or 50.0)

    confidence = 82.0

    # 1) intervalo
    confidence -= min(interval_width_ratio * 100, 28.0)

    # 2) anomalias
    confidence -= min(anomaly_score * 4.0, 18.0)

    # 3) volatilidade
    confidence -= min(volatility * 400, 18.0)

    # 4) sentimento
    confidence += sentiment_avg * 7.0

    # 5) RSI
    if rsi_value >= 75:
        confidence -= 8.0
    elif rsi_value >= 65:
        confidence -= 4.0
    elif rsi_value <= 25:
        confidence -= 6.0
    elif rsi_value <= 35:
        confidence -= 3.0
    else:
        confidence += 2.0

    # 6) tendência
    trend_strength = trend.get("strength", 0.0)
    trend_direction = trend.get("direction", "neutral")

    if trend_direction == "up":
        confidence += min(trend_strength * 100, 7.0)
    elif trend_direction == "down":
        confidence += min(trend_strength * 100, 5.0)
    else:
        confidence -= 2.0

    # 7) volume
    if direction_confirmation > 0:
        confidence += min(relative_volume * 3.0, 6.0)
    elif direction_confirmation < 0:
        confidence -= min(abs(direction_confirmation) * 6.0, 6.0)

    # 8) regime
    if regime_name == "bullish":
        confidence += 4.0
    elif regime_name == "bearish":
        confidence += 2.0
    elif regime_name == "high_volatility_bullish":
        confidence += 1.0
    elif regime_name == "high_volatility_bearish":
        confidence -= 2.0
    else:
        confidence -= 1.5

    # 9) backtest
    # 50 = neutro; acima melhora um pouco, abaixo piora
    confidence += ((backtest_quality - 50.0) / 50.0) * 12.0

    confidence = max(5.0, min(95.0, confidence))
    return round(confidence, 2)


def forecast_prices(ticker: str, hours: int = 24):
    try:
        t = yf.Ticker(ticker)
        asset_info = _get_asset_info(t, ticker)

        # Para previsão horária, usamos 1h
        data = t.history(period="60d", interval="1h")
        if data is None or data.empty:
            return {"error": "Sem dados horários no Yahoo Finance para esse ticker."}

        df = (
            data.reset_index()[["Datetime", "Close"]]
            .rename(columns={"Datetime": "ds", "Close": "y"})
            .dropna()
        )

        df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)

        if len(df) < 24 * 14:
            return {"error": "Dados insuficientes para previsão horária confiável."}

        close_series = data["Close"].dropna()

        anomaly_score = _detect_anomaly_score(close_series, lookback_hours=24 * 14)

        analyzer_kind, analyzer = _get_sentiment_analyzer()
        titles = _fetch_yahoo_news_titles(t, max_items=25)
        sentiment_avg = _sentiment_score(titles, analyzer_kind, analyzer)

        volatility = _calculate_volatility(close_series, window=24)

        rsi_series = _calculate_rsi(close_series, period=14)
        rsi_value = float(rsi_series.iloc[-1]) if not rsi_series.empty else 50.0

        trend = _calculate_trend_strength(close_series, short_window=12, long_window=48)

        volume_signal = _calculate_volume_signal(data, volume_window=24)

        market_regime = _detect_market_regime(
            volatility=volatility, trend=trend, rsi_value=rsi_value
        )

        backtest = _run_backtest(
            df=df,
            horizon_hours=hours,
            windows=3,
            min_train_points=24 * 14,
            step_hours=12,
        )

        model = _build_prophet_model()
        model.fit(df)

        future = model.make_future_dataframe(periods=hours, freq="h")
        forecast = model.predict(future)

        base = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(hours).copy()

        sentiment_weight = 0.025
        sentiment_factor = 1.0 + (sentiment_avg * sentiment_weight)

        anomaly_weight = 0.02
        anomaly_penalty = 1.0 - (min(anomaly_score, 10.0) / 10.0) * anomaly_weight

        volatility_weight = 0.03
        volatility_penalty = 1.0 - min(volatility * 15, 1.0) * volatility_weight

        trend_bonus = 1.0
        if trend["direction"] == "up":
            trend_bonus += min(trend["strength"], 0.025)
        elif trend["direction"] == "down":
            trend_bonus -= min(trend["strength"], 0.02)

        volume_factor = 1.0
        if volume_signal["direction_confirmation"] > 0:
            volume_factor += min((volume_signal["relative_volume"] - 1.0) * 0.03, 0.03)
        elif volume_signal["direction_confirmation"] < 0:
            volume_factor -= min(
                abs(volume_signal["direction_confirmation"]) * 0.03, 0.03
            )

        regime_factor = 1.0 + (market_regime["score"] * 0.02)

        backtest_factor = (
            1.0
            + ((float(backtest.get("quality_score_percent", 50.0)) - 50.0) / 100.0)
            * 0.04
        )

        adjusted_factor = (
            sentiment_factor
            * anomaly_penalty
            * volatility_penalty
            * trend_bonus
            * volume_factor
            * regime_factor
            * backtest_factor
        )

        adjusted = base.copy()
        adjusted["yhat_adj"] = (adjusted["yhat"] * adjusted_factor).astype(float)

        widen = (
            1.0 + (min(anomaly_score, 10.0) / 10.0) * 0.10 + min(volatility * 8, 0.20)
        )

        if market_regime["name"] in [
            "high_volatility_bullish",
            "high_volatility_bearish",
        ]:
            widen += 0.05

        if float(backtest.get("quality_score_percent", 50.0)) < 55.0:
            widen += 0.04

        center = adjusted["yhat_adj"]

        lower_dist = (base["yhat"] - base["yhat_lower"]).abs() * widen
        upper_dist = (base["yhat_upper"] - base["yhat"]).abs() * widen

        adjusted["yhat_lower_adj"] = (center - lower_dist).astype(float)
        adjusted["yhat_upper_adj"] = (center + upper_dist).astype(float)

        response = []
        for _, row in adjusted.iterrows():
            confidence_percent = _calculate_confidence(
                row=row,
                anomaly_score=anomaly_score,
                sentiment_avg=sentiment_avg,
                volatility=volatility,
                rsi_value=rsi_value,
                trend=trend,
                volume_signal=volume_signal,
                market_regime=market_regime,
                backtest=backtest,
            )

            response.append(
                {
                    "datetime": pd.to_datetime(row["ds"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "estimated_price": round(float(row["yhat_adj"]), 2),
                    "confidence_percent": confidence_percent,
                }
            )

        return {
            "asset": asset_info,
            "timeframe": "1h",
            "horizon_hours": hours,
            "backtest": backtest,
            "forecast": response,
        }

    except Exception as e:
        return {"error": str(e)}
