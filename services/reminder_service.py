# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com
import logging
import schedule
import time
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

class ReminderService:
    """Service for managing patient reminders and notifications."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reminders = {}  # Dict of active reminders by ID
        self.callbacks = {
            'on_reminder': []  # Callbacks to execute when reminder is triggered
        }
        self.logger.info("Reminder service initialized")
        
    def check_reminders(self):
        """
        Check all reminders and trigger notifications for any that are due.
        This method is called by the scheduler.
        """
        try:
            from app import db
            import models
            
            self.logger.info("Checking reminders...")
            current_time = datetime.now().strftime("%H:%M")
            # Get all reminders that are due now
            reminders = models.Reminder.query.filter_by(completed=False).all()
            
            reminded_count = 0
            for reminder in reminders:
                reminder_time = reminder.time
                # Check if reminder time matches current time (HH:MM)
                if reminder_time == current_time:
                    reminded_count += 1
                    self.logger.info(f"Triggering reminder: {reminder.title} for patient {reminder.patient_id}")
                    
                    # Trigger callbacks for this reminder
                    for callback in self.callbacks['on_reminder']:
                        callback(reminder)
                    
                    # If not recurring, mark as completed
                    if not reminder.recurring:
                        reminder.completed = True
                        db.session.commit()
            
            if reminded_count > 0:
                self.logger.info(f"Triggered {reminded_count} reminders")
            else:
                self.logger.debug("No reminders due at this time")
                
        except Exception as e:
            self.logger.error(f"Error checking reminders: {str(e)}")
    
    def add_reminder(self, reminder):
        """
        Add a new reminder to the service.
        
        Args:
            reminder: Reminder object with id, patient_id, title, description, time, recurring
            
        Returns:
            bool: Success of adding the reminder
        """
        try:
            reminder_id = reminder.id
            self.reminders[reminder_id] = reminder
            self.schedule_reminder(reminder)
            self.logger.info(f"Added reminder {reminder_id}: {reminder.title}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding reminder: {str(e)}")
            return False
    
    def remove_reminder(self, reminder_id):
        """
        Remove a reminder from the service.
        
        Args:
            reminder_id: ID of the reminder to remove
            
        Returns:
            bool: Success of removing the reminder
        """
        if reminder_id in self.reminders:
            # Clear the job from the scheduler
            schedule.clear(f"reminder_{reminder_id}")
            # Remove from our tracking
            del self.reminders[reminder_id]
            self.logger.info(f"Removed reminder {reminder_id}")
            return True
        
        self.logger.warning(f"Reminder {reminder_id} not found for removal")
        return False
    
    def schedule_reminder(self, reminder):
        """
        Schedule a reminder with the scheduler.
        
        Args:
            reminder: Reminder object with id, time, recurring fields
            
        Returns:
            bool: Success of scheduling
        """
        try:
            reminder_id = reminder.id
            reminder_time = reminder.time
            
            # Clear any existing job for this reminder
            schedule.clear(f"reminder_{reminder_id}")
            
            # Parse time format
            if ":" in reminder_time:  # HH:MM format
                hour, minute = reminder_time.split(":")
                
                # Schedule based on recurring flag
                if reminder.recurring:
                    # Schedule daily at this time
                    schedule.every().day.at(reminder_time).do(
                        self._trigger_reminder, 
                        reminder_id=reminder_id
                    ).tag(f"reminder_{reminder_id}")
                    self.logger.info(f"Scheduled recurring reminder {reminder_id} daily at {reminder_time}")
                else:
                    # Schedule once at this time
                    # If time is in the past for today, schedule for tomorrow
                    now = datetime.now()
                    target_time = now.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
                    
                    if target_time < now:
                        target_time += timedelta(days=1)
                    
                    # Calculate seconds until reminder
                    delay_seconds = (target_time - now).total_seconds()
                    
                    # Schedule once after the delay
                    schedule.every(delay_seconds).seconds.do(
                        self._trigger_reminder_once, 
                        reminder_id=reminder_id
                    ).tag(f"reminder_{reminder_id}")
                    
                    self.logger.info(f"Scheduled one-time reminder {reminder_id} at {target_time}")
            else:
                self.logger.error(f"Unsupported time format for reminder {reminder_id}: {reminder_time}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error scheduling reminder: {str(e)}")
            return False
    
    def _trigger_reminder(self, reminder_id):
        """
        Trigger a reminder and execute callbacks.
        
        Args:
            reminder_id: ID of the reminder being triggered
        """
        if reminder_id in self.reminders:
            reminder = self.reminders[reminder_id]
            self.logger.info(f"Triggering reminder {reminder_id}: {reminder.title}")
            
            # Execute all registered callbacks
            for callback in self.callbacks['on_reminder']:
                try:
                    callback(reminder)
                except Exception as e:
                    self.logger.error(f"Error in reminder callback: {str(e)}")
        else:
            self.logger.warning(f"Attempt to trigger unknown reminder {reminder_id}")
    
    def _trigger_reminder_once(self, reminder_id):
        """
        Trigger a one-time reminder, execute callbacks, and clear the job.
        
        Args:
            reminder_id: ID of the reminder being triggered
        """
        self._trigger_reminder(reminder_id)
        
        # Clear this job as it's one-time only
        schedule.clear(f"reminder_{reminder_id}")
        
        return schedule.CancelJob
    
    def register_callback(self, event, callback):
        """
        Register a callback function for reminder events.
        
        Args:
            event: Event type ('on_reminder')
            callback: Function to call with reminder object
            
        Returns:
            bool: Success of registering callback
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)
            self.logger.info(f"Registered callback for {event} events")
            return True
        
        self.logger.error(f"Unknown event type: {event}")
        return False
    
    def get_upcoming_reminders(self, patient_id, hours=24):
        """
        Get upcoming reminders for a patient within the specified time window.
        
        Args:
            patient_id: ID of the patient
            hours: Number of hours to look ahead
            
        Returns:
            list: Upcoming reminders for the patient
        """
        upcoming = []
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        
        for reminder_id, reminder in self.reminders.items():
            if reminder.patient_id != patient_id:
                continue
                
            try:
                # Parse the reminder time
                if ":" in reminder.time:
                    hour, minute = map(int, reminder.time.split(":"))
                    reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # If the time is in the past for today, use tomorrow
                    if reminder_time < now:
                        reminder_time += timedelta(days=1)
                    
                    # Include if within the window
                    if reminder_time <= cutoff:
                        upcoming.append({
                            'id': reminder.id,
                            'title': reminder.title,
                            'description': reminder.description,
                            'time': reminder_time.strftime('%Y-%m-%d %H:%M'),
                            'recurring': reminder.recurring
                        })
            except Exception as e:
                self.logger.error(f"Error parsing reminder time: {str(e)}")
        
        # Sort by time
        upcoming.sort(key=lambda x: x['time'])
        return upcoming
