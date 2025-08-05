import subprocess
import config
from utils import log

def is_container_running():
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", config.DOCKER_CONTAINER_NAME],
        capture_output=True, text=True
    )
    return result.stdout.strip() == "true"

def start_container():
    log("[docker] Starting container...")
    try:
        result = subprocess.run(
            ["docker", "start", config.DOCKER_CONTAINER_NAME],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            log(f"[docker] Container started: {result.stdout.strip()}")
        else:
            log(f"[docker] Error starting container: {result.stderr.strip()}")
    except Exception as e:
        log(f"[docker] Exception starting container: {e}")

def stop_container():
    log("[docker] Stopping container...")
    try:
        result = subprocess.run(
            ["docker", "stop", config.DOCKER_CONTAINER_NAME],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            log(f"[docker] Container stopped: {result.stdout.strip()}")
        else:
            log(f"[docker] Error stopping container: {result.stderr.strip()}")
    except Exception as e:
        log(f"[docker] Exception stopping container: {e}")
