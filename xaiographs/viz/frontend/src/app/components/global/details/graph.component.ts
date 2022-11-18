import { Component, OnInit, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import cytoscape from 'cytoscape';

import { ctsFiles } from '../../../constants/csvFiles';
import { nodeGraphStyle, edgeGraphStyle } from '../../../../assets/global';

@Component({
    selector: 'app-global-target-graph',
    templateUrl: './graph.component.html',
})
export class GlobalGraphComponent implements OnInit, OnDestroy {

    currentTarget = '';
    currentFeatures = 0;
    currentFrecuency = 0;

    targetSubscription: any;
    featuresSubscription: any;
    frecuencySubscription: any;

    nodeList = [];
    edgeList = [];
    nodeNames = [];

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
    }

    ngOnInit(): void { }

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

    generateGraph() {
        let elements: any[] = [];

        this.nodeList.forEach((node: any) => {
            const weight = parseFloat(node.node_weight);
            elements.push({
                data: {
                    id: node.node_name,
                    label: node.node_name,
                },
                style: {
                    'background-color': nodeGraphStyle[Math.trunc(weight / 10) - 1],
                    height: weight,
                    width: weight,
                }
            });
        });

        this.edgeList.forEach((edge: any) => {
            const weight = parseFloat(edge.edge_weight);
            elements.push({
                data: {
                    id: edge.node_1 + '-' + edge.node_2,
                    source: edge.node_1,
                    target: edge.node_2,
                },
                style: {
                    width: weight,
                    'line-color': edgeGraphStyle[Math.trunc(weight / 2)],
                }
            });
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
    }
}
