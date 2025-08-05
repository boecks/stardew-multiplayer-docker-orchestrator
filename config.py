from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# Configuration values

DOCKER_CONTAINER_NAME = "stardew"
UDP_PORT = 24642
HOST_ONLY_TIMEOUT = 60
IDLE_TIMEOUT = 60  # seconds
BOOT_WAIT = 15      # seconds to wait after container starts

# SMAPI log location (either on host or inside container)
LOG_PATH = "/config/xdg/config/StardewValley/ErrorLogs/SMAPI-latest.txt"

# Use 'docker exec' to read logs from inside container?
# Set to False if you mount the log to the host and want to read directly
USE_DOCKER_EXEC_LOGS = True
