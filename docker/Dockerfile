FROM python:3.11 as builder

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install -y bash dos2unix git

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY ./src /app

COPY ./docker/shell /app/shell

RUN chmod +x /app/shell/entrypoint.sh

RUN find /app/ -type f -exec dos2unix {} \;

EXPOSE 8000

CMD ["/app/shell/entrypoint.sh"]
