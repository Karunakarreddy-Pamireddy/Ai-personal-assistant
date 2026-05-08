import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class GeminiNLP:
    def __init__(self):
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if api_key and api_key != 'AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
        else:
            self.model = None
            self.enabled = False
    
    def parse_intent(self, text: str) -> dict:
        """Convert natural language to structured action
        
        Examples:
        - "Remind me LeetCode at 9PM" → reminder intent
        - "Schedule placement prep tomorrow 7AM" → meeting intent
        - "MongoDB project meeting Friday 3PM" → meeting intent
        """
        if not self.enabled:
            return self._fallback_parse(text)
        
        prompt = f"""
Parse this natural language command for a personal assistant:

User says: "{text}"

Context: CS student in Vijayawada (Asia/Kolkata timezone)
Common activities: LeetCode, DSA practice, placements, MongoDB projects, campus meetings

Return EXACTLY this JSON structure (no markdown, no explanations):
{{
  "intent": "reminder|meeting|note|cancel",
  "title": "short descriptive title",
  "time": "today 9PM|tomorrow 7AM|Friday 3PM|ISO datetime",
  "duration": "30m|1h|2h",
  "priority": "low|medium|high",
  "recurring": false,
  "location": "optional location",
  "category": "study|coding|placement|project|meeting"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Remove markdown if present
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return self._fallback_parse(text)
        except Exception as e:
            st.warning(f"Gemini parse error: {str(e)}")
            return self._fallback_parse(text)
    
    def _fallback_parse(self, text: str) -> dict:
        """Rule-based fallback parsing"""
        text_lower = text.lower()
        
        # Detect intent
        if any(word in text_lower for word in ['remind', 'reminder', 'alert']):
            intent = 'reminder'
        elif any(word in text_lower for word in ['meet', 'schedule', 'appointment']):
            intent = 'meeting'
        else:
            intent = 'note'
        
        # Extract time
        time_str = 'today 6PM'  # default
        if 'tomorrow' in text_lower:
            time_str = 'tomorrow 9AM'
        elif '9pm' in text_lower or '9 pm' in text_lower:
            time_str = 'today 9PM'
        elif '7am' in text_lower or '7 am' in text_lower:
            time_str = 'tomorrow 7AM'
        
        # Priority detection
        priority = 'medium'
        if 'urgent' in text_lower or 'important' in text_lower:
            priority = 'high'
        elif 'placement' in text_lower or 'interview' in text_lower:
            priority = 'high'
        
        # Category detection
        category = 'general'
        if 'leetcode' in text_lower or 'dsa' in text_lower or 'coding' in text_lower:
            category = 'coding'
        elif 'placement' in text_lower or 'interview' in text_lower:
            category = 'placement'
        elif 'project' in text_lower or 'mongodb' in text_lower:
            category = 'project'
        
        return {
            'intent': intent,
            'title': text[:100],  # Use original text as title
            'time': time_str,
            'duration': '1h',
            'priority': priority,
            'recurring': False,
            'location': '',
            'category': category
        }
    
    def smart_reply(self, event: dict) -> str:
        """Generate natural confirmation responses"""
        category_emoji = {
            'coding': '💻',
            'placement': '🎯',
            'project': '📦',
            'study': '📚',
            'meeting': '🤝'
        }
        
        emoji = category_emoji.get(event.get('category', ''), '✅')
        title = event.get('title', 'Event')
        time = event.get('time', 'soon')
        
        return f"{emoji} Got it! '{title}' scheduled for {time}"
