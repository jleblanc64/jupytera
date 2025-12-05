# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and the build script
COPY app.py .
COPY script_build.sh .
COPY script_empty_repo.sh .

# Expose the port the Flask app runs on
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]