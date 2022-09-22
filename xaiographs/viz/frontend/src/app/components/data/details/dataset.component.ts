import { Component, OnInit, ViewChild } from '@angular/core';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';

import { ChartType } from 'angular-google-charts';

import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ctsFiles } from '../../../constants/csvFiles';
import { distributionGraphStyle } from '../../../../assets/data';
import { distributionGraphWidth } from '../../../../assets/data';
import { distributionGraphHeight } from '../../../../assets/data';

@Component({
    selector: 'app-data-dataset',
    templateUrl: './dataset.component.html',
})
export class DataDatasetComponent implements OnInit {

    displayedColumns: string[] = []
    totalHeaders: string[] = []

    dataSource = new MatTableDataSource([]);
    csvDataset: any;
    csvDistribution: any;
    display: boolean = false;

    type = ChartType.ColumnChart;
    graphColumnNames = ['Key', 'Value', { role: 'style' }];
    options: any = {
        hAxis: { textPosition: 'none' },
        vAxis: { textPosition: 'none' },
        width: distributionGraphWidth,
        height: distributionGraphHeight,
        legend: 'none',
        bar: { groupWidth: "90%" },
        chartArea: { width: '70%', height: '80%' },
    };

    private sort!: MatSort;
    @ViewChild(MatSort) set matSort(ms: MatSort) {
        this.sort = ms;
        this.setDataSourceAttributes();
    }

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) { }

    ngOnInit(): void {
        this._apiReader.listDatasetHeaders({ fileName: ctsFiles.local_dataset_reliability }).subscribe({
            next: (response: any) => {
                this.displayedColumns = response;
                this.totalHeaders = response;
            },
            complete: () => {
                this.getData();
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    getData() {
        const body = {
            fileName: ctsFiles.local_dataset_reliability,
            displayedColumns: this.displayedColumns,
        }

        this._apiReader.readDatasetSelected(body).subscribe({
            next: (response: any) => {
                this.csvDataset = response.data;

                this.displayedColumns.forEach((header: any) => {
                    if(header != 'id') {
                        response.distribution[header].map((row: any, index: number) => {
                            row.push(JSON.stringify(distributionGraphStyle[index % distributionGraphStyle.length]).replace('{', '').replace('}', '').replace(/"/g, '').replace(/,/g, ';'));
                        });
                    }
                });
                this.csvDistribution = response.distribution;
            },
            complete: () => {
                this.dataSource = new MatTableDataSource(this.csvDataset);
                this.setDataSourceAttributes();
                this.display = true;
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    applyFilter(filterValue: string) {
        this.dataSource.filter = filterValue.trim().toLowerCase();
        if (this.dataSource.paginator) {
            this.dataSource.paginator.firstPage();
        }
    }

    private setDataSourceAttributes() {
        this.dataSource.sort = this.sort;
    }

    getDistributionHeaders(column: string) {
        console.log(column);
        console.log(this.csvDistribution[column].keys)
    }


}

