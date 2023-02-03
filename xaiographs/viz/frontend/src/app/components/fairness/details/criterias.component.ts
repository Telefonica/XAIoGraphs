import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { ReaderService } from 'src/app/services/reader.service'
import { SnackbarService } from 'src/app/services/snackbar.service'

import { jsonFiles } from '../../../constants/jsonFiles'

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
        this._apiReader.readJSON(jsonFiles.fairness_sumarize_criterias).subscribe({
            next: (response: any) => {
                this.listCriterias = response
                this.headers = Object.keys(response[0])
                this.listCriterias.forEach((criteria: any) => {
                    criteria[this.headers[2]] = criteria[this.headers[2]].replace('+', 'P')
                    criteria[this.headers[4]] = criteria[this.headers[4]].replace('+', 'P')
                    criteria[this.headers[6]] = criteria[this.headers[6]].replace('+', 'P')
                })
            },
            complete: () => {
                this.listCriterias.forEach((criteria: any) => {
                    criteria[this.headers[1]] = (parseFloat(criteria[this.headers[1]]) * 100).toFixed(2) + ' %'
                    criteria[this.headers[3]] = (parseFloat(criteria[this.headers[3]]) * 100).toFixed(2) + ' %'
                    criteria[this.headers[5]] = (parseFloat(criteria[this.headers[5]]) * 100).toFixed(2) + ' %'
                })
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
    openSufficiency() {
        this.dialog.open(DefSufficienceComponent, {
            width: '50%',
            height: '80%',
            autoFocus: false
        });
    }

}
