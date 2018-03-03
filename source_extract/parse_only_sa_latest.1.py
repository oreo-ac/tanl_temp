import sys
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
from html_parse_ESLoader import ESLoader
import glob, os
import shutil
def parse_main_earnings_page(filePath):
    esLoader = ESLoader()
    #processed =[]
    #errored =[]
    success =0
    failure =0
    for file in list(set(os.listdir(filePath))):
        if file.endswith("-call-transcript"):
            file_location = os.path.join(filePath, file)
            with open(file_location, "r") as myfile:
                fileName = os.path.basename(myfile.name)
                page = myfile.readlines()
                #try:
                    #print(file_location)
                esLoader.maincall(page, fileName)
                    #processed.append(fileName)
                success = success+1
                '''except:
                    print("---------------------failed-----------------------")
                    failure = failure +1
                    #error.append(fileName)
                '''
    '''for name in processed:
        shutil.move(filePath+"\\"+fileName, filePath+"\\processed\\"+fileName)
    for name in errored:
        shutil.move(filePath+"\\"+fileName, filePath+"\\error\\"+fileName)
    '''
    print("failure: " + str(failure))
    print("success: " + str(success))
def parse(response):
    print(respone)

def get_content_from_earnings(link):
    url = link["url"]
    response = requests.get(url).text
    response = BeautifulSoup(response, "html.parser")
    resp_body = response.body
    return resp_body

if __name__ == '__main__':
    print(1)
    parse_main_earnings_page(sys.argv[1])