"""
OAuth2 Server for EDEN System
Provides OAuth2 authentication for ChatGPT Business connector
"""
import os
import secrets
import time
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect, render_template_string
from functools import wraps

# Create Blueprint for OAuth2 endpoints
oauth2_bp = Blueprint('oauth2', __name__, url_prefix='/oauth')

# In-memory storage for authorization codes and tokens
# In production, use Redis or a database
authorization_codes = {}
access_tokens = {}
refresh_tokens = {}

# OAuth2 Configuration
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "eden-chatgpt-business-client")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", secrets.token_urlsafe(32))
AUTHORIZED_REDIRECT_URIS = [
    "https://chatgpt.com/auth/callback",
    "https://chat.openai.com/auth/callback",
    "http://localhost:3000/auth/callback",  # For testing
]

# Token expiration times
ACCESS_TOKEN_EXPIRY = 3600  # 1 hour
REFRESH_TOKEN_EXPIRY = 2592000  # 30 days


def generate_token():
    """Generate a random token"""
    return secrets.token_urlsafe(32)


def verify_client(client_id, client_secret):
    """Verify client credentials"""
    return client_id == CLIENT_ID and client_secret == CLIENT_SECRET


def require_oauth(f):
    """Decorator to require valid OAuth access token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'missing_token', 'error_description': 'No access token provided'}), 401

        token = auth_header[7:]  # Remove "Bearer " prefix

        # Check if token exists and is valid
        if token not in access_tokens:
            return jsonify({'error': 'invalid_token', 'error_description': 'Access token is invalid'}), 401

        token_data = access_tokens[token]

        # Check if token is expired
        if token_data['expires_at'] < time.time():
            return jsonify({'error': 'token_expired', 'error_description': 'Access token has expired'}), 401

        # Token is valid, add user info to request
        request.oauth_user = token_data['user_email']

        return f(*args, **kwargs)

    return decorated_function


@oauth2_bp.route('/authorize', methods=['GET'])
def authorize():
    """
    OAuth2 Authorization endpoint
    User is redirected here to grant access to ChatGPT
    """
    # Get parameters
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    state = request.args.get('state')
    scope = request.args.get('scope', '')
    response_type = request.args.get('response_type')

    # Validate parameters
    if not client_id or client_id != CLIENT_ID:
        return jsonify({'error': 'invalid_client'}), 400

    if not redirect_uri or redirect_uri not in AUTHORIZED_REDIRECT_URIS:
        return jsonify({'error': 'invalid_redirect_uri'}), 400

    if response_type != 'code':
        return jsonify({'error': 'unsupported_response_type'}), 400

    # In a real implementation, show a consent screen
    # For now, auto-approve (since user already authenticated with Gmail)

    # Generate authorization code
    auth_code = generate_token()

    # Store authorization code
    authorization_codes[auth_code] = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'user_email': 'spxcemxrmxid@gmail.com',  # From Gmail auth
        'expires_at': time.time() + 600,  # 10 minutes
        'used': False
    }

    # Redirect back to ChatGPT with authorization code
    redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"

    return redirect(redirect_url)


@oauth2_bp.route('/token', methods=['POST'])
def token():
    """
    OAuth2 Token endpoint
    Exchange authorization code for access token
    Or refresh access token using refresh token
    """
    grant_type = request.form.get('grant_type')

    if grant_type == 'authorization_code':
        return handle_authorization_code_grant()
    elif grant_type == 'refresh_token':
        return handle_refresh_token_grant()
    else:
        return jsonify({
            'error': 'unsupported_grant_type',
            'error_description': 'Only authorization_code and refresh_token grant types are supported'
        }), 400


def handle_authorization_code_grant():
    """Handle authorization code grant"""
    code = request.form.get('code')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    redirect_uri = request.form.get('redirect_uri')

    # Verify client credentials
    if not verify_client(client_id, client_secret):
        return jsonify({'error': 'invalid_client'}), 401

    # Validate authorization code
    if code not in authorization_codes:
        return jsonify({'error': 'invalid_grant', 'error_description': 'Authorization code is invalid'}), 400

    code_data = authorization_codes[code]

    # Check if code is expired
    if code_data['expires_at'] < time.time():
        return jsonify({'error': 'invalid_grant', 'error_description': 'Authorization code has expired'}), 400

    # Check if code was already used
    if code_data['used']:
        return jsonify({'error': 'invalid_grant', 'error_description': 'Authorization code already used'}), 400

    # Validate redirect URI
    if redirect_uri != code_data['redirect_uri']:
        return jsonify({'error': 'invalid_grant', 'error_description': 'Redirect URI mismatch'}), 400

    # Mark code as used
    code_data['used'] = True

    # Generate tokens
    access_token = generate_token()
    refresh_token = generate_token()

    # Store tokens
    access_tokens[access_token] = {
        'user_email': code_data['user_email'],
        'scope': code_data['scope'],
        'expires_at': time.time() + ACCESS_TOKEN_EXPIRY
    }

    refresh_tokens[refresh_token] = {
        'user_email': code_data['user_email'],
        'scope': code_data['scope'],
        'access_token': access_token,
        'expires_at': time.time() + REFRESH_TOKEN_EXPIRY
    }

    # Return tokens
    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRY,
        'refresh_token': refresh_token,
        'scope': code_data['scope']
    })


def handle_refresh_token_grant():
    """Handle refresh token grant"""
    refresh_token_value = request.form.get('refresh_token')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')

    # Verify client credentials
    if not verify_client(client_id, client_secret):
        return jsonify({'error': 'invalid_client'}), 401

    # Validate refresh token
    if refresh_token_value not in refresh_tokens:
        return jsonify({'error': 'invalid_grant', 'error_description': 'Refresh token is invalid'}), 400

    token_data = refresh_tokens[refresh_token_value]

    # Check if refresh token is expired
    if token_data['expires_at'] < time.time():
        return jsonify({'error': 'invalid_grant', 'error_description': 'Refresh token has expired'}), 400

    # Revoke old access token
    old_access_token = token_data['access_token']
    if old_access_token in access_tokens:
        del access_tokens[old_access_token]

    # Generate new access token
    new_access_token = generate_token()

    # Store new access token
    access_tokens[new_access_token] = {
        'user_email': token_data['user_email'],
        'scope': token_data['scope'],
        'expires_at': time.time() + ACCESS_TOKEN_EXPIRY
    }

    # Update refresh token with new access token
    token_data['access_token'] = new_access_token

    # Return new access token
    return jsonify({
        'access_token': new_access_token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRY,
        'refresh_token': refresh_token_value,
        'scope': token_data['scope']
    })


@oauth2_bp.route('/revoke', methods=['POST'])
def revoke():
    """
    OAuth2 Token revocation endpoint
    Revoke an access or refresh token
    """
    token = request.form.get('token')
    token_type_hint = request.form.get('token_type_hint')

    # Try to revoke as access token
    if token in access_tokens:
        del access_tokens[token]
        return jsonify({'success': True})

    # Try to revoke as refresh token
    if token in refresh_tokens:
        # Also revoke associated access token
        token_data = refresh_tokens[token]
        if 'access_token' in token_data and token_data['access_token'] in access_tokens:
            del access_tokens[token_data['access_token']]
        del refresh_tokens[token]
        return jsonify({'success': True})

    # Token not found, but still return success (per OAuth2 spec)
    return jsonify({'success': True})


@oauth2_bp.route('/userinfo', methods=['GET'])
@require_oauth
def userinfo():
    """
    OAuth2 UserInfo endpoint
    Returns information about the authenticated user
    """
    return jsonify({
        'email': request.oauth_user,
        'email_verified': True,
        'name': 'EDEN User',
        'picture': None
    })


@oauth2_bp.route('/.well-known/oauth-authorization-server', methods=['GET'])
def oauth_metadata():
    """
    OAuth2 Authorization Server Metadata
    Provides discovery information about the OAuth2 server
    """
    base_url = request.url_root.rstrip('/')

    return jsonify({
        'issuer': base_url,
        'authorization_endpoint': f'{base_url}/oauth/authorize',
        'token_endpoint': f'{base_url}/oauth/token',
        'userinfo_endpoint': f'{base_url}/oauth/userinfo',
        'revocation_endpoint': f'{base_url}/oauth/revoke',
        'response_types_supported': ['code'],
        'grant_types_supported': ['authorization_code', 'refresh_token'],
        'token_endpoint_auth_methods_supported': ['client_secret_post'],
        'scopes_supported': ['gmail.read', 'gmail.send', 'system.read', 'system.write'],
        'code_challenge_methods_supported': []
    })


def get_oauth_config():
    """Get OAuth configuration for display"""
    return {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'authorization_endpoint': '/oauth/authorize',
        'token_endpoint': '/oauth/token',
        'userinfo_endpoint': '/oauth/userinfo'
    }
