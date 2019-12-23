from app import application
from time import time, ctime
#from youtube.youtubeScraper import YoutubeScrape
#from app.youtube.youtubeScraper import YoutubeScrape
import datetime as dt
from app import steamproject
import sys
import csv
import flask
from flask import make_response
from flask import request
from flask import jsonify
from app.scraping import scraping


@application.route('/')
@application.route('/index')
def index():
    return "Hello, World!"

# I think it would be better to forward these to a whole new file based on the request
# for example, say a user wants to run an analysis on the like/dislike ratio of yotube videos in relation to the top 50 games
# in the fps genre
# we will
# @application.route('/GenreRequest/<string:Genre>', methods=['GET'])
# def ReadSteamCsv(Genre):

#     # use the steamproject file to obtain top 10 games in a list, pass this list onto the youyube scraping function
#     # to obtain the like/dislike ratio and other data about the genre, send this back in json to the
#     # UI application for processing
#     toReturn = steamproject.main()
#     toReturn2 = steamproject.wordOccurences(8, toReturn, 10)
#     message = {
#         'status': 200,
#         'message': 'Ok',
#         'Genre': Genre,
#         "Pls-Work": toReturn2  # 'like-dislike_ratio': """like dislike ratio dictionary"""
#     }

#     return jsonify(message)


@application.route('/DataRequest', methods=['GET'])
def driverFunction():
    # month_from = request.args.get("month_from")
    # month_to = request.args.get("month_to")
    # year_from = request.args.get("year_from")
    # year_to = request.args.get("year_to")
    # genres = request.args.get("genres")
    # youtube_videos_per_game = request.args.get("youtube_videos_per_game")

    # Filters/Values Specified by User from the Front End:
    x = dt.datetime.now()
    current_month = x.strftime("%m")
    current_year = x.strftime("%Y")

    month_from = 1              # Scrape youtube and news data from data_from until data_to
    year_from = 2019
    month_to = current_month
    year_to = current_year
    # list of genres to get data for. Empty means all genres.
    genres = []
    youtube_videos_per_game = 200
    scraping.scraping(month_from, month_to, year_from,
                      year_to, genres, youtube_videos_per_game)
#month_from, month_to, year_from, year_to, genres, youtube_videos_per_game
