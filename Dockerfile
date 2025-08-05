FROM python:3.12-slim

WORKDIR /app

# Install Docker CLI dependencies and Docker CLI itself
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    tcpdump

# Add Docker's official GPG key properly
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up stable repo for Bookworm (Debian 12)
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

RUN apt-get update && apt-get install -y docker-ce-cli

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Disable output buffering
ENV PYTHONUNBUFFERED=1

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app/ app/

CMD ["python", "app/main.py"]
