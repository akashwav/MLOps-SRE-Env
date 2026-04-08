FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything into the container
COPY . .

# Run the FastAPI server on port 7860 (Hugging Face default)
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]