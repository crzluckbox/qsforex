import copy
from decimal import Decimal, getcontext
try:
    import Queue as queue
except ImportError:
    import queue
import threading
import time

from qsforex.transaction.transaction import OANDATransactionHandler
from qsforex.portfolio.portfolio import Portfolio
from qsforex import settings
from qsforex.strategy.strategy import TestStrategy
from qsforex.data.streaming import StreamingForexPrices


def trade(events, strategy, portfolio, transaction, heartbeat):
    """
    Carries out an infinite while loop that polls the 
    events queue and directs each event to either the
    strategy component of the transaction handler. The
    loop will then pause for "heartbeat" seconds and
    continue.
    """
    while True:
        try:
            event = events.get(False)
        except queue.Empty:
            pass
        else:
            if event is not None:
                if event.type == 'TICK':
                    strategy.calculate_signals(event)
                    portfolio.update_portfolio(event)
                elif event.type == 'SIGNAL':
                    portfolio.execute_signal(event)
                elif event.type == 'ORDER':
                    transaction.execute_order(event)
        time.sleep(heartbeat)


if __name__ == "__main__":
    # Set the number of decimal places to 2
    getcontext().prec = 2

    heartbeat = 0.0  # Time in seconds between polling
    events = queue.Queue()
    equity = settings.EQUITY

    # Trade "Cable"
    pairs = ["GBPUSD"]

    # Create the OANDA market price streaming class
    # making sure to provide authentication commands
    prices = StreamingForexPrices(
        settings.STREAM_DOMAIN, settings.ACCESS_TOKEN, 
        settings.ACCOUNT_ID, pairs, events
    )

    # Create the strategy/signal generator, passing the 
    # instrument and the events queue
    strategy = TestStrategy(pairs, events)

    # Create the portfolio object that will be used to
    # compare the OANDA positions with the local, to
    # ensure backtesting integrity.
    portfolio = Portfolio(
        prices, events, equity=equity, backtest=False
    )

    # Create the transaction handler making sure to
    # provide authentication commands
    transaction = OANDATransactionHandler(
        settings.API_DOMAIN, 
        settings.ACCESS_TOKEN, 
        settings.ACCOUNT_ID
    )
    
    # Create two separate threads: One for the trading loop
    # and another for the market price streaming class
    trade_thread = threading.Thread(
        target=trade, args=(
            events, strategy, portfolio, transaction, heartbeat
        )
    )
    price_thread = threading.Thread(target=prices.stream_to_queue, args=[])
    
    # Start both threads
    trade_thread.start()
    price_thread.start()
