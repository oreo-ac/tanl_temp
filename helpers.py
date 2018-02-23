import requests
from textblob import TextBlob
import json
import nltk
from nltk.corpus import stopwords, words
from nltk.stem.snowball import SnowballStemmer
import collections

stemmer = SnowballStemmer("english")
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
stop_words.add(".")
stop_words.add(",")
stop_words.add("%")
es_url = "https://search-tanl-nswk7nthqjskczmapaqzga3c2q.us-east-1.es.amazonaws.com/"
search_type_index = "search/types/"
qanda_index = "qanda/details/"
user_index = "users/details/"

def get_search_types(text):
    temp = TextBlob(text)
    temp = temp.words
    temp = "* OR *".join(temp)
    url = es_url + search_type_index + "_search?size=10000&q=search_words:(*" + temp + "*)" 
    response = requests.get(url=url)
    if str(response.status_code) == "200":
        results = json.loads(response.text)["hits"]
    else:
        results = []
    return results


def get_users(userid, password):
    url = es_url + user_index + "_search?size=10000&q=userid:(" + userid + ")" 
    response = requests.get(url=url)
    temp = 1
    if str(response.status_code) == "200":
        results = json.loads(response.text)["hits"]["hits"]
        if len(results) >0:
            if results[0]["_source"]["password"] == password:
                temp=0
            else:
                temp = 2 
        else:
            temp = 1
    else:
        temp = 1
    return temp


