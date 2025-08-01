# SMS Integration Setup Guide

## 🚀 Your SMS Reminder API Integration

Your Rasa bot is now fully integrated with your SMS reminder API at `https://your-app-name.railway.app`!

### ✅ What's Been Integrated

1. **Refund Notifications**: Immediate SMS when refund requests are submitted
2. **Complaint Acknowledgments**: SMS confirmation for complaint submissions  
3. **Period Cycle Reminders**: Automated SMS reminders for menstrual cycles
4. **Order Tracking**: SMS notifications for delivery updates

### 🔧 Configuration Required

**Step 1: Update API Base URL**
In `actions/actions.py` line 28, replace:
```python
'sms_reminder_base_url': 'https://your-app-name.railway.app'
```
With your actual Railway app URL.

**Step 2: Test SMS API Connection**
```bash
# Test that your SMS API is working
curl -X POST https://your-app-name.railway.app/api/reminders \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "message": "Test message from Rasa bot",
    "created_at": "2025-07-30T15:00:00"
  }'
```

### 📱 How SMS Integration Works

#### Refund Process
```
User: "I want a refund"
Bot: Collects order number, email, phone number
→ Sends data to your webhook
→ Creates SMS reminder: "✅ Refund request for order #12345 submitted..."
```

#### Complaint Process  
```
User: "I have a complaint"
Bot: Collects issue type, email, phone number
→ Sends data to your webhook
→ Creates SMS reminder: "🔔 Your complaint about delivery has been submitted..."
```

#### Period Calculator
```
User: "Calculate my period cycle"
Bot: Collects last period date, cycle length, phone number
→ Creates 4 SMS reminders:
  • Fertile window reminder (5 days before ovulation)
  • 2 days before period reminder
  • Period day reminder
  • Day after period reminder
```

### 🔍 SMS Messages Sent

**Refund SMS:**
> ✅ Refund request for order #12345 has been submitted. You'll receive email confirmation within 2-3 business days.

**Complaint SMS:**
> 🔔 Your complaint about delivery has been submitted. We'll review it and contact you within 24 hours.

**Period Reminders:**
> 🌟 Cycle reminder: Your fertile window starts soon! Track your cycle for better planning.
> 🩸 Period reminder: Your period is expected in 2 days. Take care of yourself!
> 📅 Period reminder: Your period is expected today. You've got this! 💪
> 💚 Period tracker: Consider logging your symptoms today for better cycle insights.

### 📊 Data Flow

```
Rasa Bot ──→ Webhook (your endpoints) ──→ Your Database
    │
    └──→ SMS Reminder API ──→ Scheduled SMS ──→ User's Phone
```

### 🛠 Testing Your Integration

1. **Start your SMS API server** (should be running on Railway)
2. **Train and run Rasa:**
   ```bash
   rasa train
   rasa run actions &
   rasa shell
   ```
3. **Test the flows:**
   ```
   User: Hello
   Bot: [Shows bilingual menu with buttons]
   
   User: I want a refund  
   Bot: [Starts refund form, collects order, email, phone]
   → SMS sent to phone number
   
   User: Adet hesaplayıcı  
   Bot: [Turkish period calculator]
   → Multiple SMS reminders scheduled
   ```

### 🚨 Important Notes

- **Phone Number Format**: Must include country code (e.g., +905551234567)
- **Date Format**: Period dates must be YYYY-MM-DD (e.g., 2024-01-15)
- **SMS Scheduling**: Uses your existing reminder system - no new endpoints needed
- **Error Handling**: Failed SMS attempts are logged but don't break the conversation

### 📝 Logs to Monitor

Check your Rasa action server logs for:
```
INFO - SMS reminder scheduled for refund, reminder_id: 123
INFO - Successfully scheduled 4/4 period reminders for user abc123
WARNING - No phone number provided for SMS notification
ERROR - SMS scheduling failed: 400
```

### 🔗 Integration Benefits

- **Bilingual Support**: SMS content adapts to detected language
- **Smart Scheduling**: Period reminders calculated based on cycle data
- **Error Resilience**: Bot continues working even if SMS fails
- **User Experience**: Immediate confirmation via SMS for all requests
- **Analytics**: All SMS events logged with reminder IDs for tracking

Your bot now provides a complete customer service experience with real-time SMS notifications! 📱✨