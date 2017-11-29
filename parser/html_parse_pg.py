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


def parseHTML(htmlData):
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
            name, role = child.string.split("-", 1)
            callParticipant = Participant()
            callParticipant.name = name.strip()
            callParticipant.role = role.strip()
            executies.append(callParticipant)
    # SUMMARY DATA
    for summaryIndex in range(0, currentIndex):
        child = childElements[summaryIndex]
        innerAnchor = child.find("a")
        if innerAnchor and innerAnchor != -1:
            companyStockDetail = child.text
            # correct the regular expression
            exchange = next(iter(re.findall(r"\((.*?):*\)", companyStockDetail)), None).split(":")[0]
            stockName = next(iter(re.findall(r"\(*:(.*?)\)", companyStockDetail)), None)
            company = next(iter(re.findall(r"(.*?)\(", companyStockDetail)), None)
            quarterYearInfo = next(iter(re.findall(r"\](.*?)", companyStockDetail)), None)
            if (quarterYearInfo == None or len(quarterYearInfo) <= 7):  # Q4 2017
                quarterYearInfo = childElements[summaryIndex + 2].contents[0]
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
            name, company = child.string.split("-", 1)
            callParticipant = Participant()
            callParticipant.name = name.strip()
            callParticipant.company = company.strip()
            analysts.append(callParticipant)
            # analysts.update({name.strip():company.strip()})
    # UPDATES, QUESTION AND ANSWER
    qaSet = []
    currentIndex = index + 1
    updateStart = currentIndex
    for index in range(currentIndex, childLength):
        child = childElements[index]
        innerStrong = child.find("strong")
        if innerStrong and innerStrong != -1:
            content = innerStrong.contents[0]
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
# return json_string

# Main process
if len(sys.argv) > 1:
    dao = pgDAO()
    fin_words_df = pandas.read_csv('LM.csv')
    fin_words_df = fin_words_df[(fin_words_df.Positive > 0) | (fin_words_df.Negative > 0) | (fin_words_df.Uncertainty > 0)]
    fin_words_df = fin_words_df.query("Word != 'QUESTION' and Word !='QUESTIONS'")
    fin_words_list = fin_words_df["Word"].to_json(orient="records")
    fin_words_list = json.loads(fin_words_list)
    filePath = sys.argv[1]
    #client = boto3.client('dynamodb')
    for file in os.listdir(filePath):
        if file.endswith("-call-transcript"):
            file_location = os.path.join(filePath, file)
            with open(file_location, "r") as myfile:
                fileName = os.path.basename(myfile.name)
                folderPath = os.path.dirname(myfile.name)
                page = myfile.readlines()
            summary = parseHTML(page)
            summary.id = next(iter(re.findall(r"[0-9]*", file)), None)
            summary.tr_key = dao.getTr_Key(summary)
            dao.iTranscript(summary)
            for data in summary.analysts:
                data.an_key = dao.getAn_Key(data)
                dao.iAnalyst(data)
            for data in summary.executies:
                data.company = summary.company
                data.ex_key = dao.getEx_Key(data)
                dao.iExecutive(data)
            for data in summary.QAList:
                data.question = data.question.replace("\\'", "'")
                data.answer = data.answer.replace("\\'", "'")
                anKeys = [item.an_key for item in summary.analysts if item.name.lower() == data.questionedBy.lower()]
                exKeys = [item.ex_key for item in summary.executies if item.name.lower() == data.answeredBy.lower()]
                data.qa_key = hashlib.sha1(
                    json.dumps({"Question": data.question, "Answer": data.answer}, sort_keys=True).encode('utf-8')).hexdigest()
                data.tr_key = summary.tr_key
                data.questionASW = removeStopWords(data.question)
                data.answerASW = removeStopWords(data.answer)
                if (len(anKeys) > 0):
                    data.an_key = anKeys[0]
                else:
                    data.an_key = None
                if (len(exKeys) > 0):
                    data.ex_key = exKeys[0]
                else:
                    data.ex_key = None
                dao.iQA(data)
                keys = word_tokenize(data.questionASW)
                keys = list(filter(lambda d: check_if_exists_in_list(fin_words_list, d.upper()), keys))
                keys = ([(d, len(list(filter(lambda k: d in k, keys)))) for d in set(keys)])
                dao.iQAKeyword(keys, data.tr_key, data.qa_key, "Q")
                keys = word_tokenize(data.answerASW)
                keys = list(filter(lambda d: d.upper() in fin_words_list, keys))
                keys = ([(d, len(list(filter(lambda k: d in k, keys)))) for d in set(keys)])
                dao.iQAKeyword(keys, data.tr_key, data.qa_key, "A")
else:
    print("Expects HTML file root location")

