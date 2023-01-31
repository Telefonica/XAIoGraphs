import { Component, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import cytoscape from 'cytoscape';

import { ctsFiles } from '../../../constants/csvFiles';
import { positiveNodeGraphStyle0, negativeNodeGraphStyle0, edgeGraphStyle0 } from '../themes/local0';
import { positiveNodeGraphStyle1, negativeNodeGraphStyle1, edgeGraphStyle1 } from '../themes/local1';

@Component({
    selector: 'app-local-graph',
    templateUrl: './graph.component.html',
    styleUrls: ['../local.component.scss']
})
export class LocalGraphComponent implements OnDestroy {

    currentTarget: any;
    currentFeatures = 0;

    targetSubscription: any;
    featuresSubscription: any;
    themeSubscription: any;

    nodeList = [];
    edgeList = [];
    nodeNames = [];

    positiveNodeGraphStyle: any;
    negativeNodeGraphStyle: any;
    edgeGraphStyle: any;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.localTargetChangeEmitter.subscribe(() => {
            this.getData();
        });
        this.featuresSubscription = this._apiEmitter.localFeaturesChangeEmitter.subscribe(() => {
            this.getData();
        });
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.generateGraph();
        });
    }

    getData() {
        this.currentTarget = this._apiEmitter.getLocalTarget();
        this.currentFeatures = this._apiEmitter.getLocalFeatures();

        const bodyNodes = {
            fileName: ctsFiles.local_graph_nodes,
            target: this.currentTarget.id,
            numFeatures: this.currentFeatures,
        }

        this._apiReader.readLocalNodesWeights(bodyNodes).subscribe({
            next: (responseNodes: any) => {
                this.nodeList = responseNodes;
                this.nodeNames = responseNodes.map((row: any) => {
                    return row.node_name;
                });
            },
            complete: () => {
                const bodyEdges = {
                    fileName: ctsFiles.local_graph_edges,
                    target: this.currentTarget.id,
                    nodeNames: this.nodeNames,
                }

                this._apiReader.readLocalEdgesWeights(bodyEdges).subscribe({
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
        if (!this._apiEmitter.getTheme()) {
            this.positiveNodeGraphStyle = positiveNodeGraphStyle0
            this.negativeNodeGraphStyle = negativeNodeGraphStyle0
            this.edgeGraphStyle = edgeGraphStyle0
        } else {
            this.positiveNodeGraphStyle = positiveNodeGraphStyle1
            this.negativeNodeGraphStyle = negativeNodeGraphStyle1
            this.edgeGraphStyle = edgeGraphStyle1
        }
    }

    generateGraph() {
        let elements: any[] = [];

        this.nodeList.forEach((node: any) => {
            const weight = parseFloat(node.node_weight);
            const importance = parseFloat(node.node_importance);

            let backgroundColor = '';

            if (importance > 0) {
                const graphStyleIndex = (Math.trunc(weight / 10) - 1) % this.positiveNodeGraphStyle.length;
                backgroundColor = this.positiveNodeGraphStyle[graphStyleIndex];
            } else {
                const graphStyleIndex = (Math.trunc(weight / 10) - 1) % this.negativeNodeGraphStyle.length;
                backgroundColor = this.negativeNodeGraphStyle[graphStyleIndex]
            }

            elements.push({
                data: {
                    id: node.node_name,
                    label: node.node_name,
                },
                style: {
                    'background-color': backgroundColor,
                    height: weight,
                    width: weight,
                }
            });
        });

        this.edgeList.forEach((edge: any) => {
            const weight = parseFloat(edge.edge_weight);
            const weightIndex = (Math.trunc(weight / 2)) % this.edgeGraphStyle.length;
            elements.push({
                data: {
                    id: edge.node_1 + '-' + edge.node_2,
                    source: edge.node_1,
                    target: edge.node_2,
                },
                style: {
                    width: weight,
                    'line-color': this.edgeGraphStyle[weightIndex],

                }
            });
        });

        const style = [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
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

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
        this.themeSubscription.unsubscribe();
    };

}
