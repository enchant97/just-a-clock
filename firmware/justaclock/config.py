import json

from justaclock.constants import NETWORK_CONFIG_PATH, SYSTEM_CONFIG_PATH


class ConfigHandler:
    def __init__(self, fp: str) -> None:
        self._current = {}
        self._fp = fp

    def read(self):
        with open(self._fp, "r") as fo:
            self.current = json.load(fo)

    def write(self):
        with open(self._fp, "w") as fo:
            json.dump(self.current, fo)

    def current(self):
        return self._current


class SystemConfigHandler(ConfigHandler):
    def __init__(self):
        super().__init__(SYSTEM_CONFIG_PATH)


class NetworkConfigHandler(ConfigHandler):
    def __init__(self):
        super().__init__(NETWORK_CONFIG_PATH)
