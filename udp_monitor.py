import asyncio
from config import log, UDP_PORT

async def wait_for_packet():
    log(f"[udp] Listening on UDP port {UDP_PORT}")
    proc = await asyncio.create_subprocess_exec(
        'tcpdump', '-l', '-n', '-i', 'any', 'udp', 'port', str(UDP_PORT), '-c', '1',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        await proc.wait()
    except asyncio.CancelledError:
        log("[udp] Cancelled, terminating tcpdump subprocess.")
        proc.terminate()
        await proc.wait()
        raise
    log("[udp] UDP packet detected, proceeding.")
