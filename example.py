#!/usr/bin/env python3
"""
Example of using the Persistent Docker Kernel
"""

from kernel import PersistentKernel
from functions import FUNCTIONS

from dotenv import load_dotenv
load_dotenv()
import os

api_key = os.getenv("OPENAI_API_KEY")

def main():
    # Create kernel with pre-defined functions and imports
    kernel = PersistentKernel(
        namespace=FUNCTIONS | {"api_key": api_key},
        imports=f"""
import math
        """,
        timeout=30,
        session_id="example_session"
    )
    
    # Execute code using the pre-loaded functions
    result = kernel.execute("""
print(greet('Docker Kernel'))
print(api_key)
""")
    print(result)
    
    kernel.cleanup()

if __name__ == "__main__":
    main()
