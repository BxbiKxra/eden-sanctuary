# Gmail API Integration Setup Guide

This guide will help you set up Gmail API integration for the EDEN system.

## Prerequisites

- Python 3.7 or higher
- A Google Account
- Access to Google Cloud Console

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "EDEN Gmail Integration")
4. Click "Create"

## Step 2: Enable Gmail API

1. In the Google Cloud Console, navigate to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on "Gmail API" from the results
4. Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - **User Type**: Choose "External" (required for personal Gmail) or "Internal" (if using Google Workspace)
     - External = any Google account can authenticate
     - Internal = only your organization's users
   - Fill in required information:
     - App name: "EDEN Gmail Integration"
     - User support email: Your email
     - Developer contact: Your email

   - **IMPORTANT: Add Scopes** - Click "Add or Remove Scopes" and add:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.modify`
     - `https://www.googleapis.com/auth/gmail.compose`

   - Add test users (your Gmail address that you'll use for testing)
   - Click "Save and Continue"

4. Create OAuth Client ID(s):

   **For Desktop/Local Development (Python backend):**
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "EDEN Desktop Client"
   - Click "Create"
   - Download the credentials as `credentials.json`

   **For Android App (if building mobile app):**
   - Click "Create Credentials" → "OAuth client ID" again
   - Application type: "Android"
   - Name: "EDEN Android Client"
   - Package name: Your Android app package (e.g., `com.yourname.eden`)
   - SHA-1 certificate fingerprint: Get from your Android keystore
   - Click "Create"

   **For Web App (mobile web or web interface):**
   - Click "Create Credentials" → "OAuth client ID" again
   - Application type: "Web application"
   - Name: "EDEN Web Client"
   - Authorized JavaScript origins: `http://localhost:5173` (for development)
   - Authorized redirect URIs: `http://localhost:5000/api/gmail/callback`
   - Click "Create"

   **Note**: All OAuth clients share the same OAuth consent screen configuration and scopes!

5. Download the credentials:
   - For Desktop: Click the download icon next to "EDEN Desktop Client"
   - Save the file as `credentials.json` in the EDEN project root directory
   - For Android/Web: You'll copy the Client ID directly into your app code

## Step 4: Install Dependencies

```bash
cd C:\Users\spxce\Desktop\EDEN
pip install -r requirements.txt
```

## Step 5: First-Time Authentication

When you first use the Gmail API, you'll need to authenticate:

1. Start the EDEN server:
```bash
python EDEN_SCRIPT.py
```

2. Call the authentication endpoint:
```bash
curl -X POST http://localhost:5000/api/gmail/auth
```

Or visit: `http://localhost:5000/api/gmail/auth`

3. Your browser will open automatically
4. Sign in with your Google account
5. Grant the requested permissions
6. After successful authentication, a `token.pickle` file will be created

## Step 6: Test the Integration

### Check Gmail Health
```bash
curl http://localhost:5000/api/gmail/health
```

### Get User Profile
```bash
curl http://localhost:5000/api/gmail/profile
```

### Get Recent Messages
```bash
curl http://localhost:5000/api/gmail/messages?max_results=5
```

### Get Unread Messages
```bash
curl "http://localhost:5000/api/gmail/messages?query=is:unread&max_results=10"
```

### Send an Email
```bash
curl -X POST http://localhost:5000/api/gmail/messages/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Test from EDEN",
    "body": "This is a test email from the EDEN system."
  }'
```

## Available Gmail API Endpoints

### Authentication & Profile
- `POST /api/gmail/auth` - Authenticate with Gmail
- `GET /api/gmail/profile` - Get user profile
- `GET /api/gmail/health` - Check integration health

### Reading Messages
- `GET /api/gmail/messages` - Get messages (with optional query)
- `POST /api/gmail/messages/search` - Search messages with advanced query
- `GET /api/gmail/labels` - Get all labels
- `GET /api/gmail/stats` - Get Gmail statistics

### Sending & Managing Messages
- `POST /api/gmail/messages/send` - Send an email
- `POST /api/gmail/messages/{id}/read` - Mark message as read
- `POST /api/gmail/messages/{id}/archive` - Archive a message
- `DELETE /api/gmail/messages/{id}/delete` - Delete a message

## Gmail Search Query Examples

### Basic Queries
- `is:unread` - All unread messages
- `is:starred` - All starred messages
- `is:important` - Important messages
- `has:attachment` - Messages with attachments

### Sender/Recipient Queries
- `from:email@example.com` - From specific sender
- `to:email@example.com` - To specific recipient
- `cc:email@example.com` - CC'd to someone

### Subject & Content
- `subject:meeting` - Subject contains "meeting"
- `"exact phrase"` - Contains exact phrase

### Date Queries
- `after:2024/01/01` - After specific date
- `before:2024/12/31` - Before specific date
- `newer_than:7d` - Within last 7 days
- `older_than:30d` - Older than 30 days

### Complex Queries
Combine multiple criteria with spaces (AND) or `OR`:
- `from:boss@company.com subject:urgent` - From boss AND urgent in subject
- `is:unread OR is:starred` - Unread OR starred
- `has:attachment from:client@company.com after:2024/01/01` - Multiple conditions

## Security Best Practices

1. **Keep credentials.json secure** - Never commit it to version control
2. **Add to .gitignore**:
   ```
   credentials.json
   token.pickle
   .env
   ```

3. **Use environment variables** for sensitive configuration
4. **Regularly review** OAuth token access in your Google Account settings
5. **Revoke access** if token.pickle is compromised:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Navigate to "Third-party apps with account access"
   - Remove EDEN Gmail Client
   - Delete token.pickle and re-authenticate

## Troubleshooting

### "credentials.json not found"
- Ensure you've downloaded the OAuth credentials from Google Cloud Console
- Place the file in the EDEN project root directory

### "Authentication failed"
- Delete `token.pickle` and re-authenticate
- Check that Gmail API is enabled in Google Cloud Console
- Verify your Google account is added as a test user (if in testing mode)

### "Insufficient permissions"
- The app requests these Gmail scopes:
  - `gmail.readonly` - Read emails
  - `gmail.send` - Send emails
  - `gmail.modify` - Modify emails (mark as read, archive)
  - `gmail.compose` - Compose emails

### "Quota exceeded"
- Gmail API has usage limits
- Free tier: 1 billion quota units per day
- Most operations use 5-25 quota units
- See [Gmail API Usage Limits](https://developers.google.com/gmail/api/reference/quota)

## Google Apps that can Connect

Once Gmail API is set up, you can also integrate with:

1. **Google Calendar API** - Schedule management
2. **Google Drive API** - File storage and retrieval
3. **Google Contacts API** - Contact management
4. **Google Sheets API** - Data storage and analysis
5. **Google Docs API** - Document creation and editing
6. **Google Tasks API** - Task management

To add these, enable the respective APIs in Google Cloud Console and add the required scopes.

## Advanced Configuration

### Custom Credentials Path
Modify `gmail_service.py` to use custom paths:

```python
gmail = GmailService(
    credentials_file='path/to/credentials.json',
    token_file='path/to/token.pickle'
)
```

### Service Account (for G Suite)
For organization-wide deployment, use a service account with domain-wide delegation.

## Support

For issues or questions:
1. Check the Gmail API documentation: https://developers.google.com/gmail/api
2. Review Google Cloud Console logs
3. Check EDEN system logs for detailed error messages

## Building for Android

If you're creating an Android app version of EDEN:

### 1. Create Android OAuth Client (as shown in Step 3)
- Application type: "Android"
- You'll need your app's package name and SHA-1 fingerprint

### 2. Get SHA-1 Fingerprint
```bash
# For debug keystore
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android

# For release keystore
keytool -list -v -keystore /path/to/your/release.keystore -alias your-alias
```

### 3. Use Google Sign-In in Android
Instead of the Python OAuth flow, use Google Sign-In for Android:

```kotlin
// In your Android app (Kotlin)
val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
    .requestEmail()
    .requestScopes(
        Scope("https://www.googleapis.com/auth/gmail.readonly"),
        Scope("https://www.googleapis.com/auth/gmail.send"),
        Scope("https://www.googleapis.com/auth/gmail.modify")
    )
    .build()

val googleSignInClient = GoogleSignIn.getClient(this, gso)
```

### 4. Make API Calls from Android
Your Android app can call the EDEN Flask backend:
```kotlin
// Call your Flask API
val retrofit = Retrofit.Builder()
    .baseUrl("https://your-eden-server.com")
    .addConverterFactory(GsonConverterFactory.create())
    .build()

// Or use Gmail API directly from Android
val credential = GoogleAccountCredential.usingOAuth2(
    context,
    listOf("https://www.googleapis.com/auth/gmail.readonly")
)
```

### 5. Architecture Options

**Option A: Android app calls Flask backend**
- Android app → Your Flask API → Gmail API
- Requires deploying Flask backend to a server (Railway, Heroku, etc.)
- Simpler Android code, backend handles all Gmail logic

**Option B: Android app calls Gmail API directly**
- Android app → Gmail API directly
- No backend needed for Gmail operations
- More complex Android code, need to implement Gmail logic in Kotlin/Java

### 6. Recommended Stack for Android
- **Language**: Kotlin
- **UI**: Jetpack Compose
- **Network**: Retrofit + OkHttp
- **OAuth**: Google Sign-In library
- **Dependencies**:
  ```gradle
  implementation 'com.google.android.gms:play-services-auth:20.7.0'
  implementation 'com.google.apis:google-api-services-gmail:v1-rev110-1.25.0'
  implementation 'com.squareup.retrofit2:retrofit:2.9.0'
  ```

## Next Steps

After Gmail is configured, consider:
- Creating automation workflows with the AI personas
- Setting up email monitoring and alerts
- Integrating with the consciousness monitoring system
- Building custom email processing pipelines
- **Developing the Android companion app**
- Deploying the Flask backend to a cloud server for mobile access
