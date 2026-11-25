# COM
"Just A Clock" supports configuration over USB Serial by a simple text command interface.

Until WLAN is setup, the device will not display any time. Other configuration values always have defaults

## Available Commands

- `HELP` - Show available commands
- `FLUSH` - Write current configuration values to flash
- `RELOAD` - Overwrite current configuration values from flash
- `NET.HOSTNAME.GET` - Get the currently set hostname
- `NET.HOSTNAME.SET hostname-here` - Set the device hostname
- `NET.WLAN.SSID.SET the-ssid` - Set the WIFI name that the device will connect to
- `NET.WLAN.PASSWORD.SET the-password` - Set the WIFI password that the device will use to connect
- `NTP.SERVER.1.GET` - Get the currently set NTP server 1
- `NTP.SERVER.1.SET the-hostname` - Set the NTP server 1
- `NTP.SYNC-INTERVAL.GET` - Get the sync interval in hours
- `NTP.SYNC-INTERVAL.SET hours` - Set the sync interval in hours, must be >= 1
- `TIME.24-HOUR.GET` - Whether 24 hour time display is 12 hour or 24 hour
- `TIME.24-HOUR.SET` - Set 24 hour time display TRUE/FALSE

## Access Python REPL
Whilst connected over serial you can access the underlying Python REPL by pressing `CTRL+C`. After entering the REPL it will stop the "Just A Clock" firmware from running, it is best to disconnect and reconnect if you want to resume the original functionality.
