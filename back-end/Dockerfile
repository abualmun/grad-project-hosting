FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create static folder if it doesn't exist
RUN mkdir -p static

# Copy frontend files to static folder
COPY index.html static/
COPY app.js static/

# Initialize the database
RUN python init_db.py

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]