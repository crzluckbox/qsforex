# -*- coding: utf-8 -*- 
# Copyright (c) 2015 NAKATA Maho All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import calendar
import copy
import lzma
from datetime import datetime as dt
from datetime import date, time
import datetime
import os, os.path
import sys
from pytz import timezone
import pytz
import urllib
from struct import *

import numpy as np
import pandas as pd

from qsforex import settings

if __name__ == "__main__":
    try:
        symbol = sys.argv[1]
        period = sys.argv[2]
    except IndexError:
        print("You need to enter a currency symbol, e.g. GBPUSD, and period YYMM as a command line parameter.")
    else:
        tdatetime = dt.strptime(period, '%Y%m')
        week, days = calendar.monthrange(tdatetime.year, tdatetime.month)
        y = tdatetime.year
        m = tdatetime.month
        for d in range(1,days+1):
            for h in range(0,24):
                dd = dt.combine(date(y, m, d),time(h, 0))
                currentdt=dt.now(pytz.utc)
                # Don't process future tickdata
                _dd = pytz.utc.localize(dd)
                if (_dd > currentdt):
	             continue
                # Market opens 00:00-23:59 and Monday-Friday by EET, EST               
                eet=pytz.utc.localize(dd).astimezone(pytz.timezone('Europe/Athens'))
                eet.replace(tzinfo=None)
                if ( eet.isoweekday() >= 6 ):
	            continue 
		#download
                url = "http://www.dukascopy.com/datafeed/%s/%02d/%02d/%02d/%02dh_ticks.bi5" % (symbol, y, m-1, d, h)
                file = settings.CSV_DATA_DIR + "%s_%02d_%02d_%02d_%02dh_ticks.bi5" % (symbol, y, m, d, h)
                print "now downloading %s..." % url
                urllib.urlretrieve(url, file)

	#Download has been finished

        for d in range(1,days+1):
            if ( date(y, m, d).isoweekday() == 6 ): #on UTC Saturday is always closed.
                 continue
            outcsv=settings.CSV_DATA_DIR + "%s_%02d%02d%02d.csv" % (symbol, y, m, d)
            ff = open(outcsv, 'w')
            for h in range(0,24):
                dd = dt.combine(date(y, m, d),time(h, 0))
                currentdt=dt.now(pytz.utc)
                # Don't process future tickdata
                _dd = pytz.utc.localize(dd)
                if (_dd > currentdt):
                     ff.close() 
	             quit()
                # Market opens 00:00-23:59 and Monday-Friday by EET, EST               
                eet=pytz.utc.localize(dd).astimezone(pytz.timezone('Europe/Athens'))
                eet.replace(tzinfo=None)
                if ( eet.isoweekday() >= 6 ):
	            continue 

                file = settings.CSV_DATA_DIR + "%s_%02d_%02d_%02d_%02dh_ticks.bi5" % (symbol, y, m, d, h)
                try:
                    f = open(file, "r") 
                except IOError:
		    continue
                a = f.read()
                try:
		    b = lzma.decompress(a)
		except:
                    os.remove(file)
	            continue
                os.remove(file)

	        if (len(b) == 0 ):
			continue
		for _b in range(len(b)/20):
		    (__second, __ask, __bid, __askvol, __bidvol) = unpack('>IIIff',b[_b*20:((_b+1)*20)])
		    if 'ZARJPY' in symbol:
                        ask = float(__ask) / 100000
                        bid = float(__bid) / 100000
                    elif  'JPY' in symbol:
                        ask = float(__ask) / 1000
                        bid = float(__bid) / 1000
                    else:
                        ask = float(__ask) / 100000
                        bid = float(__bid) / 100000
                    __time= dd + datetime.timedelta(0,float(__second)/1000)
                    _tstr = __time.strftime('%Y.%m.%d %H:%M:%S.%f')
                    tstr = _tstr[0:23]
                    _str = tstr + "," + str(bid) + "," + str(ask) + ",%.2f" % __bidvol + ",%.2f" % __askvol + "\n"
                    ff.write(_str)
            ff.close() 

