#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

dataReturned=FALSE

for i in `$SCRIPT_DIR/runDenonCommand.sh $1 | grep received | sed 's/\r/\n/g' | sed 's/received:  //' | sed 's/ /:/' | sed 's/\n//g'`
do
    if [ "$dataReturned" = "TRUE" ]; then
        printf ", "
    fi
    dataReturned=TRUE
    printf "%s" $i
done

#$SCRIPT_DIR/runDenonCommand.sh $1 | grep received | sed 's/received:  //'

#if [ "$dataReturned" = "TRUE" ]; then
#    printf "\n"
#fi
