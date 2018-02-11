from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
import time
from selenium import webdriver
import json
from multiprocessing import Pool
#from pyvirtualdisplay import Display
import boto3
from selenium.webdriver.common.action_chains import ActionChains


def parse_main_earnings_page(ticker, noYears):
    base_url = "https://seekingalpha.com/symbol/{}/earnings/transcripts"
    url = base_url.format(ticker)
    href_links = []
    exit_code = 0
    driver = webdriver.Chrome()
    driver.get(url)
    #for iCnt in range(noYears*8):
    #    driver.execute_script("window.scrollTo(0, "+ str((iCnt+1)*100) +");")
    allLinks = driver.find_elements_by_tag_name('a')
    transcriptLinks = []
    for anchor in allLinks:
        linkURL = anchor.get_attribute("href")
        if(linkURL is not None ):
            linkURL= linkURL.lower()
            if(linkURL.endswith("results-earnings-call-transcript") or  (linkURL.endswith("transcript") and "call" in linkURL)):
                #transcriptLinks.append(linkURL.lower())
                print(anchor.get_attribute("href"))
                #driver.execute_script("arguments[0].scrollIntoView();", anchor)
                time.sleep(2)
                #anchor.send_keys(webdriver.common.keys.Keys.SPACE)
                #my_variable = driver.find_element_by_xpath('//*[@id="myId"]') #this is the checkbox
                anchor.send_keys(webdriver.common.keys.Keys.SPACE)
                print(1)
                time.sleep(100)
                break
    driver.quit()
    '''for link in transcriptLinks:
        driver = webdriver.Chrome()
        driver.get(link)       
        response = driver.find_element_by_id("a-body").get_attribute("outerHTML")
        data = response.encode('utf-8')
        print(link.replace("/article", ""))
    '''
    return transcriptLinks

def get_content_from_earnings(link):
    url = link["url"]
    response = requests.get(url).text
    response = BeautifulSoup(response, "html.parser")
    resp_body = response.body
    return resp_body


if __name__ == '__main__':
    ticker = "JPM"
    parse_main_earnings_page(ticker,4)