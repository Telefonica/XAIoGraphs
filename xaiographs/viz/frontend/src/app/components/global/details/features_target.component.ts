/*
    © 2023 Telefónica Digital España S.L.

    This file is part of XAIoGraphs.

    XAIoGraphs is free software: you can redistribute it and/or modify it under the terms of
    the Affero GNU General Public License as published by the Free Software Foundation,
    either version 3 of the License, or (at your option) any later version.

    XAIoGraphs is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the Affero GNU General Public License for more details.

    You should have received a copy of the Affero GNU General Public License along with XAIoGraphs.
    If not, see https://www.gnu.org/licenses/.
*/

import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ChartType } from 'angular-google-charts';
import html2canvas from "html2canvas";

import { jsonFiles } from '../../../constants/jsonFiles';
import { ctsTheme } from '../../../constants/theme';
import { ctsGlobal } from '../../../constants/global';

@Component({
    selector: 'app-global-target-features',
    templateUrl: './features_target.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalFeaturesTargetComponent implements OnInit, OnDestroy {
    @ViewChild('exportableArea') exportableArea;
    hidePicture: boolean = false;

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
    dataGraphNoFrec: any[] = [];
    columnNames: any[] = [];
    columnNamesNoFrec: any[] = [];
    options: any = {};
    optionsNoFrec: any = {};
    displayGraph: boolean = false;

    colorTheme: any;

    showFrecuency: boolean = true;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.globalTargetChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
            this.generateGraphNoFrec();
        });
        this.featuresSubscription = this._apiEmitter.globalFeaturesChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
            this.generateGraphNoFrec();
        });
        this.frecuencySubscription = this._apiEmitter.globalFrecuencyChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
            this.generateGraphNoFrec();
        });
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.initGraph();
            this.generateGraph();
            this.generateGraphNoFrec();
        });
        this.prepareTheme();
    }

    ngOnInit() {
        this._apiReader.readJSON(jsonFiles.global_graph_nodes).subscribe({
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                if (this.serviceResponse.length > 0) {
                    this.initGraph();
                    this.filterData();
                    this.generateGraph();
                    this.generateGraphNoFrec();
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
        this.colorTheme = JSON.parse('' + localStorage.getItem(ctsTheme.storageName))
    }

    initGraph() {
        this.dataGraph = [];
        this.dataGraphNoFrec = [];

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

        this.optionsNoFrec = {
            legend: 'none',
            bar: { groupWidth: '90%' },
            chartArea: { right: 20, top: 20, width: '75%', height: '90%' },
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

            transformDataSet.push([
                data.node_name,
                Math.abs(importance),
                (importance > 0) ? "fill-color: " + this.colorTheme.positiveValue : "fill-color: " + this.colorTheme.negativeValue,
                '<table style="padding:5px; width:150px;"><tr>' +
                '<td colspan="2" style="font-weight:bold; text-align:center; font-size:13px; color: #019ba9;">' + data.node_name + '</td>' +
                '</tr><tr>' +
                '<td colspan="2" style="border-bottom: 1px solid black; margin:10px;"></td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Importance</td>' +
                '<td style="text-align:right; padding-right: 5px">' + importance.toFixed(5) + '</td>' +
                '</tr></table>',
                parseFloat(data.node_name_ratio),
                "fill-color: " + this.colorTheme.frecuencyValue,
                '<table style="padding:5px; width:150px;"><tr>' +
                '<td colspan="2" style="font-weight:bold; text-align:center; font-size:13px; color: #019ba9;">' + data.node_name + '</td>' +
                '</tr><tr>' +
                '<td colspan="2" style="border-bottom: 1px solid black; margin:10px;"></td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Count</td>' +
                '<td style="text-align:right; padding-right: 5px">' + parseInt(data.node_count) + '</td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Frecuency</td>' +
                '<td style="text-align:right; padding-right: 5px">' + (parseFloat(data.node_name_ratio) * 100).toFixed(2) + '%' + '</td>' +
                '</tr></table>',
            ]);
        });

        this.dataGraph = transformDataSet;
    }

    generateGraphNoFrec() {
        let transformDataSet: any[] = [];

        this.columnNamesNoFrec = [
            'Feature',
            'Weight',
            { role: 'style' },
            { 'type': 'string', 'role': 'tooltip', 'p': { 'html': true } },
        ];

        this.dataSource.forEach((data: any) => {
            const importance = parseFloat(data.node_importance);

            transformDataSet.push([
                data.node_name,
                Math.abs(importance),
                (importance > 0) ? "fill-color: " + this.colorTheme.positiveValue : "fill-color: " + this.colorTheme.negativeValue,
                '<table style="padding:5px; width:150px;"><tr>' +
                '<td colspan="2" style="font-weight:bold; text-align:center; font-size:13px; color: #019ba9;">' + data.node_name + '</td>' +
                '</tr><tr>' +
                '<td colspan="2" style="border-bottom: 1px solid black; margin:10px;"></td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Importance</td>' +
                '<td style="text-align:right; padding-right: 5px">' + importance.toFixed(5) + '</td>' +
                '</tr></table>',
            ]);
        });

        this.dataGraphNoFrec = transformDataSet;
    }

    downloadPicture() {
        this.hidePicture = true
        this.generateImage2Download()
    }
    generateImage2Download() {
        this._apiSnackBar.openDownloadSnackBar(ctsGlobal.downloading_message, false).finally(() => {
            html2canvas(this.exportableArea.nativeElement).then(exportCanvas => {
                const canvas = exportCanvas.toDataURL().replace(/^data:image\/[^;]*/, 'data:application/octet-stream');
                let link = document.createElement('a');
                link.download = ctsGlobal.label_global_target_Features_values_importance + ctsGlobal.image_extension;
                link.href = canvas;
                link.click();
                this.hidePicture = false
            }).catch((err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
                this.hidePicture = false
            });
        })
    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
        this.frecuencySubscription.unsubscribe();
        this.themeSubscription.unsubscribe();
    }

}
