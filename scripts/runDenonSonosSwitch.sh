#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load DENON_AVR_NAME, DENON_INPUT and DENON_MASTER_VOLUME vars
source $SCRIPT_DIR/../variables.sh

DENON_IP=`$SCRIPT_DIR/getDenonIP.sh $DENON_AVR_NAME`

echo $DENON_AVR_NAME:$DENON_IP 

$SCRIPT_DIR/runDenonCommand.sh ZMON $DENON_INPUT
sleep 2 #wait for AVR to power up
$SCRIPT_DIR/runDenonCommand.sh $DENON_INPUT 
$SCRIPT_DIR/runDenonCommand.sh MUOFF 
$SCRIPT_DIR/runDenonCommand.sh MV$DENON_MASTER_VOLUME
