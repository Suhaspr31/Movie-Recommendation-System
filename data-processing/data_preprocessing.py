import pandas as pd
import numpy as np
import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, FloatType

def initialize_spark():
    from pyspark import SparkConf

    conf = SparkConf() \
        .set("spark.executor.memory", "2g") \
        .set("spark.driver.memory", "2g") \
        .set("spark.sql.shuffle.partitions", "100")

    spark = SparkSession.builder \
        .appName("MovieRecommendation") \
        .master("local[*]") \
        .config(conf=conf) \
        .config("spark.hadoop.io.nativefileio.disable", "true") \
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem") \
        .getOrCreate()
    return spark

def load_data(spark, ratings_path, movies_path):
    # Load ratings data
    ratings = spark.read.csv(ratings_path, header=True, inferSchema=True)
    from pyspark.sql.functions import col
    ratings = ratings.select(
        col("userId").cast(IntegerType()),
        col("movieId").cast(IntegerType()),
        col("rating").cast(FloatType())
    )
    
    # Load movies data
    movies = spark.read.csv(movies_path, header=True, inferSchema=True)
    movies = movies.select(
        col("movieId").cast(IntegerType()),
        col("title"),
        col("genres")
    )
    
    return ratings, movies

def clean_data(ratings):
    # Remove null values
    ratings = ratings.dropna()
    
    # Filter outliers (ratings between 0 and 5)
    ratings = ratings.filter((ratings.rating >= 0) & (ratings.rating <= 5))
    
    return ratings

def get_data_statistics(ratings):
    print(f"Total ratings: {ratings.count()}")
    print(f"Unique users: {ratings.select('userId').distinct().count()}")
    print(f"Unique movies: {ratings.select('movieId').distinct().count()}")
    
    ratings.show()
