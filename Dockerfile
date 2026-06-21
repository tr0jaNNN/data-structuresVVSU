# name=Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=flask_app.py
EXPOSE 5000

CMD ["python", "flask_app.py"]
