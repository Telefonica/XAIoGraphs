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

import { Injectable } from '@angular/core';
import { MatSnackBar, MatSnackBarConfig } from '@angular/material/snack-bar';

@Injectable({
    providedIn: 'root'
})

export class SnackbarService {

    constructor(private snackBar: MatSnackBar) { }

    openSnackBar(message: any, error = true) {
        const config = new MatSnackBarConfig();
        if (error) {
            config.panelClass = ['snackBarBody', 'snackBarError', 'fontWhite'];
            config.duration = 10000;
        } else {
            config.panelClass = ['snackBarBody', 'snackBarMessage', 'fontWhite'];
            config.duration = 3000;
        }
        this.snackBar.open(message, '', config);
    }

    openDownloadSnackBar(message: any, error = true) {
        return new Promise((resolve, reject) => {
            const config = new MatSnackBarConfig();
            if (error) {
                config.panelClass = ['snackBarBody', 'snackBarError', 'fontWhite'];
                config.duration = 10000;
            } else {
                config.panelClass = ['snackBarBody', 'snackBarMessage', 'fontWhite'];
                config.duration = 3000;
            }
            this.snackBar.open(message, '', config).afterOpened().subscribe(()=> {
                resolve(true)
            })
        })
    }
}
