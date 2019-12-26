from app import application
from time import time, ctime
#from youtube.youtubeScraper import YoutubeScrape
#from app.youtube.youtubeScraper import YoutubeScrape
import datetime as dt
#from app import steamproject
import sys
import csv
import flask
from flask import make_response
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin
#from app.scraping import scraping
import ast

# new strategy, values will come in as genre,date: views, split on the comma and genre will be used to index to a dictionary
# this dictioanry will have a list with {date: views} pairs, for each new data do the following
# append the date:views pairs to the dictionary
# send this to the frontend

cors = CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'
global Sentiments
# Sentiments = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0,
# 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
WordCount = {}
Sentiments = {}
Views = {}
# we want a list of dictionaries instead, of the form
#[{x:1 , y:0}, {x:2, y:0}]

# convert the data coming in from spark to a list in the format required for the chart


def convertToList(dictionary):
    returnList = {"sents": []}
    for i in dictionary.keys():
        returnList["sents"].append({"x": i, "y": dictionary[i]})
    return returnList


def convertViewsToList(dictionary):
    returnList = {"Dates": []}
    for i in dictionary.keys():
        returnList["Dates"].append({"x": i, "y": dictionary[i]})
    return returnList


@application.route('/')
@application.route('/index')
def index():
    return "Hello, World!"

# Called by the frontend to get new sentiment values
@application.route('/GetSentiment', methods=['GET'])
@cross_origin()
def handleGetSentiment():
    toSend = Sentiments
    message = {
        'status': 200,
        'message': 'Ok',
        'sentiments': toSend
    }

    return jsonify(message["sentiments"])

# Called by frontend to get new total views data, fromat currently is yyyymm, will get converted to a proper date on the front end
@application.route('/GetViews', methods=['GET'])
@cross_origin()
def handleGetViews():
    toSend = Views
    message = {
        'status': 200,
        'message': 'Ok',
        'dates': toSend
    }

    return jsonify(message["dates"])


# Called by frontend to get new total wordcount, date fromat currently is yyyymm, will get converted to a proper date on the front end
@application.route('/GetWordCount', methods=['GET'])
@cross_origin()
def handleGetWordCount():
    toSend = WordCount
    message = {
        'status': 200,
        'message': 'Ok',
        'wordcount': toSend
    }

    return jsonify(message["wordcount"])

# # updated by spark with new values as they arrive, it modifies a global disctionary
# # called Sentiments which is of the form {"month": sentiment}
# @application.route('/UpdateSentiment', methods=['POST'])
# def handleUpdateSentiment():
#     global month, values
#     if not request.form or 'data' not in request.form:
#         return "error", 400
#     month = ast.literal_eval(request.form['label'])
#     values = ast.literal_eval(request.form['data'])
#     #Sentiments[i] = sentiment/wordcount
#     Sentiments[month] = float(values[1]) / int(values[0])
#     print("labels received: " + str(month))
#     print("data received: " + str(values))
#     return "success", 201

# updated by spark with new values as they arrive, it modifies a global disctionary
# called Sentiments which is of the form {"month": sentiment}
# modified for new genre based key
@application.route('/UpdateSentiment', methods=['POST'])
def handleUpdateSentiment():
    global month, values
    if not request.form or 'data' not in request.form:
        return "error", 400
    genremonth = request.form['label']
    values = ast.literal_eval(request.form['data'])
    #Sentiments[i] = sentiment/wordcount
    genre = genremonth.split(',')[0]
    date = genremonth.split(',')[1]
    if genre not in Sentiments.keys():
        Sentiments[genre] = {date: float(values[1]) / int(values[0])}
        WordCount[genre] = {date: int(values[0])}
    else:
        Sentiments[genre][date] = float(values[1]) / int(values[0])
        WordCount[genre][date] = int(values[0])

    print("labels received: " + str(genre))
    print("data received: " + str(float(values[1]) / int(values[0])))
    return "success", 201


# updated by spark with new values as they arrive, it modifies a global disctionary
# called Sentiments which is of the form {"month": sentiment}
@application.route('/UpdateViews', methods=['POST'])
def handleUpdateViews():
    global month, values2
    if not request.form or 'data' not in request.form:
        return "error", 400
    genremonth = request.form['label']
    values2 = ast.literal_eval(request.form['data'])
    #Sentiments[i] = sentiment/wordcount
    genre = genremonth.split('~')[0]
    date = genremonth.split('~')[1]
    if genre not in Views.keys():
        Views[genre] = {date: int(values2)}
    else:
        Views[genre][date] = int(values2)

    print("labels received: " + str(genre))
    print("data received: " + str(values2))
    return "success", 201

# This function will be used to update the requirements from the front end, will work on this once we can figure ot how to get
# the scraper to run from this flask server
@application.route('/DataRequest', methods=['POST'])
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
    # scraping.scraping(month_from, month_to, year_from,
    # year_to, genres, youtube_videos_per_game)
#month_from, month_to, year_from, year_to, genres, youtube_videos_per_game
