# Use the official Python slim image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install Python dependencies
# RUN pip install "mcp[cli]"
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000
CMD ["python", "server.py"]