var PythonShell = require('python-shell');

module.exports = function(RED) {
    function AdafruitMax31855Node(config) {
        RED.nodes.createNode(this,config);
        var node = this;

        var scriptPath = './spi_read.py'
        var pyshell = new PythonShell(scriptPath, { scriptPath: __dirname });

        pyshell.on('message', function (message) {
            node.send({
                payload: message
            });
        });

        this.on("close", function() {
            if (pyshell) { pyshell.end(); }
        });
    }
    RED.nodes.registerType("adafruit-max31855", AdafruitMax31855Node);
}