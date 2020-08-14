#!/bin/bash

DENON_AVR_NAME="$1"

if [ "$DENON_AVR_NAME" = "" ]; then
    echo "ERROR: Denon AVR Name on network not supplied (E.g. Denon-AVR-X6400H)"
    exit 1
fi

GATEWAY_IP=""

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac

if [ "$machine" = "Linux" ]; then
    GATEWAY_IP=`ip route | grep default | awk '{print $3}'`
fi

if [ "$machine" = "Mac" ]; then
    GATEWAY_IP=`netstat -nr | grep default | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b"`
fi

DENON_IP=`nslookup $DENON_AVR_NAME.localdomain $GATEWAY_IP | tail -2 | grep Address | awk '{print $2}'`

if [ "$DENON_IP" = "" ]; then
    echo "ERROR: Denon AVR Named $DENON_AVR_NAME could not be found on the network"
    exit 1
fi

echo $DENON_IP 

exit 0
