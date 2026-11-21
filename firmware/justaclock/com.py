import sys
from asyncio import StreamReader

from justaclock.config import NetworkConfigHandler, SystemConfigHandler


class ComHandler:
    def __init__(
        self,
        network_config: NetworkConfigHandler,
        system_config: SystemConfigHandler,
    ):
        self._network_config = network_config
        self._system_config = system_config
        self._handlers = {
            "NET.SSID.SET": self._cmd_set_net_ssid,
            "NET.KEY.SET": self._cmd_set_net_key,
            "NET.HOSTNAME.GET": self._cmd_get_net_hostname,
            "NET.HOSTNAME.SET": self._cmd_set_net_hostname,
            "NET.NTP.GET": self._cmd_get_net_ntp,
            "NET.NTP.SET": self._cmd_set_net_ntp,
            "NET.FLUSH": self._cmd_flush_net,
            "NET.RELOAD": self._cmd_reload_net,
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
        self._network_config.write()
        print("DATA WRITTEN")

    def _cmd_reload_net(self, arg: str):
        self._network_config.read()
        print("DATA READ")

    def _cmd_set_net_ssid(self, arg: str):
        self._network_config.current()["ssid"] = arg
        print("SET '{arg}'")

    def _cmd_set_net_key(self, arg: str):
        self._network_config.current()["key"] = arg
        print("SET 'redacted'")

    def _cmd_get_net_hostname(self, arg: str):
        hostname = self._network_config.current()["hostname"]
        print(f"GET '{hostname}'")

    def _cmd_set_net_hostname(self, arg: str):
        self._network_config.current()["hostname"] = arg
        print(f"SET '{arg}'")

    def _cmd_get_net_ntp(self, arg: str):
        ntp = self._network_config.current()["ntp"]
        print(f"GET '{ntp}'")

    def _cmd_set_net_ntp(self, arg: str):
        self._network_config.current()["ntp"] = arg
        print(f"SET '{arg}'")
