import { Component, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import cytoscape from 'cytoscape';

import { ctsFiles } from '../../../constants/csvFiles';
import { nodeGraphStyle0, edgeGraphStyle0 } from '../themes/global0';
import { nodeGraphStyle1, edgeGraphStyle1 } from '../themes/global1';

@Component({
    selector: 'app-global-target-graph',
    templateUrl: './graph.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalGraphComponent implements OnDestroy {

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

    nodeGraphStyle: any;
    edgeGraphStyle: any;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.globalTargetChangeEmitter.subscribe(() => {
            this.getData();
        });
        this.featuresSubscription = this._apiEmitter.globalFeaturesChangeEmitter.subscribe(() => {
            this.getData();
        });
        this.frecuencySubscription = this._apiEmitter.globalFrecuencyChangeEmitter.subscribe(() => {
            this.getData();
        });
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.generateGraph();
        });
    }

    getData() {
        this.currentTarget = this._apiEmitter.getGlobalTarget();
        this.currentFeatures = this._apiEmitter.getGlobalFeatures();
        this.currentFrecuency = this._apiEmitter.getGlobalFrecuency();

        const bodyNodes = {
            fileName: ctsFiles.global_graph_nodes,
            target: this.currentTarget,
            numFeatures: this.currentFeatures,
            numFrecuency: this.currentFrecuency,
        }

        this._apiReader.readGlobalNodesWeights(bodyNodes).subscribe({
            next: (responseNodes: any) => {
                this.nodeList = responseNodes;
                this.nodeNames = responseNodes.map((row: any) => {
                    return row.node_name;
                });
            },
            complete: () => {
                const bodyEdges = {
                    fileName: ctsFiles.global_graph_edges,
                    target: this.currentTarget,
                    nodeNames: this.nodeNames,
                }

                this._apiReader.readGlobalEdgesWeights(bodyEdges).subscribe({
                    next: (responseEdges: any) => {
                        this.edgeList = responseEdges;
                    },
                    complete: () => {
                        this.prepareTheme();
                        this.generateGraph();
                    },
                    error: (err) => {
                        this._apiSnackBar.openSnackBar(JSON.stringify(err));
                    }
                });
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    prepareTheme() {
        if(!this._apiEmitter.getTheme()) {
            this.nodeGraphStyle = nodeGraphStyle0
            this.edgeGraphStyle = edgeGraphStyle0
        } else {
            this.nodeGraphStyle = nodeGraphStyle1
            this.edgeGraphStyle = edgeGraphStyle1
        }
    }

    generateGraph() {
        let elements: any[] = [];

        this.nodeList.forEach((node: any) => {
            const weightNode = parseFloat(node.node_weight);
            const weightNodeIndex = (Math.trunc(weightNode / 10) - 1) % this.nodeGraphStyle.length;

            elements.push({
                data: {
                    id: node.node_name,
                    label: node.node_name,
                },
                style: {
                    'background-color': this.nodeGraphStyle[weightNodeIndex],
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
        }).addListener('click', 'nodes', (event) => {
            this.getNodeDetails(event.target._private.data.id)
        });

    }

    getNodeDetails(node_name) {
        const detailsBody = {
            fileNodesName: ctsFiles.global_graph_nodes,
            fileEdgesName: ctsFiles.global_graph_edges,
            target: this.currentTarget,
            feature: node_name
        };
        this._apiReader.readGlobalGraphDetails(detailsBody).subscribe({
            next: (response: any) => {
            },
            complete: () => {
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
        this.frecuencySubscription.unsubscribe();
        this.themeSubscription.unsubscribe();
    }
}
