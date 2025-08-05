import os
from dotenv import load_dotenv

# Load .env.local first, fallback to .env
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
elif os.path.exists(".env"):
    load_dotenv(".env")

# --- Helper functions ---
def get_env(key, default=None, cast=str):
    val = os.getenv(key, default)
    try:
        return cast(val)
    except (ValueError, TypeError):
        return default

def str_to_bool(val):
    return str(val).lower() in ("1", "true", "yes", "on")

# --- Config values from env or defaults ---
DOCKER_CONTAINER_NAME = get_env("SDV_CONTAINER_NAME", "stardew")
UDP_PORT = get_env("SDV_UDP_PORT", 24642, int)
HOST_ONLY_TIMEOUT = get_env("SDV_HOST_ONLY_TIMEOUT", 600, int)
IDLE_TIMEOUT = get_env("SDV_IDLE_TIMEOUT", 300, int)
BOOT_WAIT = get_env("SDV_BOOT_WAIT", 15, int)
LOG_PATH = get_env("SDV_LOG_PATH", "/config/xdg/config/StardewValley/ErrorLogs/SMAPI-latest.txt")
USE_DOCKER_EXEC_LOGS = get_env("SDV_USE_DOCKER_EXEC_LOGS", True, str_to_bool)

# --- Optional: print config on startup ---
def show_config():
    from utils import log
    log("Loaded configuration:")
    log(f"  Container:           {DOCKER_CONTAINER_NAME}")
    log(f"  UDP Port:            {UDP_PORT}")
    log(f"  Host-only timeout:   {HOST_ONLY_TIMEOUT}s")
    log(f"  Idle timeout:        {IDLE_TIMEOUT}s")
    log(f"  Boot wait:           {BOOT_WAIT}s")
    log(f"  Log path:            {LOG_PATH}")
    log(f"  Use docker exec log: {USE_DOCKER_EXEC_LOGS}")
