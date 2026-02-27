# 🚀 JARVIS AI - Quick Start Guide

## 5-Minute Setup: From Zero to Email

### ✅ Prerequisites (Already Done!)
- ✅ Backend running on localhost:9000
- ✅ Database initialized
- ✅ Ollama LLM ready
- ✅ 13-agent mesh operational

---

## 🎯 Mission 1: Draft an Email (2 minutes)

### Step 1: Open Swagger UI
```
http://localhost:9000/docs
```

### Step 2: Find Workflows Section
- Scroll down to `workflows` section
- Look for `POST /api/workflows`

### Step 3: Click "Try it out"
- Click the blue "Try it out" button
- Request body editor will appear

### Step 4: Paste Email Workflow
```json
{
  "name": "Quick Email Draft",
  "description": "Draft a professional email",
  "trigger_type": "manual",
  "tags": ["email", "test"],
  "steps_json": "[{\"agent\": \"email_agent\", \"action\": \"draft_email\", \"params\": {\"to\": \"recipient@example.com\", \"subject\": \"Meeting Request\", \"body\": \"Hi, I'd like to schedule a meeting to discuss the upcoming project. Please let me know your availability.\"}}]"
}
```

### Step 5: Click "Execute"
- API will process
- You'll see response with `workflow_id`
- **Success!** ✅ Workflow created

### Step 6: Execute the Workflow
- Copy the `workflow_id` from response
- Find `POST /api/workflows/{id}/execute`
- Replace `{id}` with your workflow ID
- Click "Try it out" → "Execute"
- **Success!** ✅ Email drafted

---

## 🎯 Mission 2: Use the Web App (3 minutes)

### Step 1: Open React App
```
http://localhost:3000
```

### Step 2: Unlock with Passphrase
- System will ask for passphrase
- Enter: `testpass123`
- Click "Unlock"

### Step 3: View Dashboard
- See all workflows
- See chat sessions
- See execution history

### Step 4: Create New Workflow
- Click "Create Workflow" button
- Select "Email Draft" template
- Fill in recipient email
- Fill in subject
- Fill in body
- Click "Save"

### Step 5: Execute Workflow
- Select workflow from list
- Click "Execute" or "Run"
- Watch real-time status
- View results

---

## 💻 Mission 3: Use Python API (2 minutes)

### Create a File: `quick_email.py`
```python
#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:9000"

# Step 1: Create email workflow
workflow_data = {
    "name": "Quick Email",
    "trigger_type": "manual",
    "steps_json": json.dumps([{
        "agent": "email_agent",
        "action": "draft_email",
        "params": {
            "to": "user@example.com",
            "subject": "Hello",
            "body": "Testing JARVIS AI email workflow!"
        }
    }])
}

# Create
response = requests.post(f"{BASE_URL}/api/workflows", json=workflow_data)
workflow = response.json()
workflow_id = workflow.get("id")
print(f"✅ Created workflow: {workflow_id}")

# Step 2: Execute workflow
exec_response = requests.post(
    f"{BASE_URL}/api/workflows/{workflow_id}/execute"
)
print(f"✅ Executed workflow")
print(f"Response: {exec_response.json()}")
```

### Run It
```bash
python quick_email.py
```

### Output
```
✅ Created workflow: 32d4ff71-d9e3-4eeb-8abd-bb40d0b33848
✅ Executed workflow
Response: {...execution details...}
```

---

## 🔧 Mission 4: Check System Status (1 minute)

### Command 1: Health Check
```bash
curl http://localhost:9000/health
```
**Expected:** `{"status": "healthy", "database_latency_ms": X, "ollama_latency_ms": Y}`

### Command 2: List Workflows
```bash
curl http://localhost:9000/api/workflows
```
**Expected:** List of created workflows

### Command 3: View API Docs
```
http://localhost:9000/docs
```
**Expected:** Interactive Swagger UI with all 60 endpoints

---

## 📧 Common Email Workflow Templates

