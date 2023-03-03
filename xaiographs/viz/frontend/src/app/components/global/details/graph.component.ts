import { Component, OnInit, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import cytoscape from 'cytoscape';

import { jsonFiles } from '../../../constants/jsonFiles';
import { nodePositiveGraphStyle0, nodeNegativeGraphStyle0, edgeGraphStyle0 } from '../themes/global0';
import { nodePositiveGraphStyle1, nodeNegativeGraphStyle1, edgeGraphStyle1 } from '../themes/global1';

@Component({
    selector: 'app-global-target-graph',
    templateUrl: './graph.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalGraphComponent implements OnInit, OnDestroy {

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

    nodePositiveGraphStyle: any;
    nodeNegativeGraphStyle: any;
    edgeGraphStyle: any;

    nodesJson = []
    edgesJson = []

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.globalTargetChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
        });
        this.featuresSubscription = this._apiEmitter.globalFeaturesChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
        });
        this.frecuencySubscription = this._apiEmitter.globalFrecuencyChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
        });
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.generateGraph();
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
        if (!this._apiEmitter.getTheme()) {
            this.nodePositiveGraphStyle = nodePositiveGraphStyle0
            this.nodeNegativeGraphStyle = nodeNegativeGraphStyle0
            this.edgeGraphStyle = edgeGraphStyle0
        } else {
            this.nodePositiveGraphStyle = nodePositiveGraphStyle1
            this.nodeNegativeGraphStyle = nodeNegativeGraphStyle1
            this.edgeGraphStyle = edgeGraphStyle1
        }
    }

    filterData() {
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
            return edge.target == this.currentTarget
                && nodeNames.includes(edge.node_1)
                && nodeNames.includes(edge.node_2);
        });
    }

    generateGraph() {
        if (this.nodeList.length > 0) {
            let elements: any[] = [];

            this.nodeList.forEach((node: any) => {
                const importance = parseFloat(node.node_importance)
                const weightNode = parseFloat(node.node_weight);
                const weightNodeIndex = (importance > 0) ? (Math.trunc(weightNode / 10) - 1) % this.nodePositiveGraphStyle.length : (Math.trunc(weightNode / 10) - 1) % this.nodeNegativeGraphStyle.length;

                elements.push({
                    data: {
                        id: node.node_name,
                        label: node.node_name,
                    },
                    style: {
                        'background-color': (importance > 0) ? this.nodePositiveGraphStyle[weightNodeIndex] : this.nodeNegativeGraphStyle[weightNodeIndex],
                        height: weightNode,
                        width: weightNode,
                    }
                });
            });


            this.edgeList.forEach((edge: any) => {
                const weightEdge = parseFloat(edge.edge_weight);
                const weightEdgeIndex = (Math.trunc(weightEdge / 2)) % this.edgeGraphStyle.length;

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
                            'line-color': this.edgeGraphStyle[weightEdgeIndex],
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
            });
        }

    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
        this.frecuencySubscription.unsubscribe();
        this.themeSubscription.unsubscribe();
    }
}
