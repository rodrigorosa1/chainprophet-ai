import yfinance as yf
import pandas as pd
from datetime import timedelta


class MarketDataService:
    def get_ticker(self, ticker: str):
        return yf.Ticker(ticker)

    def get_asset_info(self, ticker_obj, ticker_symbol: str) -> dict:
        try:
            info = ticker_obj.info

            name = info.get("shortName") or info.get("longName") or ticker_symbol
            code = info.get("symbol")

            if code and "-" in code:
                code = code.split("-")[0]

            return {
                "name": name,
                "symbol": ticker_symbol,
                "code": code or ticker_symbol,
            }
        except Exception:
            code = (
                ticker_symbol.split("-")[0] if "-" in ticker_symbol else ticker_symbol
            )
            return {
                "name": ticker_symbol,
                "symbol": ticker_symbol,
                "code": code,
            }

    def get_hourly_history(
        self, ticker_obj, period: str = "60d", interval: str = "1h"
    ) -> pd.DataFrame:
        data = ticker_obj.history(period=period, interval=interval)
        if data is None or data.empty:
            raise ValueError("Sem dados horários no Yahoo Finance para esse ticker.")
        return data

    def build_prophet_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        datetime_col = (
            "Datetime"
            if "Datetime" in data.reset_index().columns
            else data.reset_index().columns[0]
        )

        df = (
            data.reset_index()[[datetime_col, "Close"]]
            .rename(columns={datetime_col: "ds", "Close": "y"})
            .dropna()
        )

        df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)
        return df

    def get_news_titles(self, ticker_obj, max_items: int = 20) -> list[str]:
        try:
            news = getattr(ticker_obj, "news", None) or []
            titles = []

            for item in news[:max_items]:
                title = item.get("title") or ""
                if title.strip():
                    titles.append(title.strip())

            return titles
        except Exception:
            return []

    def get_price_by_datetime(
        self,
        ticker: str,
        target_datetime,
        interval: str = "1h",
    ) -> float | None:
        ticker_obj = self.get_ticker(ticker)

        start = target_datetime - timedelta(hours=2)
        end = target_datetime + timedelta(hours=2)

        history = ticker_obj.history(
            start=start,
            end=end,
            interval=interval,
        )

        if history.empty:
            return None

        history = history.copy()
        history.index = pd.to_datetime(history.index).tz_localize(None)

        target_datetime = pd.to_datetime(target_datetime).to_pydatetime()

        if target_datetime in history.index:
            row = history.loc[target_datetime]
            return round(float(row["Close"]), 2)

        nearest_index = min(
            history.index,
            key=lambda dt: abs(dt.to_pydatetime() - target_datetime),
        )

        row = history.loc[nearest_index]
        return round(float(row["Close"]), 2)