### Template 1: Simple Email Draft
```json
{
  "name": "Simple Email",
  "trigger_type": "manual",
  "steps_json": "[{\"agent\": \"email_agent\", \"action\": \"draft_email\", \"params\": {\"to\": \"EMAIL_ADDRESS\", \"subject\": \"YOUR_SUBJECT\", \"body\": \"YOUR_MESSAGE\"}}]"
}
```

### Template 2: Email with CC/BCC
```json
{
  "name": "Email with Recipients",
  "trigger_type": "manual",
  "steps_json": "[{\"agent\": \"email_agent\", \"action\": \"draft_email\", \"params\": {\"to\": \"user@example.com\", \"cc\": \"manager@example.com\", \"bcc\": \"archive@example.com\", \"subject\": \"Report\", \"body\": \"Please review the attached report\"}}]"
}
```

### Template 3: Scheduled Email
```json
{
  "name": "Daily Report Email",
  "trigger_type": "scheduled",
  "cron_expression": "0 9 * * 1-5",
  "steps_json": "[{\"agent\": \"email_agent\", \"action\": \"draft_email\", \"params\": {\"to\": \"team@example.com\", \"subject\": \"Daily Standup Report\"}}, {\"agent\": \"email_agent\", \"action\": \"send\"}]"
}
```

### Template 4: Email from Chat
```json
{
  "name": "Chat to Email",
  "trigger_type": "manual",
  "steps_json": "[{\"agent\": \"chat_agent\", \"action\": \"chat_completion\", \"params\": {\"message\": \"Summarize the meeting notes\", \"model\": \"qwen2.5:3b\"}}, {\"agent\": \"email_agent\", \"action\": \"draft_from_chat\", \"depends_on\": [1], \"params\": {\"to\": \"manager@example.com\", \"subject\": \"Meeting Summary\"}}]"
}
```

---

## 🎬 Step-by-Step: Your First Email

### Using Swagger (Easiest)

**Step 1:** Open http://localhost:9000/docs

**Step 2:** Scroll to "workflows" section

**Step 3:** Click `POST /api/workflows`

**Step 4:** Click "Try it out"

**Step 5:** Replace body with:
```json
{
  "name": "My First Email",
  "trigger_type": "manual",
  "steps_json": "[{\"agent\": \"email_agent\", \"action\": \"draft_email\", \"params\": {\"to\": \"yourmail@example.com\", \"subject\": \"Hello World\", \"body\": \"This email was drafted by JARVIS AI!\"}}]"
}
```

**Step 6:** Click "Execute"

**Step 7:** Copy `id` from response

**Step 8:** Find `POST /api/workflows/{id}/execute`

**Step 9:** Replace `{id}` with your copied ID

**Step 10:** Click "Execute"

**Done! ✅** Your email workflow just executed!

---

## 🔐 Authentication Reminder

Your system uses **passphrase authentication**, not passwords:

### First Time Setup
```bash
curl -X POST http://localhost:9000/api/auth/passphrase \
  -H "Content-Type: application/json" \
  -d '{"passphrase": "testpass123"}'
# Response: 201 Created
```

### Unlock System
```bash
curl -X POST http://localhost:9000/api/auth/unlock \
  -H "Content-Type: application/json" \
  -d '{"passphrase": "testpass123"}'
# Response: 200 OK
```

### Check Status
```bash
curl http://localhost:9000/api/auth/status
# Response: {"locked": false, "authenticated": true}
```

---

## 📱 Web App Access

### URL
```
http://localhost:3000
```

### Login
- Passphrase: `testpass123`

### Actions Available
```
✅ Create workflows
✅ Execute workflows  
✅ View history
✅ Chat with AI
✅ Create tasks
✅ Manage settings
✅ View audit logs
```

---

## 🚀 Launch Options

### Browser Mode
```batch
START_JARVIS_BROWSER.bat
```
- Opens default browser
- Full web interface

### Desktop Mode
```batch
RUN_JARVIS_DESKTOP.bat
```
- Chrome/Edge app mode
- Desktop-like appearance
- No browser chrome

