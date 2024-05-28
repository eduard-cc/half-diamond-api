# build web UI
FROM node:18-alpine as web-builder

WORKDIR /web

RUN apk add --no-cache git
RUN git clone https://github.com/eduard-cc/netpick-web.git .

RUN npm install
RUN npm run build

FROM nikolaik/python-nodejs:python3.11-nodejs18

# system dependencies
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    nmap

WORKDIR /app

COPY ./src /app/api/src
COPY ./requirements.txt /app/api

# python dependencies
RUN pip install --no-cache-dir --upgrade -r /app/api/requirements.txt

COPY --from=web-builder /web /app/web

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000 3000

CMD ["/entrypoint.sh"]