#!/usr/bin/env python3
"""
Container-level Network Guard

This script runs inside the Docker container to enforce network restrictions
by intercepting HTTP requests and checking them against allowed endpoints.
"""

import os
import sys
import re
from typing import List, Optional

def get_allowed_endpoints() -> List[str]:
    """Get allowed endpoints from environment variable."""
    endpoints_env = os.environ.get('ALLOWED_ENDPOINTS', '')
    if not endpoints_env:
        return []
    return [endpoint.strip() for endpoint in endpoints_env.split(',') if endpoint.strip()]

def is_endpoint_allowed(url: str, allowed_endpoints: List[str]) -> bool:
    """Check if a URL is allowed based on endpoint patterns."""
    if not allowed_endpoints:
        return False
    
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    for endpoint in allowed_endpoints:
        if endpoint.startswith('regex:'):
            # Regex pattern
            pattern = endpoint[6:]
            if re.match(pattern, url) or re.match(pattern, normalized_url):
                return True
        else:
            # URL prefix match
            if url.startswith(endpoint) or normalized_url.startswith(endpoint):
                return True
    
    return False

def patch_requests_module():
    """Patch the requests module to enforce endpoint restrictions."""
    try:
        import requests
        original_request = requests.request
        allowed_endpoints = get_allowed_endpoints()
        
        def restricted_request(method, url, **kwargs):
            if not is_endpoint_allowed(url, allowed_endpoints):
                raise PermissionError(f"Access denied: URL not in whitelist: {url}")
            return original_request(method, url, **kwargs)
        
        # Patch all request methods
        requests.request = restricted_request
        requests.get = lambda url, **kwargs: restricted_request('GET', url, **kwargs)
        requests.post = lambda url, **kwargs: restricted_request('POST', url, **kwargs)
        requests.put = lambda url, **kwargs: restricted_request('PUT', url, **kwargs)
        requests.delete = lambda url, **kwargs: restricted_request('DELETE', url, **kwargs)
        
        print(f"NETWORK_GUARD: Configured restrictions for {len(allowed_endpoints)} endpoints")
        
    except ImportError:
        # requests not available, skip patching
        pass
    except Exception as e:
        print(f"NETWORK_GUARD: Error setting up restrictions: {e}")

def patch_urllib():
    """Patch urllib to enforce endpoint restrictions."""
    try:
        import urllib.request
        original_urlopen = urllib.request.urlopen
        allowed_endpoints = get_allowed_endpoints()
        
        def restricted_urlopen(url, *args, **kwargs):
            url_str = str(url)
            if not is_endpoint_allowed(url_str, allowed_endpoints):
                raise PermissionError(f"Access denied: URL not in whitelist: {url_str}")
            return original_urlopen(url, *args, **kwargs)
        
        urllib.request.urlopen = restricted_urlopen
        
    except ImportError:
        pass
    except Exception as e:
        print(f"NETWORK_GUARD: Error setting up urllib restrictions: {e}")

def setup_network_restrictions():
    """Set up all network restrictions."""
    allowed_endpoints = get_allowed_endpoints()
    
    if not allowed_endpoints:
        print("NETWORK_GUARD: No network restrictions (no endpoints specified)")
        return
    
    print(f"NETWORK_GUARD: Setting up restrictions for {len(allowed_endpoints)} endpoints")
    
    # Patch common HTTP libraries
    patch_requests_module()
    patch_urllib()
    
    # Add this module to sys.modules so it's available for import
    sys.modules['network_guard'] = sys.modules[__name__]

# Auto-setup when imported
if __name__ != "__main__":
    setup_network_restrictions()

if __name__ == "__main__":
    # Test the network guard
    setup_network_restrictions()
    
    # Test with requests if available
    try:
        import requests
        
        # This should work if httpbin.org is in allowed endpoints
        try:
            response = requests.get('https://httpbin.org/get')
            print(f"Allowed request successful: {response.status_code}")
        except PermissionError as e:
            print(f"Blocked request: {e}")
        
        # This should be blocked
        try:
            response = requests.get('https://google.com')
            print(f"ERROR: This should have been blocked!")
        except PermissionError as e:
            print(f"Successfully blocked unauthorized request: {e}")
            
    except ImportError:
        print("requests not available for testing")
