from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
import time
from selenium import webdriver
import json
from multiprocessing import Pool
#from pyvirtualdisplay import Display
import boto3
from selenium.webdriver.common.action_chains import ActionChains
import scrapy

def parse_main_earnings_page(ticker, noYears):
    base_url = "https://seekingalpha.com/symbol/{}/earnings/transcripts"
    url = base_url.format(ticker)
    href_links = []
    exit_code = 0
    driver = webdriver.Chrome()
    driver.get(url)
    iCnt=1
    for iCnt in range(100):
        driver.execute_script("window.scrollTo(0, "+ str((iCnt+1)*100) +");")
    allLinks = driver.find_elements_by_tag_name('a')
    transcriptLinks = []
    for anchor in allLinks:
        linkURL = anchor.get_attribute("href")
        if(linkURL is not None ):
            linkURL= linkURL.lower()
            if(linkURL.endswith("results-earnings-call-transcript") or  (linkURL.endswith("transcript") and "call" in linkURL)):
                #transcriptLinks.append(linkURL.lower())
                transcriptLinks.append(anchor.get_attribute("href"))
                #print(anchor.get_attribute("href"))
                if(len(transcriptLinks)>12):
                    break
    driver.quit()
    for link in transcriptLinks:
        print(link +'?part=single')
        driver = webdriver.Chrome()
        driver.get('https://seekingalpha.com/earnings/earnings-call-transcripts')
        driver.get(link+'?part=single')       
        response = driver.find_element_by_id("a-body").get_attribute("outerHTML")
        data = response.encode('utf-8')
        print(link)
        driver.quit()
    #return transcriptLinks
def parse(response):
    print(respone)

def get_content_from_earnings(link):
    url = link["url"]
    response = requests.get(url).text
    response = BeautifulSoup(response, "html.parser")
    resp_body = response.body
    return resp_body


if __name__ == '__main__':
    ticker = "JPM"
    parse_main_earnings_page(ticker,4)