import asyncio
from container_control import is_container_running, start_container
from udp_monitor import wait_for_packet
from smapi_monitor import start_monitoring_for_idle_shutdown
import config
from utils import log

async def main():
    # show current config and start
    config.show_config()
    log("Starting up...")

    while True:
        if not is_container_running():
            log("[main] Waiting for incoming connection (UDP)...")
            await wait_for_packet()
            start_container()
            await asyncio.sleep(config.BOOT_WAIT)

        # Container is running, delegate to smapi_monitor
        await start_monitoring_for_idle_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Interrupted. Exiting.")
