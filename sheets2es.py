import requests
import json
es_url = "https://search-tanl-nswk7nthqjskczmapaqzga3c2q.us-east-1.es.amazonaws.com/"
search_type_index = "train/data/"
sample_path = "C:\\Users\\vasur\\Downloads\\model_input.txt"
data = ""
with open(sample_path, 'r') as f:
    data = f.readlines()
headers = {"Content-Type" : "application/json"}
#data = data.split("\\n")
i = 0
print(len(data))
for d in data:
    col = d.split("DELIM")
    data_json = {
        "question": col[3],
        "answer": col[4],
        "category": col[5].replace("\n", "").lower()
    }
    if data_json["category"] != "":

        i = i + 1
        print(data_json)
        response = requests.post(es_url + search_type_index + str(i), data=json.dumps(data_json), headers=headers)
        print (response.status_code)
        print(response.text)