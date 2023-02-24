import { Component, OnInit } from '@angular/core';
import { ctsFairness } from 'src/app/constants/fairness';

import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { jsonFiles } from '../../../constants/jsonFiles';

@Component({
    selector: 'app-fairness-criteria-feature',
    templateUrl: './criteria-feature.component.html',
    styleUrls: ['../fairness.component.scss']
})
export class CriteriaFeatureComponent implements OnInit {

    listFeatures: string[] = [];
    featureSelected: string = ''
    featNameSelected: string = ''

    currentFeatureIndex: number = 0

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {}

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.fairness_sumarize_criterias).subscribe({
            next: (response: any) => {
                response.forEach(row => {
                    this.listFeatures.push(row[ctsFairness.sensitive_feature])
                });
            },
            complete: () => {
                this.updateFeature(0)
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    updateFeature(index) {
        this.currentFeatureIndex = index;
        this.featNameSelected = this.listFeatures[index]
    }

}
