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

SPI_PORT = 0
SPI_DEVICE = 1
MUXING = False

if(len(sys.argv) > 2):
    SPI_PORT = int(sys.argv[1])
    SPI_DEVICE = int(sys.argv[2])
    
if(len(sys.argv) > 9):
    MUXING = True
    MUXING_SELECTORS = [int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])]
    MUXING_ENABLER = int(sys.argv[7])
    MUXING_LATCH = int(sys.argv[8])
    MUXING_COUNT = int(sys.argv[9])

SAMPLING_RATE = 1.000
if(len(sys.argv) > 10):
    SAMPLING_RATE = int(sys.argv[10]) / 1000

# Raspberry Pi hardware SPI configuration.
sensor = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

if (MUXING):
    gpio = GPIO.get_platform_gpio()
    for selector in MUXING_SELECTORS:
        gpio.setup(selector, GPIO.OUT)
    gpio.setup(MUXING_ENABLER, GPIO.OUT)
    gpio.setup(MUXING_LATCH, GPIO.OUT)

def disableMuxing():
    gpio.output(MUXING_ENABLER, True)

def enableMuxing():
    gpio.output(MUXING_ENABLER, False)

def enableSelecting():
    gpio.output(MUXING_LATCH, True)

def disableSelecting():
    gpio.output(MUXING_LATCH, False)

def setMuxing(chipSelect):
    enableSelecting()
    chipSelectArray = [int(x) for x in bin(chipSelect)[2:]]
    while (len(chipSelectArray) < 4):
        chipSelectArray.insert(0, 0)
    for index, value in enumerate(chipSelectArray):
        gpio.output(MUXING_SELECTORS[index], (value == 1))
    disableSelecting()

channels = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
maxInternal = 0
last_report = 0
samples = 0

def sampledData(channel, temp):
    channels[channel] = ((channels[channel] * samples) + temp) / (samples + 1)

def completedSampling():
    samples = samples + 1
    report()

def report():
    if (time() - last_report > SAMPLING_RATE):
        last_report = time()
        for i in range(0,16):
            print('{0:0.3F},{1},{2:0.3F}'.format(time(),i, channels[i] ))

        print ('{0:0.3F},maxInternal,{1:0.3F}'.format(time(), maxInternal ))
        print ('{0:0.3F},samples,{1}'.format(time(), samples ))
        maxInternal = 0
    channels = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    samples = 0

# Loop printing measurements every second.
print('Press Ctrl-C to quit.')
while True:
    if MUXING:
        enableMuxing()
        maxInternal = 0
        for i in range(0,16):
            setMuxing(i)
            channelTemp = sensor.readTempC()
            sampledData(i, channelTemp)
            maxInternal = max(maxInternal, sensor.readInternalC())
        disableMuxing()
        completedSampling()
            
    else:
        temp = sensor.readTempC()
        internal = sensor.readInternalC()
        print('{0:0.3F},0,{1:0.3F}'.format(time(), temp ))
        print ('{0:0.3F},internal,{1:0.3F}'.format(time(), internal ))
    
    # TODO: Check for errors. Removed because 0x7 is too broad.
    #v = sensor._read32()
    #if v & 0x7:
    #    print "{0:0.3F},error,{1:0.1F}".format(time(), float( v & 0x7))
    
    sleep(0.1)