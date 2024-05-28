netpick is a toolkit for network recon and MITM attacks.

## Features

- Host discovery via passive sniffing or active probing.
- LAN recon through OS detection and port scanning.
- Man-in-the-Middle attack capabilities using ARP spoofing.
- Event-driven communication with the [web UI](https://github.com/eduard-cc/half-diamond-web) via WebSocket.

![web UI screenshot](https://github.com/eduard-cc/netpick-api/blob/main/docs/media/screenshot.png?raw=true)

## Installation

### Using Docker

The easiest way to install netpick along with its dependencies and the web UI is to use Docker.

#### 1. Pull the image:

```bash
docker pull eduardcc/netpick
```

#### 2. Run a container from the image:

```bash
docker run --privileged --net=host eduardcc/netpick
```

The web UI will run at `http://localhost:3000` and the API at `http://localhost:8000`.

### Manually compiling from source

To compile from source, make sure that you have Python 3.10 or above installed.

#### 1. Install the system dependencies

#### libpcap/Npcap

netpick uses [Scapy](https://scapy.net/) for packet manipulation. Depending on your operating system, install one of the following:

- **Linux/MacOS**: Install [libpcap](https://www.tcpdump.org/). Refer to the [Scapy documentation](https://scapy.readthedocs.io/en/latest/installation.html#platform-specific-instructions) for more details.
- **Windows**: Install [Npcap](https://npcap.com/).

#### Nmap

netpick also requires [Nmap](https://nmap.org/) to be installed locally. Download and install it from [here](https://nmap.org/download.html).

#### 2. Clone the repository

```bash
git clone https://github.com/eduard-cc/netpick-api.git
cd netpick-api
```

#### 3. Install the Python requirements

Create and activate the virtual environment:

```bash
python3 -m venv env
source env/bin/activate  # on Windows, use env\Scripts\activate
```

Install the requirements:

```bash
pip install -r requirements.txt
```

#### 4. Start the server

```bash
cd src
uvicorn main:app # for development, add --reload to enable auto-reload.
```

The API will start at `http://127.0.0.1:8000/`. To build and run the [web UI](https://github.com/eduard-cc/half-diamond-web), refer to its installation guide.

**Note**: The API requires elevated privileges to function properly.

## Swagger UI documentation

You can view the OpenAPI specification of this API [here](https://eduard-cc.github.io/netpick-api/).
