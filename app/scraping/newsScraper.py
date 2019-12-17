import requests
from bs4 import BeautifulSoup
from csv import writer


def scrape_article(link):
    response1 = requests.get(link)
    soup1 = BeautifulSoup(response1.text, 'html.parser')
    list_div1 = soup1.findAll("p")
    content1 = ""
    for tag1 in list_div1:
        content1 = content1 + str(str(tag1.get_text()).replace('\n', ' ').replace('\r', ''))
    return content1


def scrape_pcgamer(month, year):
    link = "https://www.pcgamer.com/archive/" + str(year) + "/" + str(month) + "/"
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    list_div = soup.findAll("li", {"class": "day-article"})
    with open('results.csv', 'a', encoding="utf-8") as csv_file:
        csv_writer = writer(csv_file)
        headers = ['Month/Year', 'Title', 'Link', 'Content']
        csv_writer.writerow(headers)
        for tag in list_div:
            title = tag.text
            url = tag.a.get('href')
            content = scrape_article(url)
            # print(str(month) + '/' + str(year), title, url, content)
            csv_writer.writerow([str(month) + '/' + str(year), title.strip(), url, content.strip()])  # write to csv row


def scrape_news(queue, data_from, data_to, kill_event):
    conn = queue.get()  # get connection to spark from parent process
    # scrape_pcgamer()
