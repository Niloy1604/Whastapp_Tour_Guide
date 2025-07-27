#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_fully_generative_bot():
    """Test the fully generative, voice-first bot."""
    
    tests = [
        {
            "user_id": "voice_test_1", 
            "message": "Tell me a fascinating story about the Red Fort",
            "expected_lang": "en",
            "description": "English Voice-First Story Request"
        },
        {
            "user_id": "voice_test_2", 
            "message": "मुझे ताजमहल की रोमांचक कहानी सुनाओ",
            "expected_lang": "hi",
            "description": "Hindi Voice Story Request"
        },
        {
            "user_id": "voice_test_3", 
            "message": "লাল কেল্লার একটি অসাধারণ গল্প বলুন",
            "expected_lang": "bn",
            "description": "Bengali Voice Story Request"
        },
        {
            "user_id": "voice_test_4", 
            "message": "I want to explore Kerala's hidden gems",
            "expected_lang": "en",
            "description": "English Location Exploration"
        },
        {
            "user_id": "voice_test_5", 
            "message": "நான் தமிழ்நாட்டின் கோயில்களைப் பற்றி கேட்க விரும்புகிறேன்",
            "expected_lang": "ta",
            "description": "Tamil Temple Interest"
        },
        {
            "user_id": "voice_test_6", 
            "message": "What's the most romantic place in Udaipur?",
            "expected_lang": "en",
            "description": "English Romantic Query"
        },
        {
            "user_id": "voice_test_7", 
            "message": "मुझे राजस्थान के सबसे खूबसूरत महल दिखाओ",
            "expected_lang": "hi",
            "description": "Hindi Palace Request"
        },
        {
            "user_id": "voice_test_8", 
            "message": "কেরালার ব্যাকওয়াটারে কী কী করা যায়?",
            "expected_lang": "bn",
            "description": "Bengali Kerala Activities"
        },
        {
            "user_id": "voice_test_9", 
            "message": "Tell me about Goa's nightlife scene",
            "expected_lang": "en",
            "description": "English Nightlife Query"
        },
        {
            "user_id": "voice_test_10", 
            "message": "హైదరాబాద్ లో ఏమి ప్రత్యేకం?",
            "expected_lang": "te",
            "description": "Telugu Hyderabad Special"
        }
    ]
    
    print("🎤 TESTING FULLY GENERATIVE VOICE-FIRST BOT")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(tests, 1):
        print(f"\n{i}) {test['description']}")
        print(f"   📝 Input: {test['message']}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{BASE_URL}/test",
                json=test,
                headers={"Content-Type": "application/json"},
                timeout=45  # Longer timeout for LLM calls
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                detected_lang = data['user_context']['detected_language']
                bot_response = data['response']
                voice_response = data.get('voice_response', False)
                
                print(f"   🔍 Detected: {detected_lang}")
                print(f"   🎤 Voice Mode: {voice_response}")
                print(f"   🤖 Response: {bot_response[:150]}...")
                print(f"   ⏱️ Response Time: {response_time:.2f}s")
                
                # Validation checks
                success = True
                
                # Check language detection
                if detected_lang != test['expected_lang']:
                    print(f"   ❌ Language Detection: Expected {test['expected_lang']}, got {detected_lang}")
                    success = False
                
                # Check response is not empty
                if not bot_response or len(bot_response.strip()) < 10:
                    print(f"   ❌ Response too short or empty")
                    success = False
                
                # Check for multilingual response (basic check)
                if test['expected_lang'] != 'en':
                    has_native_script = any(ord(char) > 127 for char in bot_response)
                    if not has_native_script:
                        print(f"   ❌ Response should be in {test['expected_lang']} but appears to be English")
                        success = False
                
                # Check response time (should be reasonable)
                if response_time > 30:
                    print(f"   ⚠️ Slow response time: {response_time:.2f}s")
                
                if success:
                    print(f"   ✅ ALL CHECKS PASSED")
                    passed += 1
                else:
                    failed += 1
                
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   ❌ Error: {response.text}")
                failed += 1
        
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            failed += 1
        
        # Small delay between requests
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS:")
    print(f"✅ PASSED: {passed}")
    print(f"❌ FAILED: {failed}")
    print(f"🎯 SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")
    
    if passed == len(tests):
        print("🎉 PERFECT! Your bot is fully generative and voice-first ready! 🌍✨")
    elif passed >= len(tests) * 0.8:
        print("🔥 EXCELLENT! Most tests passed. Minor tweaks needed.")
    else:
        print("⚠️ NEEDS WORK: Check LLM API keys and language enforcement.")

if __name__ == "__main__":
    test_fully_generative_bot()
