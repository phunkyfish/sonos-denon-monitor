#!/usr/bin/python
# -*- coding: utf-8 -*-

# What this does:
#
# Start this as a daemon. It connects to your Sonos Connect and your Yamaha
# Receiver. Whenever the Sonos Connect starts playing music, radio or whatever,
# it turns on the Receiver, switches to the appropriate input, sets the volume
# and changes to the Sound Program you want to (e.g. "5ch Stereo").
#
# If the Receiver is already turned on, it just switches the input and the
# Sound Program, not the Volume.
#
# If you set the standby time of the Receiver to 20 minutes, you'll have a
# decent instant-on solution for your Sonos Connect - it behaves just like
# one of Sonos' other players.
#
# Optimized for minimum use of resources. I leave this running on a Raspberry
# Pi at my place.
#
# Before installing it as a daemon, try it out first: Adapt the settings in the
# script below. Then just run the script. It'll auto-discover your Sonos
# Connect. If that fails (e.g. because you have more than one Connect in your
# home or for other reasons), you can use the UID of your Sonos Connect as the
# first and only parameter of the script. The script will output all UIDs
# neatly for your comfort.
#
# Prerequisites:
# - Your Yamaha Receiver has to be connected to the LAN.
# - Both your Yamaha Receiver and your Sonos Connect have to use fixed IP
#   addresses. You probably have to set this in your router (or whichever
#   device is your DHCP).
# - Your Yamaha Receiver's setting of "Network Standby" has to be "On".
#   Otherwise the Receiver cannot be turned on from standby mode.
#
# Software prerequisites:
# - sudo pip3 install soco



import os
import sys
import time
import re
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
import telnetlib
import soco
import queue
import signal
import subprocess
from datetime import datetime

__version__     = '0.3'

def denon_get_value(variable):
    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))+"/runDenonCommandParsedOutput.sh"
    #output = subprocess.check_output('/volume1/ROSS-STORAGE/sonos-denon-monitor/runDenonCommand.sh')
    return subprocess.check_output([script_path, variable])

def denon_switch_off():
    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))+"/runDenonCommand.sh"
    return subprocess.check_output([script_path, "ZMOFF"])

def denon_print_statuses_with_heading(heading):
    print("{} {}".format(datetime.now(), heading))
    print("{}".format("---------------------------------------------------"))
    denon_print_statuses()

def denon_print_statuses():
    print("Denon Power status:  {}".format(denon_get_value('PW?')))
    print("Denon Main Zone Power status:  {}".format(denon_get_value('ZM?')))
    print("Denon Zone 2 Power status:  {}".format(denon_get_value('Z2?')))
    print("Denon Zone 3 Power status:  {}".format(denon_get_value('Z3?')))
    print("Denon Input status:  {}".format(denon_get_value('SI?')))
    print("Denon Mute status:  {}".format(denon_get_value('MU?')))
    print("Denon Master Volume status:  {}".format(denon_get_value('MV?')))
    print() 

def auto_flush_stdout():
    unbuffered = os.fdopen(sys.stdout.fileno(), 'w')
    sys.stdout.close()
    sys.stdout = unbuffered

def handle_sigterm(*args):
    global break_loop
    print("SIGTERM caught. Exiting gracefully.")
    break_loop = True

# --- Startup  ----------------------------------------------------

print("{}".format("-----------------------------------------------------------------"))
print("{} Starting up sonos-denon-monitor daemon".format(datetime.now()))
print("{}".format("-----------------------------------------------------------------"))

# --- Discover SONOS zones ----------------------------------------------------

if len(sys.argv) >= 2:
    connect_player_name = sys.argv[1]
else:
    connect_player_name = None

if len(sys.argv) >= 3:
    denonInput = sys.argv[2]
else:
    denonInput = "SIPHONO2"

if len(sys.argv) == 4:
    noAudioTimeoutSecs = int(sys.argv[3])
else:
    noAudioTimeoutSecs = 300

print("Using supplied Connect Name: {}, Denon Input: {}, No audio power off timeout: {}".format(connect_player_name, denonInput, noAudioTimeoutSecs))
print("Discovering Sonos zones")

match_ips   = []
for zone in soco.discover():
    print("   {} (UID: {})".format(zone.player_name, zone.uid))

    if connect_player_name:
        if zone.player_name.lower() == connect_player_name.lower():
            match_ips.append(zone.ip_address)
            print("   => match")
    else:
        # we recognize Sonos Connect and ZP90 by their hardware revision number
        if zone.get_speaker_info().get('hardware_version')[:4] == '1.1.':
            match_ips.append(zone.ip_address)
            print("   => possible match")
