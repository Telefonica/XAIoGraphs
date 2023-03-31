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
import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';

import { jsonFiles } from '../../constants/jsonFiles'

@Component({
    selector: 'app-local',
    templateUrl: './local.component.html',
    styleUrls: ['./local.component.scss']
})
export class LocalComponent implements OnInit {

    fileExists: boolean = false;

    constructor(
        private _apiReader: ReaderService,
        private _apiEmitter: EmitterService,
    ) {}

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.local_dataset_reliability).subscribe({
            complete: () => {
                this.fileExists = true
            },
            error: (err) => {
                this.fileExists = false
            }
        });
    }

    openPalette() {
        this._apiEmitter.setTheme('');
    }

}
