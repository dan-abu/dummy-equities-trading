# DUMMY EQUITIES TRADING BOT

## Aim
-------------------------------------------------------------------------------------------

The aim of this project is to create an automated trading bot.

This trading bot will trade equities using real-world live data and fake money.

You can view the bot's performance by opening a new terminal and running
`poetry run python3 manage.py runserver`. This will create a webpage which you can access
by typing `http://127.0.0.1:8000/chart/` into your web browser. It will show you your
portfolio's equity position at every hour throughout the day.

**N.B.** This really is just a simple bot for learning purposes. Back testing is missing
from this iteration of the project, but I would like to add it in future.

## Method
-------------------------------------------------------------------------------------------

- `chart_app/get_data.py` pulls the latest stock market data once a minute and writes it to disk.

- `chart_app/execute_trade.py` executes trades based on a very simple market making strategy. Given
this is a simple demo for learning purposes, I have kept things simple and assumed that
the sell price will be higher than the buy price, even though this might not actually end
up being the case.

- `chart_app/main.py` manages the asynchronous running of the scripts mentioned above.

- The key files for generating the website are `chart_app/views.py`, `chart_app/urls.py`,
`chart_app/static/chart.png`, `chart_app/templates/chart_template.html`,
`trading_portfolio_site/settings.py` and `trading_portfolio_site/urls.py`.

## Requirements
------------------------------------------------------------------------------------------

We are using `Poetry` to manage dependencies and `Django` for the web framework.
You will find more information about the dependencies in `pyproject.toml`.

If you don't have `Poetry` installed, you can install it following these instructions:
`https://python-poetry.org/docs/`.

Once the repo's cloned and `Poetry`'s installed, run `poetry install` in the CLI
to install all the dependencies.

Keep in mind that you will need **2** terminal windows: one for the trading bot and the
other for the website.

```
poetry run python3 main.py NVDA GBP <LIVE_API_KEY_ID> <LIVE_API_SECRET> <PAPER_API_KEY> <PAPER_SECRET_KEY> market gtc 10 5
```
The above command will kick off the bot. The command below will create the website
`poetry run python3 manage.py runserver`.

Data is provided by `alpaca`. You will need to generate **LIVE** API keys to extract data.
You can generate keys once you've made an account here (it's free):
`https://alpaca.markets/`.

You will need **PAPER** API keys to make trades. This ensures you trade with fake
money and not your own. You can find out how to do this here:
`https://docs.alpaca.markets/docs/authentication-1`.

Add your keys to `secrets.txt` once they are ready.

## Watch outs
-----------------------------------------------------------------------------------------
If bot gets stuck in a `403 Client Error` cycle, be aware that Alpaca might be throttling
your account.

**HAPPY TRADING**