FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y cmake g++ libgmp-dev && \
    pip install --upgrade pip

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]