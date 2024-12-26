FROM python:3.11-slim-buster

# Install bash
RUN apt-get update && apt-get install -y bash

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the project folder into the container
COPY . .

# Install required libraries
RUN pip install --upgrade pip
RUN pip install bleak
RUN pip install asyncio

# Set bash as the entrypoint
ENTRYPOINT ["/bin/bash"] # or ["bash"]

# Define a command to run your script as CMD (optional)s
#CMD ["python", "control_heater.py"]
