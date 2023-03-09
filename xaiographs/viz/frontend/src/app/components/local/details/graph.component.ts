import { Component, OnInit, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import cytoscape from 'cytoscape';

import { jsonFiles } from '../../../constants/jsonFiles';
import { ctsTheme } from '../../../constants/theme';

@Component({
    selector: 'app-local-graph',
    templateUrl: './graph.component.html',
    styleUrls: ['../local.component.scss']
})
export class LocalGraphComponent implements OnInit, OnDestroy {

    currentTarget: any;
    currentFeatures = 0;

    targetSubscription: any;
    featuresSubscription: any;
    themeSubscription: any;

    nodeList = [];
    edgeList = [];
    nodeNames = [];

    nodesJson = [];
    edgesJson = [];

    colorTheme: any;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.localTargetChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
        });
        this.featuresSubscription = this._apiEmitter.localFeaturesChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
        });
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.generateGraph();
        });
    }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.local_graph_nodes).subscribe({
            next: (responseNodes: any) => {
                this.nodesJson = responseNodes;
            },
            complete: () => {
                this._apiReader.readJSON(jsonFiles.local_graph_edges).subscribe({
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
        this.colorTheme = JSON.parse('' + localStorage.getItem(ctsTheme.storageName))
    }

    filterData() {
        this.currentTarget = this._apiEmitter.getLocalTarget();
        this.currentFeatures = this._apiEmitter.getLocalFeatures();

        this.nodeList = this.nodesJson.filter((node: any) => {
            return node.id == this.currentTarget.id;
        }).slice(0, this.currentFeatures);
        const nodeNames = this.nodeList.map((node: any) => {
            return node.node_name;
        });

        this.edgeList = this.edgesJson.filter((edge: any) => {
            return edge.id == this.currentTarget.id
                && nodeNames.includes(edge.node_1)
                && nodeNames.includes(edge.node_2);
        });
    }

    generateGraph() {
        if (this.nodeList.length > 0) {
            let elements: any[] = [];

            this.nodeList.forEach((node: any) => {
                const weightNode = parseFloat(node.node_weight);
                const importance = parseFloat(node.node_importance);

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
                elements.push({
                    data: {
                        id: edge.node_1 + '-' + edge.node_2,
                        source: edge.node_1,
                        target: edge.node_2,
                    },
                    style: {
                        width: parseFloat(edge.edge_weight),
                        'line-color': this.colorTheme.frecuencyValue

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

    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
        this.themeSubscription.unsubscribe();
    };

}
