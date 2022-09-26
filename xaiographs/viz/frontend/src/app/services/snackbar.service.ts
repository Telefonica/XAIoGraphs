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
}
