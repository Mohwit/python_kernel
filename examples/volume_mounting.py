#!/usr/bin/env python3
"""
Volume Mounting Example

Simple demonstration of mounting host directories in the sandbox.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from kernel import PersistentKernel

print("=== Volume Mounting Example ===")

# Get the data folder path
data_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
print(f"Mounting data folder: {data_folder}")

# Create kernel with volume mount
kernel = PersistentKernel(
    volume_mounts={data_folder: "/app/data"},
    default_packages=["pandas"],
    session_id="volume_example"
)

print("\n1. List mounted files:")
result = kernel.execute("""
import os

print("Files in /app/data:")
if os.path.exists('/app/data'):
    files = os.listdir('/app/data')
    for file in files:
        print(f"  - {file}")
else:
    print("  Directory not found")
""")
print(result['output'])

print("\n2. Read CSV file:")
result = kernel.execute("""
import pandas as pd

try:
    df = pd.read_csv('/app/data/test.csv')
    print(f"✅ CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    print("\\nData:")
    print(df.to_string(index=False))
    
    print(f"\\nAnalysis:")
    print(f"Average age: {df['age'].mean():.1f}")
    print(f"Cities: {', '.join(df['city'].unique())}")
    
except Exception as e:
    print(f"❌ Error reading CSV: {e}")
""")
print(result['output'])

print("\n3. Test write protection:")
result = kernel.execute("""
try:
    with open('/app/data/test_write.txt', 'w') as f:
        f.write("This should fail")
    print("❌ Write succeeded (security issue!)")
except Exception as e:
    print(f"✅ Write blocked (read-only mount): {type(e).__name__}")
""")
print(result['output'])

kernel.cleanup()
print("\n✅ Volume mounting example completed!")
