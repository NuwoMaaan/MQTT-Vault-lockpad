FROM python:3.14-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir requests python-dotenv

COPY . /app/emqx

WORKDIR /app

CMD ["python", "-m", "emqx.init"]