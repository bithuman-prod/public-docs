# 🔔 Webhook Integration

> **Get real-time notifications when users interact with your avatars**

Connect your applications to receive instant HTTP callbacks when avatar events occur - from user conversations to session analytics.

---

## ✨ What Are Webhooks?

Webhooks let your application **automatically respond** to avatar events:

🎤 **User joins session** → Notify your CRM  
💬 **Chat message sent** → Log to database  
📊 **Session ends** → Update analytics  
🚨 **Agent errors** → Alert your team  

**Perfect for:** Analytics, CRM integration, Slack notifications, database logging, real-time dashboards

---

## 🚀 Quick Setup

### 1️⃣ **Configure Your Endpoint**

Set up a webhook endpoint in the [bitHuman dashboard](https://imaginex.bithuman.ai):

```http
POST https://your-app.com/webhook
Content-Type: application/json
```

### 2️⃣ **Choose Events to Receive**

Select which events trigger your webhook:
- ✅ **room_join** - User connects to avatar
- ✅ **chat_push** - Messages in conversation  
- ✅ **session_end** - User disconnects
- ✅ **agent_error** - Avatar encounters errors

### 3️⃣ **Add Authentication (Recommended)**

Secure your endpoint with custom headers:
```http
Authorization: Bearer your-api-token
X-API-Key: your-secret-key
```

---

## 📨 Webhook Payload Examples

### **Room Join Event**
```json
{
  "event": "room_join",
  "timestamp": "2024-01-15T10:30:00Z",
  "agentId": "agent_abc123",
  "sessionId": "session_xyz789",
  "user": {
    "id": "user_456",
    "ip": "192.168.1.100",
    "userAgent": "Mozilla/5.0..."
  },
  "room": {
    "name": "customer-support",
    "participants": 1
  }
}
```

### **Chat Message Event**
```json
{
  "event": "chat_push", 
  "timestamp": "2024-01-15T10:31:25Z",
  "agentId": "agent_abc123",
  "sessionId": "session_xyz789",
  "message": {
    "id": "msg_def456",
    "role": "user",
    "content": "Hello, I need help with my order",
    "type": "text"
  },
  "user": {
    "id": "user_456"
  }
}
```

---

## 🛠️ Implementation Examples

### **Flask Server (Python)**
```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "your-webhook-secret"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Verify signature (recommended)
    signature = request.headers.get('X-bitHuman-Signature', '')
    if not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    data = request.json
    event_type = data.get('event')
    
    # Handle different events
    if event_type == 'room_join':
        handle_user_joined(data)
    elif event_type == 'chat_push':
        handle_new_message(data)
    elif event_type == 'session_end':
        handle_session_ended(data)
    
    return jsonify({'status': 'success'})

def handle_user_joined(data):
    print(f"User {data['user']['id']} joined agent {data['agentId']}")
    # Add your logic: Update CRM, send notification, etc.

def handle_new_message(data):
    message = data['message']
    print(f"New {message['role']} message: {message['content']}")
    # Add your logic: Log to database, analyze sentiment, etc.

def verify_signature(payload, signature):
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

if __name__ == '__main__':
    app.run(port=3000)
```

### **Express.js Server (Node.js)**
```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

const WEBHOOK_SECRET = 'your-webhook-secret';

app.post('/webhook', (req, res) => {
  // Verify signature
  const signature = req.headers['x-bithuman-signature'];
  if (!verifySignature(req.body, signature)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  const { event, agentId, user, message } = req.body;

  switch (event) {
    case 'room_join':
      console.log(`User ${user.id} joined agent ${agentId}`);
      // Your logic here
      break;
      
    case 'chat_push':
      console.log(`New message: ${message.content}`);
      // Your logic here
      break;
      
    case 'session_end':
      console.log(`Session ${req.body.sessionId} ended`);
      // Your logic here
      break;
  }

  res.json({ status: 'success' });
});

function verifySignature(payload, signature) {
  const expected = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(JSON.stringify(payload))
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(`sha256=${expected}`),
    Buffer.from(signature)
  );
}

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

---

## 🎯 Common Use Cases

### **📊 Analytics Dashboard**
```python
# Track user engagement metrics
def handle_chat_push(data):
    db.analytics.create({
        'agent_id': data['agentId'],
        'user_id': data['user']['id'],
        'message_type': data['message']['type'],
        'timestamp': data['timestamp'],
        'content_length': len(data['message']['content'])
    })
```

### **💬 Slack Notifications**
```python
import requests

def handle_room_join(data):
    slack_webhook = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    
    message = {
        "text": f"🤖 New user joined avatar!",
        "attachments": [{
            "color": "good",
            "fields": [
                {"title": "Agent", "value": data['agentId'], "short": True},
                {"title": "User", "value": data['user']['id'], "short": True}
            ]
        }]
    }
    
    requests.post(slack_webhook, json=message)
```

### **🗃️ Database Logging**
```python
# PostgreSQL with SQLAlchemy
def handle_session_end(data):
    session = Session.create({
        'agent_id': data['agentId'],
        'user_id': data['user']['id'],
        'started_at': data['startedAt'],
        'ended_at': data['timestamp'],
        'duration': calculate_duration(data),
        'message_count': data.get('messageCount', 0)
    })
    db.session.add(session)
    db.session.commit()
```

---

## 🔒 Security Best Practices

### **Signature Verification**
Always verify webhook signatures to ensure requests come from bitHuman:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(
        f"sha256={expected}",
        signature
    )
```

### **IP Whitelisting**
Restrict webhook access to bitHuman servers:
```python
ALLOWED_IPS = ['52.14.127.', '18.216.155.']  # Example IPs

def is_allowed_ip(request_ip):
    return any(request_ip.startswith(ip) for ip in ALLOWED_IPS)
```

### **HTTPS Only**
- ✅ Always use HTTPS endpoints
- ✅ Valid SSL certificates required
- ❌ HTTP endpoints will be rejected

---

## 🧪 Testing Your Webhook

### **Local Development with ngrok**
```bash
# Expose local server for testing
ngrok http 3000

# Use the HTTPS URL in webhook settings
# Example: https://abc123.ngrok.io/webhook
```

### **Test Webhook Button**
Use the **Test** button in the bitHuman dashboard to send sample events to your endpoint.

### **Manual Testing**
```bash
curl -X POST https://your-app.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-bitHuman-Signature: sha256=..." \
  -d '{
    "event": "room_join",
    "timestamp": "2024-01-15T10:30:00Z",
    "agentId": "test_agent",
    "user": {"id": "test_user"}
  }'
```

---

## 📈 Monitoring & Debugging

### **Response Requirements**
Your webhook endpoint must:
- ✅ Return HTTP 2xx status codes
- ✅ Respond within 30 seconds
- ✅ Handle duplicate events gracefully

### **Automatic Retries**
bitHuman automatically retries failed webhooks:
- **1st retry**: After 1 second
- **2nd retry**: After 5 seconds  
- **3rd retry**: After 30 seconds
- **Max attempts**: 3 total

### **Debug Common Issues**
| Issue | Cause | Solution |
|-------|-------|----------|
| **Signature Invalid** | Wrong secret or algorithm | Check HMAC SHA256 implementation |
| **Timeout Errors** | Slow processing | Return 200 immediately, process async |
| **404 Not Found** | Incorrect URL | Verify endpoint URL in dashboard |
| **SSL Errors** | Invalid certificate | Use valid HTTPS certificate |

---

## 🎉 Ready to Integrate?

1. **🔧 Set up your endpoint** - Create webhook handler in your app
2. **🔑 Configure in dashboard** - Add URL and auth headers at [imaginex.bithuman.ai](https://imaginex.bithuman.ai)
3. **🧪 Test integration** - Use the test button to verify
4. **📊 Monitor events** - Watch real-time notifications flow in

### **Need Help?**
- 📚 **Advanced patterns**: [Real-time Events Guide](event-handling.md)
- 💬 **Community support**: [Discord](https://discord.gg/yM7wRRqu)
- 🛠️ **Technical issues**: Check our troubleshooting guide

---

*Start receiving real-time avatar events in minutes! 🚀*
