import yfinance as yf
import pandas as pd
from prophet import Prophet

def forecast_prices(ticker: str, days: int = 7):
    try:
        data = yf.Ticker(ticker).history(period="6mo", interval="1d")
        df = data.reset_index()[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})
        df = df.dropna()

        # 🛠️ Remove timezone de 'ds'
        df["ds"] = df["ds"].dt.tz_localize(None)

        if len(df) < 30:
            return {"error": "Dados insuficientes para prever."}

        model = Prophet(daily_seasonality=True)
        model.fit(df)

        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)

        result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(days)
        result["ds"] = result["ds"].dt.strftime("%Y-%m-%d")

        return result.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}
