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

import { Component, Input, OnChanges } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { ReaderService } from 'src/app/services/reader.service'
import { SnackbarService } from 'src/app/services/snackbar.service'

import { jsonFiles } from '../../../constants/jsonFiles'

import { DefIndependenceComponent } from '../definitions/independence.component';
import { DefSeparationComponent } from '../definitions/separation.component';
import { DefSufficienceComponent } from '../definitions/sufficience.component';

@Component({
    selector: 'app-feature-sufficience',
    templateUrl: './feature-sufficience.component.html',
    styleUrls: ['../fairness.component.scss']
})
export class FeatureSufficienceComponent implements OnChanges {

    listData: any[] = []
    jsonResponse: any = []
    headers: string[] = []
    moduleName: string = 'sufficiency'

    @Input() currentFeature = '';
    @Input() hidePicture = false;

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
        private dialog: MatDialog,
    ) { }

    ngOnChanges(): void {
        this.listData = [];
        let dataDict = {};
        if (this.currentFeature) {
            this._apiReader.readJSON(jsonFiles['fairness_' + this.moduleName]).subscribe({
                next: (response: any) => {
                    this.jsonResponse = response.filter((row: any) => {
                        return row.sensitive_feature == this.currentFeature
                    })
                },
                complete: () => {
                    this.jsonResponse.forEach(element => {
                        if(this.headers.indexOf(element.target_label) < 0) {
                            this.headers.push(element.target_label)
                        }
                        if (!dataDict[element.sensitive_value]) {
                            dataDict[element.sensitive_value] = {
                                sensitive_value: element.sensitive_value
                            }
                        }
                        dataDict[element.sensitive_value]['score_' + element.target_label] = element[this.moduleName + '_category']
                        dataDict[element.sensitive_value]['score_' + element.target_label + '_value'] = (parseFloat(element[this.moduleName + '_score']) * 100).toFixed(2) + ' %'
                        dataDict[element.sensitive_value]['score_' + element.target_label + '_class'] = element[this.moduleName + '_category'].replace('+', 'P')
                    });

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
            width: '40%',
            autoFocus: false
        });
    }
    openSeparation() {
        this.dialog.open(DefSeparationComponent, {
            width: '40%',
            autoFocus: false
        });

    }
    openSufficience() {
        this.dialog.open(DefSufficienceComponent, {
            width: '40%',
            autoFocus: false
        });
    }

}
