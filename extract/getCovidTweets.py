import json
import tweepy as tw
import pandas as pd
from datetime import datetime, timedelta

with open("/home/pi/tweetScrape/credentials/credentials.json", "r") as read_file:
    cred = json.load(read_file)

api_key = cred['apiKey']
api_secret = cred['apiSecret']
access_token = cred['accessToken']
access_token_secret = cred['accessSecret']

auth = tw.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth,wait_on_rate_limit=True)

# Text query example, looking for tweets from any user
text_query = "covid OR covid19 OR covid-19" + " -filter:retweets"
# Upper date range, pulls up UNTIL this date before
todayStr = datetime.now().strftime('%Y-%m-%d')
today =  datetime.now()
yesterday = today - timedelta(days=1)
yesterdayStr = yesterday.strftime('%Y-%m-%d')

# Cursor to find tweets
tweets = tw.Cursor(api.search_tweets,
              q=text_query,
              lang="en",
              geocode = "44.653954,-63.565359,10km",
              tweet_mode='extended',
              until=todayStr).items()
# Extract data from each tweet
users_locs = [[tweet.id,
                tweet.user.screen_name,
                tweet.created_at,
                tweet.user.location,
                tweet.full_text]
    for tweet in tweets]
# move into df for export
tweet_df = pd.DataFrame(data=users_locs,
                    columns=["Tweet_id",
                            "screen_name",
                            "datetime",
                            "location",
                            "text"])
# convert dates to strings, and remove weird NZ rows
tweet_df['dateStr'] = tweet_df['datetime'].dt.strftime('%Y-%m-%d')
rmv_NZ = tweet_df[~tweet_df.location.str.contains("New Zealand", case=False)]

# Get yesterday's date
yest_tweets = rmv_NZ[rmv_NZ["dateStr"] == yesterdayStr]

#Bring in daily output csv, to append it
prev_tweets = pd.read_csv("/home/pi/tweetScrape/data/routineCovidOutput.csv",encoding_errors='ignore')
#append new tweets to daily csv output
all_tweets = pd.concat([prev_tweets,yest_tweets])

# Output all tweets as overwritten csv
all_tweets.to_csv("/home/pi/tweetScrape/data/routineCovidOutput.csv", mode='w',index=False,header=True)
# output JSON file as well
all_tweets.to_json(r"/home/pi/tweetScrape/data/dailyCovidTweets.json", orient='records')



