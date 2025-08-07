# Use the official Python slim image as a secure and minimal base
FROM python:3.12-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user for security
RUN groupadd -r appuser --gid=1001 && useradd -r -s /bin/false -g appuser --uid=1001 appuser

# Set the working directory
WORKDIR /app

# --- THIS IS THE FIX ---
# Give the 'appuser' ownership of the working directory
RUN chown appuser:appuser /app

# Copy and install dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=appuser:appuser . .

# Switch to the non-root user
USER appuser

# Expose the port
EXPOSE 8000

# Healthcheck to ensure the app is running (curl is available in this image)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "30", "--max-requests", "1000", "--max-requests-jitter", "100", "--preload", "app:app"]
