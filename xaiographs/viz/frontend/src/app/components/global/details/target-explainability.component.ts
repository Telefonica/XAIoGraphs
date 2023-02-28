import { Component, OnDestroy, OnInit } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ChartType } from 'angular-google-charts';

import { ApexChart, ApexAxisChartSeries, ApexXAxis, ApexYAxis, ApexFill, ApexStroke, ApexMarkers, ApexLegend } from 'ng-apexcharts'

import { jsonFiles } from '../../../constants/jsonFiles';
import { explainabilityGraphStyle0, globalRadarColor0, targetRadarColor0 } from '../themes/global0';
import { explainabilityGraphStyle1, globalRadarColor1, targetRadarColor1 } from '../themes/global1';

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
    serviceGlobalResponse = [];
    dataSource: any[] = [];

    type = ChartType.BarChart;
    dataGraph: any[] = [];
    columnNames: any[] = [];
    options: any = {};
    displayGraph: boolean = false;

    explainabilityGraphStyle: any;
    globalRadarStyle: any;
    targetRadarStyle: any;

    showRadar: boolean = false;
    seriesRadar: ApexAxisChartSeries = []
    chartRadar: ApexChart = {
        type: 'radar',
        height: '400px',
        toolbar: {
            show: false
        }
    }
    xaxisRadar: ApexXAxis = {}
    yaxisRadar: ApexYAxis = {
        show: false
    }
    fillRadar: ApexFill = {
        opacity: 0.1,
        colors: []
    }
    strokeRadar: ApexStroke = {
        show: true,
        width: 1,
        colors: []
    }
    markersRadar: ApexMarkers = {
        size: 2,
        colors: []
    }
    legendRadar: ApexLegend = {
        show: false
    }

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.globalTargetChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
            this.generateRadar();
        });
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.showRadar = false;
            this.prepareTheme();
            this.initGraph();
            this.generateGraph();
            this.generateRadar();
        });
    }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.global_explainability).subscribe({
            next: (responseGlobal: any) => {
                this.serviceGlobalResponse = responseGlobal;
            },
            complete: () => {
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
                            this.generateRadar();
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
            },
            error: (errGlobal) => {
                this.displayGraph = false;
                this._apiSnackBar.openSnackBar(JSON.stringify(errGlobal));
            }
        });
    }

    prepareTheme() {
        if (!this._apiEmitter.getTheme()) {
            this.explainabilityGraphStyle = explainabilityGraphStyle0
            this.globalRadarStyle = globalRadarColor0
            this.targetRadarStyle = targetRadarColor0
        } else {
            this.explainabilityGraphStyle = explainabilityGraphStyle1
            this.globalRadarStyle = globalRadarColor1
            this.targetRadarStyle = targetRadarColor1
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

    generateRadar() {
        let globalFeatValues: number[] = []
        let targetFeatValues: number[] = []
        this.xaxisRadar['categories'] = []

        const radarColorSchema = [
            this.globalRadarStyle,
            this.targetRadarStyle
        ]

        this.fillRadar['colors'] = radarColorSchema
        this.strokeRadar['colors'] = radarColorSchema
        this.markersRadar['colors'] = radarColorSchema

        this.serviceGlobalResponse.forEach((globalFeat: any) => {
            this.xaxisRadar['categories'].push(globalFeat.feature_name)
            globalFeatValues.push(parseFloat(parseFloat(globalFeat.feature_importance).toFixed(2)))
            const targetFeat = this.dataSource.filter((targetFeat: any) => {
                return (targetFeat.key == globalFeat.feature_name)
            })
            targetFeatValues.push(parseFloat((targetFeat[0]['value']).toFixed(2)))
        })

        this.seriesRadar = [{
            name: "Global Features",
            data: globalFeatValues
        },
        {
            name: "Target Features",
            data: targetFeatValues
        }]
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
