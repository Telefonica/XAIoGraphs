/**
 * (c) Copyright 2022 Telefonica. All Rights Reserved.
 * The copyright to the software program(s) is property of Telefonica.
 * The program(s) may be used and or copied only with the express written consent
 * of Telefonica or in accordance with the terms and conditions stipulated in
 * the agreement/contract under which the program(s) have been supplied. 
 */

const routes = require('express').Router();
const cts = require('../config/constants');

const reader = require ('../api/reader');

routes.use('/' + cts.rootUrl + '/reader', reader);

routes.get('/', (req, res) => {
    res.status(200).json({ message: 'Connected!' });
});

module.exports = routes;
