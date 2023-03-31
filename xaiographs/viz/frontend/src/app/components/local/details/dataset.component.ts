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

import { Component, OnInit, ViewChild } from '@angular/core';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { jsonFiles } from '../../../constants/jsonFiles';

@Component({
    selector: 'app-local-dataset',
    templateUrl: './dataset.component.html',
    styleUrls: ['../local.component.scss']
})
export class LocalDatasetComponent implements OnInit {

    displayedColumns: string[] = [];
    dataSource = new MatTableDataSource([]);

    csvDataset: any;
    dataReady: boolean = false;

    currentID = 1;

    private sort!: MatSort;
    @ViewChild(MatSort) set matSort(ms: MatSort) {
        this.sort = ms;
        this.setDataSourceAttributes();
    }

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) { }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.local_dataset_reliability ).subscribe({
            next: (response: any) => {
                this.csvDataset = response;
                this.displayedColumns = Object.keys(response[0]);
            },
            complete: () => {
                this.currentID = this.csvDataset[0].id;
                this._apiEmitter.setLocalTarget(this.csvDataset[0]);
                this.dataSource = new MatTableDataSource(this.csvDataset);
                this.setDataSourceAttributes();
                this.dataReady = true;
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

    radioSelected(row: any) {
        this._apiEmitter.setLocalTarget(row);
    }

}
