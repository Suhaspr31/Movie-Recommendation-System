from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
import ast
from pathlib import Path

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'factors_loaded': item_factors_df is not None,
        'item_count': len(item_factors_df) if item_factors_df is not None else 0
    })

# Paths to CSV factors
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
USER_FACTORS_PATH = os.path.join(BASE_PATH, "models/csv_backup/user_factors")
ITEM_FACTORS_PATH = os.path.join(BASE_PATH, "models/csv_backup/item_factors")

# Global variables for factors (using pandas instead of Spark)
user_factors_df = None
item_factors_df = None

# LOAD FACTORS ON STARTUP (Ensures this runs under Gunicorn)
print("--- INITIALIZING RECOMMENDATION ENGINE ---")
# Import here to avoid circular dependency if any, but since it's global scope it's fine.
# We will define load_factors first then call it.

def find_csv_file(directory):
    """Find the actual CSV file in a directory (handles Spark output structure)"""
    path = Path(directory)
    
    # If it's a file, return it
    if path.is_file() and path.suffix == '.csv':
        return str(path)
    
    # If it's a directory, find CSV files
    if path.is_dir():
        csv_files = list(path.glob("*.csv"))
        if csv_files:
            return str(csv_files[0])
        
        # Check for part-* files (Spark output)
        part_files = list(path.glob("part-*"))
        if part_files:
            # Filter out files starting with . or _
            valid_files = [f for f in part_files if not f.name.startswith('.') and not f.name.startswith('_')]
            if valid_files:
                return str(valid_files[0])
    
    return None

def parse_features_string(features_str):
    """Parse feature string like '[0.123, 0.456, ...]' into numpy array"""
    try:
        if pd.isna(features_str):
            return None
        
        # Handle string representation of list
        if isinstance(features_str, str):
            # Remove any extra quotes and whitespace
            features_str = features_str.strip().strip('"').strip("'")
            # Use ast.literal_eval for safe evaluation
            features_list = ast.literal_eval(features_str)
            return np.array(features_list, dtype=np.float32)
        
        return None
    except Exception as e:
        print(f"Error parsing features '{features_str}': {e}")
        return None

def load_factors():
    """Load user and item factors from CSV files using pandas"""
    global user_factors_df, item_factors_df
    
    try:
        print("Loading user factors from CSV...")
        
        # Find actual CSV file
        user_csv_file = find_csv_file(USER_FACTORS_PATH)
        if not user_csv_file:
            print(f"ERROR: No CSV file found in {USER_FACTORS_PATH}")
            return False
        
        print(f"Found user factors file: {user_csv_file}")
        
        # Read with pandas
        user_factors_df = pd.read_csv(user_csv_file)
        print(f"Loaded {len(user_factors_df)} users")
        print(f"Columns: {user_factors_df.columns.tolist()}")
        print("\nSample user data:")
        print(user_factors_df.head(3))
        
        # Parse features column
        print("\nParsing user features...")
        user_factors_df['features_array'] = user_factors_df['features'].apply(parse_features_string)
        
        # Remove rows with invalid features
        valid_users = user_factors_df['features_array'].notna()
        print(f"Valid user features: {valid_users.sum()}/{len(user_factors_df)}")
        user_factors_df = user_factors_df[valid_users].reset_index(drop=True)
        
        print("\nLoading item factors from CSV...")
        
        # Find actual CSV file
        item_csv_file = find_csv_file(ITEM_FACTORS_PATH)
        if not item_csv_file:
            print(f"ERROR: No CSV file found in {ITEM_FACTORS_PATH}")
            return False
        
        print(f"Found item factors file: {item_csv_file}")
        
        # Read with pandas
        item_factors_df = pd.read_csv(item_csv_file)
        print(f"Loaded {len(item_factors_df)} items")
        print(f"Columns: {item_factors_df.columns.tolist()}")
        print("\nSample item data:")
        print(item_factors_df.head(3))
        
        # Parse features column
        print("\nParsing item features...")
        item_factors_df['features_array'] = item_factors_df['features'].apply(parse_features_string)
        
        # Remove rows with invalid features
        valid_items = item_factors_df['features_array'].notna()
        print(f"Valid item features: {valid_items.sum()}/{len(item_factors_df)}")
        item_factors_df = item_factors_df[valid_items].reset_index(drop=True)
        
        print(f"\nSuccessfully loaded {len(user_factors_df)} users and {len(item_factors_df)} items")
        
        # Show feature dimensions
        if len(user_factors_df) > 0:
            sample_features = user_factors_df['features_array'].iloc[0]
            print(f"Feature dimensions: {len(sample_features)}")
        
        return True
        
    except Exception as e:
        print(f"Error loading factors: {e}")
        import traceback
        traceback.print_exc()
        return False

