from flask import Flask, render_template, request, g, jsonify
import sys
import json
import base64
import helpers
from sklearn.externals import joblib
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
try:
    nltk.download('stopwords')
except Exception as e:
    pass
try:
    nltk.download('punkt')
except Exception as e:
    pass

app = Flask(__name__, static_url_path='/assets', static_folder="assets")
cl = joblib.load('modelfile.pkl')
@app.route("/")
def hello():
    host_url = request.headers["Host"]
    return render_template("index.html", **locals())

@app.route("/search/<string:code>/", methods=['GET'])
def search_results(code):
    year, quarter, temp, yearquarter = helpers.clean_search_text(code)
    search_response = helpers.get_search_types(code)
    search_response = search_response["hits"]
    
    if 0 == 1:
        response = {
            "analyst_container": [],
            "main_container": []
        }

    else:
        response = helpers.get_data(cl, search_response, year, quarter, temp, yearquarter)
        
    return jsonify(response)

@app.route("/test/api/<string:searchtext>/", methods=["GET"])
def test_api(searchtext):
    response = helpers.get_search_types(searchtext)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True);