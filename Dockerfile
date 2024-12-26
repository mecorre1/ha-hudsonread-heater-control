# Use a lightweight Python image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the project folder into the container
COPY . .

# Install required libraries
RUN pip install --upgrade pip
RUN pip install bleak
RUN pip install asyncio

# Define the command to run your script when the container starts
CMD ["python", "scan_bluetooth.py"]
