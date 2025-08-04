# 1. USE A VULNERABLE BASE IMAGE
# Using an old, unsupported Python version on an outdated OS (Debian Stretch)
# This will introduce hundreds of OS-level CVEs for the scanner to find.
FROM python:3.7-slim-stretch

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 2. INTRODUCE HARDCODED SECRETS
# This RUN command creates a file with fake credentials.
# The secret scanner will detect these and flag them as critical risks.
RUN echo "class Config:" > config.py && \
    echo "    AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'" >> config.py && \
    echo "    GITHUB_TOKEN = 'ghp_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0'" >> config.py && \
    echo "    DATABASE_PASSWORD = \"supersecretpassword123!\"" >> config.py

# 3. INTRODUCE A "MALWARE" SIGNATURE
# This is the EICAR test string. It's a harmless, standard file used to test
# antivirus and malware scanners. ThreatMapper will detect this as malware.
RUN echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > eicar_test_file.com

# Copy and install vulnerable dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# 4. RUN AS ROOT (SECURITY ANTI-PATTERN)
# By not specifying a non-root user, the container will run as root,
# violating the principle of least privilege.
# USER appuser (This secure practice has been removed)

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
