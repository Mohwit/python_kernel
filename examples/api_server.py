#!/usr/bin/env python3
"""
FastAPI Server for Sandbox Integration

This server provides secure endpoints that can be called from the sandbox container.
Perfect for AI agent scenarios where you want to expose specific functionality
without giving the agent direct access to sensitive resources.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
from typing import Dict, List, Any
import json
import time

app = FastAPI(title="Sandbox API Server", version="1.0.0")

# Data models
class DataProcessingRequest(BaseModel):
    data: List[float]
    operation: str  # "sum", "average", "max", "min", "sort"

class DataProcessingResponse(BaseModel):
    result: Any
    operation: str
    input_count: int
    timestamp: str

class UserInfoRequest(BaseModel):
    user_id: str
    fields: List[str]  # Fields to return: "name", "email", "role", "permissions"

class UserInfoResponse(BaseModel):
    user_id: str
    data: Dict[str, Any]
    timestamp: str

# Mock database for demonstration
MOCK_USERS = {
    "user123": {
        "name": "John Doe",
        "email": "john@example.com", 
        "role": "developer",
        "permissions": ["read", "write"],
        "department": "engineering",
        "created_at": "2024-01-15"
    },
    "user456": {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "role": "admin", 
        "permissions": ["read", "write", "delete", "admin"],
        "department": "operations",
        "created_at": "2024-02-01"
    }
}

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Sandbox API Server is running",
        "endpoints": [
            "/process-data",
            "/user-info",
            "/docs"
        ],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.post("/process-data", response_model=DataProcessingResponse)
async def process_data(request: DataProcessingRequest):
    """
    Process numerical data with various operations.
    
    This endpoint allows the sandbox to perform data processing
    without exposing the underlying computation logic.
    """
    try:
        data = request.data
        operation = request.operation.lower()
        
        if not data:
            raise HTTPException(status_code=400, detail="Data list cannot be empty")
        
        # Perform the requested operation
        if operation == "sum":
            result = sum(data)
        elif operation == "average":
            result = sum(data) / len(data)
        elif operation == "max":
            result = max(data)
        elif operation == "min":
            result = min(data)
        elif operation == "sort":
            result = sorted(data)
        elif operation == "stats":
            result = {
                "sum": sum(data),
                "average": sum(data) / len(data),
                "max": max(data),
                "min": min(data),
                "count": len(data)
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported operation: {operation}. Supported: sum, average, max, min, sort, stats"
            )
        
        return DataProcessingResponse(
            result=result,
            operation=operation,
            input_count=len(data),
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/user-info", response_model=UserInfoResponse)
async def get_user_info(request: UserInfoRequest):
    """
    Get user information with field filtering.
    
    This endpoint provides controlled access to user data,
    allowing the sandbox to request specific fields without
    exposing the entire user database.
    """
    try:
        user_id = request.user_id
        requested_fields = request.fields
        
        if user_id not in MOCK_USERS:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        user_data = MOCK_USERS[user_id]
        
        # Filter to only requested fields
        filtered_data = {}
        for field in requested_fields:
            if field in user_data:
                filtered_data[field] = user_data[field]
            else:
                filtered_data[field] = None  # Field not found
        
        return UserInfoResponse(
            user_id=user_id,
            data=filtered_data,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/users")
async def list_users():
    """List available user IDs (for testing purposes)."""
    return {
        "available_users": list(MOCK_USERS.keys()),
        "total_users": len(MOCK_USERS),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "Sandbox API Server",
        "version": "1.0.0",
        "uptime": "N/A",  # Would track actual uptime in production
        "endpoints_available": 6,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    print("🚀 Starting Sandbox API Server...")
    print("📋 Available endpoints:")
    print("   • GET  /           - Root/health check")
    print("   • POST /process-data - Data processing operations")
    print("   • POST /user-info   - User information retrieval") 
    print("   • GET  /users       - List available users")
    print("   • GET  /health      - Detailed health check")
    print("   • GET  /docs        - API documentation")
    print()
    print("🔒 This server is designed to work with sandbox containers")
    print("💡 Use this server's endpoints in your allowed_endpoints list")
    print()
    
    # Run the server
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Listen on all interfaces so Docker can access it
        port=8000,
        log_level="info"
    )
