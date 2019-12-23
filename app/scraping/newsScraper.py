import requests
from bs4 import BeautifulSoup
from csv import writer
import re
import sys
import json
import pandas as pd
from textblob import TextBlob
import os

# pip install textblob
# make sure you have the news results.csv renamed as pcGamerResults.csv in the docker container


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


def scrape_article(link):
    response1 = requests.get(link)
    soup1 = BeautifulSoup(response1.text, 'html.parser')
    list_div1 = soup1.findAll("p")
    content1 = ""
    for tag1 in list_div1:
        content1 = content1 + \
            str(str(tag1.get_text()).replace('\n', ' ').replace('\r', ''))
    return content1


def scrape_pcgamer(month, year):
    link = "https://www.pcgamer.com/archive/" + \
        str(year) + "/" + str(month) + "/"
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    list_div = soup.findAll("li", {"class": "day-article"})
    with open('pcGamerResults.csv', 'a', encoding="utf-8") as csv_file:
        csv_writer = writer(csv_file)
        headers = ['Month/Year', 'Title', 'Link', 'Content']
        if os.stat('pcGamerResults.csv').st_size == 0:      # if file empty write headers
            csv_writer.writerow(headers)
        for tag in list_div:
            title = tag.text
            url = tag.a.get('href')
            content = scrape_article(url)
            # print(str(month) + '/' + str(year), title, url, content)
            # write to csv row
            csv_writer.writerow(
                [str(month) + '/' + str(year), title.strip(), url, content.strip()])


def month_year_iter(start_month, start_year, end_month, end_year):
    ym_start = 12*start_year + start_month - 1
    ym_end = 12*end_year + end_month - 1
    for ym in range(ym_start, ym_end):
        y, m = divmod(ym, 12)
        yield y, m+1


def scrape_news(queue, month_from, year_from, month_to, year_to, genres, killEvent):
    conn = queue.get()  # get connection to spark from parent process
    articles_df = pd.read_csv("pcGamerResults.csv")
    dc = articles_df[['Month/Year', 'Content']]
    games_df = pd.read_csv("steam_games.csv")
    # selection criteria (genre, game, or some other parameter to be passed onto the scrapers, selection_criteria = [column_name, value])
    games_df = games_df[[genre in genres for genre in games_df["genre"]]]

    for row in games_df.itertuples():
        if killEvent.is_set():
            print("PcGamer Scraper: Shutting Down...3")
            break
        for y, m in month_year_iter(int(month_from), int(year_from), int(month_to), int(year_to)):
            if killEvent.is_set():
                print("PcGamer Scraper: Shutting Down...2")
                break
            if not articles_df["Month/Year"].str.contains(str(m)+'/'+str(y)).any():
                scrape_pcgamer(m, y)
            articles_from_month = dc.loc[dc['Month/Year']
                                         == str(m) + '/' + str(y)]
            articles_from_month['wc'] = articles_from_month['Content'].str.count(
                r"" + re.escape(row.name), re.IGNORECASE)
            articles_from_month['sentiment'] = articles_from_month.apply(
                lambda row1: sentiment(row1), axis=1)
            afm = articles_from_month[['Month/Year', 'wc', 'sentiment']]
            for r in afm.itertuples():
                if killEvent.is_set():
                    print("PcGamer Scraper: Shutting Down...1")
                    break
                results = json.dumps({"month": m, "year": y, "genre": row.genre.split(
                    ','), "game": row.name, "wc": r.wc, "sentiment": r.sentiment})
                print(results)
                sys.stdout.flush()
                try:
                    conn.sendall(str.encode(results + '\n'))
                except:
                    print("news send error")
                    sys.stdout.flush()
