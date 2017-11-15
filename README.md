# node-red-contrib-adafruit-max31855
Node-RED node for communicating with an Adafruit MAX31855 module. (Unofficial)

## Installation

First navigate to your node red directory `cd ~/.node-red` then install node from npm `npm install @heatworks/node-red-contrib-adafruit-max31855`. Then restart node-red.

The node should appear in the node library.

## How it works:

The simpliest way to read from the SPI was to use Adafruit's python library and then invoke it from node.

## Future

Add a paramter for number of checks, allow multiple channels.