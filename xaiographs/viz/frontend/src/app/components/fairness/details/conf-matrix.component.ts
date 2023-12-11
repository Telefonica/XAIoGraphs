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

import { ReaderService } from 'src/app/services/reader.service'
import { SnackbarService } from 'src/app/services/snackbar.service'

import html2canvas from "html2canvas";

import { jsonFiles } from '../../../constants/jsonFiles'
import { ctsFairness } from '../../../constants/fairness'
import { ctsGlobal } from '../../../constants/global'

@Component({
    selector: 'app-fairness-conf-matrix',
    templateUrl: './conf-matrix.component.html',
    styleUrls: ['../fairness.component.scss']
})
export class ConfMatrixComponent implements OnInit {
    @ViewChild('exportableArea') exportableArea;
    hidePicture: boolean = false;

    listLabels: string[] = []
    dataSource: any[] = []
    matrixValues = {}
    matrixPercent = {}
    matrixOpacity = {}
    sumRows = {}

    maxList: number[] = []
    minList: number[] = []

    displayPercent = false

    constructor(
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) { }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.fairness_confusion_matrix).subscribe({
            next: (response: any) => {
                this.listLabels = Object.keys(response[0])
                response.forEach((row: any, index) => {
                    this.dataSource.push(Object.assign({[ctsFairness.confMatrixIndex] : this.listLabels[index]}, row))
                });
            },
            complete: () => {
                this.listLabels.forEach((label: string) => {
                    this.sumRows[label] = 0
                })
                this.dataSource.forEach((matrixRow) => {
                    const matrixElement = {}
                    this.listLabels.forEach((label: string) => {
                        matrixElement[label] = 0
                    })
                    this.matrixValues[matrixRow[ctsFairness.confMatrixIndex]] = { ...matrixElement }
                    this.matrixPercent[matrixRow[ctsFairness.confMatrixIndex]] = { ...matrixElement }
                    this.matrixOpacity[matrixRow[ctsFairness.confMatrixIndex]] = { ...matrixElement }

                    let rowValues: any = []
                    rowValues = (Object.values(matrixRow)).map((str, index) => {
                        return (index > 0) ? Number(str) : null;
                    }).slice(1)
                    this.maxList.push(Math.max(...rowValues));
                    this.minList.push(Math.min(...rowValues));

                    this.listLabels.forEach((label) => {
                        this.sumRows[label] += parseInt(matrixRow[label])
                        this.matrixValues[matrixRow[ctsFairness.confMatrixIndex]][label] = parseInt(matrixRow[label])
                        this.matrixPercent[matrixRow[ctsFairness.confMatrixIndex]][label] = parseInt(matrixRow[label])
                        this.matrixOpacity[matrixRow[ctsFairness.confMatrixIndex]][label] = parseInt(matrixRow[label])
                    })
                })

                const maxValue = Math.max(...this.maxList)
                const minValue = Math.min(...this.minList)
                this.listLabels.forEach((labelRow) => {
                    this.listLabels.forEach((labelColumn) => {
                        this.matrixPercent[labelRow][labelColumn] /= this.sumRows[labelRow]
                        this.matrixOpacity[labelRow][labelColumn] /= (maxValue - minValue)
                    });
                })
            },
            error: (err) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(err))
            }
        })
    }

    getBGColor(row: string, column: string) {
        const opacity = this.matrixOpacity[row][column]
        const bgColor = { 'background-color': 'rgba(195, 95, 133, ' + opacity + ')' }
        const fontColor = { 'color': 'White' }

        return (parseFloat(opacity) < 0.5) ? bgColor : { ...bgColor, ...fontColor }
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
                link.download = ctsGlobal.label_fairness_confusion_matrix + ctsGlobal.image_extension;
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
