# -*- coding: utf-8 -*-

from __future__ import print_function

from copy import deepcopy
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
import os

import pandas as pd

from qsforex.event.event import OrderEvent
from qsforex.performance.performance import create_drawdowns
from qsforex.portfolio.position import Position
from qsforex.settings import OUTPUT_RESULTS_DIR

class Portfolio(object):
    def __init__(
        self, ticker, events, transaction, base_currency="USD", 
        leverage=20, equity=Decimal("100000.00"), 
        risk_per_trade=Decimal("0.02"), backtest=True
    ):
        self.ticker = ticker
        self.events = events
        self.base_currency = base_currency
        self.leverage = leverage
        self.equity = equity
        self.balance = deepcopy(self.equity)
        self.risk_per_trade = risk_per_trade
        self.backtest = backtest
        self.trade_units = self.calc_risk_position_size()
        self.transaction = transaction
        if self.backtest:
            self.backtest_file = self.create_equity_file()

    def calc_risk_position_size(self):
        return self.equity * self.risk_per_trade

    def create_equity_file(self):
        filename = "backtest.csv"
        out_file = open(os.path.join(OUTPUT_RESULTS_DIR, filename), "w")
        header = "Timestamp,Balance"
        for pair in self.ticker.pairs:
            header += ",%s" % pair
        header += "\n"
        out_file.write(header)
        if self.backtest:
            print(header[:-2])
        return out_file

    def output_results(self):
        # Closes off the Backtest.csv file so it can be 
        # read via Pandas without problems
        self.backtest_file.close()
        
        in_filename = "backtest.csv"
        out_filename = "equity.csv" 
        in_file = os.path.join(OUTPUT_RESULTS_DIR, in_filename)
        out_file = os.path.join(OUTPUT_RESULTS_DIR, out_filename)

        # Create equity curve dataframe
        df = pd.read_csv(in_file, index_col=0)
        df.dropna(inplace=True)
        df["Total"] = df.sum(axis=1)
        df["Returns"] = df["Total"].pct_change()
        df["Equity"] = (1.0+df["Returns"]).cumprod()
        
        # Create drawdown statistics
        drawdown, max_dd, dd_duration = create_drawdowns(df["Equity"])
        df["Drawdown"] = drawdown
        df.to_csv(out_file, index=True)
        
        print("Simulation complete and results exported to %s" % out_filename)

    def update_position_price(self, openorder):
        instrument=openorder['instrument']
        pnl = 0
        quote_currency = instrument[3:]
        if quote_currency == self.base_currency:
            if openorder['side'] == 'buy':
                price = self.ticker.prices[instrument]['bid']
                _pnl = (price - openorder['price']) * openorder['units']
                pnl = _pnl.quantize(Decimal("0.01"), ROUND_HALF_DOWN)
                openorder["floatingpnl"] = pnl
            elif openorder['side'] == 'sell':
                price = self.ticker.prices[instrument]['ask']
                _pnl = (openorder['price'] - price) * openorder['units']
                pnl = _pnl.quantize(Decimal("0.01"), ROUND_HALF_DOWN)
                openorder["floatingpnl"] = pnl
            return(pnl)
        else:
            quote_currency_pair = "%s%s" % (quote_currency, self.base_currency)
            if openorder['side'] == 'buy':
                price = self.ticker.prices[instrument]['bid']
                _pnl = (price - openorder['price']) * openorder['units'] * self.ticker.prices[quote_currency_pair]['bid']
                pnl = _pnl.quantize(Decimal("0.01"), ROUND_HALF_DOWN)
                openorder["floatingpnl"] = pnl
            elif openorder['side'] == 'sell':
                price = self.ticker.prices[instrument]['ask']
                _pnl = (openorder['price'] - price) * openorder['units'] * self.ticker.prices[quote_currency_pair]['ask']
                pnl = _pnl.quantize(Decimal("0.01"), ROUND_HALF_DOWN)
                openorder["floatingpnl"] = pnl
            return(pnl)
         

    def update_portfolio(self, tick_event):
        """
        This updates all positions ensuring an up to date
        unrealised profit and loss (PnL).
        """
        PnL = Decimal("0")
        # Close orders by stoploss and takeprofit
        openorders=self.transaction.get_open_orders()
        for openorder in openorders:
            PnL = PnL + self.transaction.orders_stoploss_takeprofit(self.ticker, openorder)

        # TODO: stop and limit order

        # TODO: marketiftouched order

        # TODO: trailing

        # Calculate profit and loss by open orders
        FloatingPnL = Decimal("0")
        openorders=self.transaction.get_open_orders()
        for openorder in openorders:
            FloatingPnL = FloatingPnL + self.update_position_price(openorder)

        self.balance = self.balance + PnL
        self.equity = self.balance + FloatingPnL
 
#        if self.backtest:
#            out_line = "%s,%s,%s" % (tick_event.time, self.balance, self.equity)
#        for pair in self.ticker.pairs:
#             out_line +=  ",%s,%s,%s" % (pair, self.ticker.prices[pair]['bid'], self.ticker.prices[pair]['ask'])
#        print(out_line)
#        self.backtest_file.write(out_line)
        
#        openorders=self.transaction.get_open_orders()
#        if len(openorders) >= 1:
#            for i in openorders:
#                print (i)
#            print("\n")

