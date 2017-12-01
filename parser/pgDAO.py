import psycopg2
import hashlib
import json


class pgDAO:
    def __init__(self):
        pass

    def openConnection(self):
        self.myConnection = psycopg2.connect(host="tanl.cgnbxyetzh4a.us-east-1.rds.amazonaws.com", user="tanl",
                                             password="Semmakata$7", dbname="tanl")

    def closeConnection(self):
        self.myConnection.close()

    def getConfig(self):
        self.openConnection()
        cur = self.myConnection.cursor()
        cur.execute("select company, quarter from transcripts")
        for company, quarter in cur.fetchall():
            print(company + quarter)
        self.closeConnection()
        return "test"

    def delete_transcripts(self, trans):
        self.openConnection()
        cur = self.myConnection.cursor()
        tables = ['questionanswer', 'keywords', 'customkeymapscore', 'transcript_sentiment_results', 'keywords_mng_talk', 'transcripts']
        for table in tables:
            sql = "DELETE FROM " + table + " WHERE tr_key=%s"
            data = (trans.tr_key,)
            cur.execute(sql, data)
        self.myConnection.commit()
        self.closeConnection()

    def iTranscript(self, trans):
        self.delete_transcripts(trans)
        self.openConnection()
        cur = self.myConnection.cursor()
        sql = """INSERT INTO transcripts(tr_key, company, year, quarter, ticker)
             VALUES(%s, %s, %s, %s, %s) """
        data = (trans.tr_key, trans.company, trans.year, trans.quarter, trans.stock,)
        cur.execute(sql, data)
        self.myConnection.commit()
        self.closeConnection()

    def iSentiment(self, trans):
        self.openConnection()
        cur = self.myConnection.cursor()
        sql = """INSERT INTO transcript_sentiment_results(tr_key, type, sentiment, words_count, count_pct)
             VALUES(%s, %s, %s, %s, %s) """
        data = (trans["tr_key"], trans["type"], trans["sentiment"], trans["words_count"], trans["count_pct"],)
        cur.execute(sql, data)
        self.myConnection.commit()
        self.closeConnection()

    def iExecutive(self, executive):
        self.openConnection()
        cur = self.myConnection.cursor()
        sql = """DELETE from executives where ex_key=%s """
        data = (executive.ex_key,)
        cur.execute(sql, data)
        sql = """INSERT INTO executives(ex_key, company, name)
             VALUES(%s, %s, %s) """
        data = (executive.ex_key, executive.company, executive.name)
        cur.execute(sql, data)
        self.myConnection.commit()
        self.closeConnection()

    def iAnalyst(self, analyst):
        self.openConnection()
        cur = self.myConnection.cursor()
        sql = """DELETE from analyst where an_key=%s """
        data = (analyst.an_key,)
        cur.execute(sql, data)
        sql = """INSERT INTO analyst(an_key, company, name)
             VALUES(%s, %s, %s) """
        data = (analyst.an_key, analyst.company, analyst.name)
        cur.execute(sql, data)
        self.myConnection.commit()
        self.closeConnection()

    def iQA(self, qa):
        self.openConnection()
        cur = self.myConnection.cursor()
        sql = """INSERT INTO questionanswer(qa_key, tr_key, an_key, ex_key, question, answer, questionasw, answerasw)
             VALUES(%s, %s, %s, %s,%s, %s, %s, %s) """
        data = (qa.qa_key, qa.tr_key, qa.an_key, qa.ex_key, qa.question, qa.answer, qa.questionASW, qa.answerASW)
        # print(cur.mogrify(sql, data))
        cur.execute(sql, data)
        self.myConnection.commit()
        self.closeConnection()

    def iQAKeyword(self, keys, tr_key, qa_key, type):
        self.openConnection()
        cur = self.myConnection.cursor()
        for (keyword,count) in keys:
            sql = """INSERT INTO keywords(qa_key, tr_key, type, keyword, count)
             VALUES(%s, %s, %s, %s, %s) """
            data = (qa_key, tr_key, type, keyword, count)
            cur.execute(sql, data)
        self.myConnection.commit()
        self.closeConnection()

    def iTalkKeyword(self, keys, tr_key, ex_key):
        self.openConnection()
        cur = self.myConnection.cursor()
        for (keyword, count) in keys:
            sql = """INSERT INTO keywords_mng_talk(tr_key, ex_key, keyword, count)
             VALUES(%s, %s, %s, %s) """
            data = (tr_key, ex_key, keyword, count)
            cur.execute(sql, data)
        self.myConnection.commit()
        self.closeConnection()

    def getTr_Key(self, trans):
        hashKey = hashlib.sha1(json.dumps({"company": trans.company, "quarter": trans.quarter, "year": trans.year},
                                          sort_keys=True).encode('utf-8')).hexdigest()
        return hashKey

    def getAn_Key(self, analyst):
        hashKey = hashlib.sha1(
            json.dumps({"company": analyst.company, "name": analyst.name}, sort_keys=True).encode('utf-8')).hexdigest()
        return hashKey

    def getEx_Key(self, executive):
        hashKey = hashlib.sha1(
            json.dumps({"company": executive.company, "name": executive.name}, sort_keys=True).encode('utf-8')).hexdigest()
        return hashKey
