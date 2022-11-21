import { Component, OnInit } from '@angular/core';

import { ChartType } from 'angular-google-charts';

import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ctsFiles } from '../../../constants/csvFiles';
import { featuresGraphStyle } from '../../../../assets/global';

@Component({
    selector: 'app-global-features',
    templateUrl: './features.component.html'
})
export class GlobalFeaturesComponent implements OnInit {

    type = ChartType.BarChart;
    dataGraph: any[] = [];
    columnNames: any[] = [];
    options: any = {};
    displayGraph: boolean = false;

    serviceResponse: any;

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) { }

    ngOnInit(): void {
        this._apiReader.readCSV({ fileName: ctsFiles.global_explainability }).subscribe({
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                if (this.serviceResponse.data.length > 0) {
                    this.initGraph();
                    this.createGraph();
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

    createGraph() {
        let transformDataSet: any[] = [];

        this.columnNames = [
            'Feature',
            'Relevance',
            { role: 'style' },
            { 'type': 'string', 'role': 'tooltip', 'p': { 'html': true } },
        ];

        this.serviceResponse.data.map((node: any, index: number) => {
            const weight = parseFloat(node.feature_weight);
            const importance = parseFloat(node.feature_importance);

            const barStyle = JSON.stringify(featuresGraphStyle[weight - 1]).replace('{', '').replace('}', '').replace(/"/g, '').replace(/,/g, ';');
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

}
