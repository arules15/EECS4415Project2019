import pandas as pd
from textblob import TextBlob
import re


def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


def get_tweet_sentiment(tweet):
    tweet_blob = TextBlob(clean_tweet(tweet))
    return tweet_blob.sentiment.polarity
    # if tweet_blob.sentiment.polarity > 0:
    #     return 1
    # elif tweet_blob.sentiment.polarity == 0:
    #     return 0
    # else:
    #     return -1


def sentiment(row):
    content = row['Content']
    return get_tweet_sentiment(content)


articles = pd.read_csv('results.csv')

dc = articles[['Month/Year', 'Content']]
for i in range(1, 12):
    myString = str(i) + '/2019'
    articles_from_month = dc.loc[dc['Month/Year'] == myString]
    articles_from_month['rleague'] = articles_from_month['Content'].str.count('Minecraft')
    articles_from_month['sentiment'] = articles_from_month.apply(lambda row: sentiment(row), axis=1)
    print(myString, articles_from_month['rleague'].sum(), articles_from_month['sentiment'].mean())
    # print(articles_from_month)
