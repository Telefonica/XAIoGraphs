import { Component, Input, OnChanges } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { ReaderService } from 'src/app/services/reader.service'
import { SnackbarService } from 'src/app/services/snackbar.service'

import { ctsFiles } from '../../../constants/csvFiles'

import { DefIndependenceComponent } from '../definitions/independence.component';
import { DefSeparationComponent } from '../definitions/separation.component';
import { DefSufficienceComponent } from '../definitions/sufficience.component';

@Component({
    selector: 'app-feature-separation',
    templateUrl: './feature-separation.component.html',
    styles: [
    ]
})
export class FeatureSeparationComponent implements OnChanges {

    listData: any[] = []
    headers: string[] = [
        'sensitive_value',
        'score_A',
        'score_A_value',
        'score_A_class',
        'score_B',
        'score_B_value',
        'score_B_class',
        'score_C',
        'score_C_value',
        'score_C_class',
        'score_D',
        'score_D_value',
        'score_D_class',
    ]
    moduleName: string = 'separation'

    @Input() currentFeature = '';

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
        private dialog: MatDialog,
    ) { }

    ngOnChanges(): void {
        this.listData = [];
        let dataDict = {};
        if (this.currentFeature) {
            this._apiReader.readFairnessFeature({
                fileName: ctsFiles['fairness_' + this.moduleName],
                feature: this.currentFeature,
            }).subscribe({
                next: (response: any) => {
                    response.forEach(element => {
                        if (!dataDict[element.sensitive_value]) {
                            dataDict[element.sensitive_value] = {
                                sensitive_value: element.sensitive_value,
                                score_A: '',
                                score_A_value: 0,
                                score_A_class: '',
                                score_B: '',
                                score_B_value: 0,
                                score_B_class: '',
                                score_C: '',
                                score_C_value: 0,
                                score_C_class: '',
                                score_D: '',
                                score_D_value: 0,
                                score_D_class: '',
                            }
                        }
                        dataDict[element.sensitive_value]['score_' + element.target_label] = element[this.moduleName + '_category']
                        dataDict[element.sensitive_value]['score_' + element.target_label + '_value'] = (parseFloat(element[this.moduleName + '_score'])*100).toFixed(2) + ' %'
                        dataDict[element.sensitive_value]['score_' + element.target_label + '_class'] = element[this.moduleName + '_category'].replace('+', 'P')
                    });
                },
                complete: () => {
                    Object.keys(dataDict).forEach((key: any) => {
                        this.listData.push(dataDict[key]);
                    });
                },
                error: (err) => {
                    this._apiSnackBar.openSnackBar(JSON.stringify(err))
                }
            })
        }

    }

    openIndependence() {
        this.dialog.open(DefIndependenceComponent, {
            width: '50%',
            height: '80%',
            autoFocus: false
        });
    }
    openSeparation() {
        this.dialog.open(DefSeparationComponent, {
            width: '50%',
            height: '80%',
            autoFocus: false
        });

    }
    openSufficience() {
        this.dialog.open(DefSufficienceComponent, {
            width: '50%',
            height: '80%',
            autoFocus: false
        });
    }

}
