import { Component, OnInit } from '@angular/core';

import { ChartType } from 'angular-google-charts';

import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ctsFiles } from '../../../constants/csvFiles';
import { distributionGraphStyle } from '../../../../assets/global';
import { distributionGraph3D } from '../../../../assets/global';
import { distributionGraphPieHole } from '../../../../assets/global';

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

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) { }

    ngOnInit(): void {
        this._apiReader.readCSV({ fileName: ctsFiles.global_target_distribution }).subscribe({
            next: (response: any) => {
                this.initGraph();
                this.createGraph(response);
            },
            complete: () => {
                this.displayGraph = true
            },
            error: (err) => {
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
            chartArea: { width: '90%', height: '80%' },
        };
    }

    createGraph(source: any) {
        let transformDataSet: any[] = [];

        this.columnNames = ['Target', 'Percentage'];

        source.data.map((data: any, index: number) => {
            transformDataSet.push([
                data.target,
                parseFloat(data.count)
            ]);
        });

        this.dataGraph = transformDataSet;
    }

}
