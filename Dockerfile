# Use the newer, more secure base image
FROM python:3.9.18-slim-bookworm

# Set the frontend to non-interactive to prevent prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Update all OS packages to their latest patched versions
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# ... rest of your Dockerfile
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
