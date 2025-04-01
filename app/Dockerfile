FROM python:3.11-slim

# Set Working Directory
WORKDIR .

# Install Dependency
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy App source
COPY . .

# FastAPI 앱 실행 (Uvicorn 사용)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
