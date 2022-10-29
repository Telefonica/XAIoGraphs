import { Component, OnInit, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import cytoscape from 'cytoscape';

import { ctsFiles } from '../../../constants/csvFiles';
import { nodeGraphStyle } from '../../../../assets/global';
import { edgeGraphStyle } from '../../../../assets/global';

@Component({
    selector: 'app-global-target-graph',
    templateUrl: './graph.component.html',
})
export class GlobalGraphComponent implements OnInit, OnDestroy {

    currentTarget = '';
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
        this.targetSubscription = this._apiEmitter.globalTargetChangeEmitter.subscribe(() => {
            this.getData();
        });
        this.featuresSubscription = this._apiEmitter.globalFeaturesChangeEmitter.subscribe(() => {
            this.getData();
        });
    }

    ngOnInit(): void { }

    getData() {
        this.currentTarget = this._apiEmitter.getGlobalTarget();
        this.currentFeatures = this._apiEmitter.getGlobalFeatures();

        const bodyNodes = {
            fileName: ctsFiles.global_graph_nodes,
            target: this.currentTarget,
            numFeatures: this.currentFeatures,
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
            const weight = parseFloat(node.node_weight) * 100;
            elements.push({
                data: {
                    id: node.node_name,
                    label: node.node_name,
                },
                style: {
                    'background-color': this.getNodeColor(weight),
                    height: weight,
                    width: weight,
                }
            });
        });

        this.edgeList.forEach((edge: any) => {
            const weight = parseFloat(edge.edge_weight) * 10;
            elements.push({
                data: {
                    id: edge.node_1 + '-' + edge.node_2,
                    source: edge.node_1,
                    target: edge.node_2,
                },
                style: {
                    width: weight,
                    'line-color': this.getEdgeColor(weight),
                }
            });
        });

        const style = [
            {
                selector: 'node',
                style: {
                    'background-color': '#666',
                    'label': 'data(label)',
                    'padding': '5px',
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
            zoomingEnabled: false,
            autoungrabify: true,
        });

    }

    getNodeColor(weight: number) {
        let colorValue = nodeGraphStyle[nodeGraphStyle.length - 1]['color'];
        nodeGraphStyle.every((style: any) => {
            if (style.limit) {
                if (weight < style.limit) {
                    colorValue = style.color;
                    return false;
                }
            }
            return true;
        });
        return colorValue;
    }

    getEdgeColor(weight: number) {
        let colorValue = edgeGraphStyle[edgeGraphStyle.length - 1]['color'];
        edgeGraphStyle.every((style: any) => {
            if (style.limit) {
                if (weight < style.limit) {
                    colorValue = style.color;
                    return false;
                }
            }
            return true;
        });
        return colorValue;
    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
    }
}
