from pandas_datareader import data, wb
import datetime
from dateutil.relativedelta import *
import pandas_datareader.data as web
from dateutil import parser

class StockPrice:
    def __init__(self):
        pass
    def getPrice(self, stock):
        if stock.get("endDate"):
            endDate = parser.parse(stock["endDate"])
        else:
            endDate = datetime.date.today()
        startDate = parser.parse(stock["startDate"])
        ticker = stock["ticker"]
        if stock.get("interval"):
            interval = stock["interval"]
            inetrvalIndicator = interval.lower()[0]
            if inetrvalIndicator=="m":
                interval ="mo"
                #Set 1st & Last Calender day of the Month
                startDate = startDate - relativedelta(days=startDate.day-1)
                endDate = endDate + relativedelta(months=1)
                endDate = endDate -  relativedelta(days= endDate.day)
            elif inetrvalIndicator=="w":
                interval = "wk"
                #Set Monday as start & Sunday as end date for search
                weekDay = startDate.weekday()
                if weekDay>0:
                    startDate = startDate - relativedelta(days=weekDay)
                weekDay = endDate.weekday()
                if weekDay>0:
                    endDate = endDate + relativedelta(days=6-weekDay)
            else:
                interval ="d"
        else:
            interval = "d"
        return web.get_data_yahoo(ticker,startDate, endDate,interval=interval)