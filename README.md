# Python Kernel

A secure, persistent Python code execution environment using Docker containers with volume-based state storage. This project provides a clean interface for running Python code in isolated Docker containers while maintaining state across executions through persistent Docker volumes.

## Features

- **Volume-Based Persistence**: State stored in isolated Docker volumes (not host memory)
- **Function Persistence**: Both pre-loaded and dynamically defined functions persist
- **Docker Isolation**: All code runs in secure, isolated Docker containers
- **Session Management**: Each kernel gets its own isolated volume namespace
- **Package Management**: Manual installation and automatic default packages
- **Package Persistence**: Installed packages persist across sessions in volumes
- **Security**: Non-root execution with volume isolation and security constraints
- **Resource Management**: Configurable memory and CPU limits
- **Timeout Protection**: Configurable execution timeouts to prevent runaway code
- **🔒 Network Security**: Endpoint-based execution with HTTP request whitelisting
- **🛡️ AI Agent Safety**: Prevent environment variable exposure through secure execution
- **🌐 Flexible Network Modes**: Choose between restricted, isolated, or default networking

## Project Structure

```
python_kernel/
├── kernel/
│   ├── __init__.py              # Package initialization
│   ├── persistent_kernel.py     # Main PersistentKernel class
│   ├── docker_runner.py         # Docker container management
│   ├── container_network_guard.py # Container-level network filtering
│   └── Dockerfile              # Docker image configuration
├── examples/
│   ├── README.md               # Examples documentation
│   ├── basic_usage.py          # Basic kernel functionality
│   ├── network_restrictions.py # Network security examples
│   ├── volume_mounting.py      # File system access examples
│   ├── api_server.py           # FastAPI server for integration
│   └── fastapi_integration.py  # FastAPI + sandbox example
├── functions.py                 # Example functions for testing
├── data/
│   └── test.csv                # Sample data file
└── README.md                   # This file
```

## Requirements

- Python 3.7+
- Docker
- Docker daemon running

## Installation

1. **Clone or download this project**

2. **Ensure Docker is installed and running**

   ```bash
   docker --version
   ```

3. **The Docker image will be built automatically on first use**

## Quick Start

### Run Examples

```bash
# Basic functionality - code execution, functions, variables, packages
python examples/basic_usage.py

# Network security - endpoint whitelisting and isolation
python examples/network_restrictions.py

# File system access - volume mounting and data processing
python examples/volume_mounting.py

# FastAPI integration - secure API endpoints
python examples/api_server.py  # Terminal 1
python examples/fastapi_integration.py  # Terminal 2
```

See [`examples/README.md`](examples/README.md) for detailed documentation.

### Basic Usage

```python
from kernel import PersistentKernel

# Create a kernel instance
kernel = PersistentKernel()

# Execute some Python code
result = kernel.execute("""
x = 42
y = x * 2
print(f"The answer is {y}")
""")

print(result['output'])  # Output: The answer is 84

# State persists across executions
result = kernel.execute("""
print(f"x is still {x}")
z = x + y
print(f"z = {z}")
""")
```

### Using Pre-defined Functions

```python
from kernel import PersistentKernel
from functions import FUNCTIONS

# Create kernel with functions in namespace
kernel = PersistentKernel(
    namespace=FUNCTIONS,
    imports="import math",
    timeout=30
)

# Use the pre-loaded functions
result = kernel.execute("""
message = greet('World')
print(message)

result = multiply(6, 7)
print(f"6 * 7 = {result}")
""")
```

### Installing Packages

#### Manual Installation

```python
# Install a package (persists across kernel sessions)
result = kernel.install_package("requests")

# Use the installed package
result = kernel.execute("""
import requests
response = requests.get('https://api.github.com')
print(f"Status: {response.status_code}")
""")
```

#### Default Packages

```python
from kernel import PersistentKernel

# Automatically install packages during initialization
kernel = PersistentKernel(
    default_packages=["requests", "numpy", "pandas"],
    session_id="data_session"
)

# Packages are already available
result = kernel.execute("""
import requests
import numpy as np
import pandas as pd

print("All packages ready to use!")
print(f"NumPy version: {np.__version__}")
""")
```

## API Reference

### PersistentKernel

#### Constructor

```python
PersistentKernel(
    namespace=None,          # Dict of functions/variables to preload
    imports="",              # String of import statements to run on init
    timeout=30,              # Execution timeout in seconds
    memory_limit="512m",     # Docker memory limit
    cpu_limit="0.5",         # Docker CPU limit
    session_id="default",    # Unique session identifier for volume isolation
    default_packages=None    # List of packages to install automatically
)
```

#### Methods

- **`execute(code: str) -> Dict[str, Any]`**

  - Execute Python code and return results
  - Returns: `{"success": bool, "output": str, "error": str}`

- **`reset() -> None`**

  - Reset kernel to initial state

- **`install_package(package_name: str) -> Dict[str, Any]`**

  - Install a Python package in the kernel environment

- **`set_variable(name: str, value: Any) -> bool`**

  - Set a variable in the kernel namespace

- **`get_variable(name: str, default=None) -> Any`**

  - Get a variable from the kernel namespace

