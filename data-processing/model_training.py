import os
import json
import logging
from pathlib import Path
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.ml.evaluation import RegressionEvaluator

logger = logging.getLogger(__name__)

def train_als_model_minimal(train_data, validation_data, spark):
    """
    Train ALS with ABSOLUTE MINIMUM parameters for low-memory systems
    
    Args:
        train_data: Training dataset
        validation_data: Validation dataset
        spark: SparkSession for checkpointing
    
    Returns:
        tuple: (model, hyperparameters, metrics)
    """
    logger.info("Initializing ALS with ULTRA-MINIMAL parameters...")
    logger.warning("Using rank=2, maxIter=1 - Model quality will be very poor!")
    logger.warning("This is only for demonstration on low-memory systems.")
    
    # Setup checkpoint directory to break lineage
    checkpoint_dir = "C:/tmp/spark-checkpoint"
    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
    spark.sparkContext.setCheckpointDir(checkpoint_dir)
    
    # Ultra-minimal ALS configuration
    als = ALS(
        maxIter=1,  # Only 1 iteration
        regParam=0.2,
        rank=2,  # Minimum rank
        userCol="userId",
        itemCol="movieId",
        ratingCol="rating",
        coldStartStrategy="drop",
        nonnegative=False,
        implicitPrefs=False,
        seed=42
    )
    
    logger.info("Starting model training (this may take a few minutes)...")
    logger.info("Parameters: rank=2, maxIter=1, regParam=0.2")
    
    try:
        # Checkpoint training data to break lineage
        train_data.checkpoint()
        
        # Train model
        model = als.fit(train_data)
        
        logger.info("Model training completed!")
        
        # Get hyperparameters
        hyperparams = {
            "maxIter": als.getMaxIter(),
            "rank": model.rank,
            "regParam": als.getRegParam(),
            "userCol": als.getUserCol(),
            "itemCol": als.getItemCol(),
            "ratingCol": als.getRatingCol(),
            "coldStartStrategy": als.getColdStartStrategy()
        }
        
        # Evaluate model
        logger.info("Evaluating model...")
        try:
            metrics = evaluate_model_minimal(model, validation_data)
        except Exception as e:
            logger.warning(f"Evaluation failed: {e}")
            metrics = {"rmse": "N/A", "mae": "N/A"}
        
        return model, hyperparams, metrics
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        logger.error("Your system may not have enough memory even for minimal training.")
        logger.error("Suggestions:")
        logger.error("1. Close all other applications")
        logger.error("2. Reduce sample_rate even more (try 0.0005)")
        logger.error("3. Consider using a system with more RAM")
        raise

def evaluate_model_minimal(model, validation_data):
    """
    Evaluate model with minimal memory usage
    
    Returns:
        dict: Dictionary containing RMSE and MAE
    """
    try:
        # Make predictions
        predictions = model.transform(validation_data)
        
        # Limit predictions for evaluation
        predictions = predictions.limit(100).cache()
        
        # Calculate RMSE
        rmse_evaluator = RegressionEvaluator(
            metricName="rmse",
            labelCol="rating",
            predictionCol="prediction"
        )
        rmse = rmse_evaluator.evaluate(predictions)
        
        # Calculate MAE
        mae_evaluator = RegressionEvaluator(
            metricName="mae",
            labelCol="rating",
            predictionCol="prediction"
        )
        mae = mae_evaluator.evaluate(predictions)
        
        predictions.unpersist()
        
        metrics = {
            "rmse": round(float(rmse), 4),
            "mae": round(float(mae), 4)
        }
        
        logger.info(f"RMSE: {rmse:.4f}, MAE: {mae:.4f}")
        logger.warning("Note: These metrics are from a minimal model and sample!")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        return {"rmse": float('inf'), "mae": float('inf')}

def save_model(model, model_dir):
    """
    Save ALS model with metadata
    
    Args:
        model: Trained ALS model
        model_dir: Directory to save model
    """
    model_path = Path(model_dir)
    
    try:
        # Create model directory
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving model to {model_path}...")
        
        # Remove existing model if present
        if model_path.exists():
            import shutil
            logger.info("Removing existing model...")
            shutil.rmtree(model_path, ignore_errors=True)
        
        # Save the model
        model.write().overwrite().save(str(model_path))
        logger.info("Model saved successfully!")
        
        # Save metadata
        metadata = {
            "rank": model.rank,
            "userCol": "userId",
            "itemCol": "movieId",
            "ratingCol": "rating",
            "note": "Ultra-minimal model for low-memory systems"
        }
        
        metadata_path = model_path.parent / "model_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Metadata saved to {metadata_path}")
        
        # Save factors as CSV (optional, for inspection)
        try:
            csv_dir = model_path.parent / "csv_backup"
            csv_dir.mkdir(exist_ok=True)
            
            logger.info("Saving user factors (may take time)...")
            user_factors_path = csv_dir / "user_factors"
            if user_factors_path.exists():
                import shutil
                shutil.rmtree(user_factors_path, ignore_errors=True)
            
            model.userFactors.coalesce(1).write.csv(
                str(user_factors_path),
                header=True,
                mode="overwrite"
            )
            
            logger.info("Saving item factors (may take time)...")
            item_factors_path = csv_dir / "item_factors"
            if item_factors_path.exists():
                import shutil
                shutil.rmtree(item_factors_path, ignore_errors=True)
            
            model.itemFactors.coalesce(1).write.csv(
                str(item_factors_path),
                header=True,
                mode="overwrite"
            )
            
            logger.info("CSV backups saved")
        except Exception as e:
            logger.warning(f"Could not save CSV backups: {e}")
        
    except Exception as e:
        logger.error(f"Error saving model: {e}", exc_info=True)
        raise

def load_model(spark, model_dir):
    """
    Load ALS model from disk
    
    Args:
        spark: SparkSession
        model_dir: Directory containing the saved model
    
    Returns:
        ALSModel: Loaded model
    """
    model_path = Path(model_dir)
    
    logger.info(f"Loading model from: {model_path}")
    
    try:
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        model = ALSModel.load(str(model_path))
        logger.info("Model loaded successfully!")
        
        # Load metadata
        metadata_path = model_path.parent / "model_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            logger.info(f"Metadata: {metadata}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error loading model: {e}", exc_info=True)
        raise