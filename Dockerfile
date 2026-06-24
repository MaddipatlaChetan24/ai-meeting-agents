# ══════════════════════════════════════════════════════════════════════════════
# AI Meeting Assistant — Multi-stage Docker Build
# ══════════════════════════════════════════════════════════════════════════════
# Stage 1: Build dependencies in a virtual environment
# Stage 2: Copy only the runtime into a slim final image
# ══════════════════════════════════════════════════════════════════════════════

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build-time system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment for clean dependency isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (cached layer — only rebuilds when requirements change)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt


# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Labels
LABEL maintainer="AI Meeting Assistant" \
      description="Transcribe, summarize, extract insights and chat with meetings" \
      version="1.0"

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime system dependencies
#   - ffmpeg: Required for audio processing (yt-dlp, pydub, whisper)
#   - curl: Used by Docker health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user for security
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Set up the application directory
WORKDIR /app

# Copy application source code
COPY --chown=appuser:appuser . /app/

# Create runtime directories with correct ownership
RUN mkdir -p /app/downloads /app/vector_db && \
    chown -R appuser:appuser /app/downloads /app/vector_db

# Create Streamlit config to suppress email prompt in headless mode
RUN mkdir -p /home/appuser/.streamlit && \
    echo '[general]\nemail = ""\n' > /home/appuser/.streamlit/credentials.toml && \
    chown -R appuser:appuser /home/appuser/.streamlit

# Switch to non-root user
USER appuser

# Expose Streamlit's default port
EXPOSE 8501

# Health check — Streamlit exposes /_stcore/health
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit in headless mode (no browser, bind to all interfaces)
ENTRYPOINT ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--server.fileWatcherType=none", \
    "--browser.gatherUsageStats=false"]
