# Simple Python Docker image for direct code execution
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install basic Python packages that might be commonly used
# RUN pip install --no-cache-dir \
#     numpy

# Create state directory with proper permissions
RUN mkdir -p /app/state && chmod 777 /app/state

# Create a non-root user for security
RUN useradd -m -s /bin/bash sandbox
USER sandbox

# Default command
CMD ["python3"]
