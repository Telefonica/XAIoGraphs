'use strict';

const fs = require('fs');
const csv = require('csv-parser');
const cts = require('../../config/constants');
const gauss = require('gauss');

exports.index = (req, res) => {
    res.status(200).json('Welcome to reader');
};
exports.readCSV = async (req, res) => {
    if (!req.body.fileName) {
        const msg = 'Missing parameters';
        console.log('ERROR - readCSV', msg);
        return res.status(404).json({ msg: msg });
    } else {
        await getData(req.body.fileName)
            .then((response) => { return res.status(200).json(response) })
            .catch((error) => {
                console.log('ERROR - readCSV', error);
                return res.status(400).json({ msg: error })
            });
    }
};



exports.listGlobalTarget = async (req, res) => {
    if (!req.body.fileName) {
        const msg = 'Missing parameters';
        console.log('ERROR - listGlobalTarget', msg);
        return res.status(404).json({ msg: msg });
    } else {
        await getData(req.body.fileName)
            .then((response) => {
                return res.status(200).json({
                    targets: response.data.map((row) => {
                        return row.target;
                    }),
                    features: response.headers.length - 1,
                })
            })
            .catch((error) => {
                console.log('ERROR - listGlobalTarget', error);
                return res.status(400).json({ msg: error })
            });
    }
};
exports.readGlobalNodesWeights = async (req, res) => {
    if (!req.body.fileName || !req.body.target || !req.body.numFeatures) {
        const msg = 'Missing parameters';
        console.log('ERROR - readGlobalNodesWeights', msg);
        return res.status(404).json({ msg: msg });
    } else {
        await getData(req.body.fileName)
            .then((response) => {
                return res.status(200).json(
                    response.data.filter((row) => {
                        return row.target == req.body.target
                            && parseInt(row.rank) <= parseInt(req.body.numFeatures);
                    })
                );
            })
            .catch((error) => {
                console.log('ERROR - readGlobalNodesWeights', error);
                return res.status(400).json({ msg: error })
            });
    }
};
exports.readGlobalEdgesWeights = async (req, res) => {
    if (!req.body.fileName || !req.body.target || !req.body.nodeNames) {
        const msg = 'Missing parameters';
        console.log('ERROR - readGlobalEdgesWeights', msg);
        return res.status(404).json({ msg: msg });
    } else {
        await getData(req.body.fileName)
            .then((response) => {
                return res.status(200).json(
                    response.data.filter((row) => {
                        return row.target == req.body.target
                            && req.body.nodeNames.includes(row.node_1)
                            && req.body.nodeNames.includes(row.node_2);
                    })
                );
            })
            .catch((error) => {
                console.log('ERROR - readGlobalEdgesWeights', error);
                return res.status(400).json({ msg: error })
            });
    }
};



exports.readLocalDataset = async (req, res) => {
    if (!req.body.fileName) {
        const msg = 'Missing parameters';
        console.log('ERROR - readLocalDataset', msg);
        return res.status(404).json({ msg: msg });
    } else {
        await getData(req.body.fileName)
            .then((response) => {
                return res.status(200).json(response)
            })
            .catch((error) => {
                console.log('ERROR - readLocalDataset', error);
                return res.status(400).json({ msg: error })
            });
    }
};
exports.readLocalNodesWeights = async (req, res) => {
    if (!req.body.fileName || !req.body.target || !req.body.numFeatures) {
        const msg = 'Missing parameters';
        console.log('ERROR - readLocalNodesWeights', msg);
        return res.status(404).json({ msg: msg });
    } else {
        await getData(req.body.fileName)
            .then((response) => {
                return res.status(200).json(
                    response.data.filter((row) => {
                        return row.id == req.body.target
                            && parseInt(row.rank) <= parseInt(req.body.numFeatures);
                    })
                );
            })
            .catch((error) => {
                console.log('ERROR - readLocalNodesWeights', error);
                return res.status(400).json({ msg: error })
            });
    }
};
exports.readLocalEdgesWeights = async (req, res) => {
    if (!req.body.fileName || !req.body.target || !req.body.nodeNames) {
        const msg = 'Missing parameters';
        console.log('ERROR - readLocalEdgesWeights', msg);
        return res.status(404).json({ msg: msg });
    } else {
        await getData(req.body.fileName)
            .then((response) => {
                return res.status(200).json(
                    response.data.filter((row) => {
                        return row.id == req.body.target
                            && req.body.nodeNames.includes(row.node_1)
                            && req.body.nodeNames.includes(row.node_2);
                    })
                );
            })
            .catch((error) => {
                console.log('ERROR - readLocalEdgesWeights', error);
                return res.status(400).json({ msg: error })
            });
    }
};
exports.readLocalReasonWhy = async (req, res) => {
    if (!req.body.fileName || !req.body.target) {
        const msg = 'Missing parameters';
        console.log('ERROR - readLocalReasonWhy', msg);
        return res.status(404).json({ msg: msg });
    } else {
        await getData(req.body.fileName)
            .then((response) => {
                return res.status(200).json(
                    response.data.filter((row) => {
                        return row.id == req.body.target;
                    })
                );
            })
            .catch((error) => {
                console.log('ERROR - readLocalReasonWhy', error);
                return res.status(400).json({ msg: error })
            });
    }
};



