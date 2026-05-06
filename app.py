import streamlit as st
from src.gemini_nlp import GeminiNLP
from src.calendar_manager import CalendarManager
from src.reminder_engine import ReminderEngine
import pandas as pd
from datetime import datetime
import json
import os

st.set_page_config(
    page_title="AI Personal Assistant",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

# INIT
@st.cache_resource
def init_assistant():
    nlp = GeminiNLP()
    calendar = CalendarManager()
    reminders = ReminderEngine()
    reminders.start_scheduler()
    return nlp, calendar, reminders

nlp, calendar, reminders = init_assistant()

# STATE
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'events' not in st.session_state:
    st.session_state.events = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Load templates
with open('data/reminder_templates.json', 'r') as f:
    templates = json.load(f)

# HEADER
st.title("🤖 AI Personal Assistant")
st.markdown("**Reminders • Meetings • Vijayawada CS Student Schedule**")

# API Status
col_status1, col_status2 = st.columns(2)
with col_status1:
    gemini_status = "🟢 Online" if nlp.enabled else "🔴 API Key Missing"
    st.metric("Gemini NLP", gemini_status)
with col_status2:
    st.metric("Timezone", "Asia/Kolkata (IST)")

# SIDEBAR
st.sidebar.header("⚡ Quick Commands")

# Templates
st.sidebar.subheader("📋 Templates")
quick_commands = templates['quick_commands']
selected_template = st.sidebar.selectbox("Pick a template:", [""] + quick_commands)

if selected_template and st.sidebar.button("📢 Add from Template"):
    st.session_state.user_input = selected_template

# Manual reminder
st.sidebar.subheader("➕ Manual Reminder")
manual_title = st.sidebar.text_input("Title", key="manual_title")
manual_time = st.sidebar.selectbox("Time", ["9PM today", "7AM tomorrow", "3PM Friday"])
manual_priority = st.sidebar.select_slider("Priority", ["low", "medium", "high"], value="medium")

if st.sidebar.button("Add Reminder"):
    if manual_title:
        reminder = reminders.add_reminder(
            manual_title,
            manual_time,
            manual_priority,
            category='general'
        )
        st.session_state.events.append({
            'type': 'reminder',
            'title': manual_title,
            'time': manual_time,
            'priority': manual_priority,
            'status': 'pending'
        })
        st.sidebar.success("✅ Reminder added!")

# MAIN INTERFACE
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📅 Schedule", "⚙️ Settings"])

with tab1:
    # CHAT INTERFACE
    col_chat, col_info = st.columns([2, 1])
    
    with col_chat:
        st.subheader("💬 Talk to Assistant")
        
        # Chat history
        for msg in st.session_state.chat_history[-5:]:
            with st.chat_message(msg['role']):
                st.write(msg['content'])
        
        # Input
        user_input = st.chat_input("Say something like: 'Remind me LeetCode at 9PM'")
        
        if user_input or st.session_state.get('user_input'):
            text = user_input or st.session_state.user_input
            
            # Add user message
            st.session_state.chat_history.append({
                'role': 'user',
                'content': text,
                'timestamp': datetime.now().isoformat()
            })
            
            with st.spinner("🤖 Processing..."):
                # NLP Parse
                intent = nlp.parse_intent(text)
                
                # Action dispatch
                if intent['intent'] == 'reminder':
                    reminder = reminders.add_reminder(
                        intent['title'],
                        intent['time'],
                        intent['priority'],
                        intent.get('category', 'general')
                    )
                    
                    st.session_state.events.append({
                        'type': 'reminder',
                        'title': intent['title'],
                        'time': intent['time'],
                        'priority': intent['priority'],
                        'category': intent.get('category', 'general'),
                        'status': 'pending'
                    })
                    
                    reply = nlp.smart_reply(intent)
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': reply,
                        'timestamp': datetime.now().isoformat()
                    })
                    st.success(reply)
                
                elif intent['intent'] == 'meeting':
                    try:
                        event = calendar.create_event(intent)
                        
                        st.session_state.events.append({
                            'type': 'meeting',
                            'title': event.get('summary', intent['title']),
                            'time': intent['time'],
                            'status': event.get('status', 'created'),
                            'source': event.get('source', 'local'),
                            'link': event.get('htmlLink', '')
                        })
                        
                        reply = f"📅 Meeting scheduled: {intent['title']}"
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': reply,
                            'timestamp': datetime.now().isoformat()
                        })
                        st.balloons()
                        st.success(reply)
                    except Exception as e:
                        st.error(f"Calendar error: {str(e)}")
                
                else:
                    reply = "📝 Note saved!"
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': reply,
                        'timestamp': datetime.now().isoformat()
                    })
                    st.info(reply)
            
            st.session_state.user_input = None
            st.rerun()
    
    with col_info:
        st.subheader("🎯 Your Focus Areas")
        st.markdown("""
        - 💻 LeetCode Practice
        - 📚 DSA Preparation
        - 🎯 Campus Placements
        - 📦 MongoDB Projects
        - 🏗️ System Design
        """)
        
        # Quick stats
        if st.session_state.events:
            total_events = len(st.session_state.events)
            pending = len([e for e in st.session_state.events if e.get('status') == 'pending'])
            
            st.metric("Total Events", total_events)
            st.metric("Pending", pending)

