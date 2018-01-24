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
            temp = row1 + " " + row2[2] + ": " + row2[3] + " for " + str(row2[0])
            if temp not in result:
                result.append(temp)
            
            temp = row1 + " " + row2[2] + ": " + row2[3] + " for " + str(row2[0]) + " " + row2[1]
            if temp not in result:
                result.append(temp)

            temp = row1 + " " + row2[2] + ": " + row2[3] + " for " + str(row2[0]) + " " + row2[1]
            if temp not in result:
                result.append(temp)


            temp = row1 + " " + row2[2] + ": " + row2[3] + " for last 12 months"
            if temp not in result:
                result.append(temp)





    return jsonify(sorted(list(set(result)), reverse=True))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)