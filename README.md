# RasaSupportBot V2 (Improved Version)

An intelligent conversational AI support bot built with Rasa. This improved version fixes all issues from V1 and adds advanced features for real-world customer support scenarios.

## Current Features (V2)

### **Core Capabilities**
- **Smart Greetings**: Context-aware welcome messages with action buttons
- **Refund Processing**: Complete form-based refund requests with validation
- **Complaint Management**: Structured complaint submission with issue categorization
- **Order Tracking**: Real-time tracking through Turkish carriers (PTT, ARAS, SURAT)
- **Period Calculator**: Menstrual cycle tracking with SMS reminder scheduling

### **Technical Features**
- **Form Validation**: Email, phone number, and order number validation
- **Webhook Integration**: n8n workflow automation for data processing
- **SMS Notifications**: Automated SMS reminders via external API
- **Context Memory**: Advanced slot management and conversation state
- **Fallback Handling**: Intelligent responses for unknown inputs
- **Multi-Channel Support**: REST API, SocketIO, and web interface

### **Reliability**
- Comprehensive error handling and logging
- Input sanitization and validation
- Timeout protection for external API calls
- Smart retry mechanisms

## **Getting Started**

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Configure Environment**: Copy `.env.example` to `.env` and update values
3. **Start Action Server**: `rasa run actions --port 5055`
4. **Start Rasa Server**: `rasa run --enable-api --cors "*"`
5. **Open Web Interface**: Visit `index.html` to interact with the bot

## **Available Commands**
- `/greet` - Start conversation
- `/ask_refund` - Request product refund
- `/complaint` - File a complaint
- `/ask_order_status` - Track your order
- `/ask_period_calculator` - Calculate menstrual cycle

---

**This is the fully functional V2 version with production-ready features.** 