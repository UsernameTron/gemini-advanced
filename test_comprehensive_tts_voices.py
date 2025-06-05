#!/usr/bin/env python3
"""
Comprehensive TTS Voice Testing Script
Tests all 9 OpenAI voices supported by the VectorDBRAG system
"""

import requests
import time
import json
from typing import Dict, List, Any

# All 9 supported OpenAI voices
VOICES = [
    {
        'name': 'alloy',
        'description': 'Balanced, neutral voice',
        'gender': 'neutral'
    },
    {
        'name': 'ash',
        'description': 'Clear, professional tone ideal for business',
        'gender': 'neutral'
    },
    {
        'name': 'coral',
        'description': 'Friendly, approachable voice for conversations',
        'gender': 'female'
    },
    {
        'name': 'echo',
        'description': 'Warm, expressive voice',
        'gender': 'neutral'
    },
    {
        'name': 'fable',
        'description': 'Clear, articulate voice',
        'gender': 'neutral'
    },
    {
        'name': 'nova',
        'description': 'Bright, energetic voice',
        'gender': 'female'
    },
    {
        'name': 'onyx',
        'description': 'Deep, resonant voice',
        'gender': 'male'
    },
    {
        'name': 'sage',
        'description': 'Wise, measured voice ideal for educational content',
        'gender': 'neutral'
    },
    {
        'name': 'shimmer',
        'description': 'Smooth, pleasant voice',
        'gender': 'female'
    }
]

# Test configurations
TEST_CONFIG = {
    'base_url': 'http://localhost:5001',
    'test_text': 'This is a comprehensive test of the OpenAI Text-to-Speech service with voice {voice_name}.',
    'models': ['tts-1', 'tts-1-hd'],
    'speeds': [1.0, 1.2],
    'formats': ['mp3', 'opus']
}