exports.listDatasetHeaders = async (req, res) => {
    if (!req.body.fileName) {
        const msg = 'Missing parameters';
        console.log('ERROR - listDatasetHeaders', msg);
        return res.status(404).json({ msg: msg });
    } else {
        await getData(req.body.fileName)
            .then((response) => {
                return res.status(200).json(response.headers);
            })
            .catch((error) => {
                console.log('ERROR - listDatasetHeaders', error);
                return res.status(400).json({ msg: error })
            });
    }
};
exports.readDatasetSelected = async (req, res) => {
    if (!req.body.fileName || !req.body.displayedColumns) {
        const msg = 'Missing parameters';
        console.log('ERROR - readDatasetSelected', msg);
        return res.status(404).json({ msg: msg });
    } else {
        const filteredData = [];
        const tempDistributionData = {};
        const distributionData = {};
        await getData(req.body.fileName)
            .then((response) => {
                req.body.displayedColumns.forEach(header => {
                    tempDistributionData[header] = [];
                });
                response.data.forEach(row => {
                    const filteredRow = {};
                    req.body.displayedColumns.forEach(header => {
                        filteredRow[header] = row[header];
                        tempDistributionData[header].push(row[header]);
                    });
                    filteredData.push(filteredRow);
                });

                req.body.displayedColumns.forEach(header => {
                    if (header != 'id') {
                        const gausVector = new gauss.Vector(tempDistributionData[header]);
                        const currentDistribution = gausVector.distribution();
                        if (Object.keys(currentDistribution).length == response.data.length) {
                            const quantile = gausVector.quantile(10);
                            const distributionToArray = [];
                            quantile.forEach((value) => {
                                distributionToArray.push([value, 0]);
                            });
                            console.log(header, currentDistribution);
                            distributionData[header] = distributionToArray;
                        } else {
                            const distributionToArray = [];
                            Object.keys(currentDistribution).forEach(key => {
                                distributionToArray.push([key, currentDistribution[key]]);
                            });
                            distributionData[header] = distributionToArray;
                        }
                    }
                });

                return res.status(200).json({
                    headers: req.body.displayedColumns,
                    data: filteredData,
                    distribution: distributionData,
                });
            })
            .catch((error) => {
                console.log('ERROR - readDatasetSelected', error);
                return res.status(400).json({ msg: error })
            });
    }
};




const getData = async (fileName) => {
    let csvPath = cts.csvPath + fileName;
    let csvHeaders = [];
    let csvData = [];

    return new Promise((resolve, reject) => {
        if (fs.existsSync(csvPath)) {
            console.log('getData - File ready: ', csvPath)
            fs.createReadStream(csvPath)
                .pipe(csv({
                    separator: ','
                }))
                .on('headers', (headers) => {
                    csvHeaders = headers
                })
                .on('data', (data) => {
                    csvData.push(data)
                })
                .on('end', () => {
                    resolve({
                        headers: csvHeaders,
                        data: csvData,
                    });
                })
                .on('error', (error) => {
                    console.log('ERROR - getData: ', error);
                    reject({ err: error });
                });
        } else {
            console.log('ERROR - getData: Missing file at', csvPath);
            reject({ err: 'ERROR - getData: Missing file at', csvPath });
        }
    });
};