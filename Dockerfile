# ✅ Multi-stage build for smaller final image
# Build stage
FROM python:3.11-alpine AS builder

# ✅ Working directory WORKDIR
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

# ✅ Proper layer caching (frequently changing last)
# Copy requirements first for better layer caching
COPY requirements.txt .

# ✅ Dependency installation (RUN)
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
# ✅ Minimal base image (alpine)
FROM python:3.11-alpine AS production

# ✅ Non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# ✅ Working directory WORKDIR
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# ✅ Application code copy (COPY)
COPY --chown=appuser:appgroup . .

# Make sure user path is in PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# ✅ Expose port EXPOSE
EXPOSE 8000

# ✅ Health check (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "main.py"]