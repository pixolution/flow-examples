import requests
import json
import sys

if (sys.version_info[0] < 3 or sys.version_info[1] < 8):
    sys.exit("Python 3.8 or higher is required")

SERVER_URL = "http://localhost:8983/solr/my-collection"

def printTitle(title):
    print()
    print("##########################################")
    print(title)
    print("##########################################")
    print()

def printResponse(response):
    json_rsp = response.json();
    print(json.dumps(json_rsp, indent=4))
    if json_rsp["responseHeader"]["status"] == 0:
        print("SUCCESS :-)")
    else:
        print("SOMETHING WENT WRONG :-(")


printTitle("Init pixolution Flow")
printResponse(requests.get(SERVER_URL+"/pixolution"))

printTitle("Add document to collection")
doc = [{"id":"my-id-123",
    "url":"https://picsum.photos/seed/1/250",
    "keywords": "hello world"
    }]
printResponse(requests.post(SERVER_URL+"/update?commit=true", json=doc))

printTitle("Search by keywords hell*")
printResponse(requests.get(SERVER_URL+"/select?q=keywords:hell*"))

printTitle("Search doc id 'my-id-123'")
printResponse(requests.get(SERVER_URL+"/select?q=id:my-id-123"))

printTitle("Search by random image 'https://picsum.photos/250'")
printResponse(requests.get(SERVER_URL+"/select?rank.by=url:https://picsum.photos/250&rank.mode=default&rank.threshold=0"))

printTitle("Search by color red")
printResponse(requests.get(SERVER_URL+"/select?rank.by=hex:0xff0000&rank.mode=color&rank.threshold=0"))

printTitle("Find duplicate image 'https://picsum.photos/seed/1/250'")
printResponse(requests.get(SERVER_URL+"/duplicate?dup.find=url:https://picsum.photos/seed/1/250"))

printTitle("API documentation")
print("https://docs.pixolution.org")
