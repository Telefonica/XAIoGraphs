import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { ctsFairness } from 'src/app/constants/fairness';

import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ctsFiles } from '../../../constants/csvFiles';

@Component({
    selector: 'app-fairness-criteria-feature',
    templateUrl: './criteria-feature.component.html'
})
export class CriteriaFeatureComponent implements OnInit {

    filterFeature = new FormControl();
    listFeatures: string[] = [];
    featureSelected: string = ''
    featNameSelected: string = ''

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {}

    ngOnInit(): void {
        this._apiReader.readCSV({ fileName: ctsFiles.fairness_sumarize_criterias }).subscribe({
            next: (response: any) => {
                response.data.forEach(row => {
                    this.listFeatures.push(row[ctsFairness.sensitive_value])
                });
            },
            complete: () => {
                this.filterFeature.setValue(0);
                this.updateFeature()
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    updateFeature() {
        this.featureSelected = this.filterFeature.value;
        this.featNameSelected = this.listFeatures[parseInt(this.filterFeature.value)]
    }

}
