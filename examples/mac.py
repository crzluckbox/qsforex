from __future__ import print_function

from qsforex.backtest.backtest import Backtest
from qsforex.transaction.transaction import SimulatedTransaction
from qsforex.portfolio.portfolio import Portfolio
from qsforex import settings
from qsforex.strategy.strategy import MovingAverageCrossStrategy
from qsforex.strategy.strategy import tradeEnterStrategy
from qsforex.strategy.strategy import tradeExitStrategy
from qsforex.data.price import HistoricCSVPriceHandler


if __name__ == "__main__":
    # Trade on GBP/USD and EUR/USD
#    pairs = ["EURUSD"]
    pairs = ["USDCHF"]
    
    # Create the strategy parameters
    MovingAverageCrossStrategy_params = {
        "short_window": 500, 
        "long_window": 2000
    }
    tradeEnterStrategy_params = {
        "takeprofit": 500, 
        "stoploss":   200,
        "maxpositions": 10,
        "units": 100000
    }
    tradeExitStrategy_params = {
        "takeprofit": 500, 
        "stoploss":   200
    }
    # Create and execute the backtest
    backtest = Backtest(
        pairs, HistoricCSVPriceHandler, 
        MovingAverageCrossStrategy, MovingAverageCrossStrategy_params,
        tradeEnterStrategy, tradeEnterStrategy_params,
        tradeExitStrategy, tradeExitStrategy_params,
        Portfolio, SimulatedTransaction,
        equity=settings.EQUITY, base_currency=settings.BASE_CURRENCY,
        startday=20150413, endday=20150417
    )
    backtest.simulate_trading()
