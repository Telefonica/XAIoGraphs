import { Component, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ctsFiles } from '../../../constants/csvFiles';

@Component({
    selector: 'app-local-reason',
    templateUrl: './reason.component.html',
    styleUrls: ['../local.component.scss']
})
export class LocalReasonComponent implements OnDestroy {

    currentTarget: any;

    targetSubscription: any;

    reasonWhy = '';
    display: boolean = false;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.localTargetChangeEmitter.subscribe(() => {
            this.getData();
        });
    }

    getData() {
        this.currentTarget = this._apiEmitter.getLocalTarget();
        this.reasonWhy = ''

        const body = {
            fileName: ctsFiles.local_reason_why,
            target: this.currentTarget.id,
        }

        this._apiReader.readLocalReasonWhy(body).subscribe({
            next: (response: any) => {
                if (response.length > 0)
                    this.reasonWhy = response[0].reason;
            },
            complete: () => { },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
    }

}