- **`get_namespace() -> Dict[str, Any]`**

  - Get the current namespace from volume storage

- **`cleanup() -> bool`**
  - Clean up the persistent volumes for this kernel session

### DockerRunner

Lower-level Docker execution interface.

```python
DockerRunner(
    image_name="python-kernel",
    memory_limit="512m",
    cpu_limit="0.5",
    timeout=30,
    session_id="default"     # Session ID for volume isolation
)
```

## Architecture

### Volume-Based State Persistence

The kernel uses Docker volumes for secure, isolated state storage:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  DOCKER VOLUMES │◄──►│ EXECUTION CYCLE │◄──►│  DOCKER VOLUMES │
│                 │    │                 │    │                 │
│ state-{session} │    │ 1. Load state   │    │ state-{session} │
│ ├─kernel_state  │    │ 2. Restore funcs│    │ ├─kernel_state  │
│ └─packages/     │    │ 3. Execute code │    │ └─packages/     │
│                 │    │ 4. Save state   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Security Benefits

- **No Host Memory Pollution**: State stored in isolated Docker volumes
- **Session Isolation**: Each kernel gets unique volume namespace
- **Container Isolation**: All execution happens in ephemeral containers
- **Non-root Execution**: Code runs as non-privileged sandbox user

## Network Security & AI Agent Safety

### Overview

The PersistentKernel provides advanced network security features designed specifically for AI agent use cases. These features prevent:

- **Environment Variable Exposure**: By avoiding function passing to the sandbox
- **Unauthorized Network Access**: Through endpoint whitelisting and request filtering
- **Data Exfiltration**: By restricting outbound connections to approved endpoints only

### Network Modes

#### 1. Restricted Mode (Recommended for AI Agents)

```python
kernel = PersistentKernel(
    allowed_endpoints=[
        "https://api.myservice.com",
        "https://httpbin.org",
        "regex:https://api\\.example\\.com/v[0-9]+/.*"
    ],
    network_mode="restricted"
)
```

- Only whitelisted endpoints accessible via HTTP requests
- All other network access blocked at application level
- Supports URL prefixes and regex patterns

#### 2. Isolated Mode (Maximum Security)

```python
kernel = PersistentKernel(
    network_mode="isolated"
)
```

- Complete network isolation using Docker's `--network none`
- No HTTP requests possible
- Ideal for pure computation tasks

#### 3. Default Mode (Legacy)

```python
kernel = PersistentKernel(
    network_mode="default"
)
```

- Normal Docker networking
- No restrictions (not recommended for AI agents)

### Endpoint Configuration

#### URL Patterns

```python
allowed_endpoints = [
    "https://api.example.com",                    # Exact domain match
    "https://api.example.com/v1",                 # Path prefix match
    "https://httpbin.org",                        # Domain with any path
]
```

#### Regex Patterns

```python
allowed_endpoints = [
    "regex:https://api\\.myservice\\.com/v[0-9]+/.*",  # Versioned API
    "regex:https://[a-z]+\\.example\\.com/.*",         # Subdomain pattern
]
```

### Secure Usage Example (Docker-level Restrictions)

```python
from kernel import PersistentKernel

# Create secure kernel for AI agent using Docker-level restrictions
kernel = PersistentKernel(
    namespace={},  # No functions passed - prevents env var exposure
    allowed_endpoints=[
        "https://api.myservice.com",
        "https://httpbin.org/json"
    ],
    network_mode="restricted",  # Uses Docker env vars + container filtering
    session_id="ai_agent_session"
)

# Safe execution - network restrictions enforced at Docker level
result = kernel.execute("""
import requests

# This works - endpoint is whitelisted
response = requests.get('https://httpbin.org/json')
print(f"Allowed request successful: {response.status_code}")

# This fails - blocked by container-level network guard
try:
    response = requests.get('https://google.com')
except PermissionError as e:
    print(f"Blocked unauthorized request: {e}")
""")
```

### Complete Network Isolation

```python
# For maximum security - complete network isolation
kernel = PersistentKernel(
    network_mode="isolated"  # Uses Docker --network none
)

result = kernel.execute("""
# Network requests will fail completely
try:
    import requests
    requests.get('https://httpbin.org')
except Exception as e:
    print(f"Network blocked: {type(e).__name__}")

# But local computation works fine
result = sum(x**2 for x in range(10))
print(f"Local computation: {result}")
""")
```

### Security Comparison

| Feature               | Function Passing   | Endpoint-based      |
| --------------------- | ------------------ | ------------------- |
| Environment Variables | ❌ Exposed         | ✅ Protected        |
| Network Access        | ❌ Unrestricted    | ✅ Whitelisted Only |
| Code Injection Risk   | ❌ Higher          | ✅ Lower            |
| AI Agent Suitability  | ❌ Not Recommended | ✅ Recommended      |

### Docker-level Implementation

The network security is implemented at two levels:

1. **Docker Container Level**:

   - `isolated` mode uses `docker run --network none` for complete isolation
   - `restricted` mode uses environment variables to pass endpoint whitelist
   - Uses controlled DNS servers for additional security

