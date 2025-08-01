# Telegram Bot Setup Guide

## 🤖 Setting up your Telegram Bot

### Step 1: Create a Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Start a conversation and send `/newbot`
3. Follow the instructions to choose a name and username for your bot
4. Save the **Bot Token** that BotFather provides

### Step 2: Configure Rasa
1. Open `credentials.yml` file
2. Replace `YOUR_BOT_TOKEN` with your actual bot token from BotFather
3. Replace `YOUR_VERIFY_TOKEN` with a secure random string (for webhook verification)
4. Update the webhook URL with your domain

```yaml
telegram:
  access_token: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
  verify: "my_secure_verify_token_123"
  webhook_url: "https://yourdomain.com/webhooks/telegram/webhook"
```

### Step 3: Deploy and Start
1. Make sure your Rasa server is running on a public URL (use ngrok for testing)
2. Start your Rasa server:
   ```bash
   rasa run --enable-api --cors "*"
   ```
3. Start your action server:
   ```bash
   rasa run actions
   ```

### Step 4: Configure Webhook URLs in actions.py
Update the webhook URLs in `actions/actions.py`:

```python
WEBHOOK_CONFIG = {
    'complaint_webhook': 'https://your-actual-webhook.com/complaints',
    'refund_webhook': 'https://your-actual-webhook.com/refunds', 
    'order_webhook': 'https://your-actual-webhook.com/orders',
    'sms_reminder_base_url': 'https://your-sms-api.com/api'
}
```

### Step 5: Test Your Bot
1. Find your bot on Telegram using the username you created
2. Start a conversation with `/start`
3. Test the bilingual features:
   - Try "Hello" for English
   - Try "Merhaba" for Turkish
4. Test all features:
   - Order tracking
   - Refund requests
   - Complaints
   - Period calculator

## 🌟 Features Available in Telegram

### English Commands
- `/start` - Start conversation
- `track order` - Track your orders
- `refund` - Request refunds
- `complaint` - File complaints  
- `period calculator` - Calculate menstrual cycle

### Turkish Commands
- `/start` - Sohbeti başlat
- `sipariş takip` - Siparişlerinizi takip edin
- `iade` - İade talepleri
- `şikayet` - Şikayet bildirin
- `adet hesaplayıcı` - Adet döngüsü hesaplama

## 🔧 Advanced Configuration

### For Production
1. Use HTTPS webhook URLs
2. Set up proper SSL certificates
3. Configure rate limiting
4. Set up monitoring and logging

### For Development  
Use polling instead of webhooks:

```yaml
telegram:
  access_token: "YOUR_BOT_TOKEN"
  verify: "YOUR_VERIFY_TOKEN"
  # Remove webhook_url to use polling
```

## 🚨 Security Notes
- Keep your bot token secret
- Use environment variables for production
- Regularly rotate your verify token
- Monitor bot usage and implement rate limiting

## 📱 Testing Checklist
- [ ] Bot responds in both English and Turkish
- [ ] Order tracking works with real order numbers
- [ ] Refund forms collect proper information
- [ ] Complaint system sends to webhook
- [ ] Period calculator provides accurate dates
- [ ] SMS notifications are sent (if configured)
- [ ] Webhook integrations work properly