FROM python:3.10

# Set the working directory in the container
WORKDIR /API_data

# Copy the root directory (combine) into the container
COPY . /API_data

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI default port
EXPOSE 8000

# Set environment variables
# ENV PYTHONUNBUFFERED=1

# Run the FastAPI application
CMD ["uvicorn", "API_data:app", "--host", "0.0.0.0", "--port", "8000" ]
