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

