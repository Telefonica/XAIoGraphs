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

import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';

import { ReaderService } from '../../services/reader.service';
import { SnackbarService } from '../../services/snackbar.service';

import { ctsTheme } from '../../constants/theme';

@Component({
    selector: 'app-palette',
    templateUrl: './palette.component.html',
    styleUrls: ['./palette.component.scss']
})
export class PaletteComponent implements OnInit {

    globalFeature: string = ''
    positiveValue: string = ''
    zeroValue: string = ''
    negativeValue: string = ''
    frecuencyValue: string = ''
    targets: string[] = []

    constructor(
        public dialogRef: MatDialogRef<PaletteComponent>,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService
    ) { }

    ngOnInit(): void {
        const jsonColors = JSON.parse('' + localStorage.getItem(ctsTheme.storageName))

        this.globalFeature = jsonColors.globalFeature
        this.positiveValue = jsonColors.positiveValue
        this.zeroValue = jsonColors.zeroValue
        this.negativeValue = jsonColors.negativeValue
        this.frecuencyValue = jsonColors.frecuencyValue
        this.targets = jsonColors.targets
    }

    updatePalette() {
        this.dialogRef.close({
            globalFeature: this.globalFeature,
            positiveValue: this.positiveValue,
            zeroValue: this.zeroValue,
            negativeValue: this.negativeValue,
            frecuencyValue: this.frecuencyValue,
            targets: this.targets,
        })
    }

    restorePalette() {
        let defaultColors: any;
        this._apiReader.readColors().subscribe({
            next: (response: any) => {
                defaultColors = response
            },
            complete: () => {
                this.dialogRef.close(defaultColors)
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        })
    }
}
