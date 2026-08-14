"""
Direct FDA API testing - diagnose issues without the Flask server
"""
import requests
import json

def test_fda_api():
    base_url = "https://api.fda.gov/drug/ndc.json"
    
    print("=" * 70)
    print("FDA MEDICATION API - DIRECT TEST")
    print("=" * 70)
    print()
    
    # Test 1: NDC Search
    print("TEST 1: NDC Code Search (0093-0147)")
    print("-" * 70)
    try:
        params = {
            "search": 'product_ndc:"00930147"',
            "limit": 5
        }
        print(f"URL: {base_url}")
        print(f"Params: {params}")
        
        response = requests.get(base_url, params=params, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Full URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Results: {data.get('meta', {}).get('results', {}).get('total', 0)} total")
            if data.get("results"):
                med = data["results"][0]
                print(f"First result: {med.get('generic_name', 'N/A')} - {med.get('brand_name', 'N/A')}")
        else:
            print(f"Error Response: {response.text[:300]}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print()
    print()
    
    # Test 2: Generic Name Search
    print("TEST 2: Generic Name Search (aspirin)")
    print("-" * 70)
    try:
        params = {
            "search": "generic_name:aspirin",
            "limit": 5
        }
        print(f"URL: {base_url}")
        print(f"Params: {params}")
        
        response = requests.get(base_url, params=params, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Full URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Results: {data.get('meta', {}).get('results', {}).get('total', 0)} total")
            if data.get("results"):
                med = data["results"][0]
                print(f"First result: {med.get('generic_name', 'N/A')} - {med.get('brand_name', 'N/A')}")
        else:
            print(f"Error Response: {response.text[:300]}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print()
    print()
    
    # Test 3: Brand Name Search
    print("TEST 3: Brand Name Search (tylenol)")
    print("-" * 70)
    try:
        params = {
            "search": "brand_name:tylenol",
            "limit": 5
        }
        print(f"URL: {base_url}")
        print(f"Params: {params}")
        
        response = requests.get(base_url, params=params, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Full URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Results: {data.get('meta', {}).get('results', {}).get('total', 0)} total")
            if data.get("results"):
                med = data["results"][0]
                print(f"First result: {med.get('generic_name', 'N/A')} - {med.get('brand_name', 'N/A')}")
        else:
            print(f"Error Response: {response.text[:300]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_fda_api()
