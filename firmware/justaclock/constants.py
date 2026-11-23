from micropython import const

DEFAULT_HOSTNAME = const("justaclock")
DEFAULT_NTP_SERVER = const("pool.ntp.org")

TIME_STALE_AFTER_MS = const(12 * 60 * 60 * 1000)
TIME_SYNC_INTERVAL_SECS = const(6 * 3600)
