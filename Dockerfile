FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["bash", "-c", "python tests/pre_test_migration.py &&  python ingest_mongodb.py && python tests/post_test_migration.py && python scripts/reporting_time.py  && python scripts/schema_validator.py"]
