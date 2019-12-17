import requests
import re
from bs4 import BeautifulSoup
from csv import writer
import socket
import json
import ast
import pandas as pd
import sys

# Youtube Scraper!
# A combination of https://github.com/dave2000sang/Youtube-Search-Scraper and
# https://github.com/narfman0/youtube-scraper modified to scan specified number of new results
# The scrape_youtube method is called by scraping.py
# Given the name of the game, genre(s) of the game and the number of videos to scrape,
# will extract video results and send them to spark_aggregator via port 9009

class YoutubeScrape(object):
    """ Scraper object to hold data """

    def __init__(self, soup):
        """ Initialize and scrape """
        self.soup = soup
        self.title = self.parse_string('.watch-title')
        self.poster = self.parse_string('.yt-user-info')
        self.views = self.parse_int('.watch-view-count')
        self.published = self.parse_string('.watch-time-text')
        self.published = re.sub(r'(Published|Uploaded) on', '', self.published).strip()
        for b in soup.findAll('button', attrs={'title': 'I like this'}):
            self.like = int(re.sub('[^0-9]', '', b.text))
            break
        for b in soup.findAll('button', attrs={'title': 'I dislike this'}):
            self.dislike = int(re.sub('[^0-9]', '', b.text))
            break

    def parse_int(self, selector, pos=0):
        """ Extract one integer element from soup """
        return int(re.sub('[^0-9]', '', self.parse_string(selector, pos)))

    def parse_string(self, selector, pos=0):
        """ Extract one particular element from soup """
        return self.soup.select(selector)[pos].get_text().strip()


def scrape_html(html):
    """ Return meta information about a video """
    return YoutubeScrape(BeautifulSoup(html, 'html.parser'))


def scrape_url(url):
    """ Scrape a given url for youtube information """
    # set English as scraping language
    headers1 = {"Accept-Language": "en-US,en;q=0.5"}
    html = requests.get(url, headers=headers1).text
    return scrape_html(html)


# -------------------------------------------------------------#

# getLink(search) returns the formated youtube link
def getLink(search, page):
    strArr = search.split(" ")
    result = ""
    exists = None

    for x in strArr:
        exists = True
        result += x + "+"

    if exists:
        result = result[:-1]

    return "https://www.youtube.com/results?search_query=" + result + "&page=" + str(page)


def scrape_youtube(queue, videos_per_game, kill_event):
    conn = queue.get()  # get connection to spark from parent process
    # get set of previously scraped videos if any
    try:
        with open('scrapedVideos.txt', 'r') as f:
            scraped_videos = ast.literal_eval(f.read())
    except IOError:
        scraped_videos = set()

    # for each game in the dataset, scrape videos about those games
    games_df = pd.read_csv("steam_games.csv")
    for row in games_df.itertuples():
        el = []
        number_of_videos_scraped = 0

        def scrape(page):
            global el
            global number_of_videos_scraped
            search = row.name         # set your youtube search query      row.genre.split(',') for genres of row
            link = getLink(search, page)

            # Scrape the link
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Select all parts with a href beginning with "/watch?v-" indicating a video link in list
            el = el + soup.select('a[href^="/watch?v="]')

            # Convert scrape results to JSON
            for x in el:
                if kill_event.is_set:
                    break
                if number_of_videos_scraped < videos_per_game:
                    if x.has_attr('title'):
                        name = x.get_text()
                        partial_link = x['href']
                        if partial_link not in scraped_videos:
                            full_link = "https://www.youtube.com"+partial_link
                            try:
                                more_data = scrape_url(full_link)
                            except:
                                continue
                            scraped_videos.add(partial_link)
                            number_of_videos_scraped += 1
                            # if number_of_videos_scraped % 10 == 0:
                            #     print(number_of_videos_scraped+" videos scraped")
                            likes = more_data.like
                            dislikes = more_data.dislike
                            views = more_data.views
                            published = more_data.published
                            result = json.dumps({"Name": name, "Link": full_link, "Likes": likes, "Dislikes": dislikes, "Views": views, "Published":published})
                            try:
                                conn.send(str.encode(result + '\n'))
                            except:
                                e = sys.exc_info()[0]
                                print("Error: %s" % e)
                                break
                            # TODO send result json to spark
        pg = 1
        while number_of_videos_scraped < videos_per_game and not kill_event.is_set():
            scrape(pg)
            pg += 1
        if kill_event.is_set:
            print("Youtube Scraper: saving links and exiting...")
            break

    # record set of previously scraped videos to file for next time
    try:
        with open('scrapedVideos.txt', 'w') as f:
            f.write(str(scraped_videos))
    except EnvironmentError:
        print('uh oh, error writing scraped video set to file!')


    # with open('minecraft.csv', 'a', encoding="utf-8") as csv_file:
    #     csv_writer = writer(csv_file)
    #     headers = ['Name', 'Link', 'Likes', 'Dislikes', 'Views', 'Published']
    #     csv_writer.writerow(headers)
    #
    #     # Add all findings into .csv file
    #     for x in el:
    #         # Filter tags with attribute 'title' (other tags are aria-hidden such as timestamp which is not important)
    #         if x.has_attr('title'):
    #             name = x.get_text()
    #             partial_link = x['href']
    #             full_link = "https://www.youtube.com" + partial_link
    #             try:
    #                 more_data = scrape_url(full_link)
    #             except:
    #                 continue
    #             likes = more_data.like
    #             dislikes = more_data.dislike
    #             views = more_data.views
    #             published = more_data.published
    #
    #             csv_writer.writerow([name, full_link, likes, dislikes, views, published])  # write to csv row
