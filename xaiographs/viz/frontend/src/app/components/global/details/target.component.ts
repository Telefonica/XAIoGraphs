import { Component, OnInit, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { jsonFiles } from '../../../constants/jsonFiles';
import { ctsGlobal } from '../../../constants/global';
import { ctsTheme } from '../../../constants/theme';

@Component({
    selector: 'app-global-target',
    templateUrl: './target.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalTargetComponent implements OnInit, OnDestroy {

    currentTargetIndex: number = 0

    listTarget: any[] = [];
    listFeatures: number[] = [];

    maxFeatures = 0;
    maxFrecuency = 0;
    numFeatures = 0;
    numFrecuency = 0;

    themeSubscription: any;
    colorTheme: any;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.getData();
        });
        this.prepareTheme();
    }

    ngOnInit(): void {
        this.getData();
    }

    prepareTheme() {
        this.colorTheme = JSON.parse('' + localStorage.getItem(ctsTheme.storageName))
    }

    getData() {
        this.listTarget = []
        this.listFeatures = []

        this._apiReader.readJSON(jsonFiles.global_graph_description).subscribe({
            next: (response: any) => {
                response.forEach(description => {
                    this.listTarget.push({
                        target: description.target,
                        color: this.colorTheme.targets[this._apiReader.getOrderedTarget(description.target)],
                    })
                    this.listFeatures.push(description.num_features)
                });
            },
            complete: () => {
                this.currentTargetIndex = 0;
                this.setValueLimits(0)
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    updateTarget(index) {
        this.currentTargetIndex = index;
        this.setValueLimits(index);
    }

    updateFeatures(event) {
        this._apiEmitter.setGlobalFeatures(event.value);
    }

    updateFrecuency(event) {
        this._apiEmitter.setGlobalFrecuency(event.value);
        this.maxFeatures = event.value;
        if (this.numFeatures > this.maxFeatures) {
            this.numFeatures = this.maxFeatures
        }
    }

    setValueLimits(index) {
        this.maxFeatures = this.listFeatures[index];
        this.maxFrecuency = this.listFeatures[index];

        if (ctsGlobal.frecuency_limit > 0)
            this.numFrecuency = this.maxFrecuency <= ctsGlobal.frecuency_limit ? this.maxFrecuency : ctsGlobal.frecuency_limit;
        else
            this.numFrecuency = this.maxFrecuency

        if (ctsGlobal.feature_limit > 0)
            this.numFeatures = this.maxFeatures <= ctsGlobal.feature_limit ? this.maxFeatures : ctsGlobal.feature_limit;
        else
            this.numFeatures = this.maxFeatures

        this._apiEmitter.setAllGlobal(this.listTarget[index]['target'], this.numFeatures, this.numFrecuency);
    }

    ngOnDestroy(): void {
        this.themeSubscription.unsubscribe();
    }
}
