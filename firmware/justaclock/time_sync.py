import asyncio
import time
import ntptime
import network

from firmware.justaclock.config import NetworkConfigHandler, SystemConfigHandler


class TimeSyncHandler:
    STATE_UNSYNCED = "UNSYNCED"
    STATE_SYNCING = "SYNCING"
    STATE_SYNCED = "SYNCED"

    def __init__(
        self,
        network_config: NetworkConfigHandler,
        system_config: SystemConfigHandler,
    ):
        self._network_config = network_config
        self._system_config = system_config
        self._last_sync = None
        self._state = TimeSyncHandler.STATE_UNSYNCED
        self._wlan = network.WLAN(network.STA_IF)

    def last_sync(self) -> float | None:
        return self._last_sync

    def state(self):
        return self._state

    async def _enable_net(self) -> bool:
        wlan = self._wlan
        wlan.active(True)

        if not wlan.isconnected():
            wlan.config(pm=network.WLAN.PM_PERFORMANCE)
            config = self._network_config.current()
            if hostname := config.get("hostname"):
                network.hostname(hostname)
            else:
                network.hostname("justaclock")
            ssid = config.get("ssid")
            key = config.get("key")
            if ssid is None or key is None:
                print("LOG wlan ssid or key not set")
                return False
            wlan.connect(
                ssid,
                key,
            )
            for _ in range(20):
                if wlan.isconnected():
                    break
                await asyncio.sleep(1)

        if not wlan.isconnected():
            wlan.disconnect()
            wlan.active(False)
            print("LOG wlan failed to connect")
            return False
        return True

    def _disable_net(self):
        wlan = self._wlan
        if wlan.active():
            wlan.disconnect()
            wlan.active(False)

    async def run(self):
        while True:
            delay = 6 * 3600
            if self._enable_net():
                try:
                    self._state = TimeSyncHandler.STATE_SYNCING
                    ntptime.settime()
                    self._last_sync = time.time()
                    self._state = TimeSyncHandler.STATE_SYNCED
                except Exception:
                    self._state = TimeSyncHandler.STATE_UNSYNCED
                    delay = 600
                finally:
                    self._disable_net()

            await asyncio.sleep(delay)
