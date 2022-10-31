import { Component, OnInit, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ChartType } from 'angular-google-charts';

import { ctsFiles } from '../../../constants/csvFiles';
import { featuresTargetGraphStyle } from '../../../../assets/global';

@Component({
    selector: 'app-global-target-features',
    templateUrl: './features_target.component.html',
})
export class GlobalFeaturesTargetComponent implements OnInit, OnDestroy {

    currentTarget = '';
    currentFeatures = 0;

    targetSubscription: any;
    featuresSubscription: any;

    nodeList = [];

    type = ChartType.BarChart;
    dataGraph: any[] = [];
    columnNames: any[] = [];
    options: any = {};
    displayGraph: boolean = false;

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
            },
            complete: () => {
                this.initGraph();
                this.generateGraph();
                this.displayGraph = true;
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    initGraph() {
        this.dataGraph = [];
        this.options = {
            legend: 'none',
            bar: { groupWidth: "90%" },
            chartArea: { width: '70%', height: '80%' },
        };
    }

    generateGraph() {
        let transformDataSet: any[] = [];

        this.columnNames = ['Feature', 'Weight', { role: 'style' }];

        this.nodeList.map((data: any, index: number) => {
            const barStyle = JSON.stringify(featuresTargetGraphStyle[index % featuresTargetGraphStyle.length]).replace('{', '').replace('}', '').replace(/"/g, '').replace(/,/g, ';');
            transformDataSet.push([
                data.node_name,
                parseFloat(data.node_importance),
                barStyle
            ]);
        });

        this.dataGraph = transformDataSet;

    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
    }

}
