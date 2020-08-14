
# sonos-denon-monitor

Service for switching a Denon AVR to the correct input and volume when a Sonos device is played. Supports auto power off for the AVR.

The project uses a blend of shell scripts, python 3 and golang. A future piece of work would be to convert the whole project to golang.

# Pre-requisites

Install the SoCo project: `pip3 install soco`

# Build and setup

1. Build the golang executable: `go build denon-avr.go`
2. Optionally copy and configure the service script for for your platform: `cp startup/sonos-denon-monitor /etc/init.d/`
3. Edit `variables.sh` for your environment. The follwing variables can be configured:
 - SONOS_DEVICE_NAME
 - DENON_AVR_NAME
 - DENON_INPUT
 - DENON_MASTER_VOLUME
 - DENON_NO_AUDIO_POWER_OFF_TIMEOUT_SECS

Once configured the service can be started with using the startup script or by running the service manually: `./sonos-denon-monitor.sh`

## Acknowledgements

The python script was originally from the `sonos-monitor` project which worked with a Yamaha AVR: https://github.com/michaelotto/sonos-monitor.
This was converted to Python 3 and modified to leverage the `denon-avr` project which was written in golang: https://github.com/golliher/denon-avr. The `denon-avr` project has a few minor adjustments, introducing the flags library allowing a custom ip to be used.