def clean_search_text(search_text):
    temp = TextBlob(search_text)
    temp = temp.words

    temp_year = list(filter(lambda d: len(str(d)) == 4, temp))
    temp_year = list(filter(lambda d: str(d)[0] in ["1", "2", "3", "4", "5", "6", "7", "8", "9"], temp_year))
    temp_year = list(filter(lambda d: str(d)[1] in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"], temp_year))
    temp_year = list(filter(lambda d: str(d)[2] in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"], temp_year))
    temp_year = list(filter(lambda d: str(d)[3] in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"], temp_year))
    year = []
    if len(temp_year) > 0:
        year = temp_year
    temp_quarter = list(filter(lambda d: len(str(d)) == 2, temp))
    temp_quarter = list(filter(lambda d: str(d)[0].lower() == "q", temp_quarter))
    temp_quarter = list(filter(lambda d: str(d)[1] in ["1", "2", "3", "4"], temp_quarter))
    quarter = []
    if len(temp_quarter) > 0:
        quarter = temp_quarter

    yearquarter = []
    if len(year) > 0:
        for y in year:
            if len(quarter) > 0:
                for q in quarter:
                    yearquarter.append({
                        "bool" :
                            { "must":[
                                    { "term" : {"year.keyword" : str(y)}},
                                    { "term" : {"quarter.keyword" : str(q).upper()}}
                                ]
                            }
                    })
            else:
                yearquarter.append({
                        "bool" :
                            { "must":[
                                    { "term" : {"year.keyword" : str(y)}}
                                ]
                            }
                    })
    else:
        for q in quarter:
            yearquarter.append({
                "bool" :
                    { "must":[
                            { "term" : {"quarter.keyword" : str(q).upper()}}
                        ]
                    }
            })
    temp_ticker = []
    for t in temp:
        temp_ticker.append({
            "term": {
                "ticker.keyword": str(t).upper()
            }
        })
    
    return year, quarter, temp_ticker, yearquarter

def get_data(cl, search_type, inp_year, inp_quarter, temp_keywords, yearquarter, search_context="chart"):
    input_json = get_input_json(temp_keywords, yearquarter, search_context)
    url = es_url + qanda_index + "_search"
    headers = {"Content-Type" : "application/json"}
    response = requests.post(url=url, data=json.dumps(input_json), headers=headers)
    total_questions = 0
    total_positive_questions = 0
    total_neutral_questions = 0
    total_negative_questions = 0
    total_transcripts = 0
    total_analysts = 0
    analyst_container = []
    main_container = []
    questions = []
    tickers = []
    questions = []
    allquestions = []

    if str(response.status_code) == "200":
        if search_context == "table":
            #questionandanswer=[]
            questions_output = json.loads(response.text)["hits"]["hits"]
            for question in questions_output:
                blob = TextBlob(question["_source"]["question"], classifier=cl)
                questions.append({
                    "year": question["_source"]["year"],
                    "quarter": question["_source"]["quarter"],
                    "company": question["_source"]["company"],
                    "question": question["_source"]["question"],
                    "sentiment": question["_source"]["sentiment"],
                    "category": blob.classify(),
                    "answer": question["_source"]["answer"],
                    "questionandanswer": "Q: " + question["_source"]["question"] + "<br/>   A: " + question["_source"]["answer"]
                })
                allquestions.append({"questions": question["_source"]["question"]})
                #questionandanswer.append({"questionandanswer" : "Q: " + question["_source"]["question"] + "A:" + question["_source"]["answer"]})
            result = {
                "table_container": questions
            }
            return result

        # TODO questionText = " ".join(q["questions"] for q in allquestions)
        # TODO blob = TextBlob(questionText.lower())
        # TODO words = [word for word in blob.words if word not in stop_words]
        # TODO wordCloud = ([(word, len(list(filter(lambda k: word in k, words)))) for word in set(words)])

        if search_context == "ticker":
            ticker_output = json.loads(response.text)["aggregations"]["tickerAgg"]["buckets"]
            for ticker in ticker_output:
                tickers.append(ticker["key"])

            result = {
                "search_results": {
                    "tickers": tickers,
                    "years": inp_year,
                    "quarters": inp_quarter,
                    "report_types": []
                }
            }
            return result

        if search_context == "analyst":
            analyst_output = json.loads(response.text)["aggregations"]["analystAgg"]["buckets"]
            for analyst in analyst_output:
                positive_cnt = list(filter(lambda d: d["key"] == "positive", analyst["sentimentAgg"]["buckets"]))
                if len(positive_cnt) > 0:
                    positive_cnt = positive_cnt[0]["doc_count"]
                else:
                    positive_cnt = 0
                
                negative_cnt = list(filter(lambda d: d["key"] == "negative", analyst["sentimentAgg"]["buckets"]))
                if len(negative_cnt) > 0:
                    negative_cnt = negative_cnt[0]["doc_count"]
                else:
                    negative_cnt = 0

                neutral_cnt = list(filter(lambda d: d["key"] == "neutral", analyst["sentimentAgg"]["buckets"]))
                if len(neutral_cnt) > 0:
                    neutral_cnt = neutral_cnt[0]["doc_count"]
                else:
                    neutral_cnt = 0
                
                total_cnt = positive_cnt + negative_cnt + neutral_cnt
                if total_cnt > 0:
                    positive_pct = (positive_cnt/total_cnt*100)
                    negative_pct = (negative_cnt/total_cnt*100)
                    neutral_pct = (neutral_cnt/total_cnt*100)
                else:
                    positive_pct = 0
                    negative_pct = 0
                    neutral_pct = 0
                winner = ""
                if positive_pct > negative_pct and positive_pct > neutral_pct:
                    winner = "positive"
                elif negative_pct > positive_pct and negative_pct > neutral_pct:
                    winner = "negative"
                else:
                    winner = "neutral"

                analyst_container.append({
                    "name": analyst["key"],
                    "positive_pct": round(positive_pct,0),
                    "negative_pct": round(negative_pct,0),
                    "neutral_pct": round(neutral_pct,0),
                    "pattern": winner
                })
            result = {
                "analyst_container": analyst_container
            }
            return result

        if search_context == "chart":
            main_output = json.loads(response.text)["aggregations"]["yearAgg"]["buckets"]
            main_container = {}
            temp_container = []
            temp_container1 = []
            temp_dict = {}
            for year in main_output:
                temp_dict = {}
                for quarter in year["quarterAgg"]["buckets"]:
                    for ticker in quarter["tickerAgg"]["buckets"]:
                        total_transcripts = total_transcripts + 1
                        positive_cnt = list(filter(lambda d: d["key"] == "positive", ticker["sentimentAgg"]["buckets"]))
                        if len(positive_cnt) > 0:
                            positive_cnt = positive_cnt[0]["doc_count"]
                        else:
                            positive_cnt = 0
                        
                        negative_cnt = list(filter(lambda d: d["key"] == "negative", ticker["sentimentAgg"]["buckets"]))
                        if len(negative_cnt) > 0:
                            negative_cnt = negative_cnt[0]["doc_count"]
                        else:
                            negative_cnt = 0

                        neutral_cnt = list(filter(lambda d: d["key"] == "neutral", ticker["sentimentAgg"]["buckets"]))
                        if len(neutral_cnt) > 0:
                            neutral_cnt = neutral_cnt[0]["doc_count"]
                        else:
                            neutral_cnt = 0
                        total_cnt = positive_cnt + negative_cnt + neutral_cnt
                        if total_cnt > 0:
                            positive_pct = (positive_cnt/total_cnt*100)
                            negative_pct = (negative_cnt/total_cnt*100)
                            neutral_pct = (neutral_cnt/total_cnt*100)
                        else:
                            positive_pct = 0
                            negative_pct = 0
                            neutral_pct = 0
                        winner = ""

                        if positive_pct > negative_pct and positive_pct > neutral_pct:
                            winner = "positive"
                        elif negative_pct > positive_pct and negative_pct > neutral_pct:
                            winner = "negative"
                        else:
                            winner = "neutral"


                        temp_dict = {
                            "group": ticker["key"] + " " + str(year["key"]) + " " + str(quarter["key"]),
                            "sort1": str(year["key"]) + " " + str(quarter["key"]) + ticker["key"],
                            "group1": str(year["key"]) + " " + str(quarter["key"]),
                            "ticker": ticker["key"],
                            ticker["key"] + "-pv_pct": round(positive_pct, 0),
                            ticker["key"] + "-nv_pct": round(negative_pct, 0),
                            ticker["key"] + "-nt_pct": round(neutral_pct,0),
                            "result": [
                                {
                                    "label": "positive",
                                    "value": round(positive_pct, 0),
                                    "color": "#00a65a"
                                },
                                {
                                    "label": "negative",
                                    "value": round(negative_pct, 0),
                                    "color": "#f56954"
                                },
                                {
                                    "label": "neutral",
                                    "value": round(neutral_pct,0),
                                    "color": "#3c8dbc"
                                }
                            ],
                        }
                        temp_dict["positive"] = round(positive_pct, 0)
                        temp_dict["negative"] = round(negative_pct, 0)
                        temp_dict["neutral"] = round(neutral_pct, 0)
                        temp_container.append(temp_dict)


            if len(search_type) > 0:
                default_chart = search_type[0]["_source"]["default_chart"]
            else:
                default_chart = "pie"
            result_dict = {}
            y_keys = []
            y_labels = []
            colors = []
            if len(tickers) > 1:
                samples = [("positive","#00a65a"), ("negative", "#f56954"), ("neutral","#3c8dbc")]
                for sample in samples:
                    for ticker in tickers:
                        #y_keys = y_keys + [ticker + "-positive", ticker + "-negative", ticker + "-neutral"]
                        #y_labels =y_labels +  [ticker + "-positive", ticker + "-negative", ticker + "-neutral"]
                        #colors = colors + ["#00a65a", "#f56954", "#3c8dbc"]
                        y_keys.append(ticker + "-" + sample[0])
                        y_labels.append(ticker + "-" + sample[0])
                        colors.append(sample[1])
                temp_loop = list(set([d["group1"] for d in temp_container]))
                for cont in temp_loop:
                    temp_list = list(filter(lambda d: d["group1"]== cont, temp_container))
                    temp_dict = {
                                "group1": cont,
                                "sort1": cont
                            }
                    for li in temp_list:
                        temp_dict[li["ticker"] + "-positive"] = li[li["ticker"] + "-pv_pct"]
                        temp_dict[li["ticker"] + "-negative"] = li[li["ticker"] + "-nv_pct"]
                        temp_dict[li["ticker"] + "-neutral"] = li[li["ticker"] + "-nt_pct"]
                    temp_container1.append(temp_dict)
                temp_container1 = sorted(temp_container1, key=lambda k: k['sort1'], reverse=True)
                result_dict["data1"] = temp_container1
            else:
                y_keys = ["positive", "negative", "neutral"]
                y_labels = ["positive", "negative", "neutral"]
                colors = ["#00a65a", "#f56954", "#3c8dbc"]
                temp_container = sorted(temp_container, key=lambda k: k['sort1'], reverse=True)
                result_dict["data1"] = temp_container
            result_dict["y_keys"] = y_keys
            result_dict["y_labels"] = y_labels
            result_dict["x_key"] = 'group1'
            result_dict["chartType"] = default_chart
            result_dict["colors"] = colors
            result_dict["data"] = temp_container    
            result_dict["questions"] = allquestions

            main_container = result_dict

            result = {
                "main_container": main_container
            }
            return result
    else:
        print("Error:" + str(response.text))
        return []

def get_input_json(temp_keywords, yearquarter, search_context):
    query_input = {
                "constant_score": {
                    "filter": {
                        "bool": {
                            "must": [
                                {"bool": {
                                    "should": temp_keywords
                                }
                                },
                                {"bool": {
                                    "should": yearquarter
                                }
                                }
                            ]
                        }
                    }
                }
            }


    if search_context == "table":
        input_json = {
            "_source": {
                "includes": ["year", "quarter", "question", "sentiment", "company", "answer"]
            },
            "size": 1000,
            "query": query_input
        }
    elif search_context == "ticker":
        input_json = {
            "query": query_input,
            "aggs": {
                "tickerAgg": {
                    "terms": {
                        "field": "ticker.keyword"
                    }
                }
            }
        }
    elif search_context == "analyst":
        input_json = {
            "query": query_input,
            "aggs": {
                "analystAgg": {
                    "terms": {
                        "field": "analyst_name.keyword"
                    },
                    "aggs": {
                        "sentimentAgg": {
                            "terms": {
                                "field": "sentiment.keyword"
                            }
                        }
                    }
                }
            }
        }
    elif search_context == "chart":
        input_json = {
            "query": query_input,
            "aggs": {
                "yearAgg": {
                    "terms": {
                        "field": "year.keyword"
                    },
                    "aggs": {
                        "quarterAgg": {
                            "terms": {
                                "field": "quarter.keyword"
                            },
                            "aggs": {
                                "tickerAgg": {
                                    "terms": {
                                        "field": "ticker.keyword"
                                    },
                                    "aggs": {
                                        "sentimentAgg": {
                                            "terms": {
                                                "field": "sentiment.keyword"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    return input_json