/**
 * (c) Copyright 2022 Telefonica. All Rights Reserved.
 * The copyright to the software program(s) is property of Telefonica.
 * The program(s) may be used and or copied only with the express written consent
 * of Telefonica or in accordance with the terms and conditions stipulated in
 * the agreement/contract under which the program(s) have been supplied. 
 */

'use strict';

const logger = require('morgan');
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const cors = require('cors');

module.exports = (app) => {
    app.use(logger('combined'));
    app.use(bodyParser.json());
    app.use(bodyParser.urlencoded({ extended: false }));
    app.use(cookieParser());
    app.use(cors());
};
