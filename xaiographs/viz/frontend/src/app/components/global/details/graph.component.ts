/*
    © 2023 Telefónica Digital España S.L.

    This file is part of XAIoGraphs.

    XAIoGraphs is free software: you can redistribute it and/or modify it under the terms of
    the Affero GNU General Public License as published by the Free Software Foundation,
    either version 3 of the License, or (at your option) any later version.

    XAIoGraphs is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the Affero GNU General Public License for more details.

    You should have received a copy of the Affero GNU General Public License along with XAIoGraphs.
    If not, see https://www.gnu.org/licenses/.
*/

import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import cytoscape from 'cytoscape';
import html2canvas from "html2canvas";

import { jsonFiles } from '../../../constants/jsonFiles';
import { ctsTheme } from '../../../constants/theme';
import { ctsGlobal } from '../../../constants/global';

@Component({
    selector: 'app-global-target-graph',
    templateUrl: './graph.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalGraphComponent implements OnInit, OnDestroy {
    @ViewChild('exportableArea') exportableArea;
    hidePicture: boolean = false;

    currentTarget = '';
    currentFeatures = 0;
    currentFrecuency = 0;

    targetSubscription: any;
    featuresSubscription: any;
    frecuencySubscription: any;
    themeSubscription: any;

    nodeList = [];
    edgeList = [];
    nodeNames = [];

    colorTheme: any;
    showLegend: boolean = false;

    nodesJson = []
    edgesJson = []

    detailedNode: string = ''
    nodeDetailList = [];
    edgeDetailList = [];
    nodeDetailNames: string[] = [];

    nodeOver: boolean = false
    nodeNameOver: string = ''
    nodeImportanceOver: number = 0
    nodeRatioOver: number = 0
    nodeTopOver: number = 0
    nodeLeftOver: number = 0

    mouseTopPosition: number = 0
    mouseLeftPosition: number = 0

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.globalTargetChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
            this.detailedNode = ''
        });
        this.featuresSubscription = this._apiEmitter.globalFeaturesChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
            if (this.detailedNode != '') {
                this.filterDetailData();
                this.generateDetailGraph();
            };
        });
        this.frecuencySubscription = this._apiEmitter.globalFrecuencyChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
            if (this.detailedNode != '') {
                this.filterDetailData();
                this.generateDetailGraph();
            }
        });
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.generateGraph();
            this.generateDetailGraph();
            if (this.detailedNode != '') {
                this.generateDetailGraph();
            }
        });
    }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.global_graph_nodes).subscribe({
            next: (responseNodes: any) => {
                this.nodesJson = responseNodes;
            },
            complete: () => {
                this._apiReader.readJSON(jsonFiles.global_graph_edges).subscribe({
                    next: (responseEdges: any) => {
                        this.edgesJson = responseEdges;
                    },
                    complete: () => {
                        this.prepareTheme();
                        this.filterData();
                        this.generateGraph();
                        if (this.detailedNode != '') {
                            this.filterDetailData();
                            this.generateDetailGraph();
                        }
                    },
                    error: (err) => {
                        this._apiSnackBar.openSnackBar(JSON.stringify(err));
                    }
                })
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        })
    }

    prepareTheme() {
        this.colorTheme = JSON.parse('' + localStorage.getItem(ctsTheme.storageName))
        this.showLegend = true;
    }

    filterData() {
        this.nodeNames = []

        this.currentTarget = this._apiEmitter.getGlobalTarget();
        this.currentFeatures = this._apiEmitter.getGlobalFeatures();
        this.currentFrecuency = this._apiEmitter.getGlobalFrecuency();

        this.nodeList = this.nodesJson.filter((node: any) => {
            return node.target == this.currentTarget
                && parseInt(node.node_name_ratio_rank) <= this.currentFrecuency
        }).slice(0, this.currentFeatures);
        const nodeNames = this.nodeList.map((node: any) => {
            return node.node_name;
        });

        this.edgeList = this.edgesJson.filter((edge: any) => {
            return nodeNames.includes(edge.node_1)
                && nodeNames.includes(edge.node_2);
        });
    }

    filterDetailData() {
        if (this.nodeList.filter((node: any) => node.node_name == this.detailedNode).length == 0)
            this.detailedNode = ''
        else {
            this.nodeDetailNames = []

            this.edgeDetailList = this.edgeList.filter((edge: any) => (edge.node_1 == this.detailedNode || edge.node_2 == this.detailedNode));
            this.edgeDetailList.forEach((edge: any) => {
                if (edge.node_1 != this.detailedNode)
                    this.nodeDetailNames.push(edge.node_1)
                if (edge.node_2 != this.detailedNode)
                    this.nodeDetailNames.push(edge.node_2)
            })
            this.nodeDetailNames.push(this.detailedNode)
            this.nodeDetailList = this.nodeList.filter((node: any) => this.nodeDetailNames.includes(node.node_name) && node.target == this.currentTarget)
            this.generateDetailGraph()
        }
    }

    generateGraph() {
        if (this.nodeList.length > 0) {
            let elements: any[] = [];

            this.nodeList.forEach((node: any) => {
                const importance = parseFloat(node.node_importance)
                const weightNode = parseFloat(node.node_weight);

                elements.push({
                    data: {
                        id: node.node_name,
                        label: node.node_name,
                    },
                    style: {
                        'background-color': (importance > 0) ? this.colorTheme.positiveValue : this.colorTheme.negativeValue,
                        height: weightNode,
                        width: weightNode,
                    }
                });
            });


            this.edgeList.forEach((edge: any) => {
                const weightEdge = parseFloat(edge.edge_weight);

                if (
                    (this.nodeList.filter((node: any) => node.node_name === edge.node_1).length > 0) &&
                    (this.nodeList.filter((node: any) => node.node_name === edge.node_2).length > 0)
                ) {
                    elements.push({
                        data: {
                            id: edge.node_1 + '-' + edge.node_2,
                            source: edge.node_1,
                            target: edge.node_2,
                        },
                        style: {
                            width: weightEdge,
                            'line-color': this.colorTheme.frecuencyValue
                        }
                    });
                }
            });

            const style = [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)'
                    }
                }
            ];

            const layout = {
                name: 'circle'
            };

            cytoscape({
                container: document.getElementById('divGraph'),
                elements: elements,
                style: style,
                layout: layout,
                zoomingEnabled: true,
                userZoomingEnabled: false,
            }).on('click', (event) => {
                if (event.target.edges().length == 0) {
                    this.detailedNode = event.target.id()
                    this.nodeOver = false
                    this.nodeNameOver = ''
                    this.nodeImportanceOver = 0
                    this.nodeRatioOver = 0
                    this.filterDetailData()
                    this.generateDetailGraph()
                }
            }).on('mouseover', (event) => {
                if (event.target.edges().length == 0) {
                    const nodeOver: any[] = this.nodeList.filter((node: any) => node.node_name == event.target.id())
                    if (nodeOver.length > 0) {
                        this.nodeOver = true
                        this.nodeNameOver = nodeOver[0].node_name
                        this.nodeImportanceOver = nodeOver[0].node_importance.toFixed(5)
                        this.nodeRatioOver = nodeOver[0].node_name_ratio.toFixed(5)

                        this.nodeTopOver = this.mouseTopPosition + 20
                        this.nodeLeftOver = this.mouseLeftPosition - 100
                    }
                }
            }).on('mouseout', () => {
                this.nodeOver = false
                this.nodeNameOver = ''
                this.nodeImportanceOver = 0
                this.nodeRatioOver = 0
            });
        }
    }

    generateDetailGraph() {
        if (this.nodeDetailList.length > 0) {
            let elements: any[] = [];

            this.nodeDetailList.forEach((node: any) => {
                const importance = parseFloat(node.node_importance)
                const weightNode = parseFloat(node.node_weight);

                let currentElement = {
                    data: {
                        id: node.node_name,
                        label: node.node_name,
                    },
                    style: {
                        'background-color': (importance > 0) ? this.colorTheme.positiveValue : this.colorTheme.negativeValue,
                        height: weightNode,
                        width: weightNode,
                    }
                }

                if (node.node_name == this.detailedNode) {
                    currentElement.style['border-width'] = '5px'
                    currentElement.style['border-color'] = 'black'
                }

                elements.push(currentElement);
            });


            this.edgeDetailList.forEach((edge: any) => {
                const weightEdge = parseFloat(edge.edge_weight);

                if (
                    (this.nodeDetailList.filter((node: any) => node.node_name === edge.node_1).length > 0) &&
                    (this.nodeDetailList.filter((node: any) => node.node_name === edge.node_2).length > 0)
                ) {
                    elements.push({
                        data: {
                            id: edge.node_1 + '-' + edge.node_2,
                            source: edge.node_1,
                            target: edge.node_2,
                        },
                        style: {
                            width: weightEdge,
                            'line-color': this.colorTheme.frecuencyValue
                        }
                    });
                }
            });

            const style = [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'font-size': '15px'
                    }
                }
            ];

            const layout = {
                name: 'circle',
                fit: true,
                spacingFactor: 1,
            };

            cytoscape({
                container: document.getElementById('divGraph'),
                elements: elements,
                style: style,
                layout: layout,
                zoomingEnabled: true,
                userZoomingEnabled: false,
            }).on('click', (event) => {
                if (event.target.edges().length == 0) {
                    if (event.target.id() == this.detailedNode) {
                        this.detailedNode = ''
                        this.filterData()
                        this.generateGraph()
                    } else {
                        this.detailedNode = event.target.id()
                        this.filterDetailData()
                        this.generateDetailGraph()
                    }
                }
            }).on('mouseover', (event) => {
                if (event.target.edges().length == 0) {
                    const nodeOver: any[] = this.nodeList.filter((node: any) => node.node_name == event.target.id())
                    if (nodeOver.length > 0) {
                        this.nodeOver = true
                        this.nodeNameOver = nodeOver[0].node_name
                        this.nodeImportanceOver = nodeOver[0].node_importance.toFixed(5)
                        this.nodeRatioOver = nodeOver[0].node_name_ratio.toFixed(5)

                        this.nodeTopOver = this.mouseTopPosition + 20
                        this.nodeLeftOver = this.mouseLeftPosition - 100
                    }
                }
            }).on('mouseout', () => {
                this.nodeOver = false
                this.nodeNameOver = ''
                this.nodeImportanceOver = 0
                this.nodeRatioOver = 0
            });
        }
    }

    mouseMoved(event) {
        this.mouseLeftPosition = event.offsetX
        this.mouseTopPosition = event.offsetY
    }

    downloadPicture() {
        this.hidePicture = true
        this.generateImage2Download()
    }
    generateImage2Download() {
        this._apiSnackBar.openDownloadSnackBar(ctsGlobal.downloading_message, false).finally(() => {
            html2canvas(this.exportableArea.nativeElement).then(exportCanvas => {
                const canvas = exportCanvas.toDataURL().replace(/^data:image\/[^;]*/, 'data:application/octet-stream');
                let link = document.createElement('a');
                link.download = ctsGlobal.label_global_target_Features_values_relations + ctsGlobal.image_extension;
                link.href = canvas;
                link.click();
                this.hidePicture = false
            }).catch((err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
                this.hidePicture = false
            });
        })
    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
        this.frecuencySubscription.unsubscribe();
        this.themeSubscription.unsubscribe();
    }
}
