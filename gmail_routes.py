"""
Gmail API Routes for Flask
Provides REST endpoints for Gmail operations
"""
from flask import Blueprint, jsonify, request
from gmail_service import get_gmail_service
from datetime import datetime
from typing import Dict, Any


# Create Blueprint for Gmail routes
gmail_bp = Blueprint('gmail', __name__, url_prefix='/api/gmail')


@gmail_bp.route('/auth', methods=['GET', 'POST'])
def authenticate():
    """
    Authenticate with Gmail API
    GET/POST /api/gmail/auth
    """
    try:
        gmail = get_gmail_service()
        success = gmail.authenticate()

        if success:
            profile = gmail.get_user_profile()
            return jsonify({
                'ok': True,
                'authenticated': True,
                'profile': profile,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Authentication failed',
                'message': 'Please ensure credentials.json is present and valid'
            }), 401

    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@gmail_bp.route('/profile', methods=['GET'])
def get_profile():
    """
    Get Gmail user profile
    GET /api/gmail/profile
    """
    try:
        gmail = get_gmail_service()
        profile = gmail.get_user_profile()

        if profile:
            return jsonify({
                'ok': True,
                'profile': profile
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Not authenticated'
            }), 401

    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@gmail_bp.route('/messages', methods=['GET'])
def get_messages():
    """
    Get Gmail messages
    GET /api/gmail/messages?query=is:unread&max_results=10
    """
    try:
        query = request.args.get('query', '')
        max_results = int(request.args.get('max_results', 10))

        gmail = get_gmail_service()
        messages = gmail.get_messages(query=query, max_results=max_results)

        return jsonify({
            'ok': True,
            'count': len(messages),
            'messages': messages,
            'query': query,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@gmail_bp.route('/messages/search', methods=['POST'])
def search_messages():
    """
    Search Gmail messages with query
    POST /api/gmail/messages/search
    Body: { "query": "from:example@gmail.com", "max_results": 20 }
    """
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        max_results = int(data.get('max_results', 50))

        gmail = get_gmail_service()
        messages = gmail.search_messages(query=query, max_results=max_results)

        return jsonify({
            'ok': True,
            'count': len(messages),
            'messages': messages,
            'query': query
        })

    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@gmail_bp.route('/messages/send', methods=['POST'])
def send_message():
    """
    Send an email via Gmail
    POST /api/gmail/messages/send
    Body: {
        "to": "recipient@example.com",
        "subject": "Email subject",
        "body": "Email body text"
    }
    """
    try:
        data = request.get_json() or {}

        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        from_email = data.get('from')

        if not to or not subject or not body:
            return jsonify({
                'ok': False,
                'error': 'Missing required fields: to, subject, body'
            }), 400

        gmail = get_gmail_service()
        result = gmail.send_email(
            to=to,
            subject=subject,
            body=body,
            from_email=from_email
        )

        if result.get('success'):
            return jsonify({
                'ok': True,
                'sent': True,
                'message_id': result.get('message_id'),
                'thread_id': result.get('thread_id'),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'ok': False,
                'error': result.get('error')
            }), 500

    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@gmail_bp.route('/messages/<message_id>/read', methods=['POST'])
def mark_read(message_id: str):
    """
    Mark a message as read
    POST /api/gmail/messages/{message_id}/read
    """
    try:
        gmail = get_gmail_service()
        success = gmail.mark_as_read(message_id)

        return jsonify({
            'ok': success,
            'message_id': message_id,
            'marked_read': success
        })

    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@gmail_bp.route('/messages/<message_id>/archive', methods=['POST'])
def archive_message(message_id: str):
    """
    Archive a message
    POST /api/gmail/messages/{message_id}/archive
    """
    try:
        gmail = get_gmail_service()
        success = gmail.archive_message(message_id)

        return jsonify({
            'ok': success,
            'message_id': message_id,
            'archived': success
        })

    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@gmail_bp.route('/messages/<message_id>/delete', methods=['DELETE'])
def delete_message(message_id: str):
    """
    Delete a message permanently
    DELETE /api/gmail/messages/{message_id}/delete
    """
    try:
        gmail = get_gmail_service()
        success = gmail.delete_message(message_id)

        return jsonify({
            'ok': success,
            'message_id': message_id,
            'deleted': success
        })

    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@gmail_bp.route('/labels', methods=['GET'])
def get_labels():
    """
    Get all Gmail labels
    GET /api/gmail/labels
    """
    try:
        gmail = get_gmail_service()
        labels = gmail.get_labels()

        return jsonify({
            'ok': True,
            'count': len(labels),
            'labels': labels
        })

    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@gmail_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get Gmail statistics
    GET /api/gmail/stats
    """
    try:
        gmail = get_gmail_service()

        # Get various message counts
        unread = gmail.get_messages(query='is:unread', max_results=1)
        starred = gmail.get_messages(query='is:starred', max_results=1)

        profile = gmail.get_user_profile()

        return jsonify({
            'ok': True,
            'stats': {
                'email': profile.get('email', ''),
                'total_messages': profile.get('messages_total', 0),
                'total_threads': profile.get('threads_total', 0),
                'unread_count': len(unread),
                'starred_count': len(starred)
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


# Health check endpoint
@gmail_bp.route('/health', methods=['GET'])
def health_check():
    """
    Check if Gmail integration is healthy
    GET /api/gmail/health
    """
    try:
        gmail = get_gmail_service()

        # Check if authenticated
        if gmail.service:
            status = 'authenticated'
        elif os.path.exists(gmail.token_file):
            status = 'token_exists'
        else:
            status = 'not_authenticated'

        return jsonify({
            'ok': True,
            'status': status,
            'credentials_file': os.path.exists(gmail.credentials_file),
            'token_file': os.path.exists(gmail.token_file),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


# Import os for health check
import os
