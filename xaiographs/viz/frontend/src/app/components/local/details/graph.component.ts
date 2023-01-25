import { Component, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import cytoscape from 'cytoscape';

import { ctsFiles } from '../../../constants/csvFiles';
import { positiveNodeGraphStyle, negativeNodeGraphStyle, edgeGraphStyle } from '../../../../assets/local';

@Component({
    selector: 'app-local-graph',
    templateUrl: './graph.component.html',
    styles: [
    ]
})
export class LocalGraphComponent implements OnDestroy {

    currentTarget: any;
    currentFeatures = 0;

    targetSubscription: any;
    featuresSubscription: any;

    nodeList = [];
    edgeList = [];
    nodeNames = [];

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
                        console.log(this.nodeList);
                        console.log(this.edgeList);
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
            const importance = parseFloat(node.node_importance);

            let backgroundColor = '';

            if (importance > 0) {
                const graphStyleIndex = (Math.trunc(weight / 10) - 1) % positiveNodeGraphStyle.length;
                backgroundColor = positiveNodeGraphStyle[graphStyleIndex];
            } else {
                const graphStyleIndex = (Math.trunc(weight / 10) - 1) % negativeNodeGraphStyle.length;
                backgroundColor = negativeNodeGraphStyle[graphStyleIndex]
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
            const weightIndex = (Math.trunc(weight / 2)) % edgeGraphStyle.length;
            elements.push({
                data: {
                    id: edge.node_1 + '-' + edge.node_2,
                    source: edge.node_1,
                    target: edge.node_2,
                },
                style: {
                    width: weight,
                    'line-color': edgeGraphStyle[weightIndex],

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
    };

}
