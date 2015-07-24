# -*- coding: utf-8 -*-

from __future__ import print_function

from abc import ABCMeta, abstractmethod
try:
    import httplib
except ImportError:
    import http.client as httplib
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
import urllib3
urllib3.disable_warnings()

class TransactionHandler(object):
    """
    Provides an abstract base class to handle all execution in the
    backtesting and live trading system.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self):
        """
        Send the order to the brokerage.
        """
        raise NotImplementedError("Should implement execute_order()")


class SimulatedTransaction(object):
    """
    Ticket: contains following data
      ticket ID, units, side, instrument, open time, closed/cancelled time, expiration time,
      open price, closed price, profit, takeProfit, stopLoss, trailingStop, trailingAmount, 
      status (open, closed, pending order, cancelled pending order)
 
    ** for partial close, just create new ID and copy the orginal TicketID.
    Transaction: contains following data
     transaction ID, accound ID, time, type
           MARKET_ORDER_CREATE , STOP_ORDER_CREATE, LIMIT_ORDER_CREATE, MARKET_IF_TOUCHED_ORDER_CREATE,
           ORDER_UPDATE, ORDER_CANCEL, ORDER_FILLED, TRADE_UPDATE, TRADE_CLOSE, MIGRATE_TRADE_OPEN,
           MIGRATE_TRADE_CLOSE, STOP_LOSS_FILLED, TAKE_PROFIT_FILLED, TRAILING_STOP_FILLED, MARGIN_CALL_ENTER,
           MARGIN_CALL_EXIT, MARGIN_CLOSEOUT, SET_MARGIN_RATE, TRANSFER_FUNDS, DAILY_INTEREST, FEE
     instrument, side, units, price, lowerBound, upperBound, takeProfitPrice, stopLossPrice
     trailingStopLossDistance, pl (profit/loss), interst, accountBalance,
     tradeOpened (ticket id, units), tradeReduced (ticket id, units, pl, interest)
    """
    def __init__(self):
	self.__TransactionID__=0
	self.__TicketID__=0
        self.__Transaction__ =[]
        self.__OpenTickets__ =[]

    def _order_open(self, ticker, instrument, units, side, order_type, expiary=None, price=None, lowerBound=None, upperBound=None, stopLoss=None, takeProfit=None, trailingStop=None, comment=None, magicnumber=None):
        
        # order is always successful
        newTransaction= {"id" : self.__TransactionID__, "units" : units, "side" : side, "type" : order_type } 
        self.__Transaction__.append(newTransaction)
	self.__TicketID__=self.__TicketID__+1
        self.__TransactionID__=self.__TransactionID__+1
        print (ticker.prices[instrument]["time"]) //price
        ResponseTonewTransaction= { "instrument" : instrument, "time" : "0", "price" : 1.2 }
        return ResponseTonewTransaction
        
    def _order_modify(self, ticketID):
        self.__TransactionID__=self.__TransactionID__+1

    def _order_close(self, ticketID):
        self.__TransactionID__=self.__TransactionID__+1

#    def get_open_orders(self):
 
#    def order_info(self, ticketID):
                


class OANDATransactionHandler(TransactionHandler):
    def __init__(self, domain, access_token, account_id):
        self.domain = domain
        self.access_token = access_token
        self.account_id = account_id
        self.conn = self.obtain_connection()

    def obtain_connection(self):
        return httplib.HTTPSConnection(self.domain)

    def execute_order(self, event):
        instrument = "%s_%s" % (event.instrument[:3], event.instrument[3:])
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer " + self.access_token
        }
        params = urlencode({
            "instrument" : instrument,
            "units" : event.units,
            "type" : event.order_type,
            "side" : event.side
        })
        self.conn.request(
            "POST", 
            "/v1/accounts/%s/orders" % str(self.account_id), 
            params, headers
        )
        response = self.conn.getresponse().read()
        print(response)
        