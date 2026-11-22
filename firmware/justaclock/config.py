import json
from micropython import const

from justaclock.constants import CONFIG_PATH, DEFAULT_HOSTNAME, DEFAULT_NTP_SERVER

KEY_NET_HOSTNAME = const("NET.HOSTNAME")
KEY_NET_WLAN_SSID = const("NET.WLAN.SSID")
KEY_NET_WLAN_PASSWORD = const("NET.WLAN.PASSWORD")
KEY_NTP_SERVER_1 = const("NTP.SERVER.1")


class ValidationError(Exception):
    pass


class ConfigHandler:
    def __init__(self) -> None:
        self._current = {}

    def read(self):
        try:
            with open(CONFIG_PATH, "r") as fo:
                self._current = json.load(fo)
        except Exception:
            pass

    def write(self):
        with open(CONFIG_PATH, "w") as fo:
            json.dump(self._current, fo)

    @property
    def net_hostname(self) -> str:
        return self._current.get(KEY_NET_HOSTNAME, DEFAULT_HOSTNAME)

    @net_hostname.setter
    def net_hostname(self, value: str | None):
        if value is not None and len(value) == 0:
            raise ValidationError("net_hostname must not be empty")
        self._current[KEY_NET_HOSTNAME] = value

    @property
    def net_wlan_ssid(self) -> str | None:
        return self._current.get(KEY_NET_WLAN_SSID)

    @net_wlan_ssid.setter
    def net_wlan_ssid(self, value: str | None):
        if value is not None and len(value) == 0:
            raise ValidationError("net_wlan_ssid must not be empty")
        self._current[KEY_NET_WLAN_SSID] = value

    @property
    def net_wlan_password(self) -> str | None:
        return self._current.get(KEY_NET_WLAN_PASSWORD)

    @net_wlan_password.setter
    def net_wlan_password(self, value: str | None):
        if value is not None and len(value) == 0:
            raise ValidationError("net_wlan_password must not be empty")
        self._current[KEY_NET_WLAN_PASSWORD] = value

    @property
    def ntp_server_1(self) -> str:
        return self._current.get(KEY_NTP_SERVER_1, DEFAULT_NTP_SERVER)

    @ntp_server_1.setter
    def ntp_server_1(self, value: str | None):
        if value is not None and len(value) == 0:
            raise ValidationError("ntp_server_1 must not be empty")
        self._current[KEY_NTP_SERVER_1] = value
