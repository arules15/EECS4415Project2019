from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SQLContext
import sys
import time
import requests
import re
import json

# Couldn't Implement the genre output yet, for some reason it would crash the spark job, and as it stands
# the genre is being used to filter the results anyways so the main genre can be pulled from the input from frontend
# Will continue to work on getting the genre info in there though

# ==== Spark Aggregator App ====
# Run this app second after running scraping.py
# This spark app receives data simultaneously from two web scraping scripts youtubeScraper & pcgamerScraper
# and transforms game-specific data into genre-wide data metrics, which get sent to the front end dashboard
# apt-get update && apt-get install -y netcat
# spark-submit spark_aggregator.py --master local[2]

# create spark configuration
conf = SparkConf()
conf.setAppName("TwitterStreamApp")
# create spark context with the above configuration
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
# create the Streaming Context from spark context, interval size 2 seconds
ssc = StreamingContext(sc, 2)
# setting a checkpoint for RDD recovery (necessary for updateStateByKey)
ssc.checkpoint("checkpoint_TwitterApp")
# read data from port 9009 and port 9010
# combinedDataStream = ssc.socketTextStream("twitter", 9009)
# For use in Abduls local spark instance, comment out if using in docker
combinedDataStream = ssc.socketTextStream("10.0.75.1", 9009)

# # TODO: Do RDD aggregations here... and Modify the two functions below

# we now have each individual article result stored in articles
articles = combinedDataStream.flatMap(lambda line: line.split("\n"))
# extract the wc and sentiment from each article


def seq_op(accumulator, element):
    # operation on single rdd, we want to add the sentiments and word counts together
    # word count = element[0], sentiment = element[1]

    # element[0] * element[1] = sentiment * wordcount, this ensures that articles which mention a game/genre more frequently
    # will have a greater contribution to the total overall sentiment then those that dont mention it frequently
    return (accumulator[0] + element[0], accumulator[1] + (element[0] * element[1]))


def comb_op(accumulator1, accumulator2):
    # operation to sum up the sentiments and word counts across all rdd's
    # accumulator[0] = word count, accumulator[1] = sentiment
    return (accumulator1[0] + accumulator2[0], accumulator1[1] + accumulator2[1])


# filter for streams that are actually articles by checking if the string has wc in it
usefuldata = articles.filter(lambda article: "wc" in article).map(
    lambda article: (json.loads(article)["month"], (int(
        json.loads(article)["wc"]), float(json.loads(article)["sentiment"]))))
# usefuldata now contains a list of all the month, sentiment and wordcount pairs

total_sentiment_rdd = usefuldata.transform(
    # a is the previous value, b is the current
    lambda x: x.aggregateByKey(
        (0, 0),
        seq_op,
        comb_op
    ))

ytViewsData_rdd = articles.filter(lambda article: "likes" in article).map(
    lambda article: (str(json.loads(article)["year"]) + str(json.loads(article)["month"]), int(
        json.loads(article)["views"])))

# add the previous sentiment and wordocunt values with the new values


def aggregate_months_count(new_values, total_sum):
    if total_sum is None:
        total_sum = (0.0, 0)
    values = total_sum

    if new_values:
        values = (sum([pair[0] for pair in new_values], total_sum[0]),
                  sum([pair[1] for pair in new_values], total_sum[1]))

    return values


def aggregate_views_count(new_values, total_sum):
    if total_sum is None:
        total_sum = 0
    values = total_sum
    if new_values:
        values = sum(new_values, total_sum)
    return values


sentiment_totals = total_sentiment_rdd.updateStateByKey(aggregate_months_count)

views_total = ytViewsData_rdd.updateStateByKey(aggregate_views_count)

#
# # GOAL: In the results list we send to the dashboard, we want results containing the following aggregated data:
# # <date, genre, %likes, avgViews, newsWordCount, avgNewsSentiment> - possibly more in the future
# # either like this or maybe in HighCharts format:
# # dates = []            the month/year of the data
# # genres = []           genre
# # likes = []            percentage of likes
# # views = []            average views
# # ....
# def send_results_to_dashboard(df):
#     top_tags = []
#     tags_count = []
#     # extract the hashtags from dataframe and convert them into array
#     # extract the counts from dataframe and convert them into array
#     for tag in df:
#         top_tags.append(tag[0])
#         tags_count.append(tag[1])
#     # initialize and send the data through REST API
#     url = 'http://host.docker.internal:5001/updateData'
#     request_data = {'label': str(top_tags), 'data': str(tags_count)}
#     response = requests.post(url, data=request_data)
#
#
# # process a single time interval


def send_results_to_flask(result):
    url = "http://127.0.0.1:5000/UpdateSentiment"
    request_data = {'label': '{}'.format(
        result[0]), 'data': str(result[1])}  # , result[1][1])}
    response = requests.post(url, data=request_data)
    return response.status_code


def process_interval(time, rdd):
    # print a separator
    print("----------- %s -----------" % str(time))
    try:
        sentiments = rdd.collect()
        for el in sentiments:
            # print(el)
            # elList = el.split(",")
            # print(str(len(el)))
            print('{} {} {}'.format(el[0], el[1][0], el[1][1]))
            send_results_to_flask(el)
            # formula for total sentiment weighting
            # its all about the weights, for each game
            # game sentiment += (gamewc in article) / (total word count for all articles in month) * article sentiment
            # 1. aggregate the total wc of the game for the month, for any article with wc >0, store in a list as tuple with its sentiment
            # 2. when the month changes, go through the list and divide each wc with the total wc, times that by the sentiment,
            # add that to the running sentiment
            # 3. take the sentiment, add it to running sentiment for the month(in the dictionary),and add wc to total wc for month in the dict
            # 4. at the end of the job, we'll have a list like
            # [Jan: [sentiment, wc], Feb: [sentiment, wc], Mar: [Sentiment, wc]....]
            # divide each value by wc to obtain the weighted sentiment value to be sent to the frontend
    except:
        e = sys.exc_info()[0]
        print("Error: Fuckkkkkkkkk %s" % e)


def process_views_interval(time, rdd):
    try:
        videos = rdd.collect()
        for video in videos:
            print('{} {}'.format(video[0], video[1]))
    except:
        e = sys.exc_info()[0]
        print("Error: Fuckkkkkkkkk %s" % e)


# do this for every single interval
# articles.foreachRDD(process_interval)
sentiment_totals.foreachRDD(process_interval)
# newsDataStream.foreachRDD(process_interval)
views_total.foreachRDD(process_views_interval)
# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()
