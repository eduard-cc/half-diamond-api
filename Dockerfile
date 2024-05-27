# build API
FROM python:3.9 as api-builder

WORKDIR /code

# system dependencies
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    nmap

# python dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src

# build web UI
FROM node:18-alpine as web-builder

WORKDIR /app

RUN git clone https://github.com/eduard-cc/netpick-web.git .

RUN npm install
RUN npm run build

# final stage
FROM python:3.9

WORKDIR /app

COPY --from=api-builder /code/src /app/api

COPY --from=web-builder /app/build /app/web

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000 3000

CMD ["/entrypoint.sh"]