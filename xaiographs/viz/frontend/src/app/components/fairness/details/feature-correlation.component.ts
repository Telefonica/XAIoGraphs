import { Component, Input, OnChanges } from '@angular/core';

import { ReaderService } from 'src/app/services/reader.service'
import { SnackbarService } from 'src/app/services/snackbar.service'

import { ctsFiles } from '../../../constants/csvFiles'

@Component({
    selector: 'app-feature-correlation',
    templateUrl: './feature-correlation.component.html',
    styles: [
    ]
})
export class FeatureCorrelationComponent implements OnChanges {

    listCorrelation: any[] = []

    @Input() currentFeature = '';

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) { }

    ngOnChanges(): void {
        this.listCorrelation = []
        if (this.currentFeature) {
            this._apiReader.readFairnessCorrelation({
                fileName: ctsFiles.fairness_highest_correlation,
                feature: this.currentFeature,
            }).subscribe({
                next: (response: any) => {
                    this.listCorrelation = response.map((node: any) => {
                        node.correlation_value = parseFloat(node.correlation_value).toFixed(2)
                        if(node.feature_1 != this.currentFeature) {
                            node.feature_2 = node.feature_1
                            node.feature_1 = this.currentFeature
                        }
                        return node
                    });
                },
                complete: () => { },
                error: (err) => {
                    this._apiSnackBar.openSnackBar(JSON.stringify(err))
                }
            })
        }
    }

}