print()

if len(match_ips) != 1:
    print("The number of Sonos Connect devices found was not exactly 1.")
    print("Please specify which Sonos Connect device should be used by")
    print("using its UID as the first parameter.")
    sys.exit(1)

sonos_device    = soco.SoCo(match_ips[0])
subscription    = None
renewal_time    = 120

# --- Initial Denon status ---------------------------------------------------

denon_print_statuses_with_heading("Initial Denon status")

# --- Main loop ---------------------------------------------------------------

break_loop      = False
last_status     = None
noAudioStartTime  = 0

# catch SIGTERM gracefully
signal.signal(signal.SIGTERM, handle_sigterm)
# non-buffered STDOUT so we can use it for logging
auto_flush_stdout()

while True:
    # if not subscribed to SONOS connect for any reason (first start or disconnect while monitoring), (re-)subscribe
    if not subscription or not subscription.is_subscribed or subscription.time_left <= 5:
        # The time_left should normally not fall below 0.85*renewal_time - or something is wrong (connection lost).
        # Unfortunately, the soco module handles the renewal in a separate thread that just barfs  on renewal
        # failure and doesn't set is_subscribed to False. So we check ourselves.
        # After testing, this is so robust, it survives a reboot of the SONOS. At maximum, it needs 2 minutes
        # (renewal_time) for recovery.

        if subscription:
            print("{} *** Unsubscribing from SONOS device events".format(datetime.now()))
            try:
                subscription.unsubscribe()
                soco.events.event_listener.stop()
            except Exception as e:
                print("{} *** Unsubscribe failed: {}".format(datetime.now(), e))

        print("{} *** Subscribing to SONOS device events".format(datetime.now()))
        try:
            subscription = sonos_device.avTransport.subscribe(requested_timeout=renewal_time, auto_renew=True)
        except Exception as e:
            print("{} *** Subscribe failed: {}".format(datetime.now(), e))
            # subscription failed (e.g. sonos is disconnected for a longer period of time): wait 10 seconds
            # and retry
            time.sleep(10)
            continue

    try:
        event   = subscription.events.get(timeout=10)
        status  = event.variables.get('transport_state')

        if not status:
            print("{} Invalid SONOS status: {}".format(datetime.now(), event.variables))

        if last_status != status:
            print("{} SONOS play status: {}".format(datetime.now(), status))

        if last_status != 'PLAYING' and status == 'PLAYING':
            print()
            denon_print_statuses_with_heading("Denon Status before Switch")
            script_path = os.path.abspath(os.path.dirname(sys.argv[0]))+"/runDenonSonosSwitch.sh"
            #output = subprocess.check_output('/volume1/ROSS-STORAGE/sonos-denon-monitor/runDenonCommand.sh')
            output = subprocess.check_output(script_path)
            #print("XXXXX Power status:  {}".format(output))
            print()
            denon_print_statuses_with_heading("Denon Status after Switch")

        if (last_status != 'PAUSED_PLAYBACK' and status == 'PAUSED_PLAYBACK') or (last_status != 'STOPPED' and status == 'STOPPED'):
            # then we need to start a timer in seconds
            noAudioStartTime = int(round(time.time()))
            print("no audio timer started: %d" % noAudioStartTime)
        elif status != 'PAUSED_PLAYBACK' or status != 'STOPPED':
            noAudioStartTime = 0

        last_status = status
    except queue.Empty:
        if noAudioStartTime > 0 and "PWON" in str(denon_get_value('PW?')) and (status == 'PAUSED_PLAYBACK' or status == 'STOPPED'):
            timeNow = int(round(time.time()))
            noAudioTime = timeNow - noAudioStartTime
            if noAudioTime > noAudioTimeoutSecs:
                print("no audio timer reached limit: %d" % noAudioTime)
                print("Denon Input status at no audio time is:  {}, and sonos input is: {}".format(denon_get_value('SI?'), denonInput))
                if denonInput in str(denon_get_value('SI?')):
                    denon_switch_off()
            else:
                print("no audio timer not long enough: %d" % noAudioTime)
		
        pass
    except KeyboardInterrupt:
        handle_sigterm()

    if break_loop:
        subscription.unsubscribe()
        soco.events.event_listener.stop()
        break
