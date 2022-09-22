/**
 * (c) Copyright 2022 Telefonica. All Rights Reserved.
 * The copyright to the software program(s) is property of Telefonica.
 * The program(s) may be used and or copied only with the express written consent
 * of Telefonica or in accordance with the terms and conditions stipulated in
 * the agreement/contract under which the program(s) have been supplied. 
 */

 const express = require('express');
 const path = require('path');
 const index = require('./routes/index');
 const helmet = require('helmet');
 const hpp = require('hpp');
 
 const app = express();
 require('./config/express')(app);
 
 app.use(hpp());
 app.use(helmet());
 
 app.use('/api', express.static(path.join(__dirname, 'public'), { etag: false }));
 
 app.use('/', index);
 
 app.use((req, res, next) => {
     if (req.accepts('json')) {
         res.status(404).send({ error: 'Not found' });
         return;
     }
 });
 
 app.use((err, req, res, next) => {
     if (err.name === 'UnauthorizedError') {
         res.status(401);
         res.json({ 'message': err.name + ': ' + err.message });
     }
 });
 
 module.exports = app;
 