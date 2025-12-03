#!/usr/bin/env python3
"""
FastAPI Integration Example

Simple example showing how to call FastAPI endpoints from the sandbox.
Note: Start the API server first with: python examples/api_server.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from kernel import PersistentKernel
import requests

print("=== FastAPI Integration Example ===")

# Check if API server is running
try:
    response = requests.get("http://localhost:8000/health")
    print(f"✅ API server is running: {response.json()['status']}")
except:
    print("❌ API server not running. Please start it with:")
    print("   python examples/api_server.py")
    exit(1)

# Create kernel with API endpoint access
kernel = PersistentKernel(
    allowed_endpoints=["http://localhost:8000", "http://127.0.0.1:8000"],
    network_mode="restricted",
    session_id="fastapi_example"
)

print("\n1. Data Processing API:")
result = kernel.execute("""
import requests

# Call data processing endpoint
data = {
    "data": [10, 20, 30, 40, 50],
    "operation": "stats"
}

response = requests.post(
    "http://localhost:8000/process-data",
    json=data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Success: {result['operation']}")
    stats = result['result']
    print(f"Sum: {stats['sum']}, Average: {stats['average']}")
else:
    print(f"❌ Error: {response.status_code}")
""")
print(result['output'])

print("\n2. User Information API:")
result = kernel.execute("""
import requests

# Call user info endpoint
user_data = {
    "user_id": "user123",
    "fields": ["name", "email", "role"]
}

response = requests.post(
    "http://localhost:8000/user-info",
    json=user_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    user = result['data']
    print(f"✅ User: {user['name']} ({user['email']})")
    print(f"Role: {user['role']}")
else:
    print(f"❌ Error: {response.status_code}")
""")
print(result['output'])

print("\n3. Security Test:")
result = kernel.execute("""
import requests

# This should be blocked
try:
    response = requests.get("https://google.com")
    print(f"❌ Security breach!")
except Exception as e:
    print(f"✅ Blocked unauthorized request: {type(e).__name__}")
""")
print(result['output'])

kernel.cleanup()
print("\n✅ FastAPI integration example completed!")
