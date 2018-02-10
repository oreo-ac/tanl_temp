from flask import Flask, render_template, request, g, jsonify
import sys
import json
import base64
import helpers

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
<<<<<<< HEAD
    else:
        response = helpers.get_data(search_response, year, quarter, temp, yearquarter)
        
    return jsonify(response)

@app.route("/test/api/<string:searchtext>/", methods=["GET"])
def test_api(searchtext):
    response = helpers.get_search_types(searchtext)
    return jsonify(response)
=======
        if action_type == "sentiment":
            temp_dict["positive"] = pos_cnt
            temp_dict["negative"] = neg_cnt
            temp_dict["neutral"] = neu_cnt
        temp_group_result.append(temp_dict)

    result_dict = {}
    if action_type == "sentiment":
        x_keys = ["positive", "negative", "neutral"]
        x_labels = ["positive", "negative", "neutral"]
        colors = ["#00a65a", "#f56954", "#3c8dbc"]
        result_dict["y_keys"] = x_keys
        result_dict["y_labels"] = x_labels
        result_dict["x_key"] = 'group'
        result_dict["chartType"] = chart_type
        result_dict["colors"] = colors
    result_dict["data"] = temp_group_result
    return jsonify(result_dict)

@app.route("/getqanda/<string:code>/", methods=['GET'])
def getqanda(code):
    qanda = {}
    conn = get_db()
    result_set = conn.cursor()
    query =  "SELECT qa_key, tr_key, question, answer, questionasw, answerasw FROM tanl.questionanswer where tr_key='" + code + "' ORDER BY RANDOM() LIMIT 1"
    result_set.execute(query);
    result = result_set.fetchall();
    qanda.update({result[0][2]: result[0][3]});
    return jsonify(qanda);

@app.route("/keywords/<string:code>/", methods=['GET'])
def keywords(code):
    conn = get_db()
    result_set = conn.cursor()
    query =  "SELECT qa_key, tr_key, type, keyword, count FROM tanl.keywords where tr_key='" + code + "' ORDER BY RANDOM() LIMIT 5"
    result_set.execute(query);
    result = [row[3] for row in result_set.fetchall()]
    return jsonify(result);

@app.route("/metrics/<string:code>/", methods=['GET'])
def metrics(code):
    conn = get_db()
    result_set = conn.cursor()
    query = "SELECT count(an_key), count(ex_key), count(question) FROM tanl.questionanswer where tr_key='" + code + "'"
    result_set.execute(query);
    result = result_set.fetchall()
    return jsonify(result);

@app.route("/qanda/<string:code>/", methods=['GET'])
def qanda(code):
    conn = get_db()
    result_set = conn.cursor()
    query = "SELECT t.tr_key,t.year,t.quarter,qa.question,qa.qa_key FROM tanl.questionanswer qa " \
            " left join transcripts t on t.tr_key=qa.tr_key  " \
            " where qa.tr_key='" + code + "'"
    result_set.execute(query);
    result = result_set.fetchall();
    return jsonify(result);

@app.route("/keywordsbyqakey/<string:code>/", methods=['GET'])
def keywordsbyqakey(code):
    conn = get_db()
    result_set = conn.cursor()
    query = "SELECT k.qa_key,k.tr_key,k.keyword,k.sentiment FROM tanl.keywords k " \
            " where k.qa_key='" + code + "' and k.type='Q'"
    result_set.execute(query);
    result = result_set.fetchall();
    return jsonify(result);
>>>>>>> 8358fa2638b2e63923cb7a2c7e152798c47ac067

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)