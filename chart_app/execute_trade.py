"""
Applies the market making strategy to a stock of your choice
using Alpaca's API
"""
# poetry run python3 chart_app/execute_trade.py NVDA <PAPER_API_KEY> <PAPER_SECRET_KEY> market gtc 10 5
import time
import requests
import argparse
import json
import pandas as pd
from requests.exceptions import RequestException


def retry_on_exception(max_retries=3, retry_delay=5, exceptions=(Exception,)):
    """Retry decorator"""

    def decorator_retry(func):
        def wrapper_retry(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"Exception on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print("Max retries reached. Exiting.")
                        raise

        return wrapper_retry

    return decorator_retry


@retry_on_exception(
    max_retries=3, retry_delay=5, exceptions=(pd.errors.EmptyDataError,)
)
def get_latest_bid_ask(sym: str) -> dict:
    """Gets latest bids and asks from CSV"""
    df = pd.read_csv(
        "dummy_equities_trading/data/quotes/latest_stock_quotes.csv", index_col=0
    )

    prices = {
        "Ask_price": df.loc[sym, ["Ask_price", "Bid_price"]].iloc[-1]["Ask_price"],
        "Bid_price": df.loc[sym, ["Ask_price", "Bid_price"]].iloc[-1]["Bid_price"],
    }

    return prices


@retry_on_exception(max_retries=3, retry_delay=1, exceptions=(RequestException,))
def get_open_orders(api_key: str, secret_key: str) -> str:
    """Gets all open orders"""

    url = "https://paper-api.alpaca.markets/v2/orders"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key,
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.text


@retry_on_exception(max_retries=3, retry_delay=1, exceptions=(RequestException,))
def cancel_orders(api_key: str, secret_key: str) -> str:
    """Cancels all open orders"""
    url = "https://paper-api.alpaca.markets/v2/orders"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key,
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()

    return response.text


@retry_on_exception(max_retries=10, retry_delay=1, exceptions=(RequestException,))
def place_order(
    side: str, type: str, tic: str, sym: str, qty: str, api_key: str, secret_key: str
) -> str:
    """Places buy or sell order based on instructions given"""

    url = "https://paper-api.alpaca.markets/v2/orders"

    payload = {
        "side": side,
        "type": type,
        "time_in_force": tic,
        "symbol": sym,
        "qty": qty,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key,
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.text


def main(
    sym: str, qty: int, ref_int: int, api_key: str, secret_key: str, type: str, tic: str
) -> None:
    """Applies the market making strategy based on your inputs"""
    while True:
        # Fetch latest bid and ask prices
        latest_prices = get_latest_bid_ask(sym=sym)
        current_bid = latest_prices["Bid_price"]
        current_ask = latest_prices["Ask_price"]
        current_spread = current_ask - current_bid
        print(
            f"Latest {sym} prices - ask price({current_ask}), buy price({current_bid}), spread({current_spread})"
        )

        # Cancel existing orders
        open_orders = get_open_orders(api_key=api_key, secret_key=secret_key)
        if open_orders:
            cancel_orders(api_key=api_key, secret_key=secret_key)

        # Place new bid and ask orders
        bid_order_id = json.loads(
            place_order(
                side="buy",
                type=type,
                tic=tic,
                sym=sym,
                qty=qty,
                api_key=api_key,
                secret_key=secret_key,
            )
        )
        ask_order_id = json.loads(
            place_order(
                side="sell",
                type=type,
                tic=tic,
                sym=sym,
                qty=5,
                api_key=api_key,
                secret_key=secret_key,
            )
        )

        # Print current status
        print(
            f"Buy order placed: {bid_order_id['id']}\nSell order placed: {ask_order_id['id']}"
        )

        # Wait before refreshing orders
        time.sleep(ref_int)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gets stock data from the Alpaca market data API"
    )

    parser.add_argument("symbol", type=str, help="Stock symbol to retrieve")
    parser.add_argument("paper_key", type=str, help="Alpaca PAPER API key")
    parser.add_argument("paper_secret", type=str, help="Alpaca PAPER API secret key")
    parser.add_argument(
        "type",
        type=str,
        help="Market or limit are the two order type options in this case",
    )
    parser.add_argument(
        "tic", type=str, help="Time-in-force value (day, gtc, opg, cls, ioc, fok"
    )
    parser.add_argument(
        "qty", type=int, help="Integer value for quantity of equity you want to order"
    )
    parser.add_argument(
        "ref_int", type=int, help="Refresh interval: time to wait between orders"
    )

    args = parser.parse_args()

    main(
        sym=args.symbol,
        qty=args.qty,
        ref_int=args.ref_int,
        api_key=args.paper_key,
        secret_key=args.paper_secret,
        type=args.type,
        tic=args.tic,
    )
