#!/usr/bin/env python3
"""
Basic PersistentKernel Usage Example

Simple demonstration of the persistent kernel's core functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from kernel import PersistentKernel

# Create a basic kernel
kernel = PersistentKernel(session_id="basic_example")

print("=== Basic PersistentKernel Example ===")

# Test 1: Simple calculation
print("\n1. Simple Calculation:")
result = kernel.execute("print(f'2 + 2 = {2 + 2}')")
print(result['output'])

# Test 2: Define and use a function
print("\n2. Function Definition and Usage:")
kernel.execute("""
def greet(name):
    return f"Hello, {name}!"

def calculate_square(x):
    return x * x
""")

result = kernel.execute("""
print(greet("World"))
print(f"Square of 5: {calculate_square(5)}")
""")
print(result['output'])

# Test 3: Variables persist across executions
print("\n3. Variable Persistence:")
kernel.execute("counter = 0")

for i in range(3):
    result = kernel.execute("""
counter += 1
print(f"Counter: {counter}")
""")
    print(result['output'])

# Test 4: Package installation and usage
print("\n4. Package Installation:")
result = kernel.execute("""
import subprocess
import sys

# Install a package
result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'requests'], 
                       capture_output=True, text=True)
print("Package installation completed")

# Use the package
import requests
print("Requests library imported successfully")
""")
print(result['output'])

# Cleanup
kernel.cleanup()
print("\n✅ Example completed successfully!")
