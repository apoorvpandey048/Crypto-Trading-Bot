"""
Test script to verify registration endpoint
"""
import requests
import json

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get('http://localhost:8001/health')
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_registration():
    """Test user registration"""
    url = 'http://localhost:8001/api/auth/register'
    data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'password123',
        'full_name': 'Test User'
    }
    
    try:
        print(f"\n📤 Sending registration request to {url}")
        print(f"   Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data)
        
        print(f"\n📥 Response status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print(f"✅ Registration successful!")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Registration failed")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration request failed: {e}")
        return False

def test_duplicate_registration():
    """Test duplicate registration handling"""
    url = 'http://localhost:8001/api/auth/register'
    data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'password123',
        'full_name': 'Test User'
    }
    
    try:
        print(f"\n📤 Testing duplicate registration...")
        response = requests.post(url, json=data)
        
        if response.status_code == 400:
            print(f"✅ Duplicate registration correctly rejected")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Duplicate test failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Testing Crypto Trading Bot Registration")
    print("=" * 60)
    
    # Test 1: Health check
    health_ok = test_health()
    
    if not health_ok:
        print("\n❌ Backend is not responding. Make sure it's running on port 8001")
        exit(1)
    
    # Test 2: Registration
    reg_ok = test_registration()
    
    # Test 3: Duplicate registration
    if reg_ok:
        dup_ok = test_duplicate_registration()
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"  Health Check: {'✅' if health_ok else '❌'}")
    print(f"  Registration: {'✅' if reg_ok else '❌'}")
    print("=" * 60)
