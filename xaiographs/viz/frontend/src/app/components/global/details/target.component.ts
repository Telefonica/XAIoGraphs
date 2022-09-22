import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ctsFiles } from '../../../constants/csvFiles';

@Component({
    selector: 'app-global-target',
    templateUrl: './target.component.html',
})
export class GlobalTargetComponent implements OnInit {

    filterTarget= new FormControl();
    listTarget: string[] = [];

    maxFeatures = 0;
    numFeatures = 0;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) { }

    ngOnInit(): void {
        this._apiReader.listGlobalTarget({ fileName: ctsFiles.global_target_explainability }).subscribe({
            next: (response: any) => {
                this.listTarget = response.targets;
                this.maxFeatures = response.features;
            },
            complete: () => {
                this.filterTarget.setValue(this.listTarget[0]);
                this.numFeatures = this.maxFeatures;
                this._apiEmitter.setBothGlobal(this.filterTarget.value, this.maxFeatures);
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    updateTarget() {
        this._apiEmitter.setGlobalTarget(this.filterTarget.value);
    }

    updateFeatures(event) {
        this._apiEmitter.setGlobalFeatures(event.value);
    }
}
