from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SQLContext
import sys
import time
import requests
import re
import json

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
combinedDataStream = ssc.socketTextStream("twitter", 9009)
# For use in Abduls local spark instance, comment out if using in docker
#combinedDataStream = ssc.socketTextStream("10.0.75.1", 9009)

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
    # lambda article: (article.split(",")[0][10:11], (int(article.split(",")[4][7:8]), float(article.split(",")[5][14:23]))))  # article.split(",")[10:11]
    lambda article: (json.loads(article)["month"], (int(
        json.loads(article)["wc"]), float(json.loads(article)["sentiment"]))))
# lambda article: (article["month"], article["sentiment"], article["wc"]))
# usefuldata now contains a list of all the month, sentiment and wordcount pairs
total_sentiment_rdd = usefuldata.transform(
    # a is the previous value, b is the current
    lambda x: x.aggregateByKey(
        (0, 0),
        seq_op,
        comb_op
    ))

# add the previous sentiment and wordocunt values with the new values


def aggregate_months_count(new_values, total_sum):
    if total_sum is None:
        total_sum = (0.0, 0)
    values = total_sum

    if new_values:
        values = (sum([pair[0] for pair in new_values], total_sum[0]),
                  sum([pair[1] for pair in new_values], total_sum[1]))

    return values


sentiment_totals = total_sentiment_rdd.updateStateByKey(aggregate_months_count)

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


def process_interval(time, rdd):
    # print a separator
    print("----------- %s -----------" % str(time))

    gameSentiment = []
    MonthDict = {}
    totalMonthWordCount = 0
    runningsentiment = 0
    try:
        # global overall_averages
        # # sum_count format: ('topic', (numerator, denominator))
        # # reduce keys by summing up all sentiment results for each key, counting # of keys, and adding on new values to overall averages
        # sum_count = rdd.combineByKey((lambda x: (x, 1)), (lambda x, y: (x[0] + y, x[1] + 1)), (lambda x, y: (x[0] + y[0], x[1] + y[1])))
        # for el in sum_count.collect():
        #     for i, e in enumerate(overall_averages):
        #         if e[0] == el[0]:       # if 'topic' == t1
        #             tmp = list(overall_averages[i])
        #             tmp[1] = tmp[1] + el[1][0]
        #             tmp[2] = tmp[2] + el[1][1]
        #             overall_averages[i] = tuple(tmp)
        # # print(str(overall_averages))
        # top10 = list(map(lambda k: (k[0], k[1] / k[2] if k[2] > 0 else 0), overall_averages))
        # # print it nicely
        for el in rdd.collect():
            print(el)
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

            # how this will be done in spark
            # remember these are done in 2 second intervals
            # for each stream seen in the last 2 second, divide it up into pcgamer stream, or youtube stream
            # for pcgamer stream,
            # if el.contains("Sentiment"):
            #     if el["month"] != previousMonth:
            #         #do the aggregation
            #         for i in gameSentiment:
            #             runningsentiment += ((i[1]/totalMonthWordCount) * i[0])
            #         MonthDict[previousMonth] = [MonthDict.get(previousMonth, [0, 0])[0] + runningsentiment, MonthDict.get(previousMonth, [0, 0])[1] + totalMonthWordCount]
            #         print(previousmonth + " " + str(totalMonthWordCount) + " " + runningsentiment)
            #         previousMonth = el["month"]
            #         runningsentiment = 0
            #         totalMonthWordCount = 0
            #         gameSentiment = []

            #     elif el["wc" > 0]
            #         gameSentiment.append([el["sentiment"], el["wc"]])
            #         totalMonthWordCount += el["wc"]

        # results = list()
        # for tag in results:
        #     print('{:<40} {}'.format(tag[0], tag[1]))
        # call this method to prepare top 10 hashtags DF and send them
        # send_results_to_dashboard(results)
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


# do this for every single interval
# articles.foreachRDD(process_interval)
sentiment_totals.foreachRDD(process_interval)
# newsDataStream.foreachRDD(process_interval)

# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()
