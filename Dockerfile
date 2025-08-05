FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY app/ app/

# Default entrypoint
CMD ["python", "app/main.py"]
