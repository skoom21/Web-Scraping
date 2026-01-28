# Production Dockerfile for ZocDoc Scraper
# Optimized for Google Cloud Run

FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Camoufox/Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libglib2.0-0 \
    libnss3-dev \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Set Playwright browsers path BEFORE installing
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers for Camoufox (as root, before switching users)
RUN playwright install firefox
RUN playwright install-deps firefox

# Copy application code
COPY zocdoc_scraper_production.py .
COPY app.py .
COPY preload_camoufox.py .

# Pre-download Camoufox browser binary to avoid runtime download
RUN python preload_camoufox.py || echo "Camoufox pre-download completed"

# Pre-download browserforge data files to avoid permission issues
RUN python -c "from browserforge.fingerprints import FingerprintGenerator; from browserforge.headers import HeaderGenerator; FingerprintGenerator(); HeaderGenerator()"

# Create output and log directories
RUN mkdir -p /app/output /app/logs

# Set environment variables for Cloud Run
ENV ZOCDOC_HEADLESS=true \
    ZOCDOC_OUTPUT_DIR=/app/output \
    ZOCDOC_LOG_DIR=/app/logs \
    PORT=8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ZOCDOC_OUTPUT_DIR=/app/output
# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run as non-root user
RUN useradd -m -u 1000 scraper && \
    chown -R scraper:scraper /app && \
    chown -R scraper:scraper /usr/local/lib/python3.13/site-packages/browserforge && \
    chmod -R 755 /opt/playwright && \
    mkdir -p /home/scraper/.cache && \
    cp -r /root/.cache/camoufox /home/scraper/.cache/ 2>/dev/null && \
    chown -R scraper:scraper /home/scraper/.cache
USER scraper

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# Run the HTTP server with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "2", "--timeout", "900", "app:app"]
