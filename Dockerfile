# Use official Python 3.10 image as base
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project into container
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run when container starts
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]