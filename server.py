from flask import Flask, render_template, request, g, jsonify
import psycopg2
import sys
import json
import base64
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
stop_words = set(stopwords.words('english'))
stemmer = SnowballStemmer("english")

stop_words.add(".")
stop_words.add(",")
stop_words.add("%")


app = Flask(__name__, static_url_path='/assets', static_folder="assets")
db_schema = "tanl"

def get_db():
    host="tanl.cgnbxyetzh4a.us-east-1.rds.amazonaws.com"
    database="tanl"
    db_usr="tanl"
    db_pw=base64.b64decode("U2VtbWFrYXRhJDc=").decode('utf-8')
    conn_string="host='{0}' dbname='{1}' user='{2}' password='{3}'".format(host, database, db_usr, db_pw)
    db=getattr(g, '_database', None)
    if db is None:
        db=g._database = psycopg2.connect(conn_string)
    return db

@app.route("/")
def hello():
    host_url = request.headers["Host"]
    return render_template("index.html", **locals())

@app.route("/search/<string:code>/", methods=['GET'])
def search(code):
    code_list = word_tokenize(code.lower())
    filtered_code = [w for w in code_list if not (w.lower() in stop_words or w.upper() in stop_words)]
    filtered_code = [stemmer.stem(w) for w in filtered_code]
    filtered_code = list(set(filtered_code))
    conn = get_db()
    row1_set = conn.cursor()
    row2_set = conn.cursor()
    row3_set = conn.cursor()
    row4_set = conn.cursor()
    custom_query = ""
    
    if len(filtered_code) > 0:
        reference_codes = ["lower(code) like '%" + word + "%'" for word in filtered_code]
        custom_query = "select distinct code, search_values from tanl.search_references where " + " or ".join(reference_codes)
        row1_set.execute(custom_query)
        
        time_codes = ["lower(year || '' || quarter || '' || ticker || '' || company) like '%" + word + "%'" for word in filtered_code]
        custom_query = "select distinct year,quarter, ticker, company from tanl.transcripts where " + " or ".join(time_codes) + "  order by 1 desc limit 10"
        row2_set.execute(custom_query)

        time_codes = ["lower(year|| ' ' || quarter || ' of ' || ticker) like '%" + word + "%'" for word in filtered_code]
        custom_query = "select distinct ticker from tanl.transcripts where " + " or ".join(time_codes) + "  order by 1 desc limit 5"
        row3_set.execute(custom_query)

        company_codes = ["lower(company) like '%" + word + "%'" for word in filtered_code]
        custom_query = "select distinct company from tanl.transcripts where " + " or ".join(company_codes) + "  order by 1 desc limit 5"
        row4_set.execute(custom_query)


    if row1_set.rowcount == 0 or len(filtered_code) == 0:
        custom_query = "select distinct code, search_values from tanl.search_references"
        row1_set.execute(custom_query)
    if row2_set.rowcount == 0 or len(filtered_code) == 0:
        custom_query = "select distinct year,quarter, ticker, company from tanl.transcripts order by 1 desc limit 10"
        row2_set.execute(custom_query)
    if row3_set.rowcount == 0 or len(filtered_code) == 0:
        custom_query = "select distinct quarter from tanl.transcripts  order by 1 desc limit 5"
        row3_set.execute(custom_query)
    if row4_set.rowcount == 0 or len(filtered_code) == 0:
        custom_query = "select distinct company, year||'-'||quarter, ticker from tanl.transcripts  order by 1 desc limit 5"
        row4_set.execute(custom_query) 
    result = []

    result1 = [row[0] + " " + row[1] for row in row1_set.fetchall()]
    result2 = [list(row) for row in row2_set.fetchall()]
    result3 = [row[0] for row in row3_set.fetchall()]
    result4 = [row[0] for row in row4_set.fetchall()] 

    temp = []
    for row1 in result1:
        for row2 in result2:
            temp = row1 + " " + row2[2] + " (" + row2[3] + ") for " + str(row2[0])
            if temp not in result:
                result.append(temp)
            
            temp = row1 + " " + row2[2] + " (" + row2[3] + ") for " + str(row2[0]) + " " + row2[1]
            if temp not in result:
                result.append(temp)

            temp = row1 + " " + row2[2] + " (" + row2[3] + ") for " + str(row2[0]) + " " + row2[1]
            if temp not in result:
                result.append(temp)


            temp = row1 + " " + row2[2] + " (" + row2[3] + ") for last 12 months"
            if temp not in result:
                result.append(temp)

    return jsonify(sorted(list(set(result)), reverse=True))

@app.route("/searchresults/<string:code>/", methods=['GET'])
def search_results(code):
    action_type = ""
    year = ""
    quarter = ""
    ticker = ""
    chart_type = "pie"
    
    try:
        action_type = code.split(" ")[0]
    except Exception as e:
        return jsonify({}), 404

    try:
        ticker = code.split(" ")[2]
    except Exception as e:
        return jsonify({}), 404

    filter_text = code.split(" for ")[-1]
    clause = ""

    group_query = "select year,quarter from tanl.transcripts where lower(ticker)='{0}'".format(ticker.lower())
    if filter_text == "last 12 months":
        clause = "order by year || quarter desc LIMIT 4"
    else:
        if len(filter_text.split(" ")) == 2:
            year = filter_text.split(" ")[0]
            quarter = filter_text.split(" ")[1]
            clause = " and lower(quarter)='{0}' and year={1} order by year || quarter desc".format(quarter.lower(), str(year))
        else:
            print("Debugger")
            print(filter_text)
            year = filter_text
            clause = " and year={0} order by year || quarter desc".format(str(year))

    conn = get_db()
    row1_set = conn.cursor()
    row2_set = conn.cursor()
    custom_query = "select query from tanl.search_references where code='{0}'".format(action_type)
    row1_set.execute(custom_query)
    data_query = ""
    for row in row1_set.fetchall():
        data_query = row[0]

    temp_group_result = []
    group_query =  "select * from (" + group_query + clause + ") as temp order by year ||quarter"
    row1_set.execute(group_query)
    for row in row1_set.fetchall():
        where_clause = " and lower(quarter)='{0}' and year={1} and lower(t.ticker)='{2}'".format(row[1].lower(), str(row[0]), ticker.lower())
        final_query = data_query + where_clause
        row2_set.execute(final_query)
        print(final_query)
        temp_result = []
        pos_cnt = 0
        neg_cnt = 0
        neu_cnt = 0
        for row2 in row2_set.fetchall():
            temp_result.append(json.loads(row2[0]))
            if action_type == "sentiment":
                pos_cnt = row2[1]
                neg_cnt = row2[2]
                neu_cnt = row2[3]
        temp_dict = {
            "group": str(row[0]) + ' ' + row[1],
            "result": temp_result
        }
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



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)