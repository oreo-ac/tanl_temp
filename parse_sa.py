from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
import time
from selenium import webdriver
import json
from multiprocessing import Pool
#from pyvirtualdisplay import Display
import boto3


def parse_main_earnings_page(inval):
    base_url = "https://seekingalpha.com/earnings/earnings-call-transcripts"
    href_base_url = "https://seekingalpha.com"
    url = base_url
    href_links = []
    page = inval
    exit_code = 0
    driver = webdriver.Chrome()
    while exit_code == 0 and page <= inval:
        # response = requests.get(url)
        # c = pycurl.Curl()
        # c.setopt(c.URL, url)
        # c.perform()
        # c.close()
        # response = c.getinfo(c.RESPONSE_CODE)
        # print (response)
        # response = BeautifulSoup(response, "html.parser")
        temp_text = ""
        temp_text1 = ""
        try:
            print("start:" + url)
            driver.get(url)
            if inval > 0:
                driver.get(base_url + "/" + str(inval))
            response = driver.find_element_by_tag_name("body").get_attribute("outerHTML")
            response = BeautifulSoup(response, "html.parser")
            exit_code = 0
            transcript_links = response.findAll("a", {"sasource": "earnings-center-transcripts_article"})
            try:
                temp_text = driver.find_element_by_link_text("Next Page").text
            except Exception as e:
                temp_text = ""

            try:
                temp_text1 = driver.find_element_by_link_text("1").text
            except Exception as e:
                temp_text1 = ""

            if len(transcript_links) == 0:
                if temp_text1 == "1":
                    exit_code = 1
                else:
                    print("Retrying..." + str(page))
                    driver.quit()
                    driver = webdriver.Chrome()
                    driver.get(base_url)

            else:
                for transcript in transcript_links:
                    title = transcript.get_text()
                    identifer = transcript["href"].split("/")[2].split("-")[0]
                    link = {
                        "id": identifer,
                        "name": title,
                        "url": href_base_url + transcript["href"]
                    }
                    href_links.append(link)
                    det_code = 0
                    while det_code == 0:
                        driver.get(href_base_url + transcript["href"] + "?part=single")
                        try:
                            response = driver.find_element_by_id("a-body").get_attribute("outerHTML")
                            det_code = 1
                        except Exception as e:
                            print("Retrying..." + transcript["href"].replace("/article", ""))
                            driver.quit()
                            driver = webdriver.Chrome()
                            driver.get(base_url)
                    print("Uploading: " + transcript["href"].replace("/article", ""))
                    upload_file(response, transcript["href"].replace("/article", ""))
                    print("Uploaded: " + transcript["href"].replace("/article", ""))

                print("end:" + url)
                print("Completed Successfully:" + str(page))
                page = page + 1

                url = base_url + "/" + str(page)
                # print (url)
        except Exception as e:
            print(e)
            print("Failed:" + str(page))
            exit_code = 1
    driver.quit()
    """


    for transcript in transcript_links:
        title = transcript.get_text()
        title_list = title.split(" Results - Earnings Call Transcript")
        name = title.split(" on ")[0]

        href_links.append({
            "name" : name,
            "url" : href_base_url + transcript["href"]
        })
    """

    return href_links


def loop_detail_earnings_page():
    multiplier = 0
    exit_code = 0
    while exit_code == 0 and multiplier < 1:
        cons_links = parse_main_earnings_page(multiplier)
        multiplier = multiplier + 1
        if len(cons_links) == 0:
            exit_code = 1


def upload_file(response, name):
    s3 = boto3.resource('s3')
    data = response.encode('utf-8')
    s3.Bucket('skinc-tanl-data').put_object(Key='transcripts' + name, Body=data)



def get_content_from_earnings(link):
    url = link["url"]
    response = requests.get(url).text
    response = BeautifulSoup(response, "html.parser")
    resp_body = response.body
    return resp_body


if __name__ == '__main__':
    #display = Display(visible=0, size=(800, 600))
    #display.start()
    loop_detail_earnings_page()
    #display.stop()
