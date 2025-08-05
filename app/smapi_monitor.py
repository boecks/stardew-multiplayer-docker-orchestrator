import asyncio
import re
import config
from container_control import stop_container, is_container_running
from utils import log

class SmapiMonitor:
    def __init__(self):
        self.connected_players = set()
        self.host_only_timer = None
        self.idle_timer = None
        self.host_only_start_detected = False

    async def stop_container_gracefully(self, reason):
        log(f"[smapi] {reason} timeout reached. Stopping container.")
        stop_container()

    def cancel_timers(self):
        if self.host_only_timer:
            self.host_only_timer.cancel()
            self.host_only_timer = None
        if self.idle_timer:
            self.idle_timer.cancel()
            self.idle_timer = None

    async def schedule_timer(self, delay, reason):
        await asyncio.sleep(delay)
        await self.stop_container_gracefully(reason)

    def schedule_host_only_timer(self, loop):
        if self.host_only_timer:
            return
        log("[smapi] Scheduling host-only shutdown timer.")
        self.host_only_timer = loop.create_task(self.schedule_timer(config.HOST_ONLY_TIMEOUT, "Host-only"))

    def schedule_idle_timer(self, loop):
        if self.idle_timer:
            return
        log("[smapi] Scheduling idle shutdown timer.")
        self.idle_timer = loop.create_task(self.schedule_timer(config.IDLE_TIMEOUT, "Idle"))

    def cancel_host_only_timer(self):
        if self.host_only_timer:
            log("[smapi] Cancelling host-only shutdown timer.")
            self.host_only_timer.cancel()
            self.host_only_timer = None

    def cancel_idle_timer(self):
        if self.idle_timer:
            log("[smapi] Cancelling idle shutdown timer.")
            self.idle_timer.cancel()
            self.idle_timer = None

    def process_line(self, line, loop):
        line = line.strip()
        # Debug log of every line (can comment out if noisy)
        #log(f"[smapi debug] {line}")

        # Detect host-only startup
        if re.search(r"Context: loaded save .*Main player with 1 player online", line):
            log("[smapi] Detected host-only startup.")
            self.host_only_start_detected = True
            if len(self.connected_players) == 0:
                self.schedule_host_only_timer(loop)

        # Player joins (farmhand approved)
        m_join = re.search(r"Approved request for farmhand (-?\d+)", line)
        if m_join:
            player_id = m_join.group(1)
            if player_id not in self.connected_players:
                self.connected_players.add(player_id)
                log(f"[smapi] Player joined: {player_id}")
                # Cancel timers on player join
                self.cancel_host_only_timer()
                self.cancel_idle_timer()
                # If host_only_start_detected was True, now false because players joined
                self.host_only_start_detected = False
            return

        # Player quit
        m_quit = re.search(r"Player quit: (-?\d+)", line)
        if m_quit:
            player_id = m_quit.group(1)
            if player_id in self.connected_players:
                self.connected_players.remove(player_id)
                log(f"[smapi] Player left: {player_id}")
                if len(self.connected_players) == 0:
                    log("[smapi] No more remote players connected.")
                    self.schedule_idle_timer(loop)
            return

        # Backup detection from high-level game state
        if "Game has only local clients" in line:
            log("[smapi] Game reports only local clients.")
            if len(self.connected_players) == 0:
                self.schedule_idle_timer(loop)
            return

        if "Game has remote clients" in line:
            log("[smapi] Game reports remote clients connected.")
            self.cancel_idle_timer()
            self.cancel_host_only_timer()
            self.host_only_start_detected = False
            return

async def read_full_log_and_return_lines():
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

async def start_monitoring_for_idle_shutdown():
    monitor = SmapiMonitor()
    loop = asyncio.get_running_loop()

    log("[smapi] Reading full existing log for initial state...")
    initial_lines = await read_full_log_and_return_lines()
    for line in initial_lines:
        monitor.process_line(line, loop)

    log("[smapi] Starting live log tail monitoring...")
    try:
        async for line in tail_log_lines():
            if not is_container_running():
                log("[smapi] Container stopped externally. Exiting monitor.")
                break
            monitor.process_line(line, loop)
    except asyncio.CancelledError:
        log("[smapi] Monitoring cancelled, shutting down tail subprocess.")
        # tail_log_lines will handle subprocess termination
        raise

async def main():
    try:
        await start_monitoring_for_idle_shutdown()
    except KeyboardInterrupt:
        log("[smapi] Interrupted by user. Exiting.")
