FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install Jinja2

EXPOSE 3000

CMD ["python3", "main.py"]
