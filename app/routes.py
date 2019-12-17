from app import application
from time import time, ctime
#from youtube.youtubeScraper import YoutubeScrape
#from app.youtube.youtubeScraper import YoutubeScrape
from app import steamproject
import sys
import csv
import flask
from flask import make_response
from flask import jsonify


@application.route('/')
@application.route('/index')
def index():
    return "Hello, World!"

# I think it would be better to forward these to a whole new file based on the request
# for example, say a user wants to run an analysis on the like/dislike ratio of yotube videos in relation to the top 50 games
# in the fps genre
# we will
@application.route('/GenreRequest/<string:Genre>', methods=['GET'])
def ReadSteamCsv(Genre):

    # use the steamproject file to obtain top 10 games in a list, pass this list onto the youyube scraping function
    # to obtain the like/dislike ratio and other data about the genre, send this back in json to the
    # UI application for processing
    toReturn = steamproject.main()
    toReturn2 = steamproject.wordOccurences(8, toReturn, 10)
    message = {
        'status': 200,
        'message': 'Ok',
        'Genre': Genre,
        "Pls-Work": toReturn2  # 'like-dislike_ratio': """like dislike ratio dictionary"""
    }

    return jsonify(message)
