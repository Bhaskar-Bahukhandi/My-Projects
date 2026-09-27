# Use the official, lightweight Python image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Prevent Python from writing .pyc files to disk and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only requirements first to cache the pip install step
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user for security (Enterprise Best Practice)
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose the ports that FastAPI and Streamlit will use
EXPOSE 8000 8501
