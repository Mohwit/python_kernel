# Examples

This folder contains simple, clean examples demonstrating the PersistentKernel functionality.

## Basic Examples

### `basic_usage.py`

Simple demonstration of core kernel functionality:

- Basic code execution
- Function definition and persistence
- Variable persistence across executions
- Package installation

```bash
python examples/basic_usage.py
```

### `network_restrictions.py`

Network security modes demonstration:

- Restricted mode with endpoint whitelisting
- Isolated mode with no network access
- Security testing

```bash
python examples/network_restrictions.py
```

### `volume_mounting.py`

File system access with volume mounting:

- Mount host directories (read-only)
- File reading and data processing
- Write protection testing

```bash
python examples/volume_mounting.py
```

## FastAPI Integration

### `api_server.py`

Simple FastAPI server with two endpoints:

- `/process-data` - Data processing operations
- `/user-info` - User information retrieval

Start the server:

```bash
python examples/api_server.py
```

### `fastapi_integration.py`

Demonstrates calling FastAPI endpoints from sandbox:

- Secure API calls through whitelisted endpoints
- Data processing via API
- User information lookup
- Network security testing

```bash
# Terminal 1: Start API server
python examples/api_server.py

# Terminal 2: Run integration example
python examples/fastapi_integration.py
```

## Requirements

All examples use the basic kernel functionality. For FastAPI examples:

```bash
pip install fastapi uvicorn
```

## Key Features Demonstrated

- ✅ **Persistent State**: Variables and functions persist across executions
- ✅ **Docker Isolation**: All code runs in secure containers
- ✅ **Network Security**: Endpoint whitelisting and complete isolation
- ✅ **Volume Mounting**: Read-only access to host files
- ✅ **Package Management**: Install and use Python packages
- ✅ **API Integration**: Secure FastAPI endpoint access
