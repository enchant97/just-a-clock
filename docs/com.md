# COM
"Just A Clock" supports configuration over USB Serial by a simple text command interface.

## Available Commands

- `FLUSH` - write current configuration values to flash
- `RELOAD` - overwrite current configuration values from flash
- `NET.HOSTNAME.GET`
- `NET.HOSTNAME.SET hostname-here`
- `NET.WLAN.SSID.SET the-ssid`
- `NET.WLAN.PASSWORD.SET the-password`
- `NTP.SERVER.1.GET`
- `NTP.SERVER.1.SET the-hostname`

## Access Python REPL
Whilst connected over serial you can access the underlying Python REPL by pressing `CTRL+C`. After entering the REPL it will stop the "Just A Clock" firmware from running, it is best to disconnect and reconnect if you want to resume the original functionality.
