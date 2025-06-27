# Dockerfile for FastAPI backend
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY pc-builder/pc-builder-backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY pc-builder/pc-builder-backend/ .
# Copy data-results and cdn-images from monorepo root
COPY data-results ./data-results
COPY cdn-images ./cdn-images

# Expose port
EXPOSE 8000

# Run FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
