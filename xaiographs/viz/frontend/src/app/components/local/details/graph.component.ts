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

    colorTheme: any;
    showLegend: boolean = false;

    nodesJson = [];
    edgesJson = [];

    detailedNode: string = ''
    nodeDetailList = [];
    edgeDetailList = [];
    nodeDetailNames: string[] = [];

    nodeOver: boolean = false
    nodeNameOver: string = ''
    nodeImportanceOver: number = 0
    nodeTopOver: number = 0
    nodeLeftOver: number = 0

    mouseTopPosition: number = 0
    mouseLeftPosition: number = 0

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.localTargetChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
            if (this.detailedNode != '') {
                this.filterDetailData();
                this.generateDetailGraph();
            }
        });
        this.featuresSubscription = this._apiEmitter.localFeaturesChangeEmitter.subscribe(() => {
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
            if (this.detailedNode != '') {
                this.filterDetailData();
                this.generateDetailGraph();
            }
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
            this.nodeDetailList = this.nodeList.filter((node: any) => this.nodeDetailNames.includes(node.node_name) && node.id == this.currentTarget.id)
            this.generateDetailGraph()
        }
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
            }).on('click', (event) => {
                if (event.target.edges().length == 0) {
                    this.detailedNode = event.target.id()
                    this.nodeOver = false
                    this.nodeNameOver = ''
                    this.nodeImportanceOver = 0
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

                        this.nodeTopOver = this.mouseTopPosition + 20
                        this.nodeLeftOver = this.mouseLeftPosition - 100
                    }
                }
            }).on('mouseout', () => {
                this.nodeOver = false
                this.nodeNameOver = ''
                this.nodeImportanceOver = 0
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

                        this.nodeTopOver = this.mouseTopPosition + 20
                        this.nodeLeftOver = this.mouseLeftPosition - 100
                    }
                }
            }).on('mouseout', () => {
                this.nodeOver = false
                this.nodeNameOver = ''
                this.nodeImportanceOver = 0
            });
        }
    }

    mouseMoved(event) {
        this.mouseLeftPosition = event.offsetX
        this.mouseTopPosition = event.offsetY
    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
        this.themeSubscription.unsubscribe();
    };

}
