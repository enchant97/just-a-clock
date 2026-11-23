import asyncio

import network
import ntptime

from justaclock.config import ConfigHandler
from justaclock.constants import TIME_SYNC_INTERVAL_SECS
from justaclock.state import GlobalState


class TimeSyncHandler:
    def __init__(self, config: ConfigHandler, state: GlobalState):
        self._config = config
        self._state = state
        self._wlan = network.WLAN(network.STA_IF)

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
            delay = TIME_SYNC_INTERVAL_SECS
            if await self._enable_net():
                try:
                    print("LOG starting time sync")
                    self._state.set_syncing()
                    ntptime.host = config.ntp_server_1
                    ntptime.settime()
                    self._state.set_synced()
                    print("LOG time synced")
                except Exception:  # noqa: BLE001 - ntptime may raise an exception without specific type
                    self._state.set_syncing(False)
                    delay = 600
                    print("LOG time sync failed")
                finally:
                    self._disable_net()

            await asyncio.sleep(delay)
