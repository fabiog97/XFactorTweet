import tweepy
import datetime
import xlsxwriter
import sys

consumerKey = "ebOUiqPtcpl4I7GCvZWFoaQcX"
consumerSecret = "NKjAG1fMFqNxLmU9EqJWXvcaodbze587jsVxSrudmdy6Ce9BKU"
accessToken = "2461517455-neqTDkxNsY1livV3SHlwe6j0CrXEaLWD1O03qAX"
accessTokenSecret = "dmRqjILVUd5gzh4sPymRHIPfHCSl358CeaBU60z5mrOYy"
auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)


api = tweepy.API(auth)
#api = tweepy.API(auth, wait_on_rate_limit=True)
#username = sys.argv[1]
startDate = datetime.datetime(2018, 6, 1, 0, 0, 0)
endDate =   datetime.datetime(2019, 1, 1, 0, 0, 0)

tweets = []
tmpTweets = api.home_timeline()
for tweet in tmpTweets:
    if tweet.created_at < endDate and tweet.created_at > startDate:
        tweets.append(tweet)

while (tmpTweets[-1].created_at > startDate):
    print("Last Tweet @", tmpTweets[-1].created_at, " - fetching some more")
    tmpTweets = api.home_timeline(max_id = tmpTweets[-1].id)
    for tweet in tmpTweets:
        if tweet.created_at < endDate and tweet.created_at > startDate:
            tweets.append(tweet)

workbook = xlsxwriter.Workbook("Result.xlsx")
worksheet = workbook.add_worksheet()
row = 0
for tweet in tweets:
    worksheet.write_string(row, 0, str(tweet.id))
    worksheet.write_string(row, 1, str(tweet.created_at))
    worksheet.write(row, 2, tweet.text)
    worksheet.write_string(row, 3, str(tweet.in_reply_to_status_id))
    row += 1

workbook.close()
print("Excel file ready")



'''
ckey = "ebOUiqPtcpl4I7GCvZWFoaQcX"
csecret = "NKjAG1fMFqNxLmU9EqJWXvcaodbze587jsVxSrudmdy6Ce9BKU"
atoken = "2461517455-neqTDkxNsY1livV3SHlwe6j0CrXEaLWD1O03qAX"
asecret = "dmRqjILVUd5gzh4sPymRHIPfHCSl358CeaBU60z5mrOYy"

OAUTH_KEYS = {'consumer_key':ckey, 'consumer_secret':csecret,'access_token_key':atoken, 'access_token_secret':asecret}

auth = tweepy.OAuthHandler(OAUTH_KEYS['consumer_key'], OAUTH_KEYS['consumer_secret'])

api = tweepy.API(auth)
api.update_status(status='Test')
cricTweet = tweepy.Cursor(api.search).items(10)

for tweet in cricTweet:
    print (tweet.created_at, tweet.text)

'''