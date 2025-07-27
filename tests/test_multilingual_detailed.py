#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_complete_multilingual():
    """Comprehensive multilingual test with proper Unicode handling."""
    
    tests = [
        {
            "user_id": "comprehensive_en", 
            "message": "Tell me a story about the Red Fort",
            "expected_lang": "en",
            "description": "English - Red Fort Story"
        },
        {
            "user_id": "comprehensive_hi", 
            "message": "राजस्थान के जयपुर किले के बारे में बताओ",
            "expected_lang": "hi",
            "description": "Hindi - Tell about Jaipur Fort"
        },
        {
            "user_id": "comprehensive_bn", 
            "message": "লাল কেল্লা কোথায়?",
            "expected_lang": "bn",
            "description": "Bengali - Where is Red Fort?"
        },
        {
            "user_id": "comprehensive_ta", 
            "message": "சிவப்பு கோட்டை பற்றி சொல்லுங்கள்",
            "expected_lang": "ta",
            "description": "Tamil - Tell about Red Fort"
        },
        {
            "user_id": "comprehensive_te", 
            "message": "ఎర్రకోట గురించి చెప్పండి",
            "expected_lang": "te",
            "description": "Telugu - Tell about Red Fort"
        },
        {
            "user_id": "comprehensive_ml", 
            "message": "ചുവന്ന കോട്ടയെക്കുറിച്ച് പറയൂ",
            "expected_lang": "ml",
            "description": "Malayalam - Tell about Red Fort"
        },
        {
            "user_id": "comprehensive_kn", 
            "message": "ಕೆಂಪು ಕೋಟೆಯ ಬಗ್ಗೆ ಹೇಳಿ",
            "expected_lang": "kn",
            "description": "Kannada - Tell about Red Fort"
        },
        {
            "user_id": "comprehensive_gu", 
            "message": "લાલ કિલ્લા વિશે કહો",
            "expected_lang": "gu",
            "description": "Gujarati - Tell about Red Fort"
        },
        {
            "user_id": "comprehensive_mr", 
            "message": "लाल किल्ल्याबद्दल सांगा",
            "expected_lang": "mr",
            "description": "Marathi - Tell about Red Fort"
        },
    ]
    
    print("🌍 COMPREHENSIVE MULTILINGUAL TEST")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(tests, 1):
        print(f"\n{i}) {test['description']}")
        print(f"   📝 Input: {test['message']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/test",
                json=test,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                detected_lang = data['user_context']['detected_language']
                bot_response = data['response']
                
                print(f"   🔍 Detected: {detected_lang}")
                print(f"   🤖 Response: {bot_response[:120]}...")
                
                # Check language detection
                if detected_lang == test['expected_lang']:
                    print(f"   ✅ Language Detection: CORRECT")
                    
                    # Check if response is in correct language (basic check)
                    if test['expected_lang'] != 'en':
                        # For non-English, check if response contains non-ASCII characters
                        has_native_script = any(ord(char) > 127 for char in bot_response)
                        if has_native_script:
                            print(f"   ✅ Response Language: NATIVE SCRIPT DETECTED")
                            passed += 1
                        else:
                            print(f"   ❌ Response Language: ENGLISH ONLY (should be {test['expected_lang']})")
                            failed += 1
                    else:
                        print(f"   ✅ Response Language: ENGLISH (correct)")
                        passed += 1
                else:
                    print(f"   ❌ Language Detection: WRONG (expected {test['expected_lang']}, got {detected_lang})")
                    failed += 1
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                failed += 1
        
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            failed += 1
        
        # Small delay between requests
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS:")
    print(f"✅ PASSED: {passed}")
    print(f"❌ FAILED: {failed}")
    print(f"🎯 SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED! Multilingual support is working perfectly! 🌍✨")
    else:
        print("⚠️  Some tests failed. Check the LLM system prompt enforcement.")

if __name__ == "__main__":
    test_complete_multilingual()
    
