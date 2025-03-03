# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY ./requirements.txt /app/requirements.txt

# Install any dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the application code into the container
COPY . /app

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "litellm-main:app", "--host", "0.0.0.0", "--port", "8000"]