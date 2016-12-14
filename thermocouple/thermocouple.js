var PythonShell = require('python-shell');

module.exports = function(RED) {
    function AdafruitMax31855Node(config) {
        RED.nodes.createNode(this,config);
        var node = this;

        var scriptPath = './spi_read.py'
        var pyshell = new PythonShell(scriptPath, { scriptPath: __dirname });

        pyshell.on('message', function (message) {
            // received a message sent from the Python script (a simple "print" statement)
            node.send({
                payload: message
            });
        });

        // end the input stream and allow the process to exit
        pyshell.end(function (err) {
            if (err) throw err;
            node.send('finished');
        });
    }
    RED.nodes.registerType("adafruit-max31855", AdafruitMax31855Node);
}