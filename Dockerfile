FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir . && useradd --create-home --uid 1000 app
COPY data ./data
USER app
CMD ["python", "-m", "jena_anomalies.cli", "report"]
