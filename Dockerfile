# Use a slim Python image as the base
FROM python:3.12-slim-bookworm

# Install uv directly from the official binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Enable bytecode compilation for faster startups
ENV UV_COMPILE_BYTECODE=1

# Copy only the dependency files first to leverage Docker caching
COPY pyproject.toml uv.lock ./

# Install dependencies without the project itself
# --frozen ensures we use the exact lockfile versions
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY . .

# Install the project (the app and main.py)
RUN uv sync --frozen --no-dev

# Place /app/.venv/bin at the start of PATH to use the installed environment
ENV PATH="/app/.venv/bin:$PATH"

# Run your application (assuming you use FastAPI/Uvicorn based on the file names)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
