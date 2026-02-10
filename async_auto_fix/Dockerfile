FROM python:3.11-slim

WORKDIR /app

# Install git for clone operations
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY adk/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY adk/ ./adk/

# Set environment
ENV PYTHONPATH=/app
ENV FLASK_APP=adk.ui.app

# Expose port
EXPOSE 5000

# Run the Flask app
CMD ["python", "-m", "adk.ui.app"]