2. **Container Runtime Level**:
   - `container_network_guard.py` patches Python's `requests` and `urllib` modules
   - Intercepts HTTP requests and validates against whitelist
   - Provides clear error messages for blocked requests

**Benefits of Docker-level Approach**:

- ✅ **Simpler Implementation**: No complex proxy setup or network management
- ✅ **Better Performance**: No request interception overhead for allowed endpoints
- ✅ **More Reliable**: Uses Docker's proven networking features
- ✅ **Easier Debugging**: Clear separation between Docker and application concerns
- ✅ **Lower Resource Usage**: No additional proxy containers needed

### FastAPI Integration Pattern

For AI agents that need to access external services, the recommended pattern is to create FastAPI endpoints that the sandbox can call:

```python
# api_server.py - Your secure API server
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class DataRequest(BaseModel):
    data: List[float]
    operation: str

@app.post("/process-data")
async def process_data(request: DataRequest):
    # Your secure business logic here
    if request.operation == "sum":
        result = sum(request.data)
    # ... other operations
    return {"result": result, "operation": request.operation}

# Sandbox usage
kernel = PersistentKernel(
    allowed_endpoints=["http://localhost:8000"],
    network_mode="restricted"
)

result = kernel.execute("""
import requests
response = requests.post("http://localhost:8000/process-data",
                        json={"data": [1,2,3], "operation": "sum"})
print(response.json())
""")
```

**Benefits**:

- ✅ **API-first Architecture**: Clean separation between AI agent and business logic
- ✅ **Input Validation**: Pydantic models ensure data integrity
- ✅ **Access Control**: Only expose specific functionality to AI agents
- ✅ **Audit Trail**: Log all API calls for monitoring
- ✅ **Rate Limiting**: Control API usage with FastAPI middleware

## Examples

### Example 1: Basic Math Operations

```python
from kernel import PersistentKernel

kernel = PersistentKernel()

# Define a function
kernel.execute("""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""")

# Use the function
result = kernel.execute("""
for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")
""")

print(result['output'])
```

### Example 2: Data Analysis with Session Management

```python
from kernel import PersistentKernel

# Create kernel with unique session ID
kernel = PersistentKernel(session_id="data_analysis_session")

# Install required packages (persists in session volume)
kernel.install_package("pandas")
kernel.install_package("numpy")

# Analyze data
result = kernel.execute("""
import pandas as pd
import numpy as np

# Create sample data
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'score': [85, 92, 78]
}

df = pd.DataFrame(data)
print("Data:")
print(df)
print(f"\\nAverage age: {df['age'].mean()}")
print(f"Average score: {df['score'].mean()}")
""")

# Clean up session volumes when done
kernel.cleanup()
```

## Configuration

### Docker Settings

The kernel uses the following default Docker settings:

- **Memory Limit**: 512MB
- **CPU Limit**: 0.5 cores
- **Timeout**: 30 seconds
- **User**: Non-root (`sandbox` user)
- **Security**: No new privileges

### Volume-Based Storage

- **State Storage**: `python-kernel-state-{session_id}` volume
- **Package Storage**: `python-kernel-packages-{session_id}` volume
- **Isolation**: Each session gets unique volume namespace
- **Persistence**: Volumes survive container restarts and recreation

## Security Features

- **Container Isolation**: All code runs in isolated Docker containers
- **Volume Isolation**: State stored in isolated Docker volumes (not host memory)
- **Non-root Execution**: Code runs as non-privileged `sandbox` user
- **Resource Limits**: Configurable memory and CPU constraints
- **Execution Timeouts**: Prevents runaway code execution
- **Session Isolation**: Each kernel session gets unique volume namespace
- **Security Constraints**: `no-new-privileges` and other Docker security options

## Troubleshooting

### Docker Image Build Issues

If the Docker image fails to build:

```bash
# Check Docker is running
docker ps

# Manually build the image
cd kernel/
docker build -t python-kernel -f Dockerfile .
```

### Permission Issues

If you encounter permission issues:

```bash
# Ensure Docker daemon is running
sudo systemctl start docker

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
```

### Package Installation Issues

If packages fail to install:

- Check internet connectivity in Docker container
- Try installing packages manually in a test container
- Verify package names are correct

### Volume Management

To list kernel volumes:

```bash
docker volume ls | grep python-kernel
```

To manually clean up volumes:

```bash
docker volume rm python-kernel-state-{session_id}
docker volume rm python-kernel-packages-{session_id}
```

To clean up all kernel volumes:

```bash
docker volume ls -q | grep python-kernel | xargs docker volume rm
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Feel free to use and modify as needed.

## Changelog

### v1.0.0

- **Volume-Based Architecture**: Secure state storage in Docker volumes (not host memory)
- **Function Persistence**: Both pre-loaded and dynamically defined functions persist
- **Default Packages**: Automatic package installation during kernel initialization
- **Session Management**: Isolated volume namespaces for each kernel session
- **Package Management**: Manual installation and persistent package storage
- **Docker Security**: Non-root execution with container isolation
- **Resource Management**: Configurable memory, CPU limits, and timeouts
- **Cleanup Support**: Volume cleanup functionality for session management
