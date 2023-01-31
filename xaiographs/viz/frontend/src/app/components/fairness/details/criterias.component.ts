import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { ReaderService } from 'src/app/services/reader.service'
import { SnackbarService } from 'src/app/services/snackbar.service'

import { ctsFiles } from '../../../constants/csvFiles'

import { DefIndependenceComponent } from '../definitions/independence.component';
import { DefSeparationComponent } from '../definitions/separation.component';
import { DefSufficienceComponent } from '../definitions/sufficience.component';

@Component({
    selector: 'app-fairness-criterias',
    templateUrl: './criterias.component.html',
    styleUrls: ['../fairness.component.scss']
})
export class CriteriasComponent implements OnInit {

    listCriterias: any[] = []
    headers: string[] = []

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
        private dialog: MatDialog,
    ) { }

    ngOnInit(): void {
        this._apiReader.readCSV({ fileName: ctsFiles.fairness_sumarize_criterias }).subscribe({
            next: (response: any) => {
                this.listCriterias = response.data
                this.headers = response.headers

                this.listCriterias.forEach((criteria: any) => {
                    criteria[this.headers[1]] = (parseFloat(criteria[this.headers[1]]) * 100).toFixed(2) + ' %'
                    criteria[this.headers[3]] = (parseFloat(criteria[this.headers[3]]) * 100).toFixed(2) + ' %'
                    criteria[this.headers[5]] = (parseFloat(criteria[this.headers[5]]) * 100).toFixed(2) + ' %'
                })
            },
            complete: () => {

            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err))
            }
        })
    }

    openIndependence() {
        this.dialog.open(DefIndependenceComponent, {
            width: '50%',
            height: '80%',
            autoFocus: false
        });
    }
    openSeparation() {
        this.dialog.open(DefSeparationComponent, {
            width: '50%',
            height: '80%',
            autoFocus: false
        });

    }
    openSufficience() {
        this.dialog.open(DefSufficienceComponent, {
            width: '50%',
            height: '80%',
            autoFocus: false
        });
    }

}
