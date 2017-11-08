import requests

import base64
import json
import sys
org_nm = "oreo-ac"
repo_name = "tanl_data"


def create_file(content, url_suffix):
    con = content
    input_base64 = base64.b64encode(con.encode('utf-8')).decode('ascii')
    url = "https://api.github.com/repos/" + org_nm + "/" + repo_name + "/contents/" + url_suffix
    input_data = {
      "message": "my commit message",
      "committer": {
        "name": "Vasu Rajaguru",
        "email": "vasur86@gmail.com"
      },
      "content": input_base64
    }
    response = requests.put(url = url, data = json.dumps(input_data), auth=(sys.argv[1], sys.argv[2]))
    #print (str(response.status_code) + " : " + url)
    return response.status_code

if __name__ == "__main__":
    print ("a")
    create_file("My Sample Test", "test/sbcd1234")