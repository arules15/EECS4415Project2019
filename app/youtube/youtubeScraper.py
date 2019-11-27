import requests
import re
from bs4 import BeautifulSoup
from csv import writer

# Youtube Scraper!
# A combination of https://github.com/dave2000sang/Youtube-Search-Scraper and
# https://github.com/narfman0/youtube-scraper modified to scan multiple pages of results
# Given a search query and a page range will extract video results to results.csv
# Set the query at line 69 and the page range at line 68

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


el = []
for page in range(1, 30):       # set the (min to max-1) page numbers of results that you would like to scrape from youtube
    search = "minecraft"         # set your youtube search query
    link = getLink(search, page)

    # Scrape the link
    response = requests.get(link)

    soup = BeautifulSoup(response.text, 'html.parser')

    # Select all parts with a href beginning with "/watch?v-" indicating a video link in list
    el = el + soup.select('a[href^="/watch?v="]')

# Convert scrape results to JSON
# data = []
# for x in el:
#     if x.has_attr('title'):
#         name = x.get_text()
#         partial_link = x['href']
#         full_link = "https://www.youtube.com"+partial_link
#         more_data = scrape_url(full_link)
#         likes = more_data.like
#         dislikes = more_data.dislike
#         views = more_data.views
#         published = more_data.published
#         data.append(json.dumps({"Name":name, "Link":full_link, "Likes":likes, "Dislikes":dislikes, "Views":views, "Published":published}))
#
# # send data (list of JSON) to server
# print(json.dumps(data))
# sys.stdout.flush()


with open('minecraft.csv', 'a', encoding="utf-8") as csv_file:
    csv_writer = writer(csv_file)
    headers = ['Name', 'Link', 'Likes', 'Dislikes', 'Views', 'Published']
    csv_writer.writerow(headers)

    # Add all findings into .csv file
    for x in el:
        # Filter tags with attribute 'title' (other tags are aria-hidden such as timestamp which is not important)
        if x.has_attr('title'):
            name = x.get_text()
            partial_link = x['href']
            full_link = "https://www.youtube.com" + partial_link
            try:
                more_data = scrape_url(full_link)
            except:
                continue
            likes = more_data.like
            dislikes = more_data.dislike
            views = more_data.views
            published = more_data.published

            csv_writer.writerow([name, full_link, likes, dislikes, views, published])  # write to csv row
