import { Component, Input, OnChanges } from '@angular/core';

import { ReaderService } from 'src/app/services/reader.service'
import { SnackbarService } from 'src/app/services/snackbar.service'

import { jsonFiles } from '../../../constants/jsonFiles'

@Component({
    selector: 'app-feature-correlation',
    templateUrl: './feature-correlation.component.html',
    styleUrls: ['../fairness.component.scss']
})
export class FeatureCorrelationComponent implements OnChanges {

    listCorrelation: any[] = []
    jsonResponse: any[] = []

    @Input() currentFeature = '';

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) { }

    ngOnChanges(): void {
        this.listCorrelation = []
        if (this.currentFeature) {
            this._apiReader.readJSON(jsonFiles.fairness_highest_correlation).subscribe({
                next: (response: any) => {
                    this.jsonResponse = response.filter((row: any) => {
                        return row.feature_1 == this.currentFeature
                            || row.feature_2 == this.currentFeature
                    })
                },
                complete: () => {
                    this.listCorrelation = this.jsonResponse.map((node: any) => {
                        node.correlation_value = parseFloat(node.correlation_value).toFixed(2)
                        if (node.feature_1 != this.currentFeature) {
                            node.feature_2 = node.feature_1
                            node.feature_1 = this.currentFeature
                        }
                        return node
                    });
                },
                error: (err) => {
                    this._apiSnackBar.openSnackBar(JSON.stringify(err))
                }
            })
        }
    }

}
