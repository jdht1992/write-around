# Use a minimal Python 3.13 image based on Alpine
FROM python:3.13-alpine

# Update the package index and upgrade all installed OS libraries (fixes xz-libs)
RUN apk update && apk upgrade --no-cache

# Copy the uv and uvx binaries from the official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Upgrade the system pip to resolve its 2 vulnerabilities
# hadolint ignore=DL3013
RUN python3 -m pip install --no-cache-dir --upgrade pip

# Create a non-root user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set the working directory inside the container
WORKDIR /app

# Install project dependencies globally into the system Python
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    # We use uv.lock to guarantee deterministic versions even without uv sync
    uv pip install --system --requirement pyproject.toml

# Copy the rest of the application source code into the container
COPY . .

# Transfer ownership of /app to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user — app no longer runs as root
USER appuser

# Default command to run the FastAPI application
# We no longer use "uv run" because dependencies are in the global system path
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
