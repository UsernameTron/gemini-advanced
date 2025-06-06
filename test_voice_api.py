#!/usr/bin/env python3
"""
Test script for voice API endpoints
Tests the Flask routes and integration
"""

import sys
import os
import requests
import json
import time
from threading import Thread

# Add project path
sys.path.append('/Users/cpconnor/projects/UnifiedAIPlatform')

def start_test_server():
    """Start the web interface for testing."""
    from agent_system.web_interface import app
    app.run(host='127.0.0.1', port=5555, debug=False)

def test_voice_api():
    """Test voice API endpoints."""
    base_url = "http://127.0.0.1:5555/api/voice"
    
    print("🌐 Testing Voice API Endpoints...")
    time.sleep(2)  # Wait for server to start
    
    try:
        # Test 1: Get voice profiles
        print("\n1️⃣ Testing GET /api/voice/profiles")
        response = requests.get(f"{base_url}/profiles", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('profiles'):
                print(f"✅ Found {len(data['profiles'])} voice profiles")
                for profile in data['profiles']:
                    print(f"   - {profile['id']}: {profile['title']}")
            else:
                print("❌ No profiles found in response")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
        
        # Test 2: Get specific profile
        print("\n2️⃣ Testing GET /api/voice/profiles/satirical-voice")
        response = requests.get(f"{base_url}/profiles/satirical-voice", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('profile'):
                profile = data['profile']
                print(f"✅ Loaded profile: {profile['title']}")
                print(f"   Parameters: {len(profile.get('parameters', []))}")
            else:
                print("❌ Profile not found in response")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
        
        # Test 3: Test prompt generation
        print("\n3️⃣ Testing POST /api/voice/prompt")
        test_config = {
            'profile_id': 'satirical-voice',
            'parameters': {
                'target': 'tech',
                'satireModes': 'strategic-snark'
            }
        }
        response = requests.post(f"{base_url}/prompt", json=test_config, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('prompt'):
                print(f"✅ Generated prompt ({len(data['prompt'])} chars)")
                print(f"   Preview: {data['prompt'][:100]}...")
            else:
                print("❌ No prompt in response")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
        
        print("\n🎉 All API tests PASSED!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Run API tests."""
    print("🚀 Voice API Integration Test")
    print("=" * 50)
    
    # Start server in background
    server_thread = Thread(target=start_test_server, daemon=True)
    server_thread.start()
    
    # Run tests
    success = test_voice_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎯 Voice API integration is working correctly!")
    else:
        print("⚠️  Voice API integration has issues")
    
    return success

if __name__ == "__main__":
    main()
