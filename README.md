# Python Kernel

A secure, persistent Python code execution environment using Docker containers with volume-based state storage. This project provides a clean interface for running Python code in isolated Docker containers while maintaining state across executions through persistent Docker volumes.

## Features

- **Volume-Based Persistence**: State stored in isolated Docker volumes (not host memory)
- **Function Persistence**: Both pre-loaded and dynamically defined functions persist
- **Docker Isolation**: All code runs in secure, isolated Docker containers
- **Session Management**: Each kernel gets its own isolated volume namespace
- **Package Persistence**: Installed packages persist across sessions in volumes
- **Security**: Non-root execution with volume isolation and security constraints
- **Resource Management**: Configurable memory and CPU limits
- **Timeout Protection**: Configurable execution timeouts to prevent runaway code

## Project Structure

```
python_kernel/
├── kernel/
│   ├── __init__.py              # Package initialization
│   ├── persistent_kernel.py     # Main PersistentKernel class
│   ├── docker_runner.py         # Docker container management
│   └── Dockerfile              # Docker image configuration
├── functions.py                 # Example functions for testing
├── example.py                   # Usage example
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
    session_id="default"     # Unique session identifier for volume isolation
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

### v2.0.0

- **Volume-Based Architecture**: Migrated from host memory to Docker volume storage
- **Enhanced Security**: Eliminated host memory pollution and improved isolation
- **Session Management**: Added session-based volume isolation
- **Function Persistence**: Improved function source extraction and persistence
- **Cleanup Support**: Added volume cleanup functionality
- **Code Optimization**: Cleaned up unused code and improved documentation

### v1.0.0

- Initial release
- Basic persistent kernel functionality
- Docker container isolation
- Package installation support
- Function persistence across executions
