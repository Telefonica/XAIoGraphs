import { Component, OnInit } from '@angular/core';
import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';

import { jsonFiles } from '../../constants/jsonFiles'

@Component({
    selector: 'app-local',
    templateUrl: './local.component.html',
    styleUrls: ['./local.component.scss']
})
export class LocalComponent implements OnInit {

    fileExists: boolean = false;

    constructor(
        private _apiReader: ReaderService,
        private _apiEmitter: EmitterService,
    ) {}

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.local_dataset_reliability).subscribe({
            complete: () => {
                this.fileExists = true
            },
            error: (err) => {
                this.fileExists = false
            }
        });
    }

    openPalette() {
        this._apiEmitter.setTheme('');
    }

}
