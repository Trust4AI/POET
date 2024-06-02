FROM python:3.11 as builder

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY ./src /app

COPY ./docker/shell /app/shell

RUN chmod +x /app/shell/entrypoint.sh

EXPOSE 8000

CMD ["/app/shell/entrypoint.sh"]
