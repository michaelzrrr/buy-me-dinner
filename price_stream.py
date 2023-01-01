from tda.auth import easy_client
from tda.client import Client
from tda.streaming import StreamClient
from datetime import datetime, timezone
from tda.orders.equities import equity_buy_limit, equity_sell_limit, equity_sell_short_limit, equity_buy_to_cover_limit
from tda.orders.common import Duration

import atexit
import httpx
import time
import secret_keys

def make_webdriver():
    # Import selenium here because it's slow to import
    from selenium import webdriver

    driver = webdriver.Chrome()
    atexit.register(lambda: driver.quit())
    return driver

client = easy_client(
        api_key=secret_keys.api_key,
        redirect_uri=secret_keys.redirect_url,
        token_path='/tmp/token.json',
        webdriver_func=make_webdriver)
stream_client = StreamClient(client, account_id=secret_keys.account_id)

FIELD_DATA = [StreamClient.LevelOneEquityFields.SYMBOL, 
                StreamClient.LevelOneEquityFields.BID_PRICE, 
                StreamClient.LevelOneEquityFields.ASK_PRICE, 
                StreamClient.LevelOneEquityFields.TOTAL_VOLUME,
                StreamClient.LevelOneEquityFields.OPEN_PRICE,
                StreamClient.LevelOneEquityFields.QUOTE_TIME]

async def read_stream(handler_func, market_close):
    await stream_client.login()
    await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

    stream_client.add_level_one_equity_handler(handler_func)
    await stream_client.level_one_equity_subs(symbols=['META', 'AAPL'], fields=FIELD_DATA)

    while time.time() < market_close:
        await stream_client.handle_message()
    
    return 0

def buy_limit_order(amt, num_orders=1):
    client.place_order(
        account_id=secret_keys.account_id,
        order_spec= equity_buy_limit('META', num_orders,amt)
            .set_duration(Duration.FILL_OR_KILL)
            .build()
    )
    print("order placed")

def sell_limit_order(amt, num_orders=1):
    client.place_order(
        account_id=secret_keys.account_id,
        order_spec=equity_sell_limit('META', num_orders, amt)
            .set_duration(Duration.FILL_OR_KILL)
            .build()
    )
    print("sell order placed")

def short_sell_limit_order(amt, num_orders=1):
    client.place_order(
        account_id=secret_keys.account_id,
        order_spec=equity_sell_short_limit('META', num_orders, amt)
            .set_duration(Duration.FILL_OR_KILL)
            .build()
    )
    print("short sell order placed")

def buy_to_cover_limit_order(amt, num_orders=1):
    client.place_order(
        account_id=secret_keys.account_id,
        order_spec=equity_buy_to_cover_limit('META', num_orders, amt)
            .set_duration(Duration.FILL_OR_KILL)
            .build()
    )
    print("buy to cover order placed")

def get_market_hours():
    date_format = "%Y-%m-%dT%H:%M:%S%z"
    hours = client.get_hours_for_single_market(Client.Markets.EQUITY, datetime.now())
    assert hours.status_code == httpx.codes.OK

    hours = hours.json()
    end_time = datetime.strptime(hours["equity"]["EQ"]["sessionHours"]["regularMarket"][0]['end'], date_format)
    timestamp = (end_time - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
    return int(timestamp)

def get_history():
    prices = client.get_price_history('META',
            period_type=Client.PriceHistory.PeriodType.DAY,
            frequency_type=Client.PriceHistory.FrequencyType.MINUTE,
            frequency=Client.PriceHistory.Frequency.EVERY_MINUTE,
            start_datetime=datetime.fromtimestamp(1672151765),
            end_datetime=datetime.fromtimestamp(1672173461))
    assert prices.status_code == httpx.codes.OK

    history = prices.json()
    return history["symbol"], history["candles"]
