import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict
import streamlit as st

class ReminderEngine:
    """Smart reminder system with priority queuing"""
    
    def __init__(self):
        self.reminders = []
        self.scheduler_thread = None
        self.running = False
    
    def add_reminder(self, title: str, when: str, priority: str = 'medium', category: str = 'general') -> dict:
        """Add new reminder
        
        Args:
            title: Reminder title
            when: Time in format "today 9PM", "tomorrow 7AM", etc.
            priority: low/medium/high
            category: coding/placement/project/study/meeting
        """
        reminder = {
            'id': len(self.reminders),
            'title': title,
            'time': when,
            'priority': priority,
            'category': category,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        self.reminders.append(reminder)
        
        # Schedule if time is parseable
        try:
            # Simple scheduling - would integrate with calendar_manager for complex parsing
            schedule.every().day.at(self._extract_time(when)).do(
                self.trigger_reminder, reminder['id']
            )
        except:
            pass  # Fallback: just store the reminder
        
        return reminder
    
    def _extract_time(self, time_str: str) -> str:
        """Extract HH:MM from time string"""
        time_str = time_str.lower()
        
        # Map common times
        time_map = {
            '9pm': '21:00',
            '9 pm': '21:00',
            '7am': '07:00',
            '7 am': '07:00',
            '8pm': '20:00',
            '3pm': '15:00',
            '5pm': '17:00'
        }
        
        for key, value in time_map.items():
            if key in time_str:
                return value
        
        return "18:00"  # Default 6PM
    
    def trigger_reminder(self, reminder_id: int):
        """Mark reminder as triggered"""
        for reminder in self.reminders:
            if reminder['id'] == reminder_id:
                reminder['status'] = 'triggered'
                # Add to session state notifications if available
                if 'notifications' in st.session_state:
                    st.session_state.notifications.append({
                        'title': reminder['title'],
                        'priority': reminder['priority'],
                        'time': datetime.now().isoformat()
                    })
                break
    
    def get_pending_reminders(self) -> List[Dict]:
        """Get all pending reminders"""
        return [r for r in self.reminders if r['status'] == 'pending']
    
    def get_reminders_by_category(self, category: str) -> List[Dict]:
        """Filter reminders by category"""
        return [r for r in self.reminders if r['category'] == category]
    
    def delete_reminder(self, reminder_id: int) -> bool:
        """Delete a reminder"""
        self.reminders = [r for r in self.reminders if r['id'] != reminder_id]
        return True
    
    def start_scheduler(self):
        """Start background scheduler thread"""
        if self.running:
            return
        
        def run_scheduler():
            self.running = True
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop background scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)
