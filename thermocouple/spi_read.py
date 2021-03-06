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
import math

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

    if (MUXING_COUNT > 16):
        print("Max number of muxings is 16.")
        exit()

SAMPLING_RATE = 1.000
REPORTING_RATE = 1.000
if(len(sys.argv) > 11):
    SAMPLING_RATE = float(sys.argv[10]) / 1000
    REPORTING_RATE = float(sys.argv[11]) / 1000

if(len(sys.argv) > 14):
    SPI_CLK = int(sys.argv[12])
    SPI_DO = int(sys.argv[13])
    SPI_CS = int(sys.argv[14])
    sensor = MAX31855.MAX31855(clk=SPI_CLK, do=SPI_DO, cs=SPI_CS)
else:
    sensor = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# Raspberry Pi hardware SPI configuration.


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

channels = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
maxInternal = 0
last_report = 0

def sampledData(channel, temp):
    global channels
    if not math.isnan(temp):
        channels[channel].append(temp)
    
def report():
    global channels, maxInternal, last_report
    if (time() - last_report > REPORTING_RATE):
        last_report = time()
        for i in range(0,MUXING_COUNT):
            if len(channels[i]) > 0:
                print('{0:0.3F},{1},{2:0.3F}'.format(time(),i, sum(channels[i])/len(channels[i]) ))

        print ('{0:0.3F},maxInternal,{1:0.3F}'.format(time(), maxInternal ))
        maxInternal = 0
        channels = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

# Loop printing measurements every second.
print('Press Ctrl-C to quit.')
while True:
    if MUXING:
        enableMuxing()
        maxInternal = 0
        for i in range(0,MUXING_COUNT):
            setMuxing(i)
            channelTemp = sensor.readTempC()
            sampledData(i, channelTemp)
            maxInternal = max(maxInternal, sensor.readInternalC())
        disableMuxing()
        report()
            
    else:
        temp = sensor.readTempC()
        internal = sensor.readInternalC()
        print('{0:0.3F},0,{1:0.3F}'.format(time(), temp ))
        print ('{0:0.3F},internal,{1:0.3F}'.format(time(), internal ))
    
    # TODO: Check for errors. Removed because 0x7 is too broad.
    #v = sensor._read32()
    #if v & 0x7:
    #    print "{0:0.3F},error,{1:0.1F}".format(time(), float( v & 0x7))
    
    sleep(SAMPLING_RATE)