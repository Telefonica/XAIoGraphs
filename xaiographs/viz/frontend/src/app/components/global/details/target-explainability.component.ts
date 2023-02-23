import { Component, OnDestroy, OnInit } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ChartType } from 'angular-google-charts';

import { jsonFiles } from '../../../constants/jsonFiles';
import { explainabilityGraphStyle0 } from '../themes/global0';
import { explainabilityGraphStyle1 } from '../themes/global1';

@Component({
    selector: 'app-global-target-explainability',
    templateUrl: './target-explainability.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalTargetExplainabilityComponent implements OnInit, OnDestroy {

    currentTarget = '';

    targetSubscription: any;
    themeSubscription: any;

    serviceResponse = [];
    dataSource: any[] = [];

    type = ChartType.BarChart;
    dataGraph: any[] = [];
    columnNames: any[] = [];
    options: any = {};
    displayGraph: boolean = false;

    explainabilityGraphStyle: any;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.globalTargetChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
        });
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.initGraph();
            this.generateGraph();
        });
    }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.global_target_explainability).subscribe({
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
            this.explainabilityGraphStyle = explainabilityGraphStyle0
        } else {
            this.explainabilityGraphStyle = explainabilityGraphStyle1
        }
    }

    initGraph() {
        this.dataGraph = [];
        this.options = {
            legend: 'none',
            bar: { groupWidth: '90%' },
            chartArea: { right: 20, top: 20, width: '75%', height: '85%' },
            tooltip: { type: 'string', isHtml: true },
        };
    }

    filterData() {
        this.currentTarget = this._apiEmitter.getGlobalTarget();
        this.serviceResponse.forEach((row: any) => {
            if (row.target == this.currentTarget) {
                let valuesArray: any[] = [];
                Object.keys(row).forEach((key) => {
                    if (key != 'target') {
                        valuesArray.push({
                            key: key,
                            value: row[key]
                        })
                    }
                })
                this.dataSource = valuesArray
            }
        });

        this.dataSource.sort((element1: any, element2: any) => {
            return element2.value - element1.value
        })

        const maxValue = Math.max(...this.dataSource.map(feature => feature.value))
        const minValue = Math.min(...this.dataSource.map(feature => feature.value))

        const stepSize = (maxValue - minValue) / 4

        this.dataSource.forEach((feature: any) => {
            feature['weight'] = Math.trunc((parseFloat(feature.value) - minValue) / stepSize)
        })
    }

    generateGraph() {
        let transformDataSet: any[] = [];

        this.columnNames = [
            'Feature',
            'Relevance',
            { role: 'style' },
            { 'type': 'string', 'role': 'tooltip', 'p': { 'html': true } },
        ];

        this.dataSource.forEach((feature: any) => {
            transformDataSet.push([
                feature.key,
                feature.value,
                this.JSONCleaner(this.explainabilityGraphStyle[feature.weight]),
                '<table style="padding:5px; width:150px;"><tr>' +
                '<td colspan="2" style="font-weight:bold; text-align:center; font-size:13px; color: #019ba9;">' + feature.key + '</td>' +
                '</tr><tr>' +
                '<td colspan="2" style="border-bottom: 1px solid black; margin:10px;"></td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Importance </td>' +
                '<td style="text-align:right; padding-right: 5px">' + parseFloat(feature.value).toFixed(5) + '</td>' +
                '</tr></table>',
            ]);
        })
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
        this.themeSubscription.unsubscribe();
    }

}
