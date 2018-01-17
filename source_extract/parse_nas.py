import sys
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
import time
from selenium import webdriver
import json
from multiprocessing import Pool
import boto3
from lxml import html
import string
sys.path.insert(0, string.replace(sys.path[0], "source_extract", "parser"))
from pgDAO import pgDAO

class RatingSource:
    def __init__(self):
        self.order = 0
class RatingCard:
    def __init__(self):
        self.order = 0
def obj_dict(obj):
    return obj.__dict__

def parse_main_ticker_page(ticker):
    base_url = "http://www.nasdaq.com/symbol/{}/guru-analysis".format(ticker)
    #print(base_url)
    driver = webdriver.Chrome()
    driver.get(base_url)
    
    response = driver.find_element_by_id("left-column-div").get_attribute("innerHTML")
    response = BeautifulSoup(response, "html.parser")
    ticker_rating_tables = response.findAll("table", {"width" : "495"})
    externalRatings = []
    dao = pgDAO()
    for table in ticker_rating_tables:
        ratingDetails = table.select("tr > td > h2")
        if(len(ratingDetails)>0):
            ratingSource = RatingSource()
            ratingSource.source = ratingDetails[0].get_text()
            #print(ratingDetails[0].get_text())
            linkDetails = table.select("tr > td > h5 > a")
            ratingSource.rating = linkDetails[0].get_text()
            ratingSource.link = linkDetails[0]["href"]
            ratingSource.ticker = ticker
            externalRatings.append(ratingSource)
    #print(json.dumps(externalRatings, default=obj_dict))
    ratingCards = []
    for source in externalRatings:
        print(source.link)
        driver.get(source.link)
        response = driver.find_element_by_id("reportsctor").get_attribute("innerHTML")
        response = BeautifulSoup(response, "html.parser")
        reportCard = response.select("tr")
        ratingcard = RatingCard()
        for report in reportCard:
            name = report.select("td > b > b > a")
            if(len(name)>0):
                ratingcard.clasification = name[0].get_text()
                status = report.select("td > span")
                if(len(status)>0):
                    ratingcard .status = status[0].get_text()
                    #Extract the detail from DOM
                ratingcard.detail = ""
                ratingCards.append(ratingcard)
        nasKey = dao.getNas_Key(source)
        dao.delete_nasdaq(nasKey)
        dao.iNasdaq_Ticker(source, nasKey)
        for report in ratingCards:
            dao.iNasdaq_Report(report, nasKey)
    driver.quit()
    #print(json.dumps(externalRatings, default=obj_dict))
if __name__ == '__main__':
    if len(sys.argv) > 1:
        parse_main_ticker_page(sys.argv[1])