with tab2:
    st.subheader("📅 Your Schedule")
    
    # Notifications
    if st.session_state.notifications:
        st.subheader("🔔 Recent Notifications")
        for note in st.session_state.notifications[-3:]:
            priority_color = "🔴" if note.get('priority') == 'high' else "🟡" if note.get('priority') == 'medium' else "🟢"
            st.warning(f"{priority_color} {note['title']}")
        
        if st.button("✅ Clear Notifications"):
            st.session_state.notifications = []
            st.rerun()
    
    # Events table
    if st.session_state.events:
        st.subheader("📊 All Events")
        
        df = pd.DataFrame(st.session_state.events)
        
        # Add emoji based on type and category
        def get_emoji(row):
            if row['type'] == 'reminder':
                category_emoji = {
                    'coding': '💻',
                    'placement': '🎯',
                    'project': '📦',
                    'study': '📚',
                    'meeting': '🤝'
                }
                return category_emoji.get(row.get('category', ''), '✅')
            return '📅'
        
        if 'category' in df.columns:
            df['emoji'] = df.apply(get_emoji, axis=1)
        
        # Display
        display_cols = ['emoji', 'type', 'title', 'time', 'status'] if 'emoji' in df.columns else ['type', 'title', 'time', 'status']
        st.dataframe(df[display_cols].tail(10), use_container_width=True)
        
        # Filter by category
        if 'category' in df.columns:
            categories = df['category'].unique().tolist()
            selected_category = st.selectbox("Filter by category:", ["All"] + categories)
            
            if selected_category != "All":
                filtered = df[df['category'] == selected_category]
                st.dataframe(filtered[display_cols], use_container_width=True)
    else:
        st.info("📭 No events yet. Try saying: 'Remind me LeetCode at 9PM'")

with tab3:
    st.subheader("⚙️ Settings & Info")
    
    col_set1, col_set2 = st.columns(2)
    
    with col_set1:
        st.markdown("""
        ### 🌟 Assistant Info
        - **Location**: Vijayawada, India
        - **Timezone**: Asia/Kolkata (IST)
        - **User**: CS Student
        - **Optimized for**: Placements & Coding
        
        ### 📚 Templates Available
        - LeetCode practice reminders
        - DSA revision schedules
        - Project work sessions
        - Placement prep meetings
        - System design study
        """)
    
    with col_set2:
        st.markdown("""
        ### 🔧 Configuration
        
        **Gemini API**: {} 
        **Google Calendar**: Optional
        **Reminders**: Active
        
        ### 🎯 How to Use
        1. Type natural commands like:
           - "Remind me LeetCode at 9PM"
           - "Schedule placement prep tomorrow 7AM"
           - "MongoDB project Friday 3PM"
        
        2. Use templates from sidebar
        
        3. View schedule in Schedule tab
        """.format("✅ Enabled" if nlp.enabled else "❌ Disabled"))
        
        # Calendar setup
        if st.button("🔗 Connect Google Calendar"):
            with st.spinner("Authenticating..."):
                if calendar.authenticate():
                    st.success("✅ Google Calendar connected!")
                else:
                    st.info("""
                    **Optional**: Add Google Calendar integration
                    1. Get credentials from Google Cloud Console
                    2. Save as `credentials.json`
                    3. Click connect button
                    
                    **App works without it!** Uses local storage.
                    """)

# FOOTER
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    if st.button("🔄 Refresh"):
        st.rerun()

with col_footer2:
    st.info(f"💚 {len(st.session_state.events)} events tracked")

with col_footer3:
    st.markdown("[📖 Help Guide](#)")

st.markdown("""
**✅ FREE & READY** | Powered by Google Gemini + Smart NLP  
**🎓 Perfect for CS Students** in Vijayawada  
Made with ❤️ using Streamlit
""")
