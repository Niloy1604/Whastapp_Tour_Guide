# 🤖 WhatsApp City Guide AI Bot 🇮🇳

A multilingual AI-powered city guide for Indian travelers that runs entirely through WhatsApp.  
No app installations, no websites—just text (or voice!) and explore local stories directly in your chat.

---

## 🎥 Demo

> 📱 Try the bot (via WhatsApp sandbox): 
`Send "join your-code" to +1 415 523 8886`  

## 🌟 Features

- 🌍 **Multilingual Support**: Understands English, Hindi, Bengali  
- 🎭 **Mood-Aware Recommendations**: Adventurous, Curious, Relaxed, etc.  
- 📱 **WhatsApp-First**: Fully functional over WhatsApp—no app or website needed  
- 🗣️ **Voice Notes Support**: Send voice messages and get AI-powered suggestions  
- 🧠 **GPT-Powered Storytelling**: Engaging, bite-sized cultural narratives  
- 🔢 **Menu-Driven UX**: Easy replies with “1/2/3” to dive deeper  
- 🎒 **Offline-Ready Logic**: Core logic works without user login or app  
- 🗺️ **Hyperlocal Guidance**: Geolocation (by text) + dynamic storytelling  
- 🔄 **Session Memory**: Remembers your city, mood & language over chat  

---

## 🚀 Quick Start (Dev/Test)

### 1. Installation

```
git clone https://github.com//whatsapp-city-guide
cd whatsapp-city-guide
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup Environment

Copy `.env.example` to `.env` and fill in:

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
FLASK_DEBUG=True
PORT=5000
SECRET_KEY=hackathon-secret
```

### 3. Run the bot

```
python app.py
```

Expose with `ngrok`:

```
ngrok http 5000
```

### 4. Register Ngrok Webhook in Twilio

Go to [WhatsApp Sandbox Settings](https://www.twilio.com/console/sms/whatsapp/sandbox) and:
```
Webhook: https://your-ngrok-id.ngrok.io/webhook
```
Then, send the join code via WhatsApp to start testing.

---

## 🛠️ Tech Stack

| Category        | Tools / Services                                      |
|----------------|--------------------------------------------------------|
| Language Model  | OpenAI GPT-3.5                                         |
| Voice-to-Text   | Whisper / Google STT / Sarvam AI (for Hindi/Bengali)  |
| Platform        | Twilio WhatsApp API (free sandbox)                    |
| Framework       | Flask (Python 3.9+)                                    |
| Session Mgmt    | In-memory (v1), Redis (ready for prod)                |
| Hosting         | Local (ngrok), Render or Replit ready                 |
| Data Storage    | JSON-based city/cultural data                         |

---

## 🧪 Usage Examples

### 1. **Text Query**
```
User: I'm in Jaipur and feeling curious
Bot:
1. Hawa Mahal – Palace of Winds hides secret royal stories.
2. Amber Fort – Echoes of royal battles and mirrored halls.
3. Jantar Mantar – India’s ancient star-watching playground.
Reply 1/2/3 for more 📜
```

### 2. **Voice Message**
User sends "Kolkata" or "मैं आगरा में घूमना चाहता हूँ" as voice note.  
Bot responds with local stories depending on transcribed text.

---

## 📁 Project Structure

```
whatsapp-city-guide/
├── app.py
├── config.py
├── requirements.txt
├── .env
├── models/
│   ├── language_detector.py
│   ├── mood_detector.py
│   └── story_generator.py
├── services/
│   ├── whatsapp_service.py
│   ├── speech_service.py
│   └── cache_service.py
├── utils/
│   ├── session_manager.py
│   └── helpers.py
├── data/
│   ├── cities.json
│   └── cultural_content.json
└── README.md
```

---

## How It Works

1. **User sends message (text or voice) on WhatsApp**  
2. **Bot detects language, city, and mood**  
3. **AI generates 3 concise, story-driven local recommendations**  
4. **User replies “1/2/3” for a deeper story, or sends a new city/mood**  
5. **Session is remembered for seamless chat**

---

## Extending & Customizing

- To add more cities or languages, update `data/cities.json` and relevant model files.
- To improve mood/city detection, tweak `models/language_detector.py` and `models/mood_detector.py`.
- To add your own city stories, edit `data/cultural_content.json`.

---

## License

MIT License – Free for educational & hackathon use.

---

## Authors & Support

Built by Code Eclipse.  
Pull requests and suggestions welcome!