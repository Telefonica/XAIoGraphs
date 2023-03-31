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
