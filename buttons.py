#!/usr/bin/env python3
import os
import itertools

import signal
import RPi.GPIO as GPIO

import cal
import netlist

from PIL import Image

from inky.auto import auto

# Gpio pins for each button (from top to bottom)
BUTTONS = [5, 6, 16, 24]
saturation = .5
# Set up RPi.GPIO with the "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)

# Buttons connect to ground when pressed, so we should set them up
# with a "PULL UP", which weakly pulls the input signal to 3.3V.
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
inky = auto(ask_user=True, verbose=True)


def file_generator(directory):
    files = [os.path.join(directory, file) for file in os.listdir(directory)]
    return itertools.cycle(files)


def handle_button(pin):
    # pins 5, 6, 16, 24
    image = None
    if pin == 5:
        image = cal.get_cal_image()
    elif pin == 6:
        image = netlist.get_network_image()
    else:
        filename = next(file_gen)
        image = Image.open(filename)
    inky.set_image(image, saturation=saturation)
    inky.show()


directory_path = 'images/'
file_gen = file_generator(directory_path)

for pin in BUTTONS:
    GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=250)

signal.pause()

