# -*- coding: utf-8 -*-

from __future__ import print_function

try:
    import Queue as queue
except ImportError:
    import queue
import time

from qsforex import settings


class Backtest(object):
    """
    Enscapsulates the settings and components for carrying out
    an event-driven backtest on the foreign exchange markets.
    """
    def __init__(
        self, pairs, data_handler,
        tradesignalstrategy, tradesignalstrategy_params,
        tradeenterstrategy, tradeenterstrategy_params,
        tradeexitstrategy, tradeexitstrategy_params,
        portfolio, transaction, 
        equity=100000.0, heartbeat=0.0, base_currency="USD",
        startday=20150110, endday=20150208,
        max_iters=10000000000
    ):
        """
        Initialises the backtest.
        """
        self.pairs = pairs
        self.events = queue.Queue()
        self.csv_dir = settings.CSV_DATA_DIR
        self.startday = startday
        self.endday = endday
        self.ticker = data_handler(self.pairs, self.events, self.csv_dir, self.startday, self.endday)
        self.transaction = transaction()
        self.tradesignalstrategy_params = tradesignalstrategy_params
        self.tradeenterstrategy_params = tradeenterstrategy_params
        self.tradeexitstrategy_params = tradeexitstrategy_params
        self.tradesignalstrategy = tradesignalstrategy(self.pairs, self.events, **self.tradesignalstrategy_params)
        self.tradeenterstrategy = tradeenterstrategy(self.pairs, self.transaction, self.ticker, **self.tradeenterstrategy_params)
        self.tradeexitstrategy = tradeexitstrategy(self.pairs, self.transaction, self.ticker, **self.tradeexitstrategy_params)
        self.equity = equity
        self.heartbeat = heartbeat
        self.base_currency = base_currency
        self.max_iters = max_iters
        self.portfolio = portfolio(
            self.ticker, self.events, transaction=self.transaction, equity=self.equity, base_currency=self.base_currency, backtest=True
        )

    def _run_backtest(self):
        """
        Carries out an infinite while loop that polls the 
        events queue and directs each event to either the
        strategy component of the transaction handler. The
        loop will then pause for "heartbeat" seconds and
        continue unti the maximum number of iterations is
        exceeded.
        """
        print("Running Backtest...")
        iters = 0
        while iters < self.max_iters and self.ticker.continue_backtest:
            try:
                event = self.events.get(False)
            except queue.Empty:
                self.ticker.stream_next_tick()
            else:
                if event is not None:
                    if event.type == 'TICK':
                        self.tradesignalstrategy.calculate_signals(event)
                        self.portfolio.update_portfolio(event)
                    elif event.type == 'SIGNAL':
                        self.tradeenterstrategy.execute_signal(event)
                    elif event.type == 'ORDER':
                        self.transaction.execute_order(event)
            time.sleep(self.heartbeat)
            iters += 1

    def _output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        """
        print("Calculating Performance Metrics...")
        self.portfolio.output_results()

    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        self._run_backtest()
        self._output_performance()
        print("Backtest complete.")
