#!/usr/bin/env python3
"""
Gmail Integration Test Script
Tests the Gmail API integration for EDEN system
"""
import sys
import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:5000"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_health():
    """Test Gmail integration health"""
    print_section("Testing Gmail Health")
    try:
        response = requests.get(f"{BASE_URL}/api/gmail/health")
        data = response.json()

        print(f"Status: {data.get('status', 'unknown')}")
        print(f"Credentials file exists: {data.get('credentials_file', False)}")
        print(f"Token file exists: {data.get('token_file', False)}")

        if data.get('status') == 'not_authenticated':
            print("\n⚠️  Gmail not authenticated yet!")
            print("Run: curl -X POST http://localhost:5000/api/gmail/auth")
            return False

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_profile():
    """Test getting Gmail profile"""
    print_section("Testing Gmail Profile")
    try:
        response = requests.get(f"{BASE_URL}/api/gmail/profile")
        data = response.json()

        if data.get('ok'):
            profile = data.get('profile', {})
            print(f"Email: {profile.get('email', 'N/A')}")
            print(f"Total Messages: {profile.get('messages_total', 0)}")
            print(f"Total Threads: {profile.get('threads_total', 0)}")
            return True
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_messages():
    """Test getting messages"""
    print_section("Testing Get Messages (Last 5)")
    try:
        response = requests.get(f"{BASE_URL}/api/gmail/messages?max_results=5")
        data = response.json()

        if data.get('ok'):
            messages = data.get('messages', [])
            print(f"Found {len(messages)} messages\n")

            for i, msg in enumerate(messages, 1):
                print(f"{i}. Subject: {msg.get('subject', 'No subject')}")
                print(f"   From: {msg.get('from', 'Unknown')}")
                print(f"   Date: {msg.get('date', 'Unknown')}")
                print(f"   Snippet: {msg.get('snippet', '')[:80]}...")
                print()

            return True
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_unread():
    """Test getting unread messages"""
    print_section("Testing Unread Messages")
    try:
        response = requests.get(f"{BASE_URL}/api/gmail/messages?query=is:unread&max_results=10")
        data = response.json()

        if data.get('ok'):
            messages = data.get('messages', [])
            print(f"Found {len(messages)} unread messages\n")

            for i, msg in enumerate(messages[:3], 1):  # Show first 3
                print(f"{i}. {msg.get('subject', 'No subject')}")
                print(f"   From: {msg.get('from', 'Unknown')}")
                print()

            return True
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_labels():
    """Test getting labels"""
    print_section("Testing Gmail Labels")
    try:
        response = requests.get(f"{BASE_URL}/api/gmail/labels")
        data = response.json()

        if data.get('ok'):
            labels = data.get('labels', [])
            print(f"Found {len(labels)} labels\n")

            for label in labels[:10]:  # Show first 10
                print(f"- {label.get('name')} (ID: {label.get('id')})")

            return True
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_stats():
    """Test getting Gmail stats"""
    print_section("Testing Gmail Statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/gmail/stats")
        data = response.json()

        if data.get('ok'):
            stats = data.get('stats', {})
            print(f"Email: {stats.get('email', 'N/A')}")
            print(f"Total Messages: {stats.get('total_messages', 0)}")
            print(f"Total Threads: {stats.get('total_threads', 0)}")
            print(f"Unread Count: {stats.get('unread_count', 0)}")
            print(f"Starred Count: {stats.get('starred_count', 0)}")
            return True
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_search():
    """Test searching messages"""
    print_section("Testing Message Search")

    search_query = input("Enter search query (or press Enter for 'is:starred'): ").strip()
    if not search_query:
        search_query = "is:starred"

    print(f"\nSearching for: {search_query}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/gmail/messages/search",
            json={"query": search_query, "max_results": 5}
        )
        data = response.json()

        if data.get('ok'):
            messages = data.get('messages', [])
            print(f"\nFound {len(messages)} messages\n")

            for i, msg in enumerate(messages, 1):
                print(f"{i}. {msg.get('subject', 'No subject')}")
                print(f"   From: {msg.get('from', 'Unknown')}")
                print()

            return True
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🌌 "*30)
    print("  EDEN Gmail Integration Test Suite")
    print("🌌 "*30)

    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        if not response.ok:
            print("❌ EDEN server is not responding properly")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to EDEN server at {BASE_URL}")
        print("Please start the server with: python EDEN_SCRIPT.py")
        sys.exit(1)

    print("✅ EDEN server is running\n")

    # Run tests
    results = {}

    results['health'] = test_health()

    if results['health']:
        results['profile'] = test_profile()
        results['messages'] = test_messages()
        results['unread'] = test_unread()
        results['labels'] = test_labels()
        results['stats'] = test_stats()

        # Interactive search test
        do_search = input("\nDo you want to test message search? (y/n): ").lower()
        if do_search == 'y':
            results['search'] = test_search()

    # Print summary
    print_section("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    if passed == total:
        print("\n🎉 All tests passed! Gmail integration is working correctly.")
    elif passed > 0:
        print("\n⚠️  Some tests passed. Check the failures above.")
    else:
        print("\n❌ All tests failed. Please check your setup.")

    print("\nFor more information, see GMAIL_SETUP.md")


if __name__ == "__main__":
    main()
