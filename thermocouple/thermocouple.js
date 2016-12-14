var PythonShell = require('python-shell');

module.exports = function(RED) {
    function LowerCaseNode(config) {
        RED.nodes.createNode(this,config);
        var node = this;

        
        this.on('input', function(msg) {
            msg.payload = msg.payload.toLowerCase();
            node.send(msg);
        });

        var scriptPath = '//home/pi/node-red-contrib-adafruit-max31855/thermocouple/spi_read.py'
        var pyshell = new PythonShell(scriptPath);

        pyshell.on('message', function (message) {
            // received a message sent from the Python script (a simple "print" statement)
            console.log(message);
            node.send(message);
        });

        // end the input stream and allow the process to exit
        pyshell.end(function (err) {
            if (err) throw err;
            console.log('finished');
            node.send('finished');
        });
    }
    RED.nodes.registerType("adafruit-max31855",LowerCaseNode);
}