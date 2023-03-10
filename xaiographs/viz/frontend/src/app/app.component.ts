/* ANGULAR CORE */
import { Component, OnInit } from '@angular/core';
import { Router, RoutesRecognized } from '@angular/router';

/* ANGULAR SERVICES */
import { ReaderService } from './services/reader.service';
import { SnackbarService } from './services/snackbar.service';

/* LOCAL FILES */
import { ctsGlobal } from './constants/global';
import { ctsTheme } from './constants/theme';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    title = ctsGlobal.titleApp;
    currentModule = ctsGlobal.initial_component;

    constructor(
        private router: Router,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService
    ) {
        this.router.navigate(['/global'], { skipLocationChange: true });
    }

    ngOnInit() {
        this.router.events.subscribe(val => {
            if (val instanceof RoutesRecognized) {
                if (val.state.root.firstChild) {
                    this.currentModule = val.state.root.firstChild.url[0].path;
                }
            }
        });

        let colors = localStorage.getItem(ctsTheme.storageName)
        if (!colors) {
            this._apiReader.readColors().subscribe({
                next: (response: any) => {
                    colors = response
                },
                complete: () => {
                    localStorage.setItem(ctsTheme.storageName, JSON.stringify(colors));
                },
                error: (err) => {
                    this._apiSnackBar.openSnackBar(JSON.stringify(err));
                }
            })
        }
    }
}
