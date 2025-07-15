# Use Python 3.11 slim image for AMD64 platform
FROM --platform=linux/amd64 python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for Playwright)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright system dependencies as root
RUN playwright install-deps chromium

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Install Playwright browsers as appuser
USER appuser
RUN playwright install chromium

# Copy application code
COPY --chown=appuser:appuser . .

# Expose port (Cloud Run will set PORT env var)
EXPOSE 8080

# Default command (can be overridden)
CMD ["python", "run.py"]