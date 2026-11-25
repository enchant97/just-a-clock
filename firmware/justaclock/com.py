import sys
from asyncio import StreamReader

from micropython import const

from justaclock.config import (
    KEY_NET_HOSTNAME,
    KEY_NET_WLAN_PASSWORD,
    KEY_NET_WLAN_SSID,
    KEY_NTP_SERVER_1,
    KEY_NTP_SYNC_INTERVAL,
    KEY_TIME_24_HOUR,
    ConfigHandler,
)

_OP_GET = const("GET")
_OP_SET = const("SET")
_OP_HELP = const("HELP")

_ENABLE_ARGS = const(("TRUE", "YES", "ENABLE", "1"))
_DISABLE_ARGS = const(("FALSE", "NO", "DISABLE", "0"))


async def read_line_echo(reader):
    buf = bytearray()
    while True:
        ch = await reader.read(1)
        if not ch:
            return None
        if isinstance(ch, str):
            ch = ch.encode()
        c = ch[0]

        if c in (0x0D, 0x0A):  # Enter (CR or LF)
            sys.stdout.write("\r\n")
            return bytes(buf)
        if c in (0x08, 0x7F):  # Backspace / DEL
            if buf:
                buf = buf[:-1]
                sys.stdout.write("\x08 \x08")  # back, overwrite, back
        elif c >= 0x20:  # printable
            buf.append(c)
            # NOTE this only handles ASCII character input,
            #      UTF-8 multi-byte will not work
            sys.stdout.write(ch.decode())


