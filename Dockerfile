# Use a slim Python base image
FROM docker.io/python:3.12-alpine

# Set work directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY src/ ./src/
COPY README.md ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only main

# Expose port
EXPOSE 8000

# Run FastAPI using Uvicorn
CMD ["uvicorn", "ip5_poc.main:app", "--host", "0.0.0.0", "--port", "8000"]
