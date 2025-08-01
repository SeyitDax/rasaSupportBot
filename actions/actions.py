# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import requests
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, FollowupAction, ActionExecuted
from rasa_sdk.forms import REQUESTED_SLOT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - Your actual webhook URLs (from environment variables)
import os
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_CONFIG = {
    'complaint_webhook': os.getenv('WEBHOOK_URL', 'https://seyitdax.app.n8n.cloud/webhook-test/87d3f403-3cc7-42cd-8906-9f13d0bc4333'),
    'refund_webhook': os.getenv('WEBHOOK_URL', 'https://seyitdax.app.n8n.cloud/webhook-test/87d3f403-3cc7-42cd-8906-9f13d0bc4333'),
    'order_webhook': os.getenv('WEBHOOK_URL', 'https://seyitdax.app.n8n.cloud/webhook-test/87d3f403-3cc7-42cd-8906-9f13d0bc4333'),
    'sms_reminder_base_url': os.getenv('SMS_REMINDER_BASE_URL', 'https://web-production-b03f5.up.railway.app')  # Your SMS Reminder API
}

# Turkish delivery tracking APIs
DELIVERY_APIS = {
    'PTT': 'https://gonderitakip.ptt.gov.tr/api/track',
    'ARAS': 'https://kargotakip.araskargo.com.tr/api/track', 
    'SURAT': 'https://api.suratkargo.com.tr/track'
}


class ActionGreetUser(Action):
    def name(self) -> Text:
        return "action_greet_user"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("name")
        if name:
            dispatcher.utter_message(text=f"Hello, {name}")
        else:
            dispatcher.utter_message(response="utter_ask_name")
        return[SlotSet("greeted", True), SlotSet("greetingTime", time.time())]

class ValidateRefundForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_refund_form"

    def validate_order_number(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        import re
        
        if slot_value:
            order_str = str(slot_value).strip()
            
            # Check if it looks like a phone number (starts with + or is very long)
            if order_str.startswith('+') or len(order_str) > 10:
                dispatcher.utter_message(text="That looks like a phone number. Please provide your order number (5-10 digits, numbers only).")
                return {"order_number": None}
            
            # Validate order number: only digits, 5-10 characters (reasonable range)
            if re.match(r'^\d{5,10}$', order_str):
                dispatcher.utter_message(response="utter_confirm_order_number", order_number=order_str)
                return {"order_number": order_str}
            else:
                dispatcher.utter_message(text="Please provide a valid order number (5-10 digits, numbers only).")
                return {"order_number": None}
        else:
            dispatcher.utter_message(response="utter_ask_order_number")
            return {"order_number": None}

    def validate_email(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        import re
        
        if slot_value:
            email_str = str(slot_value).strip()
            # More robust email validation
            email_pattern = r'\b[\w.%+-]+@(?:[\w-]+\.)+[a-zA-Z]{2,}\b'
            if re.match(email_pattern, email_str):
                dispatcher.utter_message(response="utter_confirm_email", email=email_str)
                return {"email": email_str}
            else:
                dispatcher.utter_message(text="Please provide a valid email address (e.g., user@domain.com).")
                return {"email": None}
        else:
            dispatcher.utter_message(response="utter_ask_email")
            return {"email": None}

    def validate_phone_number(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        import re
        
        if slot_value:
            phone = str(slot_value).strip()
            if re.match(r'^\+[1-9]\d{9,14}$', phone):
                dispatcher.utter_message(response="utter_confirm_phone_number", phone_number=phone)
                return {"phone_number": phone}
            else:
                dispatcher.utter_message(text="Please provide a valid phone number with country code (e.g., +1234567890).")
                return {"phone_number": None}
        else:
            dispatcher.utter_message(response="utter_ask_phone_number")
            return {"phone_number": None}

class ValidateComplaintForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_complaint_form"
    
    def validate_issue_type(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if slot_value:
            dispatcher.utter_message(response="utter_confirm_issue_type", issue_type=slot_value)
            return {"issue_type": slot_value}
        else:
            dispatcher.utter_message(response="utter_ask_issue_type")
            return {"issue_type": None}
    
    def validate_email(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        import re
        
        if slot_value:
            email_str = str(slot_value).strip()
            # More robust email validation
            email_pattern = r'\b[\w.%+-]+@(?:[\w-]+\.)+[a-zA-Z]{2,}\b'
            if re.match(email_pattern, email_str):
                dispatcher.utter_message(response="utter_confirm_email", email=email_str)
                return {"email": email_str}
            else:
                dispatcher.utter_message(text="Please provide a valid email address (e.g., user@domain.com).")
                return {"email": None}
        else:
            dispatcher.utter_message(response="utter_ask_email")
            return {"email": None}
    
    def validate_phone_number(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        import re
        
        if slot_value:
            phone = str(slot_value).strip()
            if re.match(r'^\+[1-9]\d{9,14}$', phone):
                dispatcher.utter_message(response="utter_confirm_phone_number", phone_number=phone)
                return {"phone_number": phone}
            else:
                dispatcher.utter_message(text="Please provide a valid phone number with country code (e.g., +9055145987858).")
                return {"phone_number": None}
        else:
            dispatcher.utter_message(response="utter_ask_phone_number")
            return {"phone_number": None}

class ValidateOrderStatusForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_order_status_form"

    def validate_order_number(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        import re
        
        if slot_value:
            order_str = str(slot_value).strip()
            
            # Check if it looks like a phone number (starts with + or is very long)
            if order_str.startswith('+') or len(order_str) > 10:
                dispatcher.utter_message(text="That looks like a phone number. Please provide your order number (5-10 digits, numbers only).")
                return {"order_number": None}
            
            # Validate order number: only digits, 5-10 characters (reasonable range)
            if re.match(r'^\d{5,10}$', order_str):
                dispatcher.utter_message(response="utter_confirm_order_number", order_number=order_str)
                return {"order_number": order_str}
            else:
                dispatcher.utter_message(text="Please provide a valid order number (5-10 digits, numbers only).")
                return {"order_number": None}
        else:
            dispatcher.utter_message(response="utter_ask_order_number")
            return {"order_number": None}

# Enhanced action classes with webhook integration
class ActionSubmitRefund(Action):
    def name(self) -> Text:
        return "action_submit_refund"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        order_number = tracker.get_slot("order_number")
        email = tracker.get_slot("email")
        
        # Prepare webhook data
        webhook_data = {
            "type": "refund_request",
            "order_number": order_number,
            "email": email,
            "timestamp": datetime.now().isoformat(),
            "user_id": tracker.sender_id
        }
        
        try:
            # Send to webhook
            response = requests.post(
                WEBHOOK_CONFIG['refund_webhook'],
                json=webhook_data,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                dispatcher.utter_message(text="✅ Your refund request has been submitted successfully. You'll receive an email confirmation shortly.")
                logger.info(f"Refund webhook successful for order {order_number}")
                
                # Trigger SMS notification to your existing SMS API
                self._send_sms_notification(email, "refund", order_number)
                
            else:
                dispatcher.utter_message(text="⚠️ There was an issue processing your refund request. Please try again or contact support.")
                logger.error(f"Refund webhook failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="⚠️ Connection error. Please try again later or contact support directly.")
            logger.error(f"Webhook request failed: {e}")
        
        return [SlotSet("order_number", None), SlotSet("email", None)]
    
    def _send_sms_notification(self, email: str, notification_type: str, order_number: str):
        """Send SMS notification using your existing SMS reminder API"""
        try:
            sms_data = {
                "recipient": email,  # Assuming your SMS API can handle email lookup
                "type": notification_type,
                "order_number": order_number,
                "message": f"Refund request for order {order_number} has been submitted."
            }
            
            requests.post(
                f"{WEBHOOK_CONFIG['sms_reminder_base_url']}/send-notification",
                json=sms_data,
                timeout=5
            )
            logger.info(f"SMS notification sent for {notification_type}")
        except Exception as e:
            logger.error(f"SMS notification failed: {e}")

class ActionSubmitComplaint(Action):
    def name(self) -> Text:
        return "action_submit_complaint"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        issue_type = tracker.get_slot("issue_type")
        email = tracker.get_slot("email")
        
        # Prepare webhook data
        webhook_data = {
            "type": "complaint",
            "issue_type": issue_type,
            "email": email,
            "timestamp": datetime.now().isoformat(),
            "user_id": tracker.sender_id,
            "conversation_history": [event.get('text', '') for event in tracker.events if event.get('event') == 'user']
        }
        
        try:
            # Send to webhook
            response = requests.post(
                WEBHOOK_CONFIG['complaint_webhook'],
                json=webhook_data,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                dispatcher.utter_message(text="✅ Your complaint has been submitted. We will review it and contact you within 24 hours.")
                logger.info(f"Complaint webhook successful for {issue_type}")
                
                # Send SMS notification
                self._send_sms_notification(email, "complaint", issue_type)
                
            else:
                dispatcher.utter_message(text="⚠️ There was an issue submitting your complaint. Please try again.")
                logger.error(f"Complaint webhook failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="⚠️ Connection error. Please try again later.")
            logger.error(f"Webhook request failed: {e}")
        
        return [SlotSet("issue_type", None), SlotSet("email", None)]
    
    def _send_sms_notification(self, email: str, notification_type: str, issue_type: str):
        """Send SMS notification using your existing SMS reminder API"""
        try:
            sms_data = {
                "recipient": email,
                "type": notification_type,
                "issue_type": issue_type,
                "message": f"Your complaint about {issue_type} has been submitted and will be reviewed soon."
            }
            
            requests.post(
                f"{WEBHOOK_CONFIG['sms_reminder_base_url']}/send-notification",
                json=sms_data,
                timeout=5
            )
            logger.info(f"SMS notification sent for {notification_type}")
        except Exception as e:
            logger.error(f"SMS notification failed: {e}")

class ActionTrackOrder(Action):
    def name(self) -> Text:
        return "action_track_order"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        order_number = tracker.get_slot("order_number")
        
        if not order_number:
            dispatcher.utter_message(text="Please provide your order number first.")
            return []
        
        # Track order through multiple carriers
        tracking_result = self._track_order_all_carriers(order_number)
        
        if tracking_result:
            status_message = f"📦 Order {order_number} Status:\n"
            status_message += f"Carrier: {tracking_result['carrier']}\n"
            status_message += f"Status: {tracking_result['status']}\n"
            status_message += f"Location: {tracking_result.get('location', 'N/A')}\n"
            
            if tracking_result.get('estimated_delivery'):
                status_message += f"Estimated Delivery: {tracking_result['estimated_delivery']}"
            
            dispatcher.utter_message(text=status_message)
            
            # Log to webhook for analytics
            self._log_tracking_request(order_number, tracking_result)
            
        else:
            dispatcher.utter_message(text="❌ Unable to track your order. Please check the order number or try again later.")
        
        return [SlotSet("order_number", None)]
    
    def _track_order_all_carriers(self, order_number: str) -> Dict[str, Any]:
        """Try tracking with all Turkish carriers"""
        for carrier, api_url in DELIVERY_APIS.items():
            try:
                response = requests.get(
                    f"{api_url}/{order_number}",
                    timeout=10,
                    headers={"User-Agent": "RasaBot/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('found', False):
                        return {
                            'carrier': carrier,
                            'status': data.get('status', 'Unknown'),
                            'location': data.get('location'),
                            'estimated_delivery': data.get('estimated_delivery'),
                            'tracking_details': data.get('tracking_history', [])
                        }
                        
            except requests.exceptions.RequestException as e:
                logger.error(f"Error tracking with {carrier}: {e}")
                continue
                
        return None
    
    def _log_tracking_request(self, order_number: str, result: Dict[str, Any]):
        """Log tracking request to webhook for analytics"""
        try:
            log_data = {
                "type": "order_tracking",
                "order_number": order_number,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
            requests.post(
                WEBHOOK_CONFIG['order_webhook'],
                json=log_data,
                timeout=5
            )
        except Exception as e:
            logger.error(f"Failed to log tracking request: {e}")

# Period cycle calculator action
class ActionPeriodCalculator(Action):
    def name(self) -> Text:
        return "action_period_calculator"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        last_period_date = tracker.get_slot("last_period_date")
        cycle_length = tracker.get_slot("cycle_length") or 28  # Default 28 days
        
        if not last_period_date:
            dispatcher.utter_message(text="When was your last period? Please provide the date (YYYY-MM-DD format).")
            return []
        
        try:
            # Parse the date
            last_date = datetime.strptime(last_period_date, "%Y-%m-%d")
            
            # Calculate next period
            next_period = last_date + timedelta(days=int(cycle_length))
            
            # Calculate ovulation (typically 14 days before next period)
            ovulation_date = next_period - timedelta(days=14)
            
            # Fertile window (5 days before to 1 day after ovulation)
            fertile_start = ovulation_date - timedelta(days=5)
            fertile_end = ovulation_date + timedelta(days=1)
            
            response_text = f"📅 **Period Cycle Information**\n\n"
            response_text += f"Last Period: {last_date.strftime('%B %d, %Y')}\n"
            response_text += f"Next Period: {next_period.strftime('%B %d, %Y')} ({(next_period - datetime.now()).days} days)\n"
            response_text += f"Ovulation: {ovulation_date.strftime('%B %d, %Y')}\n"
            response_text += f"Fertile Window: {fertile_start.strftime('%B %d')} - {fertile_end.strftime('%B %d')}\n\n"
            response_text += "Would you like me to set up SMS reminders for these dates?"
            
            dispatcher.utter_message(text=response_text)
            
            # Set up SMS reminders using your existing SMS API
            self._setup_period_reminders(last_period_date, cycle_length, tracker.sender_id)
            
            return [
                SlotSet("next_period_date", next_period.strftime("%Y-%m-%d")),
                SlotSet("ovulation_date", ovulation_date.strftime("%Y-%m-%d"))
            ]
            
        except ValueError:
            dispatcher.utter_message(text="Please provide a valid date in YYYY-MM-DD format (e.g., 2024-01-15).")
            return []
        except Exception as e:
            dispatcher.utter_message(text="There was an error calculating your cycle. Please try again.")
            logger.error(f"Period calculation error: {e}")
            return []
    
    def _setup_period_reminders(self, last_period_date: str, cycle_length: int, user_id: str):
        """Set up SMS reminders using your existing SMS reminder API"""
        try:
            last_date = datetime.strptime(last_period_date, "%Y-%m-%d")
            next_period = last_date + timedelta(days=int(cycle_length))
            
            # Set up reminders
            reminders = [
                {
                    "type": "period_reminder",
                    "user_id": user_id,
                    "reminder_date": (next_period - timedelta(days=2)).isoformat(),
                    "message": "Your period is expected in 2 days. 🩸",
                    "category": "health"
                },
                {
                    "type": "period_reminder", 
                    "user_id": user_id,
                    "reminder_date": next_period.isoformat(),
                    "message": "Your period is expected today. 📅",
                    "category": "health"
                }
            ]
            
            for reminder in reminders:
                requests.post(
                    f"{WEBHOOK_CONFIG['sms_reminder_base_url']}/schedule-reminder",
                    json=reminder,
                    timeout=5
                )
            
            logger.info(f"Period reminders set up for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to set up period reminders: {e}")


# Enhanced fallback action to prevent circuit breaker
class ActionFallbackWithContext(Action):
    def name(self) -> Text:
        return "action_fallback_with_context"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get conversation context
        recent_intents = [event.get('parse_data', {}).get('intent', {}).get('name') 
                         for event in tracker.events[-5:] 
                         if event.get('event') == 'user']
        
        fallback_messages = [
            "I'm sorry, I didn't understand that. Here's what I can help you with:",
            "• Track your order (/ask_order_status)",
            "• Request a refund (/ask_refund)",
            "• File a complaint (/complaint)", 
            "• Calculate period cycle (/period_calculator)"
        ]
        
        # Provide contextual help based on recent intents
        if 'ask_order_status' in recent_intents:
            fallback_messages.append("\nCould you please provide your order number?")
        
        dispatcher.utter_message(text="\n".join(fallback_messages))
        
        return []

class ValidatePeriodCalculatorForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_period_calculator_form"

    def validate_last_period_date(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        try:
            if slot_value:
                # Try to parse the date
                datetime.strptime(str(slot_value), "%Y-%m-%d")
                dispatcher.utter_message(response="utter_confirm_last_period_date", last_period_date=slot_value)
                return {"last_period_date": slot_value}
            else:
                dispatcher.utter_message(response="utter_ask_last_period_date")
                return {"last_period_date": None}
        except ValueError:
            dispatcher.utter_message(text="Please provide a valid date in YYYY-MM-DD format (e.g., 2024-01-15).")
            return {"last_period_date": None}

    def validate_cycle_length(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        import re
        
        try:
            if slot_value:
                input_str = str(slot_value).strip()
                
                # Extract number from various formats
                # Handle: "26", "26 days", "26 Days since my last cycle", etc.
                number_match = re.search(r'(\d{1,2})', input_str)
                
                if number_match:
                    cycle_days = int(number_match.group(1))
                    if 20 <= cycle_days <= 45:  # Valid cycle range
                        dispatcher.utter_message(response="utter_confirm_cycle_length", cycle_length=cycle_days)
                        return {"cycle_length": str(cycle_days)}
                    else:
                        dispatcher.utter_message(text="Cycle length should be between 20-45 days. Please provide a valid number.")
                        return {"cycle_length": None}
                else:
                    dispatcher.utter_message(text="Please provide a valid number of days (e.g., 28).")
                    return {"cycle_length": None}
            else:
                dispatcher.utter_message(response="utter_ask_cycle_length")
                return {"cycle_length": None}
        except (ValueError, AttributeError):
            dispatcher.utter_message(text="Please provide a valid number of days (e.g., 28).")
            return {"cycle_length": None}

# Contextual memory and follow-up handler
class ActionContextualFollowUp(Action):
    def name(self) -> Text:
        return "action_contextual_followup"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get conversation context
        last_action = None
        recent_actions = []
        
        for event in reversed(tracker.events):
            if event.get('event') == 'action':
                if not last_action:
                    last_action = event.get('name')
                recent_actions.append(event.get('name'))
                if len(recent_actions) >= 3:
                    break
        
        # Provide contextual follow-up based on last action
        if last_action == "action_track_order":
            dispatcher.utter_message(text="Would you like to track another order or is there anything else I can help you with?")
                
        elif last_action == "action_submit_refund":
            dispatcher.utter_message(text="Your refund request has been received. You'll be notified by email within 2-3 business days. Is there anything else I can help you with?")
                
        elif last_action == "action_submit_complaint":
            dispatcher.utter_message(text="Your complaint has been recorded. We'll get back to you within 24 hours. Do you need support with anything else?")
                
        elif last_action == "action_period_calculator":
            dispatcher.utter_message(text="Your period cycle has been calculated and SMS reminders have been set up. Would you like to make another calculation?")
        
        return []

# Enhanced greeting with context awareness
class ActionSmartGreeting(Action):
    def name(self) -> Text:
        return "action_smart_greeting"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Check if user has been here before (based on conversation history)
        is_returning_user = len([e for e in tracker.events if e.get('event') == 'user']) > 1
        
        if is_returning_user:
            dispatcher.utter_message(text="Welcome back! How can I assist you today?")
        else:
            greeting_text = "Hello! I'm your personal assistant. How can I help you today?"
            dispatcher.utter_message(
                text=greeting_text,
                buttons=[
                    {"title": "Track Order", "payload": "/ask_order_status"},
                    {"title": "Request Refund", "payload": "/ask_refund"},
                    {"title": "File Complaint", "payload": "/complaint"},
                    {"title": "Period Calculator", "payload": "/ask_period_calculator"}
                ]
            )
        
        return [SlotSet("greeted", True)]

# Context-aware product recommendation
class ActionSmartProductInfo(Action):
    def name(self) -> Text:
        return "action_smart_product_info"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        product_name = tracker.get_slot("product_name")
        
        # Check user's order history from recent conversations
        previous_orders = []
        for event in tracker.events:
            if event.get('event') == 'slot' and event.get('name') == 'order_number':
                order_num = event.get('value')
                if order_num and order_num not in previous_orders:
                    previous_orders.append(order_num)
        
        if product_name:
            # Simulate product information (in real implementation, this would query a product database)
            product_info = f"Information about {product_name}: This product is highly rated by our customers. "
            if previous_orders:
                product_info += "I see you've shopped with us before, you might be eligible for special discounts!"
            dispatcher.utter_message(text=product_info)
        else:
            dispatcher.utter_message(text="Which product would you like information about?")
        
        return []