class ComHandler:
    def __init__(
        self,
        config: ConfigHandler,
    ):
        self._config = config
        self._handlers = {
            "HELP": self._cmd_help,
            "FLUSH": self._cmd_flush,
            f"FLUSH.{_OP_HELP}": self._cmd_flush_help,
            "RELOAD": self._cmd_reload,
            f"RELOAD.{_OP_HELP}": self._cmd_reload_help,
            f"{KEY_NET_HOSTNAME}.{_OP_HELP}": self._cmd_help_net_hostname,
            f"{KEY_NET_HOSTNAME}.{_OP_GET}": self._cmd_get_net_hostname,
            f"{KEY_NET_HOSTNAME}.{_OP_SET}": self._cmd_set_net_hostname,
            f"{KEY_NET_WLAN_SSID}.{_OP_HELP}": self._cmd_help_net_wlan_ssid,
            f"{KEY_NET_WLAN_SSID}.{_OP_SET}": self._cmd_set_net_wlan_ssid,
            f"{KEY_NET_WLAN_PASSWORD}.{_OP_HELP}": self._cmd_help_net_wlan_pw,
            f"{KEY_NET_WLAN_PASSWORD}.{_OP_SET}": self._cmd_set_net_wlan_pw,
            f"{KEY_NTP_SERVER_1}.{_OP_HELP}": self._cmd_help_net_ntp,
            f"{KEY_NTP_SERVER_1}.{_OP_GET}": self._cmd_get_net_ntp,
            f"{KEY_NTP_SERVER_1}.{_OP_SET}": self._cmd_set_net_ntp,
            f"{KEY_NTP_SYNC_INTERVAL}.{_OP_HELP}": self._cmd_help_ntp_sync_interval,
            f"{KEY_NTP_SYNC_INTERVAL}.{_OP_GET}": self._cmd_get_ntp_sync_interval,
            f"{KEY_NTP_SYNC_INTERVAL}.{_OP_SET}": self._cmd_set_ntp_sync_interval,
            f"{KEY_TIME_24_HOUR}.{_OP_HELP}": self._cmd_help_time_24_hour,
            f"{KEY_TIME_24_HOUR}.{_OP_GET}": self._cmd_get_time_24_hour,
            f"{KEY_TIME_24_HOUR}.{_OP_SET}": self._cmd_set_time_24_hour,
        }

    async def run(self):
        reader = StreamReader(sys.stdin)

        while True:
            raw = await read_line_echo(reader)
            if raw is None:
                break

            line = raw.decode().strip()

            cmd_token, _, arg = line.partition(" ")
            cmd_token = cmd_token.upper()

            if cmd_token == "":
                continue

            if handler := self._handlers.get(cmd_token):
                handler(arg)
            else:
                print(f"ERR incorrect command '{cmd_token}'")

    def _cmd_help(self, arg: str):
        print("Available Commands:")
        for key in self._handlers:
            print(key)

    def _cmd_flush_help(self, arg: str):
        print("FLUSH:")
        print("Write current configuration values to flash")

    def _cmd_flush(self, arg: str):
        self._config.write()
        print("DATA WRITTEN")

    def _cmd_reload(self, arg: str):
        self._config.read()
        print("DATA READ")

    def _cmd_reload_help(self, arg: str):
        print("RELOAD:")
        print("Overwrite current configuration values from flash")

    def _cmd_help_net_hostname(self, arg: str):
        print(f"{KEY_NET_HOSTNAME}.{_OP_GET}:")
        print("Get the currently set hostname")
        print(f"{KEY_NET_HOSTNAME}.{_OP_SET}:")
        print("Set the device hostname")

    def _cmd_get_net_hostname(self, arg: str):
        hostname = self._config.net_hostname
        print(f"GET '{hostname}'")

    def _cmd_set_net_hostname(self, arg: str):
        self._config.net_hostname = arg
        print(f"SET '{arg}'")

    def _cmd_help_net_wlan_ssid(self, arg: str):
        print(f"{KEY_NET_WLAN_SSID}.{_OP_SET}:")
        print("Set the WIFI name that the device will connect to")

    def _cmd_set_net_wlan_ssid(self, arg: str):
        self._config.net_wlan_ssid = arg
        print(f"SET '{arg}'")

    def _cmd_help_net_wlan_pw(self, arg: str):
        print(f"{KEY_NET_WLAN_PASSWORD}.{_OP_SET}:")
        print("Set the WIFI password that the device will use to connect")

    def _cmd_set_net_wlan_pw(self, arg: str):
        self._config.net_wlan_password = arg
        print("SET 'redacted'")

    def _cmd_help_net_ntp(self, arg: str):
        print(f"{KEY_NTP_SERVER_1}.{_OP_GET}:")
        print("Get the currently set NTP server 1")
        print(f"{KEY_NTP_SERVER_1}.{_OP_SET}:")
        print("Set the NTP server 1")

    def _cmd_get_net_ntp(self, arg: str):
        ntp = self._config.ntp_server_1
        print(f"GET '{ntp}'")

    def _cmd_set_net_ntp(self, arg: str):
        self._config.ntp_server_1 = arg
        print(f"SET '{arg}'")

    def _cmd_help_ntp_sync_interval(self, arg: str):
        print(f"{KEY_NTP_SYNC_INTERVAL}.{_OP_GET}:")
        print("Get the sync interval in hours")
        print(f"{KEY_NTP_SYNC_INTERVAL}.{_OP_SET}:")
        print("Set the sync interval in hours, must be >= 1")

    def _cmd_get_ntp_sync_interval(self, arg: str):
        interval = self._config.ntp_sync_interval_hours
        print(f"GET '{interval}'")

    def _cmd_set_ntp_sync_interval(self, arg: str):
        self._config.ntp_sync_interval_hours = int(arg)
        print(f"SET '{arg}'")

    def _cmd_help_time_24_hour(self, arg: str):
        print(f"{KEY_TIME_24_HOUR}.{_OP_GET}:")
        print("Whether 24 hour time display is 12 hour or 24 hour")
        print(f"{KEY_TIME_24_HOUR}.{_OP_SET}:")
        print("Set 24 hour time display TRUE/FALSE")

    def _cmd_get_time_24_hour(self, arg: str):
        enabled = self._config.time_24_hour
        if enabled:
            print("GET '24 hour time'")
        else:
            print("GET '12 hour time'")

    def _cmd_set_time_24_hour(self, arg: str):
        arg = arg.upper()
        if arg in _ENABLE_ARGS:
            self._config.time_24_hour = True
            print("SET '24 hour time'")
        elif arg in _DISABLE_ARGS:
            self._config.time_24_hour = False
            print("SET '12 hour time'")
        else:
            print("ERR 'incorrect value'")
