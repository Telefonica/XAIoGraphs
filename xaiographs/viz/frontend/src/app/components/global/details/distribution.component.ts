import { Component, OnInit } from '@angular/core';

import { ChartType } from 'angular-google-charts';

import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ctsFiles } from '../../../constants/csvFiles';
import { distributionGraphStyle, distributionGraph3D, distributionGraphPieHole } from '../../../../assets/global';

@Component({
    selector: 'app-global-distribution',
    templateUrl: './distribution.component.html',
})
export class GlobalDistributionComponent implements OnInit {

    type = ChartType.PieChart;
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
        this._apiReader.readCSV({ fileName: ctsFiles.global_target_distribution }).subscribe({
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                if(this.serviceResponse.data.length > 0) {
                    this.serviceResponse.data.sort((element1, element2) => parseInt(element2.count) - parseInt(element1.count) );
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
            is3D: distributionGraph3D,
            pieHole: distributionGraphPieHole,
            slices: distributionGraphStyle,
            chartArea: { top: 15, width: '90%', height: '80%' },
            tooltip: { type: 'string', isHtml: true },
            legend:{position: 'bottom'},
        };
    }

    createGraph() {
        let transformDataSet: any[] = [];

        this.columnNames = [
            'Target',
            'Percentage',
            { 'type': 'string', 'role': 'tooltip', 'p': { 'html': true } },
        ];
        const totalCount = this.serviceResponse.data.reduce((accumulator, target) => {
            return accumulator + parseInt(target.count);
        }, 0);

        this.serviceResponse.data.map((data: any) => {
            const count = parseInt(data.count);

            transformDataSet.push([
                data.target,
                count,
                '<table style="padding:5px; width:150px;"><tr>' +
                '<td colspan="2" style="font-weight:bold; text-align:center; font-size:13px; color: #019ba9;">' + data.target + '</td>' +
                '</tr><tr>' +
                '<td colspan="2" style="border-bottom: 1px solid black; margin:10px;"></td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Count</td>' +
                '<td style="text-align:right; padding-right: 5px">' + count + '</td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Frecuency</td>' +
                '<td style="text-align:right; padding-right: 5px">' + (count / totalCount * 100).toFixed(2) + '%' + '</td>' +
                '</tr></table>',
            ]);
        });

        this.dataGraph = transformDataSet;
    }

}
