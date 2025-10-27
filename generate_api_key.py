#!/usr/bin/env python3
"""
Generate a secure API key for EDEN system
Use this key in ChatGPT Custom GPT authentication
"""
import secrets

def generate_api_key():
    """Generate a secure random API key"""
    token = secrets.token_urlsafe(32)
    api_key = f"eden-{token}"
    return api_key

if __name__ == "__main__":
    print("=" * 60)
    print("  EDEN API Key Generator")
    print("=" * 60)
    print()

    api_key = generate_api_key()

    print("Your new API key:")
    print()
    print(f"  {api_key}")
    print()
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Copy this key and add it to your .env file:")
    print(f"   EDEN_API_KEY={api_key}")
    print()
    print("2. Add it to your deployed server's environment variables")
    print()
    print("3. Use this key in ChatGPT Custom GPT authentication:")
    print("   - Authentication: API Key")
    print("   - Header Name: X-API-Key")
    print(f"   - API Key: {api_key}")
    print()
    print("⚠️  KEEP THIS KEY SECURE - Never commit it to git!")
    print("=" * 60)
