# Dockerfile for FastAPI backend
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app ./app

# Create directory and copy local CSV file as fallback
RUN mkdir -p /workspace/data-results
COPY graphics-cards.csv /workspace/data-results/graphics-cards.csv

# Expose port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
