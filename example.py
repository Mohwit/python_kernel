#!/usr/bin/env python3
"""
Example of using the Persistent Docker Kernel with Volume Mounting
"""

from kernel import PersistentKernel
from functions import FUNCTIONS
import os

from dotenv import load_dotenv
load_dotenv()

def main():
    # Get the absolute path to the data folder
    data_folder = os.path.join(os.path.dirname(__file__), "data")
    print(f"Mounting data folder: {data_folder}")
    
    # Create kernel with volume mounting for the data folder
    kernel = PersistentKernel(
        namespace=FUNCTIONS,
        imports="""

        """,
        timeout=30,
        session_id="test_session",
        default_packages=["requests", "pandas"],
        volume_mounts={
            data_folder: "/app/data"  # Mount data folder as read-only
        }
    )
    
    print("\n=== Testing Pre-loaded Functions ===")
    # Execute code using the pre-loaded functions
    result = kernel.execute("""
import math
import pandas as pd
import os
print("Files in /app/data:")
if os.path.exists('/app/data'):
    files = os.listdir('/app/data')
    for file in files:
        print(f"  - {file}")
else:
    print("  /app/data directory not found")

# Try to read the CSV file
try:
    df = pd.read_csv('/app/data/test.csv')
    print(f"\\nCSV file loaded successfully!")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\\nData preview:")
    print(df.to_string(index=False))
    
    # Perform some analysis
    print(f"\\nAnalysis:")
    print(f"Average age: {df['age'].mean():.1f}")
    print(f"Cities: {', '.join(df['city'].unique())}")
    
except Exception as e:
    print(f"Error reading CSV: {e}")
""")
    print("Output:", result.get('output', ''))
    if result.get('error'):
        print("Error:", result['error'])
    
    print("\n=== Testing Write Attempt (Should Fail - Read Only) ===")
    # Test that we cannot write to the mounted volume (read-only)
    result = kernel.execute("""
try:
    with open('/app/data/write_test.txt', 'w') as f:
        f.write("This should not work")
    print("ERROR: Write succeeded (this shouldn't happen!)")
except Exception as e:
    print(f"Expected error - cannot write to read-only mount: {e}")
""")
    print("Output:", result.get('output', ''))
    if result.get('error'):
        print("Error:", result['error'])

    
    # Optionally cleanup 
    kernel.cleanup()

if __name__ == "__main__":
    main()
