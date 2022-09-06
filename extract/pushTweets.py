import boto3
import pandas as pd

s3 = boto3.resource('s3')

#Location on Pi of files to go to s3
filesToPush = [
	'/home/pi/tweetScrape/data/dailyTweets.json',
	'/home/pi/tweetScrape/data/dailyCovidTweets.json',
	'/home/pi/tweetScrape/data/covidCorpus.json',
	'/home/pi/tweetScrape/data/covidSentiment.json',
	'/home/pi/tweetScrape/data/fluCorpus.json',
	'/home/pi/tweetScrape/data/fluSentiment.json',
	'/home/pi/tweetScrape/data/covidSentWeek.json',
	'/home/pi/tweetScrape/data/fluSentWeek.json']

#Name of files in s3 bucket
fileNames = [
	'dailyTweets.json',
	'dailyCovidTweets.json',
	'covidCorpus.json',
	'covidSentiment.json',
	'fluCorpus.json',
	'fluSentiment.json',
	'covidSentWeek.json',
	'fluSentWeek.json']

for i in range(len(filesToPush)):
	if len(filesToPush) != len(fileNames):
		print("Error: Lists must be of some length")
		break
	s3.Bucket('tweetscrapestorage').upload_file(filesToPush[i],fileNames[i],ExtraArgs={'ACL':'public-read'})
