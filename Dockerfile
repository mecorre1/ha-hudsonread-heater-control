FROM arm64v8/python:3.11-slim-buster

# Install bluez and bluez-tools
RUN apt-get update && apt-get install -y bluez bluez-tools

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the project folder into the container
COPY . .

# Install required librariess
RUN pip install --upgrade pip
RUN pip install bleak
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Start Flask API
CMD ["python", "api.py"]







