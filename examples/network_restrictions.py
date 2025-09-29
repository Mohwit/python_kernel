#!/usr/bin/env python3
"""
Network Restrictions Example

Simple demonstration of network security modes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from kernel import PersistentKernel

print("=== Network Restrictions Example ===")

# Test 1: Restricted mode with allowed endpoints
print("\n1. Restricted Mode (Allowed Endpoints Only):")
kernel_restricted = PersistentKernel(
    allowed_endpoints=["https://httpbin.org"],
    network_mode="restricted",
    session_id="restricted_example"
)

result = kernel_restricted.execute("""
import requests

print("Testing allowed endpoint (httpbin.org):")
try:
    response = requests.get('https://httpbin.org/json')
    print(f"✅ Success: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\\nTesting blocked endpoint (google.com):")
try:
    response = requests.get('https://google.com')
    print(f"❌ Should not succeed: {response.status_code}")
except Exception as e:
    print(f"✅ Blocked as expected: {type(e).__name__}")
""")
print(result['output'])

kernel_restricted.cleanup()

# Test 2: Isolated mode (no network access)
print("\n2. Isolated Mode (No Network Access):")
kernel_isolated = PersistentKernel(
    network_mode="isolated",
    session_id="isolated_example"
)

result = kernel_isolated.execute("""
print("Testing network isolation:")
try:
    import requests
    response = requests.get('https://httpbin.org')
    print(f"❌ Network should be blocked")
except Exception as e:
    print(f"✅ Network blocked: {type(e).__name__}")

print("\\nLocal computation still works:")
numbers = [1, 2, 3, 4, 5]
total = sum(x * x for x in numbers)
print(f"Sum of squares: {total}")
""")
print(result['output'])

kernel_isolated.cleanup()

print("\n✅ Network restrictions example completed!")
