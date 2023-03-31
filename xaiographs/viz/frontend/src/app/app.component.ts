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
import { Router, RoutesRecognized } from '@angular/router';

import { ReaderService } from './services/reader.service';
import { SnackbarService } from './services/snackbar.service';

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
