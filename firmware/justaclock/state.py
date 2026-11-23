import time

from micropython import const

from justaclock.constants import TIME_STALE_AFTER_MS

TIME_STATE_UNSYNCED = const(0x01)
TIME_STATE_STALE = const(0x02)
TIME_STATE_SYNCING = const(0x04)
TIME_STATE_SYNCED = const(0x08)


class GlobalState:
    __slots__ = (
        "_is_syncing",
        "_last_sync_ticks",
    )

    def __init__(self):
        self._is_syncing = False
        self._last_sync_ticks = None

    @property
    def is_syncing(self) -> bool:
        return self._is_syncing

    @property
    def last_sync_ticks(self) -> int | None:
        return self._last_sync_ticks

    def set_syncing(self, enable: bool = True):
        self._is_syncing = enable

    def set_synced(self):
        self._is_syncing = False
        self._last_sync_ticks = time.ticks_ms()

    def time_state(self) -> int:
        if self.last_sync_ticks is None:
            state = TIME_STATE_UNSYNCED
        elif time.ticks_diff(time.ticks_ms(), self.last_sync_ticks) > TIME_STALE_AFTER_MS:
            state = TIME_STATE_STALE
        else:
            state = TIME_STATE_SYNCED
        if self.is_syncing:
            state |= TIME_STATE_SYNCING
        return state
