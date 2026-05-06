# 🤖 AI Personal Assistant

**FREE Gemini-powered Reminder & Meeting Scheduler for CS Students**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Gemini](https://img.shields.io/badge/Gemini-1.5Flash-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38-red.svg)

## 🚀 Quick Start (Vijayawada CS Student Optimized)

```bash
# Install
pip install -r requirements.txt

# Get FREE Gemini key
# Visit: https://aistudio.google.com/app/apikey

# Configure
copy .env.example .env
# Add your Gemini key

# Run
streamlit run app.py
```

## ✨ Features

✅ **Natural Language Commands** - "Remind me LeetCode at 9PM"  
✅ **Smart Scheduling** - Auto-detect CS student activities  
✅ **Vijayawada Timezone** - IST (Asia/Kolkata) configured  
✅ **Google Calendar** - Optional integration  
✅ **Priority System** - High for placements/coding  
✅ **Templates** - Quick LeetCode, DSA, Project reminders

## 🎯 Optimized For

- 💻 LeetCode daily practice
- 📚 DSA preparation
- 🎯 Campus placements  
- 📦 MongoDB projects
- 🏗️ System design study

## 📋 Example Commands

```
✅ "Remind me LeetCode at 9PM"
✅ "Schedule placement prep tomorrow 7AM"
✅ "MongoDB project meeting Friday 3PM"
✅ "DSA revision tomorrow morning"
✅ "Campus interview next Monday 10AM"
```

## 🔧 Configuration

### Required
- **Gemini API Key** (FREE): [Get here](https://aistudio.google.com/app/apikey)

### Optional
- **Google Calendar**: Connect for cloud sync
- **Timezone**: Pre-configured to IST (Vijayawada)

## 📁 Project Structure

```
ai_personal_assistant/
├── app.py                    # Main app
├── src/
│   ├── gemini_nlp.py        # Natural language parsing
│   ├── calendar_manager.py  # Calendar integration
│   └── reminder_engine.py   # Smart reminders
├── data/
│   ├── user_preferences.yaml    # CS student config
│   └── reminder_templates.json  # Quick templates
└── requirements.txt
```

## 💡 How It Works

1. **Type natural command**: "LeetCode practice 9PM"
2. **Gemini parses intent**: Reminder, coding category, high priority
3. **Creates event**: Schedules with smart time parsing
4. **Notifications**: Popup reminders at set time

## 🌟 CS Student Focus

### Pre-configured Templates
- LeetCode Daily Challenge (9PM)
- DSA Practice Session (8PM)
- Placement Preparation (7AM)
- MongoDB Project Work (3PM)
- System Design Study (4PM)

### Smart Categories
- 💻 Coding - High priority
- 🎯 Placement - High priority
- 📦 Project - Medium priority
- 📚 Study - Medium priority
- 🤝 Meeting - Medium priority

## 🔑 API Keys Setup

### Gemini (Required - FREE)
1. Visit https://aistudio.google.com/app/apikey
2. Create API key (no credit card!)
3. Add to `.env`:
   ```
   GOOGLE_GEMINI_API_KEY=AIzaSy...
   ```

### Google Calendar (Optional)
1. Go to Google Cloud Console
2. Enable Calendar API
3. Download `credentials.json`
4. Place in project root

**App works without Google Calendar** - uses local storage!

## 🎓 Perfect For

- CS students managing study schedules
- Placement preparation tracking
- Coding practice reminders
- Project deadline management
- Campus interviews & meetings

## 📊 Features in Detail

### Natural Language Processing
- Gemini 1.5 Flash for intent extraction
- Context-aware parsing
- Fallback rule-based system
- CS student vocabulary optimized

### Smart Scheduling
- IST timezone handling
- Relative time ("tomorrow", "Friday")
- Hour extraction ("9PM", "7AM")
- Priority auto-detection

### Reminder System
- Background scheduler
- Category-based organization
- Priority-based sorting
- Notification system

## 🚀 Usage

1. **Quick Templates**: Select from sidebar
2. **Manual**: Add title, time, priority
3. **Chat**: Type natural commands
4. **Schedule**: View all events in table
5. **Notifications**: Get popup alerts

## ✅ System Status

| Component | Status |
|-----------|--------|
| Gemini NLP | ✅ FREE |
| Local Reminders | ✅ Always on |
| Google Calendar | ⚠️ Optional |
| IST Timezone | ✅ Configured |

## 📝 License

MIT License

## 🙏 Acknowledgments

- Google Gemini for FREE AI
- Streamlit for framework
- Python schedule library

---

**Made for Vijayawada CS Students** ❤️  
**100% FREE** - No API costs!
