import { Component, OnInit, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ctsFiles } from '../../../constants/csvFiles';

@Component({
    selector: 'app-local-reason',
    templateUrl: './reason.component.html',
    styles: [
    ]
})
export class LocalReasonComponent implements OnInit {

    currentTarget = '';

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

    ngOnInit(): void { }

    getData() {
        this.currentTarget = this._apiEmitter.getLocalTarget();

        const body = {
            fileName: ctsFiles.local_reason_why,
            target: this.currentTarget,
        }

        this._apiReader.readLocalReasonWhy(body).subscribe({
            next: (response: any) => {
                if (response)
                    this.reasonWhy = response[0].reason;
            },
            complete: () => {
                this.display = true;
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

}
