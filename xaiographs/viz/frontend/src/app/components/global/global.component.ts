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
import { MatDialog } from '@angular/material/dialog';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';

import { PaletteComponent } from 'src/app/shared/palette/palette.component';

import { jsonFiles } from '../../constants/jsonFiles';

@Component({
    selector: 'app-global',
    templateUrl: './global.component.html',
    styleUrls: ['./global.component.scss']
})
export class GlobalComponent implements OnInit {

    serviceResponse: any;
    fileExists: boolean = false;

    constructor(
        private dialog: MatDialog,
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
    ) { }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.global_target_distribution).subscribe({
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                let orderedTarget: any[] = [];
                if (this.serviceResponse.length > 0) {
                    this.serviceResponse.sort((element1, element2) => parseInt(element2.count) - parseInt(element1.count));
                    this.serviceResponse.forEach((target: any) => {
                        orderedTarget.push(target.target)
                    });
                }
                this._apiReader.setOrderedTarget(orderedTarget)
                this.fileExists = true
            },
            error: (err) => {
                this.fileExists = false
            }
        });
    }

    openPalette() {
        this.dialog.open(PaletteComponent, {
            width: '50%',
            autoFocus: false
        }).afterClosed().subscribe(response => {
            if (response)
                this._apiEmitter.setTheme(response)
        });
    }

}
