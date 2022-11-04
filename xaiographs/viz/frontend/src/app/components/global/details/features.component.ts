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

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) { }

    ngOnInit(): void {
        this._apiReader.readCSV({ fileName: ctsFiles.global_explainability }).subscribe({
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
            legend: 'none',
            bar: { groupWidth: "90%" },
            chartArea: { width: '70%', height: '80%' },
        };
    }

    createGraph(source: any) {
        let transformDataSet: any[] = [];

        this.columnNames = ['Feature', 'Relevance', { role: 'style' }];

        source.data.map((node: any, index: number) => {
            const barStyle = JSON.stringify(featuresGraphStyle[parseFloat(node.feature_weight)- 1]).replace('{', '').replace('}', '').replace(/"/g, '').replace(/,/g, ';');
            transformDataSet.push([
                node.feature_name,
                parseFloat(node.feature_importance),
                barStyle
            ]);
        });

        this.dataGraph = transformDataSet;
    }

}
