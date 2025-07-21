FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (including poppler-utils for PDF to image conversion)
RUN apt-get update && \
    apt-get install -y poppler-utils gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose the ports for the applications
EXPOSE 8501 8502 8503

# Copy the script to launch multiple apps
COPY run_apps.sh .

# Make the script executable
RUN chmod +x run_apps.sh

# Default command to run the script
CMD ["./run_apps.sh"]
