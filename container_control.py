import asyncio
import docker
import config
from utils import log
import subprocess  # Still needed for log reading, for now

# Initialize Docker client
client = docker.from_env()

def is_container_running():
    try:
        container = client.containers.get(config.DOCKER_CONTAINER_NAME)
        return container.status == "running"
    except docker.errors.NotFound:
        log(f"[docker] Container '{config.DOCKER_CONTAINER_NAME}' not found.")
    except Exception as e:
        log(f"[docker] Error checking container status: {e}")
    return False

def start_container():
    log("[docker] Starting container...")
    try:
        container = client.containers.get(config.DOCKER_CONTAINER_NAME)
        container.start()
        log("[docker] Container started.")
    except docker.errors.NotFound:
        log(f"[docker] Container '{config.DOCKER_CONTAINER_NAME}' not found.")
    except Exception as e:
        log(f"[docker] Exception starting container: {e}")

def stop_container():
    log("[docker] Stopping container...")
    try:
        container = client.containers.get(config.DOCKER_CONTAINER_NAME)
        container.stop()
        log("[docker] Container stopped.")
    except docker.errors.NotFound:
        log(f"[docker] Container '{config.DOCKER_CONTAINER_NAME}' not found.")
    except Exception as e:
        log(f"[docker] Exception stopping container: {e}")

# --- Still using subprocess for log reading (for now) ---

async def read_full_log_lines():
    cmd = ["docker", "exec", config.DOCKER_CONTAINER_NAME, "cat", config.LOG_PATH]
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
    lines = []
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        lines.append(line.decode(errors='ignore').rstrip('\n'))
    await proc.wait()
    return lines

async def tail_log_lines():
    cmd = ["docker", "exec", config.DOCKER_CONTAINER_NAME, "tail", "-n", "0", "-F", config.LOG_PATH]
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
    try:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            yield line.decode(errors='ignore').rstrip('\n')
    except asyncio.CancelledError:
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=5)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
        raise
