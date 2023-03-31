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

import { Component, OnInit, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { jsonFiles } from '../../../constants/jsonFiles';

@Component({
    selector: 'app-local-reason',
    templateUrl: './reason.component.html',
    styleUrls: ['../local.component.scss']
})
export class LocalReasonComponent implements OnInit, OnDestroy {

    currentTarget: any;

    targetSubscription: any;

    reasonJson = []

    reasonWhy = '';
    display: boolean = false;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.localTargetChangeEmitter.subscribe(() => {
            this.filterData();
        });
    }

    ngOnInit() {
        this._apiReader.readJSON(jsonFiles.local_reason_why).subscribe({
            next: (response: any) => {
                this.reasonJson = response
            },
            complete: () => {
                this.filterData();
            },
            error: (err) => { }
        });
    }

    filterData() {
        this.currentTarget = this._apiEmitter.getLocalTarget();
        const reasonRow = this.reasonJson.filter((row: any) => {
            return row.id == this.currentTarget.id
        });

        if(reasonRow.length > 0) {
            this.reasonWhy = reasonRow[0]['reason']
        }
    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
    }

}
