"""
Debug authentication issues
"""
import requests
import json

BASE_URL = "http://localhost:8001"

print("=" * 70)
print("Authentication Debug Test")
print("=" * 70)

# Test 1: Register a new user
print("\n1. Testing Registration...")
register_data = {
    "email": "debug_user@test.com",
    "username": "debug_user",
    "password": "Debug123!"
}
try:
    r = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    if r.status_code == 201:
        print("   ✓ Registration successful")
    elif r.status_code == 400:
        print("   ✓ User already exists (expected)")
    else:
        print(f"   ✗ Unexpected status code")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Login with the registered user
print("\n2. Testing Login...")
login_data = {
    "username": "debug_user@test.com",
    "password": "Debug123!"
}
try:
    r = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    print(f"   Status: {r.status_code}")
    response_data = r.json()
    print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    if r.status_code == 200:
        if 'access_token' in response_data:
            token = response_data['access_token']
            print(f"   ✓ Login successful")
            print(f"   Token (first 50 chars): {token[:50]}...")
            
            # Test 3: Use the token to access protected endpoint
            print("\n3. Testing Protected Endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
            print(f"   Status: {r.status_code}")
            print(f"   Response: {r.json()}")
            if r.status_code == 200:
                print("   ✓ Protected endpoint access successful")
            else:
                print("   ✗ Protected endpoint access failed")
        else:
            print(f"   ✗ No access_token in response. Keys: {list(response_data.keys())}")
    else:
        print(f"   ✗ Login failed")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 70)
print("Debug test completed")
print("=" * 70)
