const express = require('express');
const controller = require('./reader.controller');
const router = express.Router();

router.get('/', controller.index);
router.post('/readCSV', controller.readCSV);
router.post('/listGlobalTarget', controller.listGlobalTarget);
router.post('/readGlobalNodesWeights', controller.readGlobalNodesWeights);
router.post('/readGlobalEdgesWeights', controller.readGlobalEdgesWeights);

router.post('/readLocalDataset', controller.readLocalDataset);
router.post('/readLocalNodesWeights', controller.readLocalNodesWeights);
router.post('/readLocalEdgesWeights', controller.readLocalEdgesWeights);
router.post('/readLocalReasonWhy', controller.readLocalReasonWhy);

router.post('/listDatasetHeaders', controller.listDatasetHeaders);
router.post('/readDatasetSelected', controller.readDatasetSelected);

module.exports = router;