def compute_dot_product(user_features, item_features):
    """Compute dot product between user and item feature vectors"""
    try:
        if user_features is None or item_features is None:
            return 0.0
        
        # Ensure both arrays have same length
        min_len = min(len(user_features), len(item_features))
        
        # Compute dot product
        dot_product = np.dot(user_features[:min_len], item_features[:min_len])
        return float(dot_product)
    except Exception as e:
        print(f"Error computing dot product: {e}")
        return 0.0

@app.route('/recommend', methods=['POST'])
def recommend():
    """Generate recommendations for a user"""
    try:
        if item_factors_df is None:
            return jsonify({'error': 'Item factors not loaded'}), 500
        
        data = request.json
        user_id = data.get('userId')
        liked_movie_ids = data.get('likedMovieIds', []) or [] # ensure it is a list
        limit = int(data.get('limit', 10))
        
        print(f"\n[INFO] Rec request: userId={user_id}, likedCount={len(liked_movie_ids)}")
        
        user_features = None
        
        # Scenario A: User has history
        if liked_movie_ids:
            # item_factors_df['id'] comes from CSV, could be int or string.
            # Convert all to clean strings for robust matching.
            liked_movie_ids_str = [str(mid).strip() for mid in liked_movie_ids]
            
            # Create a local ID string column to avoid global state issues
            df_ids = item_factors_df['id'].astype(str).str.strip()
            liked_items = item_factors_df[df_ids.isin(liked_movie_ids_str)]
            
            if not liked_items.empty:
                # Average features to create dynamic profile
                features_list = liked_items['features_array'].tolist()
                user_features = np.mean(features_list, axis=0)
                print(f"[INFO] Created profile from {len(liked_items)} matched movies")
            else:
                # Log safe slice of the search list
                search_preview = liked_movie_ids_str[:5]
                print(f"[WARN] No liked movies found in factors. Search: {search_preview}...")

        # Scenario B: Fallback to model's pre-trained user factors
        if user_features is None and user_id is not None:
            # Try matching as string or int
            if user_factors_df is not None:
                user_matches = user_factors_df[user_factors_df['id'].astype(str) == str(user_id)]
                if not user_matches.empty:
                    user_features = user_matches['features_array'].iloc[0]
                    print(f"[INFO] Using pre-trained factors for User {user_id}")

        # Scenario C: Pure fallback (shuffled popular-ish)
        if user_features is None:
            print("[INFO] Fallback to popular movies (no user data)")
            # Take a larger pool and shuffle to avoid "stuck UI"
            pool_size = min(100, len(item_factors_df))
            sample_pool = item_factors_df.head(pool_size).sample(n=min(limit, pool_size))
            
            recs = []
            for _, row in sample_pool.iterrows():
                recs.append({
                    'movieId': str(row['id']),
                    'predictedRating': 4.0
                })
            
            return jsonify({
                'userId': str(user_id), 
                'recommendations': recs,
                'note': 'fallback_shuffled'
            })

        # Compute Similarity
        print(f"[INFO] Computing similarity for {len(item_factors_df)} items...")
        
        # Filter out movies the user already knows/likes
        exclude_ids = set([str(mid).strip() for mid in liked_movie_ids])
        
        item_scores = []
        for _, item_row in item_factors_df.iterrows():
            item_id_str = str(item_row['id']).strip()
            if item_id_str in exclude_ids:
                continue
                
            item_features = item_row['features_array']
            if item_features is not None:
                score = compute_dot_product(user_features, item_features)
                item_scores.append({
                    'movieId': item_id_str,
                    'predictedRating': round(float(score), 4)
                })
        
        # Sort and return top N
        item_scores.sort(key=lambda x: x['predictedRating'], reverse=True)
        top_recs = item_scores[:limit]
        
        print(f"[INFO] Generated {len(top_recs)} recs")
        return jsonify({
            'userId': str(user_id),
            'recommendations': top_recs
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/user/<int:user_id>/info', methods=['GET'])
def get_user_info(user_id):
    """Get information about a specific user"""
    try:
        if user_factors_df is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        user_row = user_factors_df[user_factors_df['id'] == user_id]
        
        if len(user_row) == 0:
            return jsonify({
                'error': f'User {user_id} not found',
                'availableUsers': user_factors_df['id'].tolist()[:10]
            }), 404
        
        user_features = user_row['features_array'].iloc[0]
        
        return jsonify({
            'userId': user_id,
            'featureDimensions': len(user_features) if user_features is not None else 0,
            'exists': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/item/<int:item_id>/info', methods=['GET'])
def get_item_info(item_id):
    """Get information about a specific item"""
    try:
        if item_factors_df is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        item_row = item_factors_df[item_factors_df['id'] == item_id]
        
        if len(item_row) == 0:
            return jsonify({
                'error': f'Item {item_id} not found',
                'availableItems': item_factors_df['id'].tolist()[:10]
            }), 404
        
        item_features = item_row['features_array'].iloc[0]
        
        return jsonify({
            'movieId': item_id,
            'featureDimensions': len(item_features) if item_features is not None else 0,
            'exists': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about the loaded model"""
    try:
        if user_factors_df is None or item_factors_df is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        user_count = len(user_factors_df)
        item_count = len(item_factors_df)
        
        # Get feature dimensions
        sample_features = user_factors_df['features_array'].iloc[0]
        feature_dims = len(sample_features) if sample_features is not None else 0
        
        return jsonify({
            'totalUsers': user_count,
            'totalItems': item_count,
            'featureDimensions': feature_dims,
            'modelType': 'ALS Matrix Factorization',
            'status': 'loaded',
            'sampleUserIds': user_factors_df['id'].tolist()[:10],
            'sampleItemIds': item_factors_df['id'].tolist()[:10]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reload', methods=['POST'])
def reload_model():
    """Reload the model factors"""
    try:
        success = load_factors()
        if success:
            return jsonify({'status': 'success', 'message': 'Model reloaded'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to reload model'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# LOAD MODEL ON STARTUP
# This ensures data is loaded even when running via Gunicorn
print("\n[STARTUP] Pre-loading model factors for production...")
load_factors()

if __name__ == '__main__':
    print("=" * 60)
    print("Movie Recommendation API - Starting (Local Dev)...")
    print("Using Pure Python/Pandas (No Spark Required)")
    # load_factors() already called above
    print("=" * 60)
    
    # Load factors on startup
    print("\nLoading model factors...")
    # if load_factors(): # This call is now handled by the global load_factors() above
    if user_factors_df is not None and item_factors_df is not None: # Check if global load was successful
        print("\n" + "=" * 60)
        print("Model loaded successfully!")
        print("=" * 60)
        print("\nAPI Endpoints:")
        print("  POST   /recommend          - Get recommendations for a user")
        print("  GET    /user/<id>/info     - Get user information")
        print("  GET    /item/<id>/info     - Get item information")
        print("  GET    /stats              - Get model statistics")
        print("  GET    /health             - Health check")
        print("  POST   /reload             - Reload model")
        print("\nStarting Flask server on port 5001...")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Failed to load model factors!")
        print("=" * 60)
        print("Please check the paths:")
        print(f"  User factors: {USER_FACTORS_PATH}")
        print(f"  Item factors: {ITEM_FACTORS_PATH}")
        print("=" * 60)
    
    app.run(debug=True, port=5001, host='0.0.0.0')