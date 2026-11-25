import asyncio
from collections import namedtuple
from time import gmtime

from ht16k33 import HT16K33SegmentBig
from machine import Timer
from micropython import const

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

_DISPLAY_UPDATE_INTERVAL_MS = const(100)

DisplayWiring = namedtuple("DisplayWiring", ("i2c_bus", "i2c_address"))
DisplayUpdate = namedtuple("DisplayUpdate", ("state", "h", "m"))

display: HT16K33SegmentBig
global_state: GlobalState
last_display_update = None


def into_digits(value: int):
    tens = value // 10
    ones = value % 10
    return tens, ones


def update_display_callback(*_):
    global last_display_update

    time_state = global_state.time_state()
    enable_24h = global_state.enable_24h_display()

    now = gmtime()

    display_hour = now[3] if enable_24h else (now[3] % 12 or 12)

    hour_digits = into_digits(display_hour)
    minute_digits = into_digits(now[4])

    display_update = DisplayUpdate(
        time_state,
        hour_digits,
        minute_digits,
    )

    if display_update == last_display_update:
        return

    last_display_update = display_update

    display.clear()

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

    display.draw()


async def run(display_wiring: DisplayWiring):
    global display, global_state

    display = HT16K33SegmentBig(display_wiring.i2c_bus, display_wiring.i2c_bus)

    display.set_brightness(0)
    display.clear()
    display.draw()

    config = ConfigHandler()
    config.read()

    global_state = GlobalState(config)

    t = Timer()
    t.init(
        mode=Timer.PERIODIC,
        period=_DISPLAY_UPDATE_INTERVAL_MS,
        callback=update_display_callback,
    )
    update_display_callback()

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


def main(display_wiring: DisplayWiring):
    try:
        asyncio.run(run(display_wiring))
    except KeyboardInterrupt:
        pass
    finally:
        # reset old tasks for REPL use
        asyncio.new_event_loop()
