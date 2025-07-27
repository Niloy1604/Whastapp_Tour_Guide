# 🤖 CityChai — Fully Generative Voice-First WhatsApp City Guide 🇮🇳

A conversational, multilingual, voice-enabled AI guide for Indian travelers—accessible entirely through WhatsApp.

## 🚩 Problem Statement

Travelers in India often face the challenge of finding reliable, local, and culturally rich information during their trips. Although India is one of the most traveled countries in the world, exploring its vast and diverse regions typically requires hiring a local guide — which can be expensive and sometimes inconvenient.

Moreover, India’s linguistic diversity—with dozens of languages and dialects—poses significant communication barriers for many travelers, especially on platforms like WhatsApp, where most chatbots are limited to English or offer repetitive, canned responses.

As a result, the experience of discovering cities and cultural treasures often feels impersonal, fragmented, and costly due to the need for a physical guide and language limitations.

## 💡 Our Solution: CityChai

**CityChai** is an advanced AI-powered assistant designed to solve these common travel pain points **without any extra cost**:

- Acts as a **virtual local guide available 24/7 on WhatsApp**, eliminating the need to hire costly human guides.
- Supports **13 major Indian languages**, effectively bridging the language barrier.
- Provides **dynamic, personalized, and culturally contextual recommendations** for any city or region in India.
- Handles **both text and voice inputs**, enabling effortless interaction in the user's preferred language.
- Offers **rich storytelling and localized advice** tailored to the traveler’s mood, location, and preferences.
- **Accessible freely via WhatsApp—no app downloads or payments required.**

CityChai empowers every traveler to confidently explore India’s incredible cultural diversity and vast geography on their own terms, with instant, interactive, and dynamic AI-powered guidance.

## 🏗️ Architecture Overview

**How CityChai Processes a WhatsApp Query:**

```
User on WhatsApp
      │
      ▼
WhatsApp (Twilio Sandbox)
      │ (Webhook)
      ▼
Flask Server (app.py)
      │
      ▼
─────────────────────────────────
│ Language Detection             │
│ Mood & Location Extraction     │
│ Conversation Context (Redis)   │
─────────────────────────────────
      │
      ▼
LLM API (Groq / OpenAI)
      │
      ▼
───────────────────────────────
│ If Story Mode:              │
│   └─► TTS (gTTS)            │
│   └─► Generate Audio File   │
│ Else:                       │
│   └─► Text Reply            │
───────────────────────────────
      │
      ▼
WhatsApp (via Twilio API)
      │
      ▼
User receives personalized text or voice/story reply!
```

## 🗂️ Project Structure

```
whatsapp-city-guide/
├── app.py                    # Main Flask server and webhook handling
├── config.py                 # Configuration (API keys, Twilio numbers, etc.)
├── requirements.txt          # Python dependencies
├── .env.example              # Sample environment variables template
├── models/
│   ├── llm_agent.py          # Groq/OpenAI LLM API integration
│   ├── language_detector.py  # Multilingual language detection
│   ├── mood_analyzer.py      # Mood and sentiment analysis
├── services/
│   ├── whatsapp_service.py   # Twilio WhatsApp API wrapper
│   ├── speech_service.py     # Speech-to-text (Whisper)
│   ├── tts_service.py        # Text-to-speech (gTTS)
│   └── cache_service.py      # Redis session and cache handling
├── utils/
│   └── location_extractor.py # Indian city/state/location extraction
├── data/
│   ├── languages.json        # 13-language configs and voice settings
│   ├── cities.json           # Indian cities and related metadata
│   ├── cultural_facts.json   # Cultural stories and facts for locations
│   └── responses/            # Language-specific prompt templates
│       ├── en_responses.json
│       ├── hi_responses.json
│       ├── bn_responses.json
│       └── ... (remaining language files)
└── tests/
    ├── test_voice_first_bot.py      # Multilingual automated tests
    └── test_enhanced_multilingual.py
```

