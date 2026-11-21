import json

from justaclock.constants import CONFIG_PATH


class ConfigHandler:
    def __init__(self) -> None:
        self._current = {}
        self._fp = CONFIG_PATH

    def restore_defaults(self):
        self._current["ssid"] = None
        self._current["key"] = None
        self._current["hostname"] = None
        self._current["ntp"] = "pool.ntp.org"

    def read(self):
        try:
            self.restore_defaults()
            with open(self._fp, "r") as fo:
                self._current = json.load(fo)
        except Exception:
            pass

    def write(self):
        with open(self._fp, "w") as fo:
            json.dump(self._current, fo)

    def current(self) -> dict:
        return self._current