### Swagger API Docs
```
http://localhost:9000/docs
```
- Interactive API explorer
- Test all endpoints
- View request/response

---

## 📊 Workflow Status Monitoring

### Check Workflow Details
```bash
curl http://localhost:9000/api/workflows/{id}
```

### Get Execution History
```bash
curl http://localhost:9000/api/workflows/{id}/executions
```

### Get Workflow List
```bash
curl http://localhost:9000/api/workflows
```

### Search Workflows
```bash
curl "http://localhost:9000/api/workflows/search?query=email"
```

---

## 🎯 Common Use Cases

### ✅ Use Case 1: Send Daily Report
```
1. Create workflow with schedule: "0 9 * * *" (9 AM daily)
2. Add email agent to draft report
3. Add execution to send
4. Deploy - runs automatically!
```

### ✅ Use Case 2: Voice-to-Email
```
1. Record voice message
2. Voice agent transcribes to text
3. Email agent drafts from transcription
4. Send or save for later
```

### ✅ Use Case 3: Chat-to-Email
```
1. Chat with AI using natural language
2. AI summarizes conversation
3. Email agent converts to professional email
4. Ready to send!
```

### ✅ Use Case 4: Task Email Notification
```
1. Workflow completes a task
2. Email agent notifies stakeholders
3. Includes results and next steps
4. Automatic follow-up
```

---

## ⚡ Performance Tips

### Optimize Email Workflows
```
1. Use templates (faster than building from scratch)
2. Cache common responses
3. Batch send multiple emails in one workflow
4. Schedule off-peak hours for heavy workflows
```

### Monitor Performance
```
1. Check health endpoint for latency
2. Monitor database response times
3. Watch Ollama inference time
4. Scale if needed (currently local, can be remote)
```

---

## 🆘 Troubleshooting

### Backend not responding?
```bash
# Check if running
curl http://localhost:9000/health

# If not running, start backend:
# See main README or IMPLEMENTATION_PLAN.md
```

### Workflow not executing?
```bash
1. Check workflow ID is correct
2. Verify workflow exists: GET /api/workflows/{id}
3. Check auth status: GET /api/auth/status
4. Try with Swagger UI first (easier debugging)
```

### Email not creating?
```bash
1. Verify email_agent exists in system
2. Check parameters are valid
3. Look at response error message
4. Try simpler workflow first
```

### Need API documentation?
```bash
1. Go to: http://localhost:9000/docs (Swagger)
2. Go to: http://localhost:9000/redoc (ReDoc)
3. Or download: http://localhost:9000/openapi.json
```

---

## 🎉 Success Checklist

```
✅ Backend running on localhost:9000
✅ Swagger UI accessible at localhost:9000/docs
✅ Web app accessible at localhost:3000
✅ Email workflow created & executed
✅ Can draft emails via API
✅ 13-agent mesh confirmed operational
✅ Database persisting workflows
✅ Authentication working
✅ Ready for production!
```

---

## 📖 Learn More

### Full Documentation
- [SYSTEM_OPERATIONAL_STATUS.md](SYSTEM_OPERATIONAL_STATUS.md)
- [BACKEND_STATUS_REPORT.md](BACKEND_STATUS_REPORT.md)
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

### API Reference
- Swagger UI: http://localhost:9000/docs
- OpenAPI Schema: http://localhost:9000/openapi.json

### Quick Scripts
- `test_email_workflow.py` - Full test suite
- `test_backend_real.py` - Backend verification
- `verify_workflows.py` - Check workflows in database

---

## 🚀 You're Ready!

Your JARVIS AI system is fully operational and ready to:
1. Draft emails
2. Execute workflows  
3. Automate tasks
4. Process voice input
5. Coordinate 13-agent mesh
6. Scale to production

**Start with email workflows - they're working perfectly! ✅**

Questions? Check the docs, use Swagger UI, or examine the test scripts for examples!
