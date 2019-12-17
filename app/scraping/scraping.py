import multiprocessing as mp
import logging
import socket
import pandas as pd
import datetime as dt
from youtubeScraper import scrape_youtube
import time

# Get current month and year, format: 012018
x = dt.datetime.now()
current = x.strftime("%m") + x.strftime("%Y")

# Filters/Values Specified by User from the Front End:
data_from = "012019"        # Scrape youtube and news data from data_from until data_to
dara_to = current
genres = []                 # list of genres to get data for. Empty means all genres.
youtube_videos_per_game = 200

if __name__ == '__main__':
    logger = mp.log_to_stderr()
    logger.setLevel(logging.INFO)
    # ==== setup local connection(s) to spark aggregator ====
    # IP and port of local machine or Docker
    TCP_IP = socket.gethostbyname(socket.gethostname())  # returns local IP
    TCP_PORT = 9009
    # setup local connection, expose socket, listen for spark app
    conn = None
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)
    print("Waiting for TCP connection...")
    # if the connection is accepted, proceed
    conn, addr = s.accept()
    print("Connected... Starting to scrape youtube game data.")

    # second port connection for news scraper goes here

    # ==== Listen to Front End ====
    # connect and listen to front end, change filters/values to new values

    # ==== Invoke Scrapers ====
    killEvent = mp.Event()  # event that causes both scrapers to save progress, shut down and terminate
    killEvent.clear()
    print(str(killEvent.is_set()))
    queue = mp.Queue()      # used to pass connection to spark to processes so they can send data
    p1 = mp.Process(target=scrape_youtube, args=(queue, youtube_videos_per_game, killEvent))
    # p2 = mp.Process(target=scrape_news, args=(queue1, data_from, data_to, killEvent))
    p1.start()
    queue.put(conn)  # send connection with spark to youtube scraper
    # p2.start()
    # queue1.put(conn)
    try:
        p1.join()
        # p2.join()
    except KeyboardInterrupt:
        killEvent.set()
        p1.join()
        # p2.join()
