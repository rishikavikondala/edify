#!/usr/bin/env python3
# matplotlib
# sentiment / time
# https://stackoverflow.com/questions/53075939/calling-rest-api-with-an-api-key-using-the-requests-package-in-python
import requests
from requests.auth import HTTPBasicAuth
import matplotlib.pyplot as plt

def parse_chat(filename):
    counts = {}
    api_text = ""
    messages = open(filename, "r").readlines()
    for message in messages:
        parsed_message = message.split("\t")
        name = parsed_message[1][:-1].strip()
        text = parsed_message[2].strip()
        text = text + " "
        if name in counts:
            counts[name] = counts.get(name) + 1
        else:
            counts[name] = 1
        api_text = api_text + text.replace(" ", "%20")
    return api_text, counts

def parse_sentiment(output):
    scores = {}
    output = output['document_tone']['tones']
    for sentiment in output:
        score = sentiment['score']
        emotion = sentiment['tone_name']
        scores[emotion] = score
    return scores

def graph(dict, title, outputFile):
    keys = list(dict.keys())
    values = list(dict.values())
    plt.bar(keys, values)
    plt.suptitle(title)
    #plt.show()
    plt.savefig(outputFile)
    plt.clf()

def sentimentMain(inputFile, outputFile):
    words = "Team%2C%20I%20know%20that%20times%20are%20tough%21%20Product%20sales%20have%20been%20disappointing%20for%20the%20past%20three%20quarters.%20We%20have%20a%20competitive%20product%2C%20but%20we%20need%20to%20do%20a%20better%20job%20of%20selling%20it%20"
    url_raw = "https://api.us-south.tone-analyzer.watson.cloud.ibm.com/instances/45ef3914-2ba6-4b58-b386-cdbbe97221db/v3/tone?version=2017-09-21"
    chat, counts = parse_chat(inputFile)
    url_txt = "https://api.us-south.tone-analyzer.watson.cloud.ibm.com/instances/45ef3914-2ba6-4b58-b386-cdbbe97221db/v3/tone?version=2017-09-21&sentences=false&text="
    url_final = url_txt + chat
    headers = {"Accept": "application/json"}
    auth = HTTPBasicAuth('apikey', "[Redacted]")
    req = requests.get(url_final, headers=headers, auth=auth) #, files=files)
    req = req.json()
    # output = {'document_tone': {'tones': [{'score': 0.539093, 'tone_id': 'sadness', 'tone_name': 'Sadness'}, {'score': 0.681439, 'tone_id': 'joy', 'tone_name': 'Joy'}, {'score': 0.730648, 'tone_id': 'tentative', 'tone_name': 'Tentative'}]}}
    parsed_sentiment = parse_sentiment(req)
    graph(parsed_sentiment, 'Class Sentiment Trends', outputFile)
    # print(parsed_sentiment)

if __name__=="__main__":
    main()
