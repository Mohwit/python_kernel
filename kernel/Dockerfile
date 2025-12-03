# Python Docker image with Docker-level network restrictions
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Install basic Python packages that might be commonly used
RUN pip install --no-cache-dir \
    requests \
    urllib3

# Create state directory with proper permissions
RUN mkdir -p /app/state && chmod 777 /app/state

# Create a non-root user for security
RUN useradd -m -s /bin/bash sandbox

# Create .local directory with proper permissions for the sandbox user
RUN mkdir -p /home/sandbox/.local && chown -R sandbox:sandbox /home/sandbox/.local

# Copy network guard script
COPY container_network_guard.py /app/network_guard.py
RUN chmod 644 /app/network_guard.py

USER sandbox

# Default command
CMD ["python3"]
