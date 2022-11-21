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
            tooltip: { type: 'string', isHtml: true },
        };
    }

    generateGraph() {
        let transformDataSet: any[] = [];

        this.columnNames = [
            'Feature',
            'Weight',
            { role: 'style' },
            { 'type': 'string', 'role': 'tooltip', 'p': { 'html': true } },
        ];

        this.serviceResponse.forEach((data: any, index: number) => {
            let barStyle = '';
            const nodeImportance = parseFloat(data.node_importance);

            if (nodeImportance > 0) {
                const barStyleIndex = (Math.trunc(parseFloat(data.node_weight) / 10) - 1) % positiveFeaturesGraphStyle.length;
                barStyle = this.JSONCleaner(positiveFeaturesGraphStyle[barStyleIndex]);
            } else {
                const barStyleIndex = (Math.trunc(parseFloat(data.node_weight) / 10) - 1) % negativeFeaturesGraphStyle.length;
                barStyle = this.JSONCleaner(negativeFeaturesGraphStyle[barStyleIndex]);
            }
            transformDataSet.push([
                data.node_name,
                nodeImportance,
                barStyle,
                '<table style="padding:5px; width:150px;"><tr>' +
                '<td colspan="2" style="font-weight:bold; text-align:center; font-size:13px; color: #019ba9;">' + data.node_name + '</td>' +
                '</tr><tr>' +
                '<td colspan="2" style="border-bottom: 1px solid black; margin:10px;"></td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Importance</td>' +
                '<td style="text-align:right; padding-right: 5px">' + nodeImportance.toFixed(5) + '</td>' +
                '</tr></table>',
            ]);
        });

        this.dataGraph = transformDataSet;
    }

    JSONCleaner(value) {
        return JSON.stringify(value)
            .replace('{', '')
            .replace('}', '')
            .replace(/"/g, '')
            .replace(/,/g, ';')
    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
    }

}
