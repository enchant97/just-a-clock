import sys
from asyncio import StreamReader

from firmware.justaclock.config import (
    KEY_NET_HOSTNAME,
    KEY_NET_WLAN_PASSWORD,
    KEY_NET_WLAN_SSID,
    KEY_NTP_SERVER_1,
    ConfigHandler,
)


class ComHandler:
    def __init__(
        self,
        config: ConfigHandler,
    ):
        self._config = config
        self._handlers = {
            "FLUSH": self._cmd_flush_net,
            "RELOAD": self._cmd_reload_net,
            f"{KEY_NET_HOSTNAME}.GET": self._cmd_get_net_hostname,
            f"{KEY_NET_HOSTNAME}.SET": self._cmd_set_net_hostname,
            f"{KEY_NET_WLAN_SSID}.SET": self._cmd_set_net_wlan_ssid,
            f"{KEY_NET_WLAN_PASSWORD}.SET": self._cmd_set_net_wlan_pw,
            f"{KEY_NTP_SERVER_1}.GET": self._cmd_get_net_ntp,
            f"{KEY_NTP_SERVER_1}.SET": self._cmd_set_net_ntp,
        }

    async def run(self):
        reader = StreamReader(sys.stdin)

        while True:
            raw = await reader.readline()
            if not raw:
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
