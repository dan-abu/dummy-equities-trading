"""
Gets latest stock quote(s) from Alpaca
Gets your current positions from Alpaca
"""
# poetry run python3 chart_app/get_data.py NVDA GBP <API_KEY_ID> <API_SECRET>
import argparse
import requests
import json
import os
from execute_trade import retry_on_exception
from datetime import datetime as dt
import pandas as pd
from requests.exceptions import RequestException


@retry_on_exception(max_retries=3, retry_delay=1, exceptions=(RequestException,))
def extract_latest_quote_data(sym: str, currency: str, key: str, secret: str) -> str:
    """Pulls latest stock quotes from Alpaca Markets"""

    url = f"https://data.alpaca.markets/v2/stocks/quotes/latest?symbols={sym}&feed=iex&currency={currency}"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": key,
        "APCA-API-SECRET-KEY": secret,
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def clean_latest_quote_data(data: str, currency: str) -> pd.DataFrame:
    """Transforms the data into a DF and adds and renames columns"""
    # Extracting data we want from json payload
    json_response = json.loads(data)
    json_quotes = json_response["quotes"]

    # Adding future columns to the data
    keys_list = list(json_quotes.keys())
    creation_time = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    for i in range(len(json_quotes.keys())):
        json_quotes[keys_list[i]]["Currency"] = currency
        json_quotes[keys_list[i]]["Created_at"] = creation_time

    # Creating and cleaning the DataFrame
    new_df = pd.DataFrame.from_dict(data=json_quotes, orient="index")
    new_df = new_df[["ap", "bp", "Currency", "Created_at"]]
    new_df.columns = ["Ask_price", "Bid_price", "Currency", "Created_at"]
    return new_df


def main(sym: str, currency: str, key: str, secret: str) -> str:
    """Module entry point: creates CSV of quotes data"""
    quotes_data = extract_latest_quote_data(
        sym=sym, currency=currency, key=key, secret=secret
    )
    df = clean_latest_quote_data(data=quotes_data, currency=currency)
    if not os.listdir("dummy_equities_trading/data/quotes"):
        df.to_csv("dummy_equities_trading/data/quotes/latest_stock_quotes.csv")
    else:
        old_df = pd.read_csv(
            "dummy_equities_trading/data/quotes/latest_stock_quotes.csv", index_col=0
        )
        new_df = pd.concat([old_df, df], axis=0)
        new_df.to_csv("dummy_equities_trading/data/quotes/latest_stock_quotes.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gets stock data from the Alpaca market data API"
    )

    parser.add_argument("symbol", type=str, help="Stock symbol to retrieve")
    parser.add_argument("currency", type=str, help="Currency type (e.g., USD)")
    parser.add_argument("live_key", type=str, help="Alpaca LIVE API key")
    parser.add_argument("live_secret", type=str, help="Alpaca LIVE API secret key")

    args = parser.parse_args()

    main(
        sym=args.symbol,
        currency=args.currency,
        key=args.live_key,
        secret=args.live_secret,
    )
