FROM python:3.12-slim

WORKDIR /app

# Copy dependency file first so this layer is cached and isn't re-run
# every time application code changes.
COPY requirements.txt .

# Upgrade pip, then install dependencies.
# --default-timeout and --retries make the install resilient to a flaky
# connection instead of dying with BrokenPipeError partway through a
# multi-hundred-MB download.
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --default-timeout=120 --retries 10 -r requirements.txt

# Copy application code
COPY . .

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
