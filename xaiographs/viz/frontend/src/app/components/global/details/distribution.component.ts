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

import { ChartType } from 'angular-google-charts';
import html2canvas from "html2canvas";

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { jsonFiles } from '../../../constants/jsonFiles';
import { ctsTheme } from '../../../constants/theme';
import { ctsGlobal } from '../../../constants/global';

@Component({
    selector: 'app-global-distribution',
    templateUrl: './distribution.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalDistributionComponent implements OnInit, OnDestroy {
    @ViewChild('exportableArea') exportableArea;
    hidePicture: boolean = false;

    type = ChartType.PieChart;
    dataGraph: any[] = [];
    columnNames: any[] = [];
    options: any = {};
    displayGraph: boolean = false;

    serviceResponse: any;

    themeSubscription
    colorTheme: any;

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
        this.prepareTheme();
    }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.global_target_distribution).subscribe({
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                if (this.serviceResponse.length > 0) {
                    this.serviceResponse.sort((element1, element2) => parseInt(element2.count) - parseInt(element1.count));
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
        this.colorTheme = JSON.parse('' + localStorage.getItem(ctsTheme.storageName))
    }

    initGraph() {
        this.dataGraph = [];
        this.options = {
            is3D: false,
            pieHole: 0.3,
            colors: this.colorTheme.targets,
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

    downloadPicture() {
        this.hidePicture = true
        this.generateImage2Download()
    }
    generateImage2Download() {
        this._apiSnackBar.openDownloadSnackBar(ctsGlobal.downloading_message, false).finally(() => {
            html2canvas(this.exportableArea.nativeElement).then(exportCanvas => {
                const canvas = exportCanvas.toDataURL().replace(/^data:image\/[^;]*/, 'data:application/octet-stream');
                let link = document.createElement('a');
                link.download = ctsGlobal.label_global_distribution + ctsGlobal.image_extension;
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
        this.themeSubscription.unsubscribe()
    }

}
