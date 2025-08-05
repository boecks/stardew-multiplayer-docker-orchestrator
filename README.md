# Stardew Valley Dedicated Server Auto-Control Script

## Overview

This repository contains a Python script designed to manage your Stardew Valley dedicated server efficiently. It automatically starts the server when a player attempts to join and stops it after a configurable idle timeout, reducing unnecessary power consumption.

---

## Why This Repo Exists

After purchasing multiple Stardew Valley licenses to enjoy indie gaming with friends on my local LAN, I initially hosted the dedicated server on my PC. However, this setup lacked flexibility.

I then moved the server to a Proxmox cluster using the excellent [stardew-multiplayer-docker](https://github.com/cavazos-apps/stardew-multiplayer-docker) project. While playing, I noticed a 30W increase in my rack's power draw due to the server running idle — the Stardew Valley server consumed both of the 2 vCPUs on my Ryzen 5 5600, even when no players were online.

To optimize power usage, I needed the server to shut down when not in use and start only on demand—without manually interacting with Proxmox or SSH every time.

This script automates that process.

---

## How It Works

- The script is modular, with `main.py` orchestrating the workflow.
- **UDP Monitor Module**: Listens on UDP port `24642` (Stardew Valley's default port). When a packet from a client arrives (indicating a player trying to join), the script starts the server container.
- Players initially need to attempt to join the LAN server twice: the first attempt wakes the server, and within seconds, the server is ready to accept connections.
- Once the container is running, the script switches to monitoring the SMAPI logs inside the container.
- These logs indicate player activity:
  - If only the host is online, or if players have left, the script tracks idle time.
  - When no players remain after a configurable timeout, the server container is automatically stopped.

---

## Features

- Automatic server startup on player connection attempt.
- Automatic server shutdown after configurable idle timeout.
- Transparent to players: minimal wait time before joining.
- Reduces power consumption by avoiding idle server runtime.

---

## Requirements & Notes

- Written in vanilla Python 3 (tested on Ubuntu 24.04).
- Requires `tcpdump` installed on the host for UDP packet monitoring.
- The service needs appropriate privileges to run `tcpdump`:
  - Running manually as `root` or with `sudo` works out of the box.
  - When containerized, the container must run as root or have appropriate capabilities (`CAP_NET_RAW`, `CAP_NET_ADMIN`) granted.
  - *In a future version there may be another, less privileged method to detect user demand to start the container.*
- The script controls the Stardew Valley server container via the Docker socket:
  - Needs access to the Docker socket (`/var/run/docker.sock`) to start/stop the container.
  - Uses `docker exec` to read SMAPI logs inside the container.
- Configuration is currently managed via `config.py`. Environment variable support for configuration is planned to improve Docker compatibility.

---

## Configuration

Copy `sample.env` to `.env` and adjust as needed:

```sh
cp sample.env .env
```

---

## Usage

Run the script manually:

```bash
sudo python3 main.py
# or if you are root:
python3 main.py
```
