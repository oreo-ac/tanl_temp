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

class TranscriptSpider(scrapy.Spider):
     name = 'transcripts'
     start_urls = ['"https://seekingalpha.com/symbol/JPM/earnings/transcripts"']
     lsURL = ['https://seekingalpha.com/article/4113161-jp-morgan-chase-jpm-q3-2017-results-earnings-call-transcript','https://seekingalpha.com/article/4087810-jpmorgan-chases-jpm-ceo-jamie-dimon-q2-2017-results-earnings-call-transcript','https://seekingalpha.com/article/4062354-jpmorgan-chases-jpm-ceo-jamie-dimon-q1-2017-results-earnings-call-transcript','https://seekingalpha.com/article/4036816-jpmorgan-chase-jpm-ceo-jamie-dimon-q4-2016-results-earnings-call-transcript']
     for href in lsURL:
         print(href)

    def parse(self, response):
        print(respone)