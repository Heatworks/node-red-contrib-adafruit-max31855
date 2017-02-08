#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Can enable debug output by uncommenting:
#import logging
#logging.basicConfig(level=logging.DEBUG)

from time import time, sleep
import random
import sys

import Adafruit_GPIO.SPI as SPI
import Adafruit_GPIO.GPIO as GPIO
import Adafruit_MAX31855.MAX31855 as MAX31855


# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0


# Uncomment one of the blocks of code below to configure your Pi or BBB to use
# software or hardware SPI.

# Raspberry Pi software SPI configuration.
#CLK = 25
#CS  = 24
#DO  = 18
#sensor = MAX31855.MAX31855(CLK, CS, DO)

# GPI 3,4,5,6
# MUX - A0, A1, A2, A3

SPI_PORT = 0
SPI_DEVICE = 1
MUXING = False

if(len(sys.argv) > 2):
    SPI_PORT = int(sys.argv[1])
    SPI_DEVICE = int(sys.argv[2])
    
if(len(sys.argv) > 6):
    MUXING = True
    MUXING_SELECTORS = [int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])]

# Raspberry Pi hardware SPI configuration.
sensor = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# BeagleBone Black software SPI configuration.
#CLK = 'P9_12'
#CS  = 'P9_15'
#DO  = 'P9_23'
#sensor = MAX31855.MAX31855(CLK, CS, DO)

# BeagleBone Black hardware SPI configuration.
#SPI_PORT   = 1
#SPI_DEVICE = 0
#sensor = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

if (MUXING):
    gpio = GPIO.get_platform_gpio()
    for selector in MUXING_SELECTORS:
        gpio.setup(selector, GPIO.OUT)

def setMuxing(chipSelect):
    chipSelectArray = [int(x) for x in bin(chipSelect)[2:]]
    while (len(chipSelectArray) < 4):
        chipSelectArray.insert(0, 0)
    for index, value in enumerate(chipSelectArray):
        gpio.output(MUXING_SELECTORS[index], (value == 1))

# Loop printing measurements every second.
print('Press Ctrl-C to quit.')
while True:

    if MUXING:
        for i in range(0,16):
            setMuxing(i)
            temp = sensor.readTempC()
            internal = sensor.readInternalC()
            print('{0:0.3F},{1},{2:0.3F}'.format(time(),i, temp ))
            print ('{0:0.3F},internal,{1:0.3F}'.format(time(), internal ))
    else:
        temp = sensor.readTempC()
        internal = sensor.readInternalC()
        print('{0:0.3F},0,{1:0.3F}'.format(time(), temp ))
        print ('{0:0.3F},internal,{1:0.3F}'.format(time(), internal ))
    
    #print('Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, c_to_f(temp)))
    #print('    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, c_to_f(internal)))
    
    v = sensor._read32()
    if v & 0x7:
        print "{0:0.3F},error,{1:0.1F}".format(time(), float( v & 0x7))
    
    sleep(1.0)