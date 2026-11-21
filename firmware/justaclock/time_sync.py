import asyncio
import time
import ntptime
import network

from justaclock.config import ConfigHandler


class TimeSyncHandler:
    STATE_UNSYNCED = "UNSYNCED"
    STATE_SYNCING = "SYNCING"
    STATE_SYNCED = "SYNCED"

    def __init__(self, config: ConfigHandler):
        self._config = config
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
            config = self._config
            network.hostname(config.net_hostname)
            ssid = config.net_wlan_ssid
            key = config.net_wlan_password
            if ssid is None or key is None:
                print("LOG wlan ssid or password not set")
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
        config = self._config
        while True:
            delay = 6 * 3600
            if await self._enable_net():
                try:
                    print("LOG starting time sync")
                    self._state = TimeSyncHandler.STATE_SYNCING
                    ntptime.host = config.ntp_server_1
                    ntptime.settime()
                    self._last_sync = time.time()
                    self._state = TimeSyncHandler.STATE_SYNCED
                    print("LOG time synced")
                except Exception:
                    self._state = TimeSyncHandler.STATE_UNSYNCED
                    delay = 600
                    print("LOG time sync failed")
                finally:
                    self._disable_net()

            await asyncio.sleep(delay)
