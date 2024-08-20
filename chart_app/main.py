"""
Gets latest stock data for a given stock once every minute as per get_data.py
Trades until capital's exhausted or all stocks are sold as per execute_trade.py
"""
# poetry run python3 main.py NVDA GBP <LIVE_API_KEY_ID> <LIVE_API_SECRET> <PAPER_API_KEY> <PAPER_SECRET_KEY> market gtc 10 5
import asyncio
import get_data
import execute_trade
import argparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_get_data(
    sym: str, currency: str, live_key: str, live_secret: str
) -> None:
    """Runs get_data.main()"""
    while True:
        try:
            logger.info(f"Fetching data for {sym}")
            await asyncio.to_thread(
                get_data.main,
                sym=sym,
                currency=currency,
                key=live_key,
                secret=live_secret,
            )
            logger.info(f"Data fetched successfully for {sym}")
        except Exception as e:
            logger.error(f"Error fetching data for {sym}: {str(e)}")
        await asyncio.sleep(60)  # Wait for 60 seconds before the next execution


async def run_execute_trade(
    sym: str,
    qty: int,
    ref_int: int,
    paper_key: str,
    paper_secret: str,
    type: str,
    tic: str,
) -> None:
    """Runs executre_trade.main()"""
    while True:
        try:
            logger.info(f"Executing trade for {sym}")
            await asyncio.to_thread(
                execute_trade.main,
                sym=sym,
                qty=qty,
                ref_int=ref_int,
                api_key=paper_key,
                secret_key=paper_secret,
                type=type,
                tic=tic,
            )
            logger.info(f"Trade executed successfully for {sym}")
        except Exception as e:
            logger.error(f"Error executing trade for {sym}: {str(e)}")


async def main(
    sym: str,
    currency: str,
    live_key: str,
    live_secret: str,
    qty: int,
    ref_int: int,
    paper_key: str,
    paper_secret: str,
    type: str,
    tic: str,
) -> None:
    """
    Runs get_data.main() once every minute and execute_trade.main() the rest of the time
    """
    logger.info("Starting main function")
    get_data_task = asyncio.create_task(
        run_get_data(sym, currency, live_key, live_secret)
    )
    execute_trade_task = asyncio.create_task(
        run_execute_trade(sym, qty, ref_int, paper_key, paper_secret, type, tic)
    )
    try:
        await asyncio.gather(get_data_task, execute_trade_task)
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gets stock data from Google Finance")

    parser.add_argument("symbol", type=str, help="Stock symbol to retrieve")
    parser.add_argument("currency", type=str, help="Currency type (e.g., USD)")
    parser.add_argument("live_key", type=str, help="Alpaca LIVE API key")
    parser.add_argument("live_secret", type=str, help="Alpaca LIVE API secret key")
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

    logger.info("Starting script")
    try:
        asyncio.run(
            main(
                sym=args.symbol,
                currency=args.currency,
                live_key=args.live_key,
                live_secret=args.live_secret,
                qty=args.qty,
                ref_int=args.ref_int,
                paper_key=args.paper_key,
                paper_secret=args.paper_secret,
                type=args.type,
                tic=args.tic,
            )
        )
    except Exception as e:
        logger.error(f"Script terminated with error: {str(e)}")
    finally:
        logger.info("Script finished")
