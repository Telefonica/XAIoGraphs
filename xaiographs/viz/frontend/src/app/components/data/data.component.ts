import { Component, OnInit } from '@angular/core';

import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { jsonFiles } from '../../constants/jsonFiles';

@Component({
    selector: 'app-data',
    templateUrl: './data.component.html',
    styleUrls: ['./data.component.scss']
})
export class DataComponent implements OnInit {

    jsonResponse: any[] = []
    displayColumns: string[] = []

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) { }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.local_dataset_reliability).subscribe({
            next: (response: any) => {
                this.jsonResponse = response
            },
            complete: () => {
                this.displayColumns = Object.keys(this.jsonResponse[0]).slice(1)
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

}
