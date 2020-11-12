#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load DENON_AVR_NAME, DENON_INPUT and DENON_MASTER_VOLUME vars
source $SCRIPT_DIR/variables.sh

python3 $SCRIPT_DIR/scripts/sonos-denon-monitor.py "$SONOS_DEVICE_NAME" "$DENON_INPUT" "$DENON_NO_AUDIO_POWER_OFF_TIMEOUT_SECS"


