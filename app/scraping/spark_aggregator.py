from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SQLContext
import sys
import requests

# ==== Spark Aggregator App ====
# Run this app second after running scraping.py
# This spark app receives data simultaneously from two web scraping scripts youtubeScraper & pcgamerScraper
# and transforms game-specific data into genre-wide data metrics, which get sent to the front end dashboard

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
youtubeDataStream = ssc.socketTextStream("twitter", 9009)
newsDataStream = ssc.socketTextStream("twitter", 9010)


# TODO: Do RDD aggregations here... and Modify the two functions below


# GOAL: In the results list we send to the dashboard, we want results containing the following aggregated data:
# <date, genre, %likes, avgViews, newsWordCount, avgNewsSentiment> - possibly more in the future
# either like this or maybe in HighCharts format:
# dates = []            the month/year of the data
# genres = []           genre
# likes = []            percentage of likes
# views = []            average views
# ....
def send_results_to_dashboard(df):
    top_tags = []
    tags_count = []
    # extract the hashtags from dataframe and convert them into array
    # extract the counts from dataframe and convert them into array
    for tag in df:
        top_tags.append(tag[0])
        tags_count.append(tag[1])
    # initialize and send the data through REST API
    url = 'http://host.docker.internal:5001/updateData'
    request_data = {'label': str(top_tags), 'data': str(tags_count)}
    response = requests.post(url, data=request_data)


# process a single time interval
def process_interval(time, rdd):
    # print a separator
    print("----------- %s -----------" % str(time))
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
        results = list()
        for tag in results:
            print('{:<40} {}'.format(tag[0], tag[1]))

        # call this method to prepare top 10 hashtags DF and send them
        send_results_to_dashboard(results)
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


# do this for every single interval
youtubeDataStream.foreachRDD(process_interval)
newsDataStream.foreachRDD(process_interval)

# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()
