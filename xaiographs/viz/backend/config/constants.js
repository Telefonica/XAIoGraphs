/**
 * (c) Copyright 2022 Telefonica. All Rights Reserved.
 * The copyright to the software program(s) is property of Telefonica.
 * The program(s) may be used and or copied only with the express written consent
 * of Telefonica or in accordance with the terms and conditions stipulated in
 * the agreement/contract under which the program(s) have been supplied. 
 */

const fs = require('fs');
const ini = require('ini');
const config = ini.parse(fs.readFileSync('./backend/config.ini', 'utf-8'));

const cts = {};
module.exports = cts;

cts.rootUrl = config.root.url;
cts.csvPath = config.root.csvPath;
