from app import application
from time import time, ctime


@application.route('/')
@application.route('/index')
def index():
    return "Hello, World!"

# I think it would be better to forward these to a whole new file based on the request
# for example, say a user wants to run an analysis on the like/dislike ratio of yotube videos in relation to the top 50 games
# in the fps genre
# we will
@application.route('/YoutubeRequest')
def timeDisplay():
    t = time()
    return ctime(t)
