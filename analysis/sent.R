library(dplyr)
library(tidytext)
library(sentimentr)
library(jsonlite)

#dataPath <- '/Users/markbennett/Documents/outputCheck/'
dataPath <- '/home/pi/tweetScrape/data/'

# Import data
a.flu <- read.csv(paste(dataPath, 'routineOutput.csv', sep=""))
a.covid <- read.csv(paste(dataPath, 'routineCovidOutput.csv', sep=""))

#### Functions ####
tweetSentiment <- function(tweetDf, covid=FALSE, flu=FALSE) {
  b.select <- tweetDf %>%
    select(screen_name,text,dateStr) %>%
    mutate_if(is.character, utf8::utf8_encode) %>%
    mutate(strip=text, date_fmt = as.Date(dateStr, format='%Y-%m-%d'))
  b.select$strip <- iconv(b.select$strip, to = "UTF-8")
  gsubList <- list("@\\w+", "http\\w+", "&amp","(RT|via)((?:\\b\\W*@\\w+)+)","@\\w+","[[:punct:]]","[[:digit:]]","http\\w+","[ \t]{2,}","^\\s+|\\s+$")
  for(i in gsubList){
    b.select$strip <- gsub(i,"", b.select$strip)
  }
  c.unnest <- b.select %>%
    select(strip) %>%
    unnest_tokens(word,strip)
  if(flu){
    excludeList <- c('im', 'ive', 'youre', 'dont', 'didnt','doesnt','isnt','pretty', 'flu','influenza','amp','youll','wasnt', 'wont')
  }
  if(covid){
    excludeList <- c('im', 'ive', 'youre', 'dont', 'didnt','doesnt','isnt','pretty','covid','amp','youll','wasnt','wont')
  }
  d.corpus <- c.unnest %>%
    anti_join(stop_words) %>%
    filter(!word %in% excludeList) %>%
    count(word, sort = TRUE) %>%
    filter(n >= 3)
  e.sent <- d.corpus %>%
    left_join(get_sentiments("bing")) %>%
    replace(is.na(.), "Neutral")
  e.sentTweet <- sentiment(get_sentences(b.select$strip)) %>%
    group_by(element_id) %>%
    summarize(meanSent = mean(sentiment)) %>%
    mutate(meanCat = ifelse(meanSent>0,"Positive",ifelse(meanSent<0, "Negative","Neutral"))) %>%
    count(meanCat)
  e.sentWeekly <- sentiment(get_sentences(b.select$strip)) %>%
    group_by(element_id,) %>%
    summarize(meanSent = mean(sentiment)) %>%
    group_by(week = cut(b.select$date_fmt, "week")) %>%
    summarise(weeklyMean = mean(meanSent))
  corpusOut <- toJSON(e.sent)
  sentOut <- toJSON(e.sentTweet)
  sentWeek <- toJSON(e.sentWeekly)
  return(list(corpusOut,sentOut,sentWeek))
}

#### Store output into new list ####
#output form function is [1]: corpus of words with bing sentiment; [2]: summary of tweet sentiments
fluTweets <- tweetSentiment(a.flu, flu = TRUE)
covidTweets <- tweetSentiment(a.covid, covid = TRUE)

#### Cleaning tweets for analysis ####
write(unlist(fluTweets[1]),paste(dataPath, 'fluCorpus.json', sep=""))
write(unlist(fluTweets[3]),paste(dataPath, 'fluSentWeek.json', sep=""))

write(unlist(covidTweets[1]),paste(dataPath, 'covidCorpus.json', sep=""))
write(unlist(covidTweets[3]),paste(dataPath, 'covidSentWeek.json', sep=""))
