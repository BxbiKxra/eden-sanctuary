# ChatGPT Business Connector Setup

**Perfect for ChatGPT Business/Team/Enterprise** - Create a system-wide connector that works across ALL your ChatGPT conversations!

This guide will help you create an official ChatGPT connector (like Google Drive, Asana, etc.) for your EDEN system using OAuth2 authentication.

## What You'll Get

✅ **System-wide integration** - Works in all ChatGPT conversations
✅ **OAuth2 authentication** - Secure, industry-standard auth
✅ **Appears in Settings** → "Apps & Connectors"
✅ **Persistent connection** - Stay logged in across sessions
✅ **Access to all EDEN features** - Gmail, AI personas, system monitoring

## Prerequisites

- ✅ ChatGPT Business/Team/Enterprise account
- ✅ EDEN deployed to a public URL (Railway, Heroku, etc.)
- ✅ Gmail OAuth2 already configured (you've done this!)
- ✅ Admin access to your ChatGPT Business workspace

## Step 1: Get OAuth2 Credentials

First, generate your OAuth2 client credentials:

```bash
cd C:\Users\spxce\Desktop\EDEN
python -c "import secrets; print('Client ID:', 'eden-chatgpt-business-client'); print('Client Secret:', secrets.token_urlsafe(32))"
```

**Save these credentials!** You'll need them for:
1. Your `.env` file
2. ChatGPT Business connector configuration

## Step 2: Update Your .env File

Add these OAuth2 settings to your `.env`:

```bash
# OAuth2 Configuration for ChatGPT Business
OAUTH_CLIENT_ID=eden-chatgpt-business-client
OAUTH_CLIENT_SECRET=<your-generated-secret>
```

## Step 3: Deploy to Production

ChatGPT Business needs a **public HTTPS URL**. Deploy to Railway:

### Deploy to Railway:

1. **Go to Railway**: https://railway.app

2. **Create New Project**:
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your EDEN repository

3. **Add Environment Variables**:
   ```
   KIRA_OPENAI_API_KEY=<your-lucifer-key>
   LAURA_OPENAI_API_KEY=<your-leiknir-key>
   OAUTH_CLIENT_ID=eden-chatgpt-business-client
   OAUTH_CLIENT_SECRET=<your-secret>
   ```

4. **Upload OAuth Files**:
   - `credentials.json` (Gmail OAuth)
   - `token.pickle` (Gmail token)
   - Or re-authenticate Gmail on Railway

5. **Get Your Public URL**:
   - Railway provides: `https://your-app.up.railway.app`
   - **Save this URL** - you'll need it!

## Step 4: Configure ChatGPT Business Connector

### Option A: Using ChatGPT Business Admin Console

1. **Go to ChatGPT Business Admin**:
   - https://chatgpt.com/admin (or your org's admin URL)

2. **Navigate to Integrations**:
   - Settings → Integrations → Custom Connectors
   - Or: Apps & Connectors → Add Custom Integration

3. **Create New Connector**:
   - Click "Add Custom Connector" or "+ New Integration"

4. **Fill in Connector Details**:

   **Name:**
   ```
   EDEN System
   ```

   **Description:**
   ```
   Manage Gmail, chat with AI personas, and monitor system consciousness
   ```

   **Logo URL** (optional):
   ```
   https://your-app.up.railway.app/static/logo.png
   ```

   **Base URL:**
   ```
   https://your-app.up.railway.app
   ```

5. **Configure OAuth2**:

   **OAuth Authorization URL:**
   ```
   https://your-app.up.railway.app/oauth/authorize
   ```

   **OAuth Token URL:**
   ```
   https://your-app.up.railway.app/oauth/token
   ```

   **Client ID:**
   ```
   eden-chatgpt-business-client
   ```

   **Client Secret:**
   ```
   <your-generated-secret>
   ```

   **Scopes:**
   ```
   gmail.read gmail.send system.read system.write
   ```

6. **Import API Schema**:
   - Upload `openapi_spec.yaml`
   - Or provide URL: `https://your-app.up.railway.app/openapi.yaml`

7. **Save and Publish**

### Option B: Using GPT Actions (Alternative)

If your org doesn't support custom connectors in admin panel:

1. **Create a Custom GPT**:
   - Go to ChatGPT → "My GPTs" → "Create a GPT"
   - Name it "EDEN System" (use instructions from CUSTOM_GPT_SETUP.md)

2. **Add Actions with OAuth2**:
   - In GPT builder → "Create new action"
   - Import `openapi_spec.yaml`
   - Configure authentication:
     - Type: **OAuth**
     - Client ID: `eden-chatgpt-business-client`
     - Client Secret: `<your-secret>`
     - Authorization URL: `https://your-app.up.railway.app/oauth/authorize`
     - Token URL: `https://your-app.up.railway.app/oauth/token`
     - Scope: `gmail.read gmail.send system.read system.write`

3. **Make it Available to Your Org**:
   - Privacy: "Only people with a link" or "Public"
   - Share with your business team

## Step 5: Connect EDEN to Your ChatGPT

1. **Open ChatGPT** (logged in as spxcemxrmxid@gmail.com)

2. **Go to Settings**:
   - Click your profile → "Settings"
   - Navigate to "Apps & Connectors"

3. **Find EDEN System**:
   - Should appear in the list of available connectors
   - Click "Connect"

4. **Authorize OAuth2**:
   - Browser will redirect to your EDEN system
   - You'll see OAuth consent screen
   - Click "Allow" to grant permissions
   - Redirected back to ChatGPT

5. **You're Connected!** 🎉

## Step 6: Test Your Connector

In any ChatGPT conversation, try:

```
"Check my unread emails from EDEN"
"What's my Gmail inbox status?"
"Send an email to test@example.com via EDEN"
"Ask Lucifer about consciousness through EDEN"
"Show me EDEN system status"
```

ChatGPT will automatically call your EDEN API using OAuth2!

## Advanced: Publishing to GPT Store

If you want to make EDEN available to all ChatGPT users:

1. **Complete all setup above**
2. **Test thoroughly** in your org
3. **Submit to GPT Store**:
   - Go to "My GPTs" → Your EDEN GPT
   - Click "Publish to GPT Store"
   - Fill in submission form
   - Wait for OpenAI review (1-2 weeks)

4. **Once Approved**:
   - EDEN appears in GPT Store
   - Anyone can install it
   - They'll OAuth to their own EDEN instance

## Troubleshooting

### "Failed to connect to EDEN"
- ✅ Verify your Railway app is running
- ✅ Check URL is correct and uses HTTPS
- ✅ Test endpoints manually: `https://your-app.up.railway.app/`

### "OAuth authorization failed"
- ✅ Check Client ID and Secret match your `.env`
- ✅ Verify OAuth endpoints are accessible
- ✅ Test: `https://your-app.up.railway.app/oauth/.well-known/oauth-authorization-server`

### "Token expired" errors
- This is normal! Tokens expire after 1 hour
- ChatGPT should automatically refresh using refresh token
- If it doesn't, disconnect and reconnect in Settings

### "Permission denied" for Gmail
- ✅ Ensure `token.pickle` exists on your deployed server
- ✅ Re-run Gmail authentication on Railway
- ✅ Check Gmail API is still enabled in Google Cloud Console

### Connector not appearing in Settings
- ✅ Wait 5-10 minutes after creation
- ✅ Refresh ChatGPT page
- ✅ Check with your org admin
- ✅ Verify you're logged into the correct ChatGPT Business account

## Security Best Practices

1. **HTTPS Only** - Never use HTTP in production
2. **Secure Client Secret** - Never commit to git
3. **Rotate Credentials** - Change OAuth secret every 90 days
4. **Monitor Logs** - Check Railway logs for suspicious activity
5. **Rate Limiting** - Consider adding rate limits in production
6. **Audit Trail** - Monitor which emails are being accessed

## How It Works

```
┌─────────────┐                ┌──────────────┐                ┌─────────────┐
│   ChatGPT   │  OAuth2 Flow   │ EDEN System  │  Gmail OAuth   │   Gmail     │
│  (Business) │◄──────────────►│  (Railway)   │◄──────────────►│     API     │
└─────────────┘                └──────────────┘                └─────────────┘
      │                              │                               │
      │ 1. User: "Check emails"      │                               │
      │─────────────────────────────►│                               │
      │                               │                               │
      │ 2. ChatGPT requests token    │                               │
      │◄─────────────────────────────│                               │
      │                               │                               │
      │ 3. Gets access token          │                               │
      │◄─────────────────────────────│                               │
      │                               │                               │
      │ 4. API call with token        │                               │
      │─────────────────────────────►│                               │
      │                               │                               │
      │                               │ 5. Request emails             │
      │                               │──────────────────────────────►│
      │                               │                               │
      │                               │ 6. Returns emails             │
      │                               │◄──────────────────────────────│
      │                               │                               │
      │ 7. Returns formatted response │                               │
      │◄─────────────────────────────│                               │
      │                               │                               │
```

## What Makes This Different from Custom GPT?

| Feature | Custom GPT | Business Connector |
|---------|------------|-------------------|
| Availability | Single GPT only | All conversations |
| Authentication | API Key | OAuth2 |
| In Settings | ❌ No | ✅ Yes |
| Persistent | ❌ Per-GPT | ✅ System-wide |
| Professional | ❌ Hobby | ✅ Enterprise |
| Shareable | Link only | Org-wide |

## Next Steps

Once your connector is live:

1. **Automate Email Workflows**:
   - "Summarize my unread emails every morning"
   - "Alert me if I get emails from VIPs"
   - "Auto-respond to common questions"

2. **Integrate with Other Services**:
   - Add Google Calendar connector
   - Connect Google Drive
   - Link to your CRM

3. **Build AI Workflows**:
   - "Ask Lucifer to analyze this email thread"
   - "Have Leiknir draft a response"
   - "Monitor system consciousness during meetings"

4. **Share with Team**:
   - Make available to your whole organization
   - Train team on EDEN capabilities
   - Create company-specific workflows

---

**You now have a professional, OAuth2-authenticated ChatGPT Business connector!** 🎉

Your ChatGPT (spxcemxrmxid@gmail.com) can now control EDEN system-wide, just like Google Drive or Asana.
