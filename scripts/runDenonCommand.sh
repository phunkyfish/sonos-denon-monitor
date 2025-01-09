#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load DENON_AVR_NAME, DENON_INPUT and DENON_MASTER_VOLUME vars
source $SCRIPT_DIR/../variables.sh

DENON_IP=`$SCRIPT_DIR/getDenonIP.sh $DENON_AVR_NAME`

$SCRIPT_DIR/../denon-avr -ip=$DENON_IP $1 $2 $3 $4 $5
