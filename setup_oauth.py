#!/usr/bin/env python3
"""
Setup OAuth2 credentials for EDEN ChatGPT Business Connector
Generates Client ID and Client Secret for OAuth2 authentication
"""
import secrets
import os

def generate_oauth_credentials():
    """Generate OAuth2 client credentials"""

    client_id = "eden-chatgpt-business-client"
    client_secret = secrets.token_urlsafe(32)

    return client_id, client_secret

def main():
    print("=" * 70)
    print("  EDEN OAuth2 Setup for ChatGPT Business Connector")
    print("=" * 70)
    print()

    client_id, client_secret = generate_oauth_credentials()

    print("✅ OAuth2 Credentials Generated!")
    print()
    print("Client ID:")
    print(f"  {client_id}")
    print()
    print("Client Secret:")
    print(f"  {client_secret}")
    print()
    print("=" * 70)
    print()

    print("📝 Next Steps:")
    print()

    print("1️⃣  Add to your .env file:")
    print("   " + "-" * 60)
    print(f"   OAUTH_CLIENT_ID={client_id}")
    print(f"   OAUTH_CLIENT_SECRET={client_secret}")
    print("   " + "-" * 60)
    print()

    print("2️⃣  Add to Railway environment variables (when deploying):")
    print("   - OAUTH_CLIENT_ID")
    print("   - OAUTH_CLIENT_SECRET")
    print()

    print("3️⃣  Use in ChatGPT Business Connector:")
    print("   - Authorization URL: https://your-app.up.railway.app/oauth/authorize")
    print("   - Token URL: https://your-app.up.railway.app/oauth/token")
    print(f"   - Client ID: {client_id}")
    print(f"   - Client Secret: {client_secret}")
    print()

    print("=" * 70)
    print()

    # Ask if user wants to update .env file
    update_env = input("Would you like to update your .env file now? (y/n): ").lower()

    if update_env == 'y':
        try:
            # Check if .env exists
            env_path = '.env'

            if not os.path.exists(env_path):
                # Create from .env.example
                if os.path.exists('.env.example'):
                    with open('.env.example', 'r') as f:
                        content = f.read()

                    with open(env_path, 'w') as f:
                        f.write(content)

                    print("✅ Created .env from .env.example")
                else:
                    with open(env_path, 'w') as f:
                        f.write("")
                    print("✅ Created new .env file")

            # Read existing .env
            with open(env_path, 'r') as f:
                lines = f.readlines()

            # Update or add OAuth credentials
            client_id_found = False
            client_secret_found = False
            new_lines = []

            for line in lines:
                if line.startswith('OAUTH_CLIENT_ID='):
                    new_lines.append(f'OAUTH_CLIENT_ID={client_id}\n')
                    client_id_found = True
                elif line.startswith('OAUTH_CLIENT_SECRET='):
                    new_lines.append(f'OAUTH_CLIENT_SECRET={client_secret}\n')
                    client_secret_found = True
                else:
                    new_lines.append(line)

            # Add if not found
            if not client_id_found:
                new_lines.append(f'\nOAUTH_CLIENT_ID={client_id}\n')

            if not client_secret_found:
                new_lines.append(f'OAUTH_CLIENT_SECRET={client_secret}\n')

            # Write back
            with open(env_path, 'w') as f:
                f.writelines(new_lines)

            print("✅ Updated .env file with OAuth2 credentials")
            print()

        except Exception as e:
            print(f"❌ Error updating .env: {e}")
            print("   Please add the credentials manually")
            print()

    print("⚠️  IMPORTANT: Keep these credentials secure!")
    print("   - Never commit them to git")
    print("   - Add them to your deployed server's environment variables")
    print("   - Store the Client Secret safely (you won't be able to retrieve it later)")
    print()

    print("📚 Next: Follow CHATGPT_BUSINESS_CONNECTOR.md for full setup")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
