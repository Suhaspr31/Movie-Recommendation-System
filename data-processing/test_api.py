import requests
import json

# API base URL
BASE_URL = "http://localhost:5001"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_stats():
    """Test stats endpoint"""
    print("\n" + "="*60)
    print("Testing Stats Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_user_info(user_id):
    """Test user info endpoint"""
    print("\n" + "="*60)
    print(f"Testing User Info Endpoint (User ID: {user_id})")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/user/{user_id}/info")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_item_info(item_id):
    """Test item info endpoint"""
    print("\n" + "="*60)
    print(f"Testing Item Info Endpoint (Item ID: {item_id})")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/item/{item_id}/info")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_recommendations(user_id, limit=10):
    """Test recommendation endpoint"""
    print("\n" + "="*60)
    print(f"Testing Recommendations Endpoint (User ID: {user_id}, Limit: {limit})")
    print("="*60)
    
    payload = {
        "userId": user_id,
        "limit": limit
    }
    
    response = requests.post(
        f"{BASE_URL}/recommend",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if 'recommendations' in result and result['recommendations']:
        print(f"\nTop 5 Recommendations:")
        for i, rec in enumerate(result['recommendations'][:5], 1):
            print(f"  {i}. Movie ID: {rec['movieId']}, "
                  f"Predicted Rating: {rec['predictedRating']:.4f}")
    
    return result

def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*60)
    print("MOVIE RECOMMENDATION API - TEST SUITE")
    print("="*60)
    
    try:
        # Test 1: Health check
        health_result = test_health()
        
        if not health_result.get('model_loaded', False):
            print("\n⚠ Model not loaded! Please check the API logs.")
            return
        
        # Test 2: Stats
        stats_result = test_stats()
        
        # Test 3: User info (use IDs from your CSV)
        test_user_info(10)  # From your CSV
        test_user_info(20)
        
        # Test 4: Item info
        test_item_info(30)  # From your CSV
        test_item_info(70)
        
        # Test 5: Get recommendations
        test_recommendations(10, limit=10)
        test_recommendations(20, limit=5)
        
        # Test 6: Non-existent user
        print("\n" + "="*60)
        print("Testing Non-Existent User (Should return 404)")
        print("="*60)
        test_recommendations(99999, limit=5)
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API!")
        print("Please make sure the Flask API is running on port 5001")
        print("\nTo start the API, run:")
        print("  python pyspark_recommendation_engine.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()