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
from elasticsearch import Elasticsearch
from textblob import TextBlob

import nltk
#nltk.download()
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
stop_words = set(stopwords.words('english'))

stop_words.add(".")
stop_words.add(",")
stop_words.add("%")


# stop_words.add("\\xe2\\x80\\x99")
class EarningsCall:
    def __init__(self):
        pass


class UpdateDetail:
    def __init__(self):
        self.order = 0


class QuestionAnswer:
    def __init__(self):
        self.sno = 0.0

class WordCount:
    def __init__(self):
        pass

class Participant:
    def __init__(self):
        pass


def obj_dict(obj):
    return obj.__dict__


def removeStopWords(data):
    word_tokens = word_tokenize(data.lower())
    tagged = nltk.pos_tag(word_tokens)
    tagged = list(filter(lambda d: d[1][0] == "N", tagged))
    #namedEnt = nltk.ne_chunk(tagged, binary=True)
    #print(namedEnt  )
    #print(list(filter(lambda d: d[0].lower() == "okay", tagged)))
    word_tokens = [d[0] for d in tagged]
    #for word,tag in tagged:
    #    print (word + "," + tag)
    filtered_sentence = [w for w in word_tokens if not (w.lower() in stop_words or w.upper() in stop_words)]
    return " ".join(filtered_sentence)

def getPercentage(part, total):
    if(part ==0):
        pct = round(0.0,2)
    else:
        pct = round(part / total, 2)
    return pct

