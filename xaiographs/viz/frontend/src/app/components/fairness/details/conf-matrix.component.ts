import { Component, OnInit } from '@angular/core'

import { ReaderService } from 'src/app/services/reader.service'
import { SnackbarService } from 'src/app/services/snackbar.service'

import { ctsFiles } from '../../../constants/csvFiles'
import { ctsFairness } from '../../../constants/fairness'

@Component({
    selector: 'app-fairness-conf-matrix',
    templateUrl: './conf-matrix.component.html',
    styleUrls: ['../fairness.component.scss']
})
export class ConfMatrixComponent implements OnInit {

    listLabels: string[] = []
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
        this._apiReader.readCSV({ fileName: ctsFiles.fairness_confusion_matrix }).subscribe({
            next: (response: any) => {
                this.listLabels = response.headers.splice(1)
                this.listLabels.forEach((label: string) => {
                    this.sumRows[label] = 0
                })
                response.data.forEach((matrixRow) => {
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
            },
            complete: () => {
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

}
