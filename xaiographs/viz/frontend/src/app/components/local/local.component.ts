import { Component } from '@angular/core';
import { EmitterService } from 'src/app/services/emitter.service';

@Component({
    selector: 'app-local',
    templateUrl: './local.component.html',
    styleUrls: ['./local.component.scss']
})
export class LocalComponent {

    theme: boolean = false

    constructor(
        private _apiEmitter: EmitterService,
    ) { }

    openPalette() {
        this._apiEmitter.setTheme('');
    }

}
