#!/usr/bin/env python3
"""
Google Gemini API Fix - Test with newer models
"""

import os
from dotenv import load_dotenv
load_dotenv()

def test_gemini_with_new_models():
    """Test Google Gemini API with updated model names"""
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No Google API key found")
        return False
        
    try:
        import google.generativeai as genai
        
        # Configure with API key
        genai.configure(api_key=api_key)
        
        # List all available models
        print("🔍 Listing all available Gemini models...")
        models = list(genai.list_models())
        
        print(f"📊 Found {len(models)} total models")
        
        # Filter for content generation models
        content_models = [model for model in models if 'generateContent' in model.supported_generation_methods]
        print(f"📝 Found {len(content_models)} content generation models:")
        
        for model in content_models[:10]:  # Show first 10
            print(f"   • {model.name}")
            
        # Test with gemini-1.5-flash (the recommended replacement)
        try:
            print("\n🧪 Testing with gemini-1.5-flash...")
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Say 'API test successful'")
            print(f"✅ Success! Response: {response.text.strip()}")
            return True
            
        except Exception as e:
            print(f"❌ gemini-1.5-flash failed: {e}")
            
            # Try with the first available model
            if content_models:
                test_model_name = content_models[0].name
                print(f"\n🧪 Testing with {test_model_name}...")
                model = genai.GenerativeModel(test_model_name)
                response = model.generate_content("Say 'API test successful'")
                print(f"✅ Success! Response: {response.text.strip()}")
                return True
            else:
                print("❌ No content generation models available")
                return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Google Gemini API with updated models...")
    success = test_gemini_with_new_models()
    print(f"\n📊 Test result: {'SUCCESS' if success else 'FAILED'}")