## 🚀 Quick Start Guide — Run Locally

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/Niloy1604/Whastapp_Tour_Guide.git
cd whatsapp-city-guide
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy `.env.example` to `.env` and fill in your API keys and credentials:

```ini
# Twilio WhatsApp Sandbox config
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+14155238886  # Your Twilio sandbox number

# LLM API keys
GROQ_API_KEY=gsk_your_groq_api_key
OPENAI_API_KEY=sk-your_openai_api_key

# Redis config (optional if used)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# Flask settings
SECRET_KEY=your-secret-key
FLASK_DEBUG=True
```

### 3. Start Redis (if used locally)

```bash
redis-server
```

### 4. Run the Flask App

```bash
python app.py
```

You should see logs indicating successful initialization of models and services, and Flask running on `http://127.0.0.1:5000`.

### 5. Expose Your Local Server to the Internet

Use [ngrok](https://ngrok.com/) or similar:

```bash
ngrok http 5000
```

Copy the HTTPS URL provided (e.g., `https://abc123.ngrok.io`).

## 🧪 Testing

Before deploying, verify the bot works correctly with automated testing:

```bash
python tests/test_voice_first_bot.py
```

or for enhanced tests covering over 50 test cases:

```bash
python tests/test_enhanced_multilingual.py
```

These tests validate language detection, dynamic response generation, voice storytelling, and conversation context handling across all 13 languages.

## 🚀 Quick Start Guide — Chatting via Twilio WhatsApp Sandbox

Once tested locally, follow these steps to chat with CityChai on WhatsApp via Twilio:

### 1. Configure Twilio WhatsApp Sandbox Webhook

- Login to [Twilio Console — WhatsApp Sandbox](https://www.twilio.com/console/sms/whatsapp/sandbox)
- Set **"WHEN A MESSAGE COMES IN"** webhook URL to:

```
https://YOUR_NGROK_ID.ngrok.io/webhook
```

(replace `YOUR_NGROK_ID` with your actual ngrok or deployed domain)

### 2. Join the WhatsApp Sandbox

- Save the Twilio sandbox WhatsApp number (typically +1 415 523 8886) in your contacts.
- Send the **join code** (e.g., `join orange-cat`) via WhatsApp message to the sandbox number.
- Upon successful join, Twilio will confirm.

### 3. Start Chatting!

- Send any text or voice message to the sandbox number.
- Examples:
  - Text: “Tell me a story about the Taj Mahal”
  - Voice note: “मुझे लाल किले की कहानी सुनाओ”
  - Others: “I’m tired in Mumbai, suggest a calm place”

- CityChai will reply dynamically with:
  - Text answers for normal queries.
  - Audio-only replies for storytelling or voice requests.

## 🔧 How It Works — Summary

1. User sends a text or voice message on WhatsApp.  
2. Twilio forwards message via webhook to Flask app.  
3. Flask app detects language, mood, and location.  
4. Query sent to LLM (Groq/OpenAI) with dynamic context.  
5. If story requested, LLM response converted to voice with gTTS.  
6. CityChai replies via Twilio with text or audio message to the user.

## 🛠️ Technology Stack

| Component            | Technology                   |
|----------------------|-----------------------------|
| Language Model       | Groq Llama3-8B, OpenAI GPT  |
| Speech-to-Text       | OpenAI Whisper              |
| Text-to-Speech       | Google gTTS                 |
| WhatsApp Integration | Twilio API                  |
| Caching              | Redis                       |
| Web Framework        | Flask (Python async)        |
| Data Storage         | JSON city & cultural data   |

## 📜 License & Contribution

- Licensed under the MIT License.  
- Contributions and issues are welcome via GitHub.  
- Contact: ghoshnil3293639@gmail.com

**CityChai empowers every traveler to explore India’s vibrant culture and hidden stories in their own language — all through WhatsApp with no apps or downloads!** 🇮🇳✨
