from spark_env_fix import *
from pyspark.sql.functions import col, lit

def get_recommendations(model, user_id, num_recommendations=10, spark=None):
    if spark is None:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder \
            .appName("MovieRecommender") \
            .master("local[*]") \
            .config("spark.executorEnv.PYSPARK_PYTHON", os.environ["PYSPARK_PYTHON"]) \
            .config("spark.executorEnv.PYSPARK_DRIVER_PYTHON", os.environ["PYSPARK_DRIVER_PYTHON"]) \
            .config("spark.hadoop.io.nativefileio.disable", "true") \
            .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem") \
            .config("spark.executor.memory", "2g") \
            .config("spark.driver.memory", "2g") \
            .getOrCreate()
    # Generate top-N recommendations for user
    user_recommendations = model.recommendForUserSubset(
        spark.createDataFrame([(user_id,)], ["userId"]),
        num_recommendations
    )

    recommendations = user_recommendations.select(
        col("userId"),
        col("recommendations.movieId").alias("movieId"),
        col("recommendations.rating").alias("predictedRating")
    )

    return recommendations

def get_all_recommendations(model, num_recommendations=10):
    # Get top-N recommendations for all users
    all_recommendations = model.recommendForAllUsers(num_recommendations)
    return all_recommendations

def predict_ratings(model, test_data):
    predictions = model.transform(test_data)
    return predictions
