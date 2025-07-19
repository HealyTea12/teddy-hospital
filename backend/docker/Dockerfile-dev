FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Install dependencies
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
# COPY . /app

# Run FastAPI with uvicorn
CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]
