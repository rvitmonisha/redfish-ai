import asyncio

from app.database import save_telemetry
from app.state import telemetry


class MonitoringService:
    def __init__(self, interval=10):
        self.interval = interval
        self.collector = telemetry
        self.running = False

    async def start(self):
        self.running = True

        while self.running:
            try:
                data = self.collector.collect()
                save_telemetry(data)
            except Exception as exc:
                print(f"Telemetry collection failed: {exc}")

            await asyncio.sleep(self.interval)

    def stop(self):
        self.running = False