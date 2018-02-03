import sys
import json
import glob, os
from bs4 import BeautifulSoup
from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize, sent_tokenize
import pandas
import re
import boto3
import hashlib
import psycopg2
from pgDAO import pgDAO
from nltk.stem import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
import psycopg2
import hashlib
import json
import datetime
import sys

fin_words_df = pandas.read_csv('LM.csv')
fin_words_df = fin_words_df[(fin_words_df.Positive > 0) | (fin_words_df.Negative > 0) | (fin_words_df.Uncertainty > 0)]
fin_words_df = fin_words_df.query("Word != 'QUESTION' and Word !='QUESTIONS'")
fin_words_list = fin_words_df["Word"].to_json(orient="records")
fin_words_list = json.loads(fin_words_list)

fin_words_df_pos = fin_words_df[
    (fin_words_df.Positive > 0) & (fin_words_df.Negative == 0) & (fin_words_df.Uncertainty == 0)]
fin_words_list_pos = fin_words_df_pos["Word"].to_json(orient="records")
fin_words_list_pos = json.loads(fin_words_list_pos)

fin_words_df_neg = fin_words_df[
    (fin_words_df.Negative > 0) & (fin_words_df.Positive == 0) & (fin_words_df.Uncertainty == 0)]
fin_words_list_neg = fin_words_df_neg["Word"].to_json(orient="records")
fin_words_list_neg = json.loads(fin_words_list_neg)

fin_words_df_neu = fin_words_df[
    (fin_words_df.Uncertainty > 0) & (fin_words_df.Negative == 0) & (fin_words_df.Positive == 0)]
fin_words_list_neu = fin_words_df_neu["Word"].to_json(orient="records")
fin_words_list_neu = json.loads(fin_words_list_neu)
class pgDAO1:
    def __init__(self):
        pass

    def openConnection(self):
        try:
            self.myConnection = psycopg2.connect(host="tanl.cgnbxyetzh4a.us-east-1.rds.amazonaws.com", user="tanl",
                                             password="Semmakata$7", dbname="tanl")
        except:
            self.myConnection = psycopg2.connect(host="tanl.cgnbxyetzh4a.us-east-1.rds.amazonaws.com", user="tanl",
                                             password="Semmakata$7", dbname="tanl")

    def closeConnection(self):
        self.myConnection.close()

    def getConfig(self):
        self.openConnection()
        cur = self.myConnection.cursor()
        cur.execute("select distinct keyword from keywords")
        #print(cur.fetchall())
        for keyword in cur.fetchall():
            keyword = keyword[0]
            print(keyword)
            cnt = len(filter(lambda keyw: keyw.lower() == keyword.lower(), fin_words_list_pos))
            #print(cnt)
            sentiment=""
            if cnt>0:
                sentiment = "positive"
            else:
                cnt = len(filter(lambda keyw: keyw.lower() == keyword.lower(), fin_words_list_neg))
                #print(cnt)
                if cnt>0:
                    sentiment = "negative"
                else:
                    cnt = len(filter(lambda keyw: keyw.lower() == keyword.lower(), fin_words_list_neu))
                    #print(cnt)
                    if cnt>0:
                        sentiment = "neutral"
            print(sentiment)
            if len(sentiment)>0:
                sql = """update keywords set sentiment=%s where keyword=%s"""
                data = (sentiment,keyword)
                cur.execute(sql, data)
                self.myConnection.commit()
        self.closeConnection()
        #print(fin_words_list_pos)
if len(sys.argv):
    dao = pgDAO1()
    dao.getConfig()