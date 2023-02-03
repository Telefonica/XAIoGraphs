import { Component, OnDestroy, OnInit } from '@angular/core';

import { ChartType } from 'angular-google-charts';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { jsonFiles } from '../../../constants/jsonFiles';
import { distributionGraphStyle0, distributionGraph3D0, distributionGraphPieHole0 } from '../themes/global0';
import { distributionGraphStyle1, distributionGraph3D1, distributionGraphPieHole1 } from '../themes/global1';

@Component({
    selector: 'app-global-distribution',
    templateUrl: './distribution.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalDistributionComponent implements OnInit, OnDestroy {

    type = ChartType.PieChart;
    dataGraph: any[] = [];
    columnNames: any[] = [];
    options: any = {};
    displayGraph: boolean = false;

    serviceResponse: any;

    distributionGraphStyle
    distributionGraph3D
    distributionGraphPieHole
    themeSubscription

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
        this._apiReader.readJSON(jsonFiles.global_target_distribution).subscribe({
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                if (this.serviceResponse.length > 0) {
                    this.serviceResponse.sort((element1, element2) => parseInt(element2.count) - parseInt(element1.count));
                    this.prepareTheme();
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

    prepareTheme() {
        if (!this._apiEmitter.getTheme()) {
            this.distributionGraphStyle = distributionGraphStyle0
            this.distributionGraph3D = distributionGraph3D0
            this.distributionGraphPieHole = distributionGraphPieHole0
        } else {
            this.distributionGraphStyle = distributionGraphStyle1
            this.distributionGraph3D = distributionGraph3D1
            this.distributionGraphPieHole = distributionGraphPieHole1
        }
    }

    initGraph() {
        this.dataGraph = [];
        this.options = {
            is3D: this.distributionGraph3D,
            pieHole: this.distributionGraphPieHole,
            slices: this.distributionGraphStyle,
            chartArea: { top: 15, width: '90%', height: '80%' },
            tooltip: { type: 'string', isHtml: true },
            legend: { position: 'bottom' },
        };
    }

    createGraph() {
        let transformDataSet: any[] = [];

        this.columnNames = [
            'Target',
            'Percentage',
            { 'type': 'string', 'role': 'tooltip', 'p': { 'html': true } },
        ];
        const totalCount = this.serviceResponse.reduce((accumulator, target) => {
            return accumulator + parseInt(target.count);
        }, 0);

        this.serviceResponse.map((data: any) => {
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

    ngOnDestroy(): void {
        this.themeSubscription.unsubscribe()
    }

}
