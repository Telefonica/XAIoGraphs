import { Component, OnInit } from '@angular/core';
import { ReaderService } from 'src/app/services/reader.service';

import { jsonFiles } from '../../constants/jsonFiles'

@Component({
    selector: 'app-fairness',
    templateUrl: './fairness.component.html',
    styleUrls: ['./fairness.component.scss']
})
export class FairnessComponent implements OnInit {

    fileExists: boolean = false;

    constructor(
        private _apiReader: ReaderService,
    ) { }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.fairness_confusion_matrix).subscribe({
            complete: () => {
                this.fileExists = true
            },
            error: (err) => {
                this.fileExists = false
            }
        });
    }

}
