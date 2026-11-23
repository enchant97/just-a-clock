import asyncio
from collections import namedtuple
from time import gmtime

from ht16k33 import HT16K33SegmentBig
from machine import I2C, Timer

from justaclock.com import ComHandler
from justaclock.config import ConfigHandler
from justaclock.state import (
    TIME_STATE_STALE,
    TIME_STATE_SYNCED,
    TIME_STATE_SYNCING,
    TIME_STATE_UNSYNCED,
    GlobalState,
)
from justaclock.time_sync import TimeSyncHandler

display = HT16K33SegmentBig(I2C(0))
global_state = GlobalState()
DisplayUpdate = namedtuple("DisplayUpdate", ("state", "h", "m"))
last_display_update = None


def into_digits(value: int):
    tens = value // 10
    ones = value % 10
    return tens, ones


def update_display_callback(*_):
    global last_display_update

    time_state = global_state.time_state()
    now = gmtime()
    hour_digits = into_digits(now[3])
    minute_digits = into_digits(now[4])

    display_update = DisplayUpdate(
        time_state,
        hour_digits,
        minute_digits,
    )

    if display_update == last_display_update:
        return

    last_display_update = display_update

    if not (time_state & TIME_STATE_UNSYNCED):
        display.set_number(hour_digits[0], 0)
        display.set_number(hour_digits[1], 1)
        display.set_number(minute_digits[0], 2)
        display.set_number(minute_digits[1], 3)

    if time_state & TIME_STATE_SYNCED:
        display.set_colon(0x02)
    elif time_state & TIME_STATE_SYNCING:
        display.set_colon(0x04 | 0x08)
    elif time_state & TIME_STATE_STALE:
        display.set_colon(0x04)

    display.clear()
    display.draw()


async def main():
    display.set_brightness(0)
    display.clear()
    display.draw()

    t = Timer()
    t.init(mode=Timer.PERIODIC, period=1_000, callback=update_display_callback)
    update_display_callback()

    config = ConfigHandler()
    config.read()

    com_task = asyncio.create_task(
        ComHandler(
            config,
        ).run()
    )
    sync_task = asyncio.create_task(
        TimeSyncHandler(
            config,
            global_state,
        ).run()
    )

    try:
        await asyncio.gather(com_task, sync_task)
    except asyncio.CancelledError:
        pass
    finally:
        t.deinit()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        # reset old tasks for REPL use
        asyncio.new_event_loop()
