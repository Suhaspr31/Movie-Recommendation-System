import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_hadoop_environment():
    """Configure Hadoop environment for Windows"""
    hadoop_home = Path("C:/hadoop")
    os.environ["HADOOP_HOME"] = str(hadoop_home)
    os.environ['HADOOP_DISABLE_NATIVE'] = 'true'
    
    logger.info(f"HADOOP_HOME set to: {os.environ.get('HADOOP_HOME')}")
    
    winutils_path = hadoop_home / "bin" / "winutils.exe"
    if not winutils_path.exists():
        logger.error("winutils.exe not found!")
        return False
    
    logger.info(f"winutils.exe found")
    return True

def initialize_spark_minimal():
    """Initialize Spark with ABSOLUTE MINIMUM memory settings"""
    from pyspark.sql import SparkSession
    
    logger.info("Initializing Spark with minimal memory...")
    
    # Set ultra-low memory before Spark initialization
    os.environ['SPARK_DRIVER_MEMORY'] = '512m'
    os.environ['SPARK_EXECUTOR_MEMORY'] = '512m'
    
    spark = (
        SparkSession.builder
        .appName("MovieALS_Minimal")
        .master("local[1]")  # ONLY 1 core
        .config("spark.driver.memory", "512m")  # Minimum
        .config("spark.executor.memory", "512m")
        .config("spark.driver.maxResultSize", "256m")
        .config("spark.sql.warehouse.dir", "C:/tmp/spark-warehouse")
        .config("spark.local.dir", "C:/tmp/spark-temp")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.default.parallelism", "1")
        .config("spark.memory.fraction", "0.6")
        .config("spark.memory.storageFraction", "0.2")
        .config("spark.rdd.compress", "true")
        .config("spark.shuffle.compress", "true")
        .config("spark.shuffle.spill.compress", "true")
        .config("spark.cleaner.periodicGC.interval", "1min")
        # Stack size
        .config("spark.executor.extraJavaOptions", "-Xss2m -XX:+UseSerialGC")
        .config("spark.driver.extraJavaOptions", "-Xss2m -XX:+UseSerialGC")
        # Serialization
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .config("spark.kryoserializer.buffer.max", "256m")
        # Hadoop
        .config("spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version", "2")
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
        .getOrCreate()
    )
    
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Spark session started with 512MB memory")
    return spark

def validate_paths(*paths):
    """Validate that all required file paths exist"""
    for path in paths:
        if not Path(path).exists():
            logger.error(f"Required file not found: {path}")
            return False
    return True

def main():
    """Main execution pipeline with ultra-minimal settings"""
    try:
        # Setup environment
        if not setup_hadoop_environment():
            logger.error("Hadoop environment setup failed")
            sys.exit(1)
        
        # Define paths
        BASE_DIR = Path(r"C:\BDA\movie-recommendation-system\data-processing")
        ratings_path = BASE_DIR / "datasets" / "ratings.csv"
        movies_path = BASE_DIR / "datasets" / "movies.csv"
        model_path = BASE_DIR / "models" / "als_model"
        
        # Validate paths
        if not validate_paths(ratings_path, movies_path):
            logger.error("Required data files not found")
            sys.exit(1)
        
        # Initialize Spark with minimal memory
        spark = initialize_spark_minimal()
        
        # Import after Spark is initialized
        from data_preprocessing import load_data, clean_data
        from model_training import train_als_model_minimal, save_model
        
        # Load data
        logger.info("Loading data...")
        ratings, movies = load_data(spark, str(ratings_path), str(movies_path))
        initial_count = ratings.count()
        logger.info(f"Data loaded: {initial_count} ratings")
        
        # Clean data
        logger.info("Cleaning data...")
        ratings = clean_data(ratings)
        
        # ULTRA MINIMAL SAMPLE - 0.1%
        sample_rate = 0.001
        logger.info(f"Sampling {sample_rate*100}% of data...")
        ratings_sampled = ratings.sample(sample_rate, seed=42).repartition(1)
        ratings_sampled.cache()
        
        sample_count = ratings_sampled.count()
        logger.info(f"Sampled: {sample_count} ratings")
        
        if sample_count < 50:
            logger.error(f"Sample too small ({sample_count} rows). Need at least 50.")
            logger.info("Increase sample_rate in code or use smaller dataset.")
            sys.exit(1)
        
        # Split data
        logger.info("Splitting data...")
        train, validation = ratings_sampled.randomSplit([0.8, 0.2], seed=42)
        
        train = train.repartition(1).cache()
        validation = validation.repartition(1).cache()
        
        train_count = train.count()
        val_count = validation.count()
        logger.info(f"Train: {train_count}, Validation: {val_count}")
        
        if train_count < 20:
            logger.error("Training set too small.")
            sys.exit(1)
        
        # Train with absolute minimal parameters
        logger.info("Training ULTRA-MINIMAL ALS model...")
        logger.warning("Model quality will be poor due to memory constraints!")
        
        model, hyperparams, metrics = train_als_model_minimal(train, validation, spark)
        
        logger.info("Training completed!")
        logger.info(f"Hyperparameters: {hyperparams}")
        logger.info(f"Metrics: {metrics}")
        
        # Save model
        logger.info(f"Saving model...")
        save_model(model, str(model_path))
        logger.info(f"Model saved to: {model_path}")
        
        # Cleanup
        logger.info("Cleaning up...")
        ratings_sampled.unpersist()
        train.unpersist()
        validation.unpersist()
        
        logger.info("=" * 50)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if 'spark' in locals():
            logger.info("Stopping Spark...")
            spark.stop()
            logger.info("Spark stopped")

if __name__ == "__main__":
    main()