# -*- coding: utf-8 -*-

class Event(object):
    pass


class TickEvent(Event):
    def __init__(self, instrument, time, bid, ask):
        self.type = 'TICK'
        self.instrument = instrument
        self.time = time
        self.bid = bid
        self.ask = ask

    def __str__(self):
        return "Type: %s, Instrument: %s, Time: %s, Bid: %s, Ask: %s" % (
            str(self.type), str(self.instrument), 
            str(self.time), str(self.bid), str(self.ask)
        )

    def __repr__(self):
        return str(self)


class SignalEvent(Event):
    def __init__(self, instrument, order_type, side, time):
        self.type = 'SIGNAL'
        self.instrument = instrument
        self.order_type = order_type
        self.side = side
        self.time = time  # Time of the last tick that generated the signal

    def __str__(self):
        return "Type: %s, Instrument: %s, Order Type: %s, Side: %s" % (
            str(self.type), str(self.instrument), 
            str(self.order_type), str(self.side)
        )

    def __repr__(self):
        return str(self)


class OrderEvent(Event):
    def __init__(self, instrument, units, side, order_type, expiry=None, price=None, lowerBound=None, upperBound=None, stopLoss=None, takeProfit=None, trailingStop=None):
        self.type = 'ORDER'
        self.instrument = instrument
        self.units = units
<<<<<<< HEAD
        self.order_type = order_type
        self.side = side

    def __str__(self):
        return "Type: %s, Instrument: %s, Units: %s, Order Type: %s, Side: %s" % (
            str(self.type), str(self.instrument), str(self.units),
            str(self.order_type), str(self.side)
        )

    def __repr__(self):
        return str(self)
=======
        self.side = side        
        self.order_type = order_type
        self.expiry = expiry
        self.price = price
        self.lowerBound = lowerBound
        self.upperBound = upperBound
        self.stopLoss = stopLoss
        self.takeProfit = takeProfit
        self.trailingStop = trailingStop
>>>>>>> nkm/master
