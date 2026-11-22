import os

from micropython import const

from justaclock.constants import (
    DEFAULT_HOSTNAME,
    DEFAULT_NTP_SERVER,
)

CONFIG_PATH = const("/config.conf")

MAX_CONFIG_LINE_SIZE = const(256)

KEY_NET_HOSTNAME = const("NET.HOSTNAME")
KEY_NET_WLAN_SSID = const("NET.WLAN.SSID")
KEY_NET_WLAN_PASSWORD = const("NET.WLAN.PASSWORD")
KEY_NTP_SERVER_1 = const("NTP.SERVER.1")


def line_reader(stream, *, line_max: int, chunk_size: int):
    chunk = bytearray(chunk_size)
    cmv = memoryview(chunk)
    line = bytearray(line_max)
    lmv = memoryview(line)
    n = 0

    while True:
        got = stream.readinto(chunk)
        if not got:
            break
        start = 0
        while True:
            nl = chunk.find(b"\n", start, got)
            if nl < 0:
                line[n : n + got - start] = cmv[start:got]
                n += got - start
                break
            line[n : n + nl - start] = cmv[start:nl]
            yield lmv[: n + nl - start]
            n = 0
            start = nl + 1

    if n:
        yield lmv[:n]


class ValidationError(Exception):
    pass


class ConfigHandler:
    __slots__ = (
        "_get_handlers",
        "_net_hostname",
        "_net_wlan_password",
        "_net_wlan_ssid",
        "_ntp_server_1",
        "_set_handlers",
    )

    def __init__(self) -> None:
        self._set_handlers = {
            KEY_NET_HOSTNAME: lambda v: setattr(self, "net_hostname", v),
            KEY_NET_WLAN_SSID: lambda v: setattr(self, "net_wlan_ssid", v),
            KEY_NET_WLAN_PASSWORD: lambda v: setattr(self, "net_wlan_password", v),
            KEY_NTP_SERVER_1: lambda v: setattr(self, "ntp_server_1", v),
        }
        self._get_handlers = {
            KEY_NET_HOSTNAME: lambda: self.net_hostname,
            KEY_NET_WLAN_SSID: lambda: self.net_wlan_ssid,
            KEY_NET_WLAN_PASSWORD: lambda: self.net_wlan_password,
            KEY_NTP_SERVER_1: lambda: self.ntp_server_1,
        }

    def items(self):
        for k, handler in self._get_handlers.items():
            yield k, handler()

    def read(self):
        try:
            with open(CONFIG_PATH, "rb") as fo:
                handlers = self._set_handlers
                for raw_line in line_reader(
                    fo,
                    line_max=MAX_CONFIG_LINE_SIZE,
                    chunk_size=64,
                ):
                    line = bytes(raw_line).decode()
                    key, _, value = line.partition(" ")
                    if handler := handlers.get(key):
                        handler(value)

        except Exception:
            pass

    def write(self):
        tmp = f"{CONFIG_PATH}.tmp"
        lines = (f"{k} {v}\n" for k, v in self.items() if v is not None)
        with open(tmp, "w") as fo:
            fo.writelines(lines)
        os.remove(CONFIG_PATH)
        os.rename(tmp, CONFIG_PATH)

    @property
    def net_hostname(self) -> str:
        return self._net_hostname or DEFAULT_HOSTNAME

    @net_hostname.setter
    def net_hostname(self, value: str | None):
        if value is not None and len(value) == 0:
            msg = "net_hostname must not be empty"
            raise ValidationError(msg)
        self._net_hostname = value

    @property
    def net_wlan_ssid(self) -> str | None:
        return self._net_wlan_ssid

    @net_wlan_ssid.setter
    def net_wlan_ssid(self, value: str | None):
        if value is not None and len(value) == 0:
            msg = "net_wlan_ssid must not be empty"
            raise ValidationError(msg)
        self._net_wlan_ssid = value

    @property
    def net_wlan_password(self) -> str | None:
        return self._net_wlan_password

    @net_wlan_password.setter
    def net_wlan_password(self, value: str | None):
        if value is not None and len(value) == 0:
            msg = "net_wlan_password must not be empty"
            raise ValidationError(msg)
        self._net_wlan_password = value

    @property
    def ntp_server_1(self) -> str:
        return self._ntp_server_1 or DEFAULT_NTP_SERVER

    @ntp_server_1.setter
    def ntp_server_1(self, value: str | None):
        if value is not None and len(value) == 0:
            msg = "ntp_server_1 must not be empty"
            raise ValidationError(msg)
        self._ntp_server_1 = value
