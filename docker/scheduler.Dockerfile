FROM python:3.12-slim

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/scheduler.txt

COPY . .

CMD ["python", "-m", "scheduler.main"]
