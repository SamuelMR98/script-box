#!/usr/bin/env python3

"""
URL Status Checker

Checks URL availability, response time, and status code.

Usage:
    python url_status_checker.py <url>
"""

import sys
import requests

def check_url_status(url):
    try:
        response = requests.get(url, timeout=5)
        status_code = response.status_code
        response_time = response.elapsed.total_seconds()
        return status_code, response_time
    except requests.exceptions.RequestException as e:
        print(f"Error checking URL: {e}")
        return None, None
    
def main():
    if len(sys.argv) != 2:
        print("Usage: python url_status_checker.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    status_code, response_time = check_url_status(url)

    if status_code is not None:
        print(f"URL: {url}")
        print(f"Status Code: {status_code}")
        print(f"Response Time: {response_time:.2f} seconds")
    else:
        print("Failed to retrieve URL status.")

if __name__ == "__main__":
    main()
