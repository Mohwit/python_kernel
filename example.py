#!/usr/bin/env python3
"""
Example of using the Persistent Docker Kernel
"""

from kernel import PersistentKernel
from functions import FUNCTIONS

from dotenv import load_dotenv
load_dotenv()
import os

def main():
    # Create kernel with pre-defined functions and imports
    kernel = PersistentKernel(
        namespace=FUNCTIONS,
        imports=f"""
import math
        """,
        timeout=30,
        session_id="test_session",
        default_packages=["requests"]
        
    )
    
    # Execute code using the pre-loaded functions
    result = kernel.execute("""
print(greet('Docker Kernel'))
print(api_key)
print(requests.get('https://api.github.com').status_code)
""")
    print(result)
    
    # kernel.cleanup()

if __name__ == "__main__":
    main()
