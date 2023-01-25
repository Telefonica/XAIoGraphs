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
            bar: { groupWidth: '90%' },
            chartArea:{right:20,top:20,width:'75%',height:'90%'},
            series: {
                0: { targetAxisIndex: 0 },
                1: { targetAxisIndex: 1 }
            },
            yAxes: {
                0: { title: 'importance' },
                1: { title: 'frecuency' }
            },
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
            'Frecuency',
            { role: 'style' },
            { 'type': 'string', 'role': 'tooltip', 'p': { 'html': true } },
        ];

        this.serviceResponse.forEach((data: any) => {
            const importance = parseFloat(data.node_importance);
            const count = parseInt(data.node_count);
            const frecuency = parseFloat(data.node_name_ratio);

            const barStyleIMPIndex = (Math.trunc(parseFloat(data.node_weight) / 10) - 1) % featuresImportanceTargetGraphStyle.length;
            const barStyleFRECIndex = (Math.trunc(parseFloat(data.node_name_ratio_weight) / 10) - 1) % featuresFrecuencyTargetGraphStyle.length;

            const barStyleIMP = this.JSONCleaner(featuresImportanceTargetGraphStyle[barStyleIMPIndex]);
            const barStyleFREC = this.JSONCleaner(featuresFrecuencyTargetGraphStyle[barStyleFRECIndex]);

            transformDataSet.push([
                data.node_name,
                importance,
                barStyleIMP,
                '<table style="padding:5px; width:150px;"><tr>' +
                '<td colspan="2" style="font-weight:bold; text-align:center; font-size:13px; color: #019ba9;">' + data.node_name + '</td>' +
                '</tr><tr>' +
                '<td colspan="2" style="border-bottom: 1px solid black; margin:10px;"></td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Importance</td>' +
                '<td style="text-align:right; padding-right: 5px">' + importance.toFixed(5) + '</td>' +
                '</tr></table>',
                parseFloat(data.node_name_ratio),
                barStyleFREC,
                '<table style="padding:5px; width:150px;"><tr>' +
                '<td colspan="2" style="font-weight:bold; text-align:center; font-size:13px; color: #019ba9;">' + data.node_name + '</td>' +
                '</tr><tr>' +
                '<td colspan="2" style="border-bottom: 1px solid black; margin:10px;"></td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Count</td>' +
                '<td style="text-align:right; padding-right: 5px">' + count + '</td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Frecuency</td>' +
                '<td style="text-align:right; padding-right: 5px">' + (frecuency * 100).toFixed(2) + '%' + '</td>' +
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
