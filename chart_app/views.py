"""
Gets your Alpaca portfolio data from their API
Visualises your Alpaca portfolio's value over 1 day (i.e. today)
"""
# poetry run python3 manage.py runserver
import requests
import json
import matplotlib.pyplot as plt
import multiprocessing
from datetime import datetime as dt, timedelta
import pandas as pd
import os
from dotenv import load_dotenv
from requests.exceptions import RequestException
from django.shortcuts import render
from chart_app.execute_trade import retry_on_exception

@retry_on_exception(max_retries=3, retry_delay=1, exceptions=(RequestException,))
def get_portfolio_data(paper_key: str, paper_secret: str) -> dict:
    """Gets Alpaca portfolio data."""
    url = "https://paper-api.alpaca.markets/v2/account/portfolio/history?period=1D&timeframe=1H&intraday_reporting=continuous&start=2024-08-20T00%3A00%3A00Z&pnl_reset=per_day"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": paper_key,
        "APCA-API-SECRET-KEY": paper_secret,
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return json.loads(response.text)

def create_timestamp_sequence(sequence_length: int) -> list:
    """Returns a list of `sequence_length` number of timestamps starting from midnight."""
    start_time = dt.strptime("00:00:00", "%H:%M:%S")
    time_increment = timedelta(hours=1)
    timestamp_list = []
    for _ in range(sequence_length):
        timestamp_list.append(start_time.strftime("%H:%M:%S"))
        start_time += time_increment
    return timestamp_list

def clean_portfolio_data(portfolio_data: dict) -> pd.DataFrame:
    """Converts timestamp IDs to timestamps, removes superfluous keys and returns dataframe."""
    portfolio_data["timestamp_id"] = portfolio_data.pop("timestamp")
    portfolio_data["timestamp"] = create_timestamp_sequence(len(portfolio_data["timestamp_id"]))

    keys_to_delete = [
        "timestamp_id",
        "profit_loss",
        "profit_loss_pct",
        "base_value",
        "base_value_asof",
        "timeframe",
    ]

    for key in keys_to_delete:
        del portfolio_data[key]

    portfolio_data = pd.DataFrame(portfolio_data)

    return portfolio_data

def generate_plot(data: pd.DataFrame, output):
    """Generates a plot and saves it to the output buffer."""
    plt.figure()
    plt.plot(data['timestamp'], data['equity'], marker='o')
    plt.title('Portfolio Value Over 1 Day')
    plt.xlabel('Time')
    plt.ylabel('Equity')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("chart_app/static/chart.png", format='png')
    plt.close()

def portfolio_view(request):
    """Django view to fetch portfolio data, plot it, and return the image."""
    load_dotenv()
    paper_key = os.getenv("PAPER_API_KEY")
    paper_secret = os.getenv("PAPER_SECRET_KEY")
    portfolio_data = get_portfolio_data(paper_key, paper_secret)
    cleaned_data = clean_portfolio_data(portfolio_data)

    # Create a separate process for plotting
    plot_process = multiprocessing.Process(target=generate_plot, args=(cleaned_data, None))
    plot_process.start()
    plot_process.join()  # Wait for the process to finish

    response = render(request, "chart_template.html")

    return response