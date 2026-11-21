import asyncio
from time import gmtime
from ht16k33 import HT16K33SegmentBig
from machine import I2C, Timer

from justaclock.com import ComHandler
from justaclock.config import SystemConfigHandler, NetworkConfigHandler
from justaclock.time_sync import TimeSyncHandler


display = HT16K33SegmentBig(I2C(0))


def into_digits(value: int):
    tens = value // 10
    ones = value % 10
    return tens, ones


def update_display_callback(*_):
    now = gmtime()
    hour_digits = into_digits(now[3])
    minute_digits = into_digits(now[4])

    display.clear()
    display.set_colon(0x02)
    display.set_number(hour_digits[0], 0)
    display.set_number(hour_digits[1], 1)
    display.set_number(minute_digits[0], 2)
    display.set_number(minute_digits[1], 3)
    display.draw()


async def main():
    display.set_brightness(0)
    display.clear()
    display.draw()

    t = Timer()
    t.init(mode=Timer.PERIODIC, period=60_000, callback=update_display_callback)
    update_display_callback()

    network_config = NetworkConfigHandler()
    system_config = SystemConfigHandler()

    com_task = asyncio.create_task(
        ComHandler(
            network_config,
            system_config,
        ).run()
    )
    sync_task = asyncio.create_task(
        TimeSyncHandler(
            network_config,
            system_config,
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