def test_voice_endpoint() -> Dict[str, Any]:
    """Test the /api/tts/voices endpoint"""
    print("Testing voices endpoint...")
    
    try:
        response = requests.get(f"{TEST_CONFIG['base_url']}/api/tts/voices")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Voices endpoint: {data['total']} voices available")
            
            # Verify all 9 voices are present
            # The API returns voices as a dict, not a list
            if isinstance(data['voices'], dict):
                returned_voices = set(data['voices'].keys())
            else:
                returned_voices = set(voice['name'] for voice in data['voices'])
            
            expected_voices = set(voice['name'] for voice in VOICES)
            
            if returned_voices == expected_voices:
                print("✅ All 9 voices present in API response")
                return {'status': 'success', 'voices': data['voices']}
            else:
                missing = expected_voices - returned_voices
                extra = returned_voices - expected_voices
                print(f"❌ Voice mismatch. Missing: {missing}, Extra: {extra}")
                return {'status': 'error', 'error': 'Voice count mismatch'}
        else:
            print(f"❌ Voices endpoint failed: {response.status_code}")
            return {'status': 'error', 'error': f"HTTP {response.status_code}"}
    
    except Exception as e:
        print(f"❌ Voices endpoint error: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def test_single_voice(voice: Dict[str, str], model: str = 'tts-1', speed: float = 1.0, 
                     response_format: str = 'mp3') -> Dict[str, Any]:
    """Test a single voice with specified parameters"""
    
    # Fixed f-string syntax - using proper formatting
    test_text = TEST_CONFIG['test_text'].format(voice_name=voice['name'])
    
    print(f"Testing voice: {voice['name']} ({voice['description']})")
    
    try:
        payload = {
            'text': test_text,
            'voice': voice['name'],
            'model': model,
            'speed': speed,
            'response_format': response_format
        }
        
        response = requests.post(
            f"{TEST_CONFIG['base_url']}/api/tts/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            audio_size = len(data.get('audio_b64', ''))
            
            result = {
                'voice': voice['name'],
                'status': 'success',
                'model': model,
                'speed': speed,
                'format': response_format,
                'audio_size_bytes': audio_size,
                'duration': data.get('duration', 0),
                'character_count': data.get('character_count', 0),
                'processing_time': data.get('processing_time', 0)
            }
            
            print(f"  ✅ Success: {audio_size} bytes, {data.get('duration', 0):.2f}s")
            return result
            
        else:
            print(f"  ❌ Failed: HTTP {response.status_code}")
            try:
                error_data = response.json()
                return {
                    'voice': voice['name'],
                    'status': 'error',
                    'error': error_data.get('error', 'Unknown error')
                }
            except:
                return {
                    'voice': voice['name'],
                    'status': 'error',
                    'error': f"HTTP {response.status_code}"
                }
    
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")
        return {
            'voice': voice['name'],
            'status': 'error',
            'error': str(e)
        }

def run_comprehensive_test() -> Dict[str, Any]:
    """Run comprehensive test of all 9 voices"""
    
    print("=" * 60)
    print("COMPREHENSIVE TTS VOICE TESTING")
    print("Testing all 9 OpenAI voices supported by VectorDBRAG")
    print("=" * 60)
    
    # Test voices endpoint first
    voices_result = test_voice_endpoint()
    if voices_result['status'] != 'success':
        print("❌ Voices endpoint failed, aborting comprehensive test")
        return voices_result
    
    print("\nStarting individual voice tests...")
    
    results = {
        'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'voices_endpoint': voices_result,
        'voice_tests': [],
        'summary': {}
    }
    
    successful_tests = 0
    failed_tests = 0
    
    # Test each voice
    for voice in VOICES:
        print(f"\n--- Testing {voice['name']} ---")
        
        # Test with default parameters
        test_result = test_single_voice(voice)
        results['voice_tests'].append(test_result)
        
        if test_result['status'] == 'success':
            successful_tests += 1
        else:
            failed_tests += 1
        
        # Small delay between requests
        time.sleep(0.5)
    
    # Test summary
    results['summary'] = {
        'total_voices_tested': len(VOICES),
        'successful_tests': successful_tests,
        'failed_tests': failed_tests,
        'success_rate': f"{(successful_tests / len(VOICES)) * 100:.1f}%"
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total voices tested: {len(VOICES)}")
    print(f"Successful tests: {successful_tests}")
    print(f"Failed tests: {failed_tests}")
    print(f"Success rate: {results['summary']['success_rate']}")
    
    if failed_tests > 0:
        print("\nFailed voices:")
        for test in results['voice_tests']:
            if test['status'] == 'error':
                print(f"  ❌ {test['voice']}: {test['error']}")
    
    if successful_tests == len(VOICES):
        print("\n🎉 ALL 9 VOICES WORKING PERFECTLY! 🎉")
        print("TTS voice count expansion from 6 to 9 voices is COMPLETE!")
    
    return results

def test_voice_variety() -> None:
    """Test a variety of configurations to showcase voice capabilities"""
    
    print("\n" + "=" * 60)
    print("VOICE VARIETY DEMONSTRATION")
    print("=" * 60)
    
    test_scenarios = [
        {
            'voice': 'ash',
            'text': 'Welcome to our quarterly business review meeting.',
            'description': 'Business/Professional context'
        },
        {
            'voice': 'coral',
            'text': 'Hi there! Thanks for choosing our service today.',
            'description': 'Friendly/Customer service context'
        },
        {
            'voice': 'sage',
            'text': 'Let us explore the fundamental principles of quantum mechanics.',
            'description': 'Educational/Academic context'
        },
        {
            'voice': 'onyx',
            'text': 'The deep resonance of this voice provides gravitas to important announcements.',
            'description': 'Authoritative/Announcement context'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{scenario['description']}:")
        print(f"Voice: {scenario['voice']}")
        print(f"Text: \"{scenario['text']}\"")
        
        voice_data = next(v for v in VOICES if v['name'] == scenario['voice'])
        result = test_single_voice(voice_data, model='tts-1', speed=1.0)
        
        if result['status'] == 'success':
            print(f"✅ Generated successfully ({result['audio_size_bytes']} bytes)")
        else:
            print(f"❌ Failed: {result['error']}")

if __name__ == "__main__":
    # Run comprehensive test
    test_results = run_comprehensive_test()
    
    # Run variety demonstration
    test_voice_variety()
    
    # Save results to file
    output_file = "comprehensive_tts_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📁 Test results saved to: {output_file}")
    
    # Final status
    if 'summary' in test_results and test_results['summary']['successful_tests'] == 9:
        print("\n🎯 MISSION ACCOMPLISHED!")
        print("All 9 OpenAI voices are now successfully supported!")
        print("Voice count expansion from 6 to 9 voices is COMPLETE! ✅")
    elif 'summary' in test_results:
        print(f"\n⚠️  Partial success: {test_results['summary']['successful_tests']}/9 voices working")
        print("Check individual voice errors above for troubleshooting.")
    else:
        print("\n❌ Test failed at voices endpoint validation stage")
        print("Please check server status and endpoint availability.")
