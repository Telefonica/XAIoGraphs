import { Component, OnDestroy, OnInit } from '@angular/core';

import { ChartType } from 'angular-google-charts';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { jsonFiles } from '../../../constants/jsonFiles';
import { featuresGraphStyle0,  } from '../themes/global0';
import { featuresGraphStyle1 } from '../themes/global1';

@Component({
    selector: 'app-global-features',
    templateUrl: './features.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalFeaturesComponent implements OnInit, OnDestroy {

    type = ChartType.BarChart;
    dataGraph: any[] = [];
    dataBreakDownGraph: any[] = [];
    columnNames: any[] = [];
    columnBreakDownNames: any[] = [];
    options: any = {};
    optionsBreakDown: any = {};
    displayGraph: boolean = false;

    serviceResponse: any;
    serviceResponseTarget: any;
    featureList: string[] = [];

    themeSubscription: any;
    featuresGraphStyle: any;

    showBreakdown: boolean = false;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.initGraph();
            this.createGraph();
        });
    }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.global_explainability).subscribe({
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                if (this.serviceResponse.length > 0) {
                    this.prepareTheme();
                    this.initGraph();
                    this.createGraph();
                    this.displayGraph = true;

                    this._apiReader.readJSON(jsonFiles.global_target_explainability).subscribe({
                        next: (responseTarget: any) => {
                            this.serviceResponseTarget = responseTarget;
                        },
                        complete: () => {
                            this.initBreakDownGraph();
                            this.createBreakDownGraph();
                        },
                        error: (errTarget) => {
                            this.displayGraph = false;
                            this._apiSnackBar.openSnackBar(JSON.stringify(errTarget));
                        }
                    });
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
            this.featuresGraphStyle = featuresGraphStyle0
        } else {
            this.featuresGraphStyle = featuresGraphStyle1
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

    initBreakDownGraph() {
        this.dataBreakDownGraph = [];
        this.optionsBreakDown = {
            bar: { groupWidth: '90%' },
            chartArea: { right: 20, top: 20, width: '75%', height: '85%' },
            tooltip: { type: 'string', isHtml: true },
            isStacked: true,
            hAxis: { textPosition: 'none' },
            legend: { position: 'bottom' },
        };
    }

    createGraph() {
        let transformDataSet: any[] = [];

        this.columnNames = [
            'Feature',
            'Relevance',
            { role: 'style' },
            { 'type': 'string', 'role': 'tooltip', 'p': { 'html': true } },
        ];

        this.serviceResponse.map((node: any) => {
            this.featureList.push(node.feature_name);
            const weight = parseFloat(node.feature_weight);
            const importance = parseFloat(node.feature_importance);

            const barStyle = JSON.stringify(this.featuresGraphStyle[weight - 1]).replace('{', '').replace('}', '').replace(/"/g, '').replace(/,/g, ';');
            transformDataSet.push([
                node.feature_name,
                importance,
                barStyle,
                '<table style="padding:5px; width:150px;"><tr>' +
                '<td colspan="2" style="font-weight:bold; text-align:center; font-size:13px; color: #019ba9;">' + node.feature_name + '</td>' +
                '</tr><tr>' +
                '<td colspan="2" style="border-bottom: 1px solid black; margin:10px;"></td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Importance</td>' +
                '<td style="text-align:right; padding-right: 5px">' + importance.toFixed(5) + '</td>' +
                '</tr></table>'
            ]);
        });

        this.dataGraph = transformDataSet;
    }

    createBreakDownGraph() {
        this.columnBreakDownNames = ['Feature']

        this.serviceResponseTarget.forEach((target: any) => {
            this.columnBreakDownNames.push(
                target.target,
                { role: 'style' },
                { 'type': 'string', 'role': 'tooltip', 'p': { 'html': true } }
            )
        });

        const targetLength = this.serviceResponseTarget.length


        this.featureList.forEach((featName: any) => {
            let featRow: any[] = [];
            featRow.push(featName)

            this.serviceResponseTarget.forEach((targetInfo: any, index: number) => {
                featRow.push(
                    targetInfo[featName],
                    JSON.stringify(this.featuresGraphStyle[targetLength - index -1]).replace('{', '').replace('}', '').replace(/"/g, '').replace(/,/g, ';'),
                    '<table style="padding:5px; width:150px;"><tr>' +
                    '<td colspan="2" style="font-weight:bold; text-align:center; font-size:13px; color: #019ba9;">' + targetInfo.target + '</td>' +
                    '</tr><tr>' +
                    '<td colspan="2" style="border-bottom: 1px solid black; margin:10px;"></td>' +
                    '</tr><tr>' +
                    '<td style="font-weight:bold; padding-left: 5px">' + featName + '</td>' +
                    '<td style="text-align:right; padding-right: 5px">' + targetInfo[featName].toFixed(5) + '</td>' +
                    '</tr></table>'
                )
            })

            this.dataBreakDownGraph.push(featRow);
        });

        console.log(this.dataBreakDownGraph);
    }

    ngOnDestroy(): void {
        this.themeSubscription.unsubscribe();
    }

}
