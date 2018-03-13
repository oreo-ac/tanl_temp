import requests
from textblob import TextBlob
import json
from textblob.classifiers import NaiveBayesClassifier
from sklearn.externals import joblib

es_url = "https://search-tanl-nswk7nthqjskczmapaqzga3c2q.us-east-1.es.amazonaws.com/"
search_type_index = "train/data/"

def get_train_data():
    url = es_url + search_type_index + "_search" 
    response = requests.get(url=url)
    if str(response.status_code) == "200":
        results = json.loads(response.text)["hits"]["hits"]
        results = [(d["_source"]["question"] + d["_source"]["answer"], d["_source"]["category"]) for d in results]
    else:
        results = []
    return results

def create_persist_model(train_data):
    cl = NaiveBayesClassifier(train_data)
    joblib.dump(cl, 'modelfile.pkl')

if __name__ == "__main__":
    train_data = get_train_data()
    create_persist_model(train_data)