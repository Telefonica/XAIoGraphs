import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ctsFiles } from '../../../constants/csvFiles';
import { ctsGlobal }  from '../../../constants/global';

@Component({
    selector: 'app-global-target',
    templateUrl: './target.component.html',
})
export class GlobalTargetComponent implements OnInit {

    filterTarget= new FormControl();
    listTarget: string[] = [];
    listFeatures: number[] = [];

    maxFeatures = 0;
    numFeatures = 0;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) { }

    ngOnInit(): void {
        this._apiReader.readGlobalDescription({ fileName: ctsFiles.global_graph_description }).subscribe({
            next: (response: any) => {
                response.forEach(description => {
                    this.listTarget.push(description.target)
                    this.listFeatures.push(description.num_features)
                });
            },
            complete: () => {
                this.filterTarget.setValue(0);
                this.maxFeatures = this.listFeatures[0];
                this.numFeatures = this.maxFeatures <= ctsGlobal.feature_limit ? this.maxFeatures: ctsGlobal.feature_limit;
                this._apiEmitter.setBothGlobal(this.listTarget[0], this.numFeatures);
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    updateTarget() {
        const index = this.filterTarget.value;
        this._apiEmitter.setBothGlobal(this.listTarget[index], this.numFeatures);
    }

    updateFeatures(event) {
        this._apiEmitter.setGlobalFeatures(event.value);
    }
}
