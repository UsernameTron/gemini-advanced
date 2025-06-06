#!/usr/bin/env python3
"""
Test script for voice template integration
Tests the complete voice configuration system
"""

import sys
import os
import json

# Add project path
sys.path.append('/Users/cpconnor/projects/UnifiedAIPlatform')

from voice.voice_config import voice_loader, build_voice_prompt_prefix, get_current_param


def test_voice_profile_loading():
    """Test loading voice profiles."""
    print("🔍 Testing Voice Profile Loading...")
    
    # Get available profiles
    profiles = voice_loader.get_available_profiles()
    print(f"Available profiles: {profiles}")
    
    if 'satirical-voice' not in profiles:
        print("❌ ERROR: satirical-voice profile not found!")
        return False
    
    # Load the satirical voice profile
    profile = voice_loader.get_profile('satirical-voice')
    if not profile:
        print("❌ ERROR: Could not load satirical-voice profile!")
        return False
    
    print(f"✅ Loaded profile: {profile.title}")
    print(f"   Description: {profile.description}")
    print(f"   Parameters: {len(profile.parameters)} parameters")
    print(f"   Categories: {len(profile.satire_mode_definitions) if hasattr(profile, 'satire_mode_definitions') else 0} satire modes")
    
    return True


def test_parameter_handling():
    """Test parameter handling functionality."""
    print("\n🔧 Testing Parameter Handling...")
    
    profile = voice_loader.get_profile('satirical-voice')
    if not profile:
        return False
    
    # Test parameter options
    target_options = profile.get_param_options('target')
    print(f"Target options: {len(target_options)} options")
    
    # Test default values
    default_target = profile.get_param_default('target')
    print(f"Default target: {default_target}")
    
    # Test parameter labels
    target_label = profile.get_param_label('target')
    print(f"Target label: {target_label}")
    
    return True


def test_prompt_generation():
    """Test prompt generation functionality."""
    print("\n📝 Testing Prompt Generation...")
    
    # Set current profile
    voice_loader.set_current_profile('satirical-voice')
    
    # Test basic prompt generation
    test_config = {
        'target': 'corporate',
        'satireModes': 'strategic-snark',
        'techniques': 'exaggeration'
    }
    
    try:
        prompt_prefix = build_voice_prompt_prefix(test_config)
        print(f"✅ Generated prompt prefix ({len(prompt_prefix)} chars)")
        print(f"Preview: {prompt_prefix[:200]}...")
        return True
    except Exception as e:
        print(f"❌ ERROR generating prompt: {e}")
        return False


def test_session_integration():
    """Test session-like configuration."""
    print("\n🔄 Testing Session Integration...")
    
    # Simulate session configuration
    session_config = {
        'profile_id': 'satirical-voice',
        'parameters': {
            'target': 'tech',
            'satireModes': 'high-satire',
            'techniques': 'parody',
            'voiceStyle': 'caustic'
        }
    }
    
    try:
        # Set profile
        voice_loader.set_current_profile(session_config['profile_id'])
        
        # Generate prompt with session config
        prompt = build_voice_prompt_prefix(session_config['parameters'])
        print(f"✅ Session-based prompt generated ({len(prompt)} chars)")
        
        # Test parameter retrieval
        current_target = get_current_param('target', session_config['parameters'])
        print(f"Current target from session: {current_target}")
        
        return True
    except Exception as e:
        print(f"❌ ERROR in session integration: {e}")
        return False


def main():
    """Run all voice integration tests."""
    print("🚀 Voice Template Integration Test")
    print("=" * 50)
    
    tests = [
        test_voice_profile_loading,
        test_parameter_handling,
        test_prompt_generation,
        test_session_integration
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("❌ Test failed!")
        except Exception as e:
            print(f"❌ Test error: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All voice integration tests PASSED!")
        return True
    else:
        print("⚠️  Some tests failed - check configuration")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
