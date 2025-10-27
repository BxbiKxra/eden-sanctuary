"""
API Key Authentication for EDEN System
Allows secure access from ChatGPT Custom GPT and other external clients
"""
import os
from functools import wraps
from flask import request, jsonify
from datetime import datetime


# Default API key - CHANGE THIS in production!
# Get from environment variable or use default for development
DEFAULT_API_KEY = os.getenv("EDEN_API_KEY", "eden-dev-key-change-in-production")


def require_api_key(f):
    """
    Decorator to require API key authentication for endpoints
    Usage: @require_api_key
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')

        # Also check query parameter for easier testing
        if not api_key:
            api_key = request.args.get('api_key')

        # Strip "Bearer " prefix if present
        if api_key and api_key.startswith('Bearer '):
            api_key = api_key[7:]

        # Validate API key
        if not api_key:
            return jsonify({
                'ok': False,
                'error': 'API key required',
                'message': 'Please provide an API key in X-API-Key header or api_key query parameter'
            }), 401

        if api_key != DEFAULT_API_KEY:
            return jsonify({
                'ok': False,
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 403

        # API key is valid, proceed
        return f(*args, **kwargs)

    return decorated_function


def optional_api_key(f):
    """
    Decorator for optional API key (doesn't block if missing, but logs if present)
    Usage: @optional_api_key
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')

        if api_key and api_key.startswith('Bearer '):
            api_key = api_key[7:]

        # Store whether request is authenticated for use in endpoint
        request.is_authenticated = (api_key == DEFAULT_API_KEY)

        return f(*args, **kwargs)

    return decorated_function


def get_api_key():
    """
    Get the current API key
    Returns the API key that clients should use
    """
    return DEFAULT_API_KEY


def generate_api_key():
    """
    Generate a new random API key
    """
    import secrets
    return f"eden-{secrets.token_urlsafe(32)}"
