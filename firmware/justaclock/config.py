import json
from micropython import const

from justaclock.constants import CONFIG_PATH, DEFAULT_HOSTNAME, DEFAULT_NTP_SERVER

KEY_NET_HOSTNAME = const("NET.HOSTNAME")
KEY_NET_WLAN_SSID = const("NET.WLAN.SSID")
KEY_NET_WLAN_PASSWORD = const("NET.WLAN.PASSWORD")
KEY_NTP_SERVER_1 = const("NTP.SERVER.1")


class ConfigHandler:
    def __init__(self) -> None:
        self._current = {}
        self._fp = CONFIG_PATH

    def read(self):
        try:
            with open(self._fp, "r") as fo:
                self._current = json.load(fo)
        except Exception:
            pass

    def write(self):
        with open(self._fp, "w") as fo:
            json.dump(self._current, fo)

    def current(self) -> dict:
        return self._current

    @property
    def net_hostname(self) -> str:
        return self._current.get(KEY_NET_HOSTNAME, DEFAULT_HOSTNAME)

    @property
    def net_wlan_ssid(self) -> str | None:
        return self._current.get(KEY_NET_WLAN_SSID)

    @property
    def net_wlan_password(self) -> str | None:
        return self._current.get(KEY_NET_WLAN_PASSWORD)

    @property
    def ntp_server_1(self) -> str:
        return self._current.get(KEY_NTP_SERVER_1, DEFAULT_NTP_SERVER)
