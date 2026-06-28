# Use a slim image to reduce container size and security vulnerabilities
FROM python:3.13-slim

# Create a non-root user for secure execution
RUN useradd -m appuser

WORKDIR /app

# Copy ONLY requirements first to leverage Docker layer caching (speeds up subsequent builds)
COPY requirements.txt .

# Best Practice: Chain apt-get update, install, pip install, and apt-get purge in a single RUN command. 
# This prevents the heavy build compilers from being saved in a cached Docker layer, keeping your final image size minimal.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libgomp1 \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . .

# Secure the container by switching away from the root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose the Flask port defined in app.py
EXPOSE 5001

# Execute the API using a production WSGI server with 4 worker processes
CMD ["gunicorn", "--workers=4", "--bind", "0.0.0.0:5001", "app:app"]
