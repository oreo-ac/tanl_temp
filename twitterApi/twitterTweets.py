import twitter;
from twitterConfig import *;

class twitterAPI:
    def __init__(self):
        pass
    def tweetResponse(self, searchkey):
        if searchkey == "":
            print ("Entered Method")
            return "No input provided";
        else:
            api = connectToAPI();
            print api.GetSearch(searchkey);
            return "Successfully connected to Twitter API";

def connectToAPI():
    return twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret,
                      access_token_key=access_key, access_token_secret=access_secret);
if __name__ == '__main__':
    twitterAPI.tweetResponse(twitterAPI(), 'finance');