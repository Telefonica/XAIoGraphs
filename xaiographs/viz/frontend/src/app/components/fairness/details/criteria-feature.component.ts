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

import { Component, OnInit, ViewChild } from '@angular/core';
import { ctsFairness } from 'src/app/constants/fairness';

import html2canvas from "html2canvas";

import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { jsonFiles } from '../../../constants/jsonFiles';
import { ctsGlobal } from '../../../constants/global'

@Component({
    selector: 'app-fairness-criteria-feature',
    templateUrl: './criteria-feature.component.html',
    styleUrls: ['../fairness.component.scss']
})
export class CriteriaFeatureComponent implements OnInit {
    @ViewChild('exportableArea') exportableArea;
    hidePicture: boolean = false;

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

    downloadPicture() {
        this.hidePicture = true
        this.generateImage2Download()
    }
    generateImage2Download() {
        this._apiSnackBar.openDownloadSnackBar(ctsGlobal.downloading_message, false).finally(() => {
            html2canvas(this.exportableArea.nativeElement).then(exportCanvas => {
                const canvas = exportCanvas.toDataURL().replace(/^data:image\/[^;]*/, 'data:application/octet-stream');
                let link = document.createElement('a');
                link.download = ctsGlobal.label_fairness_feature_fairness_criterias + ctsGlobal.image_extension;
                link.href = canvas;
                link.click();
                this.hidePicture = false
            }).catch((err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
                this.hidePicture = false
            });
        })
    }

}
