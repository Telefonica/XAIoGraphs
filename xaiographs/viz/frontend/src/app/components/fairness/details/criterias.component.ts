import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { ReaderService } from 'src/app/services/reader.service'
import { SnackbarService } from 'src/app/services/snackbar.service'

import html2canvas from "html2canvas";

import { jsonFiles } from '../../../constants/jsonFiles'
import { ctsGlobal } from '../../../constants/global'

import { DefIndependenceComponent } from '../definitions/independence.component';
import { DefSeparationComponent } from '../definitions/separation.component';
import { DefSufficienceComponent } from '../definitions/sufficience.component';

@Component({
    selector: 'app-fairness-criterias',
    templateUrl: './criterias.component.html',
    styleUrls: ['../fairness.component.scss']
})
export class CriteriasComponent implements OnInit {
    @ViewChild('exportableArea') exportableArea;
    hidePicture: boolean = false;

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
            width: '40%',
            autoFocus: false
        });
    }
    openSeparation() {
        this.dialog.open(DefSeparationComponent, {
            width: '40%',
            autoFocus: false
        });

    }
    openSufficiency() {
        this.dialog.open(DefSufficienceComponent, {
            width: '40%',
            autoFocus: false
        });
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
                link.download = ctsGlobal.label_fairness_criteria_score + ctsGlobal.image_extension;
                link.href = canvas;
                link.click();
                this.hidePicture = false
            }).catch((err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
                this.hidePicture = false
            });
        })
    }

}
