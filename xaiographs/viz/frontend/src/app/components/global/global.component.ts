import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';

import { PaletteComponent } from 'src/app/shared/palette/palette.component';

import { jsonFiles } from '../../constants/jsonFiles';

@Component({
    selector: 'app-global',
    templateUrl: './global.component.html',
    styleUrls: ['./global.component.scss']
})
export class GlobalComponent implements OnInit {

    serviceResponse: any;
    fileExists: boolean = false;

    constructor(
        private dialog: MatDialog,
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
    ) { }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.global_target_distribution).subscribe({
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                let orderedTarget: any[] = [];
                if (this.serviceResponse.length > 0) {
                    this.serviceResponse.sort((element1, element2) => parseInt(element2.count) - parseInt(element1.count));
                    this.serviceResponse.forEach((target: any) => {
                        orderedTarget.push(target.target)
                    });
                }
                this._apiReader.setOrderedTarget(orderedTarget)
                this.fileExists = true
            },
            error: (err) => {
                this.fileExists = false
            }
        });
    }

    openPalette() {
        this.dialog.open(PaletteComponent, {
            width: '50%',
            autoFocus: false
        }).afterClosed().subscribe(response => {
            if (response)
                this._apiEmitter.setTheme(response)
        });
    }

}
