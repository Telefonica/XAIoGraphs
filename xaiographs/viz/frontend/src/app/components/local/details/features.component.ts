import { Component, OnDestroy } from '@angular/core';

import { ChartType } from 'angular-google-charts';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ctsFiles } from '../../../constants/csvFiles';
import { positiveFeaturesGraphStyle, negativeFeaturesGraphStyle } from '../../../../assets/local';

@Component({
    selector: 'app-local-features',
    templateUrl: './features.component.html'
})
export class LocalFeaturesComponent implements OnDestroy {

    currentTarget = '';
    currentFeatures = 0;

    targetSubscription: any;
    featuresSubscription: any;

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
            target: this.currentTarget,
            numFeatures: this.currentFeatures,
        }

        this._apiReader.readLocalNodesWeights(bodyNodes).subscribe({
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                if(this.serviceResponse.length > 0) {
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
        };
    }

    generateGraph() {
        let transformDataSet: any[] = [];

        this.columnNames = ['Feature', 'Weight', { role: 'style' }];

        this.serviceResponse.forEach((data: any, index: number) => {
            let barStyle = '';
            const nodeImportance = parseFloat(data.node_importance);
            if(nodeImportance > 0) {
                barStyle = JSON.stringify(positiveFeaturesGraphStyle[Math.trunc(parseFloat(data.node_weight) / 10) - 1]).replace('{', '').replace('}', '').replace(/"/g, '').replace(/,/g, ';');
            } else {
                barStyle = JSON.stringify(negativeFeaturesGraphStyle[Math.trunc(parseFloat(data.node_weight) / 10) - 1]).replace('{', '').replace('}', '').replace(/"/g, '').replace(/,/g, ';');
            }
            transformDataSet.push([
                data.node_name,
                nodeImportance,
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
