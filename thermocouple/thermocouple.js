var PythonShell = require('python-shell');

module.exports = function(RED) {
    function AdafruitMax31855Node(config) {
        RED.nodes.createNode(this,config);
        this.muxing = config.muxing;
        var node = this;

        var scriptPath = './spi_read.py'
        
        var args = []
        console.log("Adafruit MAX 31855: Checking for muxing... "+this.muxing)
        if (this.muxing == 1) {
            console.log("Adafruit MAX 31855: Enabled muxing.")
            args = [0,1,17,6,5,4,7,18,parseInt(config.channels),parseInt(config.sampling),parseInt(config.reporting)]
        }

        var pyshell = new PythonShell(scriptPath, { scriptPath: __dirname, args: args });

        pyshell.on('message', function (message) {
            node.send({
                payload: message
            });
        });

        this.on("close", function() {
            if (pyshell) {
                pyshell.end(); 
                pyshell.kill();
            }
        });
    }
    RED.nodes.registerType("adafruit-max31855", AdafruitMax31855Node);
}