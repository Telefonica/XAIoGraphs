/**
 * (c) Copyright 2022 Telefonica. All Rights Reserved.
 * The copyright to the software program(s) is property of Telefonica.
 * The program(s) may be used and or copied only with the express written consent
 * of Telefonica or in accordance with the terms and conditions stipulated in
 * the agreement/contract under which the program(s) have been supplied. 
 */

/**
 * Module dependencies.
 */

const app = require('../app');
const debug = require('debug')('api-server:server');
const http = require('http');
const environment = require('../config/environment');

/**
 * Get port from environment and store in Express.
 */
let nodeEnvironment = {};
if (process.env.NODE_ENV == 'production') {
    nodeEnvironment = environment.prod;
} else {
    nodeEnvironment = environment.dev;
}
console.log('Environment: ' + (process.env.NODE_ENV == 'production' ? 'Production' : 'Development'));
const port = normalizePort(nodeEnvironment.port || 3001);
app.set('port', port);

/**
 * Create HTTP server.
 */
const server = http.createServer(app);

/**
 * Listen on provided port, on all network interfaces.
 */
server.listen(port);
server.on('error', onError);
server.on('listening', onListening);

/**
 * Normalize a port into a number, string, or false.
 */
function normalizePort(val) {
    const port = parseInt(val, 10);

    if (isNaN(port)) {
        return val;
    }

    if (port >= 0) {
        return port;
    }

    return false;
}

/**
 * Event listener for HTTP server "error" event.
 */
function onError(error) {
    if (error.syscall !== 'listen') {
        throw error;
    }

    const bind = typeof port === 'string' ? 'Pipe ' + port : 'Port ' + port;
    switch (error.code) {
        case 'EACCES':
            console.error(bind + ' requires elevated privileges');
            process.exit(1);
            break;
        case 'EADDRINUSE':
            console.error(bind + ' is already in use');
            process.exit(1);
            break;
        default:
            throw error;
    }
}

/**
 * Event listener for HTTP server "listening" event.
 */
function onListening() {
    const addr = server.address();
    const bind = typeof addr === 'string' ? 'pipe ' + addr : 'port ' + addr.port;
    debug('Listening on ' + bind);
}