def parseHTML(htmlData, pageId):
    summary = EarningsCall()
    soup = BeautifulSoup(str(htmlData), 'html.parser')
    body = soup.find("div", {"id": "a-body"})
    secCompleted = False
    childElements = list(body.children)
    childLength = len(childElements)
    currentIndex = 0
    # EXECUTIES
    executies = []
    for index in range(currentIndex, childLength):
        child = childElements[index]
        innerStrong = child.find("strong")
        if innerStrong and innerStrong != -1:
            content = innerStrong.contents[0]
            if content == "Executives":
                break
    currentIndex = index + 1
    for index in range(currentIndex, childLength):
        child = childElements[index]
        innerStrong = child.find("strong")
        if innerStrong and innerStrong != -1:
            content = innerStrong.contents[0]
            if content == "Analysts":
                break
        elif str(type(child)) == "<class 'bs4.element.Tag'>":
            #print(child.string)
            name, role = child.string.split("-", 1)
            callParticipant = Participant()
            callParticipant.name = name.strip() #+pageId
            callParticipant.role = role.strip()
            executies.append(callParticipant)
    # SUMMARY DATA
    for summaryIndex in range(0, currentIndex):
        child = childElements[summaryIndex]
        innerAnchor = child.find("a")
        if innerAnchor and innerAnchor != -1:
            companyStockDetail = child.text
            # correct the regular expression
            print(companyStockDetail)
            exchange = next(iter(re.findall(r"\((.*?):*\)", companyStockDetail)), None).split(":")[0]
            stockName = next(iter(re.findall(r"\(*:(.*?)\)", companyStockDetail)), None)
            company = next(iter(re.findall(r"(.*?)\(", companyStockDetail)), None)
            #quarterYearInfo = next(iter(re.findall(r"\](.*?)", companyStockDetail)), None)
            first, second = companyStockDetail.split(")", 1)
            
            if(second.strip()!=""):
                quarterYearInfo = second.strip()
            else:
                quarterYearInfo = None
            if (quarterYearInfo == None or len(quarterYearInfo) <= 7):  # Q4 2017
                if(str(type(childElements[summaryIndex + 2].contents[0])) == "<class 'bs4.element.NavigableString'>"):
                    quarterYearInfo = childElements[summaryIndex + 2].contents[0]
                else:
                    quarterYearInfo = childElements[summaryIndex + 2].contents[0].text
            quarter = ""
            year = ""
            if (quarterYearInfo != None and (
                    quarterYearInfo.lower().find("call") != -1 or quarterYearInfo.lower().find("earn") != -1)):
                if (quarterYearInfo[0].lower() == "q"):
                    quarter = quarterYearInfo[:2]
                    year = next(iter(re.findall(r"[0-9]{4,4}", quarterYearInfo)), None)
            summary.company = company.strip()
            summary.exchange = exchange.strip()
            summary.stock = stockName.strip()
            summary.quarter = quarter
            summary.year = year
            print(json.dumps(summary, default=obj_dict))
            break
    # ANALYSTS
    analysts = []
    currentIndex = index + 1
    for index in range(currentIndex, childLength):
        child = childElements[index]
        innerStrong = child.find("strong")
        if innerStrong and innerStrong != -1:
            content = innerStrong.contents[0]
            if content == "Operator":
                break
        elif str(type(child)) == "<class 'bs4.element.Tag'>":
            #print(child.string)
            #print(type(child.string))
            name, company = child.string.split("-", 1)
            callParticipant = Participant()
            callParticipant.name = name.strip()#+pageId
            callParticipant.company = company.strip()
            analysts.append(callParticipant)
            # analysts.update({name.strip():company.strip()})
    #print(json.dumps(analysts, default=obj_dict))
    # UPDATES, QUESTION AND ANSWER
    qaSet = []
    currentIndex = index + 1
    updateStart = currentIndex
    for index in range(currentIndex, childLength):
        child = childElements[index]
        innerStrong = child.find("strong")
        if innerStrong and innerStrong != -1:
            content = innerStrong.contents[0].strip()
            if content == "Question-and-Answer Session":
                break
    if (index > childLength):
        # IMPLEMENT:implement for older html with out header question section
        pass
    updates = []
    updateOrder = 1
    for updateIndex in range(updateStart, index):
        child = childElements[updateIndex]
        innerStrong = child.find("strong")
        if innerStrong and innerStrong != -1:
            if innerStrong.contents[0] != "Operator" and len(
                    child.contents) == 1 and innerStrong.string == child.string:
                updateBy = innerStrong.contents[0]
                updateDetail = ""
                updateIndex = updateIndex + 1
                while (updateIndex <= index):
                    child = childElements[updateIndex]
                    innerStrong = child.find("strong")
                    if innerStrong and innerStrong != -1 and len(
                            child.contents) == 1 and innerStrong.string == child.string:
                        # address for older version with out question section
                        break
                    if str(type(child)) == "<class 'bs4.element.Tag'>" and len(child.contents) > 0:
                        for dataIndex in range(0, len(child.contents)):
                            updateDetail = updateDetail + " " + str(child.contents[dataIndex])
                    updateIndex = updateIndex + 1
                update = UpdateDetail()
                update.by = updateBy
                # update.detail = removeStopWords(updateDetail)
                update.detail = updateDetail
                update.order = updateOrder
                updateOrder = updateOrder + 1
                updates.append(update)
    currentIndex = index + 1
    for index in range(currentIndex, childLength):
        child = childElements[index]
        innerStrong = child.find("strong")
        if innerStrong and innerStrong != -1:
            content = innerStrong.contents[0]
            if content == "Operator":
                break

    currentIndex = index + 1
    questionClass = "question"
    answerClass = "answer"
    QACount = 1.0
    while (currentIndex < childLength):
        question = ""
        answer = ""
        questionedBy = ""
        answeredBy = ""
        index = 0  # 0:Looking QBy;1:looking Q;2:Looking ABy;3:Looking A;4:addition answer;5:QA Populated
        while (index < 5 and currentIndex < childLength):
            child = childElements[currentIndex]
            innerStrong = child.find("strong")
            if innerStrong and innerStrong != -1 and len(list(innerStrong.children)) == 1:
                childContent = list(innerStrong.children)[0]
                if str(type(childContent)) == "<class 'bs4.element.Tag'>":
                    if index == 0 and childContent["class"][0] == questionClass:
                        index = 1
                        # questionedBy = innerStrong.string
                        #print(innerStrong)
                        questionedBy = innerStrong.string.split("-")[0].strip()
                    elif index == 2 and childContent["class"][0] == answerClass:
                        index = 3
                        # answeredBy = innerStrong.string
                        answeredBy = innerStrong.string.split("-")[0].strip()
                    elif index == 4:  # Skip as we reached next highlited P, So treat as next question section
                        index = 5
                        currentIndex = currentIndex - 1
            else:
                if child.name == "p":
                    if index == 1:
                        index = 2
                        question = child.string
                    elif index == 2 and child.string is not None:  # additional Question
                        question = question + " " + child.string
                    elif index == 3:
                        index = 4
                        answer = child.string
                    elif index == 4 and child.string is not None:  # additional Answer
                        answer = answer + " " + child.string
            currentIndex = currentIndex + 1
        if index == 5:
            # objectQA = QA(questionedBy, question, answeredBy, answer)
            objectQA = QuestionAnswer()
            # objectQA.question = removeStopWords(question)
            # objectQA.answer = removeStopWords(answer)
            objectQA.question = question
            objectQA.answer = answer
            objectQA.questionedBy = questionedBy
            objectQA.answeredBy = answeredBy
            objectQA.sno = QACount
            qaSet.append(objectQA)
            QACount = round(QACount + 1)

    summary.updates = updates
    summary.QAList = qaSet
    summary.analysts = analysts
    summary.executies = executies
    return summary

def check_if_exists_in_list(input_list, value):
    temp = list(filter(lambda d: d == value, input_list))
    if len(temp) > 0:
        return True
    else:
        return False

def get_sentiment_by_blob(text):
    blob = TextBlob(text)
    # determine if sentiment is positive, negative, or neutral
    if blob.sentiment.polarity < 0:
        dataSentiment = "negative"
    elif blob.sentiment.polarity == 0:
        dataSentiment = "neutral"
    else:
        dataSentiment = "positive"
    return dataSentiment

# Main process
if len(sys.argv) > 1:
    es = Elasticsearch(["https://search-tanl-nswk7nthqjskczmapaqzga3c2q.us-east-1.es.amazonaws.com"])
    stemmer = SnowballStemmer("english")
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

    filePath = sys.argv[1]
    for file in os.listdir(filePath):
        ques_words = []
        ans_words = []
        tr_key_temp = ""
        if file.endswith("-call-transcript"):
            file_location = os.path.join(filePath, file)
            with open(file_location, "r") as myfile:
                fileName = os.path.basename(myfile.name)
                folderPath = os.path.dirname(myfile.name)
                page = myfile.readlines()
            reference = fileName.split("-")[0]
            summary = parseHTML(page, reference)
            summary.id = next(iter(re.findall(r"[0-9]*", file)), None)
            iQAcnt =1
            for objectQA in summary.QAList:
                data = QuestionAnswer()
                data.company = summary.company
                data.ticker = summary.stock
                data.year = summary.year
                data.quarter = summary.quarter
                data.question = objectQA.question.replace("\\'", "'")
                data.answer = objectQA.answer.replace("\\'", "'")
                data.exchange = summary.exchange
                data.analyst_name = objectQA.questionedBy
                anKeys = [item for item in summary.analysts if item.name.lower() == objectQA.questionedBy.lower()]
                if (len(anKeys) > 0):
                    data.analyst_company = anKeys[0].company
                else:
                    data.analyst_company = ""
                data.executive_name = objectQA.answeredBy
                exKeys = [item for item in summary.executies if item.name.lower() == objectQA.answeredBy.lower()]
                data.executive_company = data.company
                if (len(exKeys) > 0):
                    data.executive_position = exKeys[0].role
                else:
                    data.executive_position = ""
                data.sentiment = get_sentiment_by_blob(data.question)
                data.answerSentiment = get_sentiment_by_blob(data.answer)
                qaJSON = json.dumps(data, default=obj_dict)
                #es.delete("qanda", "details", id = (int(reference) * 1000) +iQAcnt)
                es.index("qanda", "details", id = (int(reference) * 1000) +iQAcnt , body=qaJSON)
                #es.delete("qanda", "details", body={"query": {"match_all": {}}})
                
                #http://localhost:9200/qanda/details/<<increment_number>>
                #es.index(index="my-index", doc_type="test-type", id=str(data.refernceId)+"-"+str(iQAcnt), body=qaJSON)
                iQAcnt = iQAcnt +1
                #es.delete(index='my-index', doc_type='test-type')
                #es.delete(index="test", id=1) # delete id=2
                #es.indices.delete(index='test', ignore=[400, 404]) # remove all records
                #es.delete(index='test', ignore=[400, 404])
                #print(qaJSON)

else:
    print("Expects HTML file root location")
