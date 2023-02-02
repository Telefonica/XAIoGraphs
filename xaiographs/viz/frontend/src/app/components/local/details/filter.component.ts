import { Component, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';

@Component({
    selector: 'app-local-filter',
    templateUrl: './filter.component.html',
    styleUrls: ['../local.component.scss']
})
export class LocalFilterComponent implements OnDestroy {

    maxFeatures = 0;
    numFeatures = 0;

    targetSubscription: any;

    currentTarget = {};

    constructor(
        private _apiEmitter: EmitterService,
    ) {
        this.targetSubscription = this._apiEmitter.localTargetChangeEmitter.subscribe(() => {
            this.getData();
        });
    }

    getData() {
        this.currentTarget = this._apiEmitter.getLocalTarget();
        this.maxFeatures = Object.keys(this.currentTarget).length -1;

        if(this.numFeatures == 0) {
            this.numFeatures = this.maxFeatures
        }

        if (!this._apiEmitter.getLocalFeatures()) {
            this._apiEmitter.setLocalFeatures(this.maxFeatures);
        }
    }

    updateFeatures(event) {
        this._apiEmitter.setLocalFeatures(event.value);
    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
    }

}
