import { Injectable } from '@angular/core';
import { MatSnackBar, MatSnackBarConfig } from '@angular/material/snack-bar';

@Injectable({
    providedIn: 'root'
})

export class SnackbarService {

    constructor(private snackBar: MatSnackBar) { }

    openSnackBar(message: any, error = true) {
        const config = new MatSnackBarConfig();
        config.duration = 3000;
        if (error) {
            config.panelClass = ['snackBarBody', 'snackBarError', 'fontWhite'];
        } else {
            config.panelClass = ['snackBarBody', 'snackBarMessage', 'fontWhite'];
        }
        this.snackBar.open(message, '', config);
    }
}
