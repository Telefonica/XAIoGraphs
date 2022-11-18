import { Component, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ChartType } from 'angular-google-charts';

import { ctsFiles } from '../../../constants/csvFiles';
import { featuresImportanceTargetGraphStyle, featuresFrecuencyTargetGraphStyle } from '../../../../assets/global';

@Component({
    selector: 'app-global-target-features',
    templateUrl: './features_target.component.html',
})
export class GlobalFeaturesTargetComponent implements OnDestroy {

    currentTarget = '';
    currentFeatures = 0;
    currentFrecuency = 0;

    targetSubscription: any;
    featuresSubscription: any;
    frecuencySubscription: any;

    serviceResponse: any;

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
        this.frecuencySubscription = this._apiEmitter.globalFrecuencyChangeEmitter.subscribe(() => {
            this.getData();
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
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                if (this.serviceResponse.length > 0) {
                    this.initGraph();
                    this.generateGraph();
                    this.displayGraph = true;
                } else {
                    this.displayGraph = false;
                }
            },
            error: (err) => {
                this.displayGraph = false;
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
            series: {
                0: { targetAxisIndex: 0 },
                1: { targetAxisIndex: 1 }
            },
            yAxes: {
                0: { title: 'parsecs' },
                1: { title: 'apparent magnitude' }
            }
        };
    }

    generateGraph() {
        let transformDataSet: any[] = [];

        this.columnNames = ['Feature', 'Weight', { role: 'style' }, 'Frecuency', { role: 'style' }];

        this.serviceResponse.forEach((data: any) => {
            const barStyleIMP = JSON.stringify(featuresImportanceTargetGraphStyle[Math.trunc(parseFloat(data.node_weight) / 10) - 1]).replace('{', '').replace('}', '').replace(/"/g, '').replace(/,/g, ';');
            const barStyleFREC = JSON.stringify(featuresFrecuencyTargetGraphStyle[Math.trunc(parseFloat(data.node_name_ratio_weight) / 10) - 1]).replace('{', '').replace('}', '').replace(/"/g, '').replace(/,/g, ';');
            transformDataSet.push([
                data.node_name,
                parseFloat(data.node_importance),
                barStyleIMP,
                parseFloat(data.total_count),
                barStyleFREC
            ]);
        });

        this.dataGraph = transformDataSet;
    }


    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
    }

}
