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
