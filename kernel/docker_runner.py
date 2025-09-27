#!/usr/bin/env python3
"""
Docker runner for direct Python execution
"""

import subprocess
import json
import os
import time
from dataclasses import dataclass
from typing import Optional, Dict
from pathlib import Path

@dataclass
class DockerExecutionResult:
    output: str
    error: str
    success: bool
    execution_time: float

class DockerRunner:
    """Simple Docker runner for Python code execution."""

    def __init__(self, 
                 image_name: str = "python-kernel",
                 memory_limit: str = "512m",
                 cpu_limit: str = "0.5",
                 timeout: int = 30,
                 session_id: str = "default",
                 volume_mounts: Optional[Dict[str, str]] = None):
        """Initialize the Docker runner."""
        self.image_name = image_name
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.timeout = timeout
        self.session_id = session_id
        self.volume_mounts = volume_mounts or {}
        self.dockerfile_path = os.path.join(os.path.dirname(__file__), "Dockerfile")
        
        # Create persistent package directory
        self.packages_dir = Path.home() / ".python_sandbox_packages"
        self.packages_dir.mkdir(exist_ok=True)
        
        # Create persistent volumes for state and packages
        self.state_volume_name = f"python-kernel-state-{session_id}"
        self.packages_volume_name = f"python-kernel-packages-{session_id}"
        self._ensure_volumes_exist()
        
    def build_image(self) -> bool:
        """Build the Docker image."""
        try:
            print("Building Docker image...")
            
            result = subprocess.run([
                "docker", "build", 
                "-t", self.image_name,
                "-f", self.dockerfile_path,
                os.path.dirname(self.dockerfile_path)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"Failed to build Docker image: {result.stderr}")
                return False
                
            print("Docker image built successfully!")
            return True
            
        except subprocess.TimeoutExpired:
            print("Docker build timed out")
            return False
        except Exception as e:
            print(f"Error building Docker image: {e}")
            return False
    
    def execute(self, python_code: str) -> DockerExecutionResult:
        """Execute Python code in a Docker container."""
        start_time = time.time()
        
        # Build image if it doesn't exist
        if not self._image_exists():
            if not self.build_image():
                return DockerExecutionResult(
                    output="",
                    error="Failed to build Docker image",
                    success=False,
                    execution_time=time.time() - start_time
                )
        
        try:
            # Prepare Docker run command with persistent volumes
            docker_cmd = [
                "docker", "run",
                "--rm",  # Remove container after execution
                "--memory", self.memory_limit,
                "--cpus", self.cpu_limit,
                "--security-opt", "no-new-privileges:true",
                "-v", f"{self.state_volume_name}:/app/state",
                "-v", f"{self.packages_volume_name}:/home/sandbox/.local",
            ]
            
            # Add user-specified volume mounts (read-only)
            for host_path, container_path in self.volume_mounts.items():
                docker_cmd.extend(["-v", f"{host_path}:{container_path}:ro"])
            
            # Add user and command
            docker_cmd.extend([
                "--user", "sandbox",
                self.image_name,
                "python3", "-c", python_code
            ])
            
            # Execute the container
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            execution_time = time.time() - start_time
            
            return DockerExecutionResult(
                output=result.stdout,
                error=result.stderr,
                success=result.returncode == 0,
                execution_time=execution_time
            )
            
        except subprocess.TimeoutExpired:
            return DockerExecutionResult(
                output="",
                error=f"Execution timed out after {self.timeout} seconds",
                success=False,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return DockerExecutionResult(
                output="",
                error=f"Docker execution error: {str(e)}",
                success=False,
                execution_time=time.time() - start_time
            )
    
    def _image_exists(self) -> bool:
        """Check if the Docker image exists."""
        try:
            result = subprocess.run([
                "docker", "images", "-q", self.image_name
            ], capture_output=True, text=True)
            return bool(result.stdout.strip())
        except:
            return False
    
    def _ensure_volumes_exist(self) -> None:
        """Create Docker volumes if they don't exist."""
        for volume_name in [self.state_volume_name, self.packages_volume_name]:
            try:
                # Check if volume exists
                result = subprocess.run([
                    "docker", "volume", "inspect", volume_name
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    # Create volume if it doesn't exist
                    subprocess.run([
                        "docker", "volume", "create", volume_name
                    ], capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError:
                print(f"Warning: Could not create volume {volume_name}")
    
    def cleanup_volumes(self) -> bool:
        """Remove the persistent volumes for this session."""
        try:
            for volume_name in [self.state_volume_name, self.packages_volume_name]:
                subprocess.run([
                    "docker", "volume", "rm", volume_name
                ], capture_output=True, text=True)
            return True
        except:
            return False
