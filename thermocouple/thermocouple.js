var pyshell = require('python-shell');

module.exports = function(RED) {
    function LowerCaseNode(config) {
        RED.nodes.createNode(this,config);
        var node = this;

        
        this.on('input', function(msg) {
            msg.payload = msg.payload.toLowerCase();
            node.send(msg);
        });
        
        pyshell.run('spi_read.py', function (err) {
            if (err) throw err;
            console.log('finished');
        });
        pyshell.on('message', function (message) {
            // received a message sent from the Python script (a simple "print" statement)
            console.log(message);
        });

        // end the input stream and allow the process to exit
        pyshell.end(function (err) {
            if (err) throw err;
            console.log('finished');
        });
    }
    RED.nodes.registerType("adafruit-max31855",LowerCaseNode);
}