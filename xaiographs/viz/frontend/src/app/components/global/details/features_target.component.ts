import { Component, OnInit, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ChartType } from 'angular-google-charts';

import { jsonFiles } from '../../../constants/jsonFiles';
import { featuresImportanceTargetGraphStyle0, featuresFrecuencyTargetGraphStyle0 } from '../themes/global0';
import { featuresImportanceTargetGraphStyle1, featuresFrecuencyTargetGraphStyle1 } from '../themes/global1';

@Component({
    selector: 'app-global-target-features',
    templateUrl: './features_target.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalFeaturesTargetComponent implements OnInit, OnDestroy {

    currentTarget = '';
    currentFeatures = 0;
    currentFrecuency = 0;

    themeSubscription: any;
    targetSubscription: any;
    featuresSubscription: any;
    frecuencySubscription: any;

    serviceResponse = [];
    dataSource = [];

    type = ChartType.BarChart;
    dataGraph: any[] = [];
    columnNames: any[] = [];
    options: any = {};
    displayGraph: boolean = false;

    featuresImportanceTargetGraphStyle: any;
    featuresFrecuencyTargetGraphStyle: any;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.globalTargetChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
        });
        this.featuresSubscription = this._apiEmitter.globalFeaturesChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
        });
        this.frecuencySubscription = this._apiEmitter.globalFrecuencyChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
        });
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.initGraph();
            this.generateGraph();
        });
    }

    ngOnInit() {
        this._apiReader.readJSON(jsonFiles.global_graph_nodes).subscribe({
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                if (this.serviceResponse.length > 0) {
                    this.prepareTheme();
                    this.initGraph();
                    this.filterData();
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

    prepareTheme() {
        if (!this._apiEmitter.getTheme()) {
            this.featuresImportanceTargetGraphStyle = featuresImportanceTargetGraphStyle0
            this.featuresFrecuencyTargetGraphStyle = featuresFrecuencyTargetGraphStyle0
        } else {
            this.featuresImportanceTargetGraphStyle = featuresImportanceTargetGraphStyle1
            this.featuresFrecuencyTargetGraphStyle = featuresFrecuencyTargetGraphStyle1
        }
    }

    initGraph() {
        this.dataGraph = [];
        this.options = {
            legend: 'none',
            bar: { groupWidth: '90%' },
            chartArea: { right: 20, top: 20, width: '75%', height: '90%' },
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

    filterData() {
        this.currentTarget = this._apiEmitter.getGlobalTarget();
        this.currentFeatures = this._apiEmitter.getGlobalFeatures();
        this.currentFrecuency = this._apiEmitter.getGlobalFrecuency();

        this.dataSource = this.serviceResponse.filter((row: any) => {
            return row.target == this.currentTarget
                && parseInt(row.node_name_ratio_rank) <= this.currentFrecuency;
        }).slice(0, this.currentFeatures);
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

        this.dataSource.forEach((data: any) => {
            const importance = parseFloat(data.node_importance);
            const count = parseInt(data.node_count);
            const frecuency = parseFloat(data.node_name_ratio);

            const barStyleIMPIndex = (Math.trunc(parseFloat(data.node_weight) / 10) - 1) % this.featuresImportanceTargetGraphStyle.length;
            const barStyleFRECIndex = (Math.trunc(parseFloat(data.node_name_ratio_weight) / 10) - 1) % this.featuresFrecuencyTargetGraphStyle.length;

            const barStyleIMP = this.JSONCleaner(this.featuresImportanceTargetGraphStyle[barStyleIMPIndex]);
            const barStyleFREC = this.JSONCleaner(this.featuresFrecuencyTargetGraphStyle[barStyleFRECIndex]);

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
        this.frecuencySubscription.unsubscribe();
        this.themeSubscription.unsubscribe();
    }

}
