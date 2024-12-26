FROM arm64v8/python:3.11-slim-buster # Or correct base image for your pi

# Install bluez and bluez-tools
RUN apt-get update && apt-get install -y bluez bluez-tools

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the project folder into the container
COPY . .

# Install required libraries
RUN pip install --upgrade pip
RUN pip install bleak

CMD ["python", "control_heater.py"]