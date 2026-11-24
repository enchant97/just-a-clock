import sys
from asyncio import StreamReader

from micropython import const

from justaclock.config import (
    KEY_NET_HOSTNAME,
    KEY_NET_WLAN_PASSWORD,
    KEY_NET_WLAN_SSID,
    KEY_NTP_SERVER_1,
    KEY_NTP_SYNC_INTERVAL,
    ConfigHandler,
)

_OP_GET = const("GET")
_OP_SET = const("SET")


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
            "FLUSH": self._cmd_flush_net,
            "RELOAD": self._cmd_reload_net,
            f"{KEY_NET_HOSTNAME}.{_OP_GET}": self._cmd_get_net_hostname,
            f"{KEY_NET_HOSTNAME}.{_OP_SET}": self._cmd_set_net_hostname,
            f"{KEY_NET_WLAN_SSID}.{_OP_SET}": self._cmd_set_net_wlan_ssid,
            f"{KEY_NET_WLAN_PASSWORD}.{_OP_SET}": self._cmd_set_net_wlan_pw,
            f"{KEY_NTP_SERVER_1}.{_OP_GET}": self._cmd_get_net_ntp,
            f"{KEY_NTP_SERVER_1}.{_OP_SET}": self._cmd_set_net_ntp,
            f"{KEY_NTP_SYNC_INTERVAL}.{_OP_GET}": self._cmd_get_ntp_sync_interval,
            f"{KEY_NTP_SYNC_INTERVAL}.{_OP_SET}": self._cmd_set_ntp_sync_interval,
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

    def _cmd_flush_net(self, arg: str):
        self._config.write()
        print("DATA WRITTEN")

    def _cmd_reload_net(self, arg: str):
        self._config.read()
        print("DATA READ")

    def _cmd_get_net_hostname(self, arg: str):
        hostname = self._config.net_hostname
        print(f"GET '{hostname}'")

    def _cmd_set_net_hostname(self, arg: str):
        self._config.net_hostname = arg
        print(f"SET '{arg}'")

    def _cmd_set_net_wlan_ssid(self, arg: str):
        self._config.net_wlan_ssid = arg
        print(f"SET '{arg}'")

    def _cmd_set_net_wlan_pw(self, arg: str):
        self._config.net_wlan_password = arg
        print("SET 'redacted'")

    def _cmd_get_net_ntp(self, arg: str):
        ntp = self._config.ntp_server_1
        print(f"GET '{ntp}'")

    def _cmd_set_net_ntp(self, arg: str):
        self._config.ntp_server_1 = arg
        print(f"SET '{arg}'")

    def _cmd_get_ntp_sync_interval(self, arg: str):
        interval = self._config.ntp_sync_interval
        print(f"GET '{interval}'")

    def _cmd_set_ntp_sync_interval(self, arg: str):
        self._config.ntp_sync_interval = int(arg)
        print(f"SET '{arg}'")
