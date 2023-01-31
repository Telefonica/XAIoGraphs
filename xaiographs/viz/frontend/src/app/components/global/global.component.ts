import { Component, OnInit } from '@angular/core';
import { EmitterService } from 'src/app/services/emitter.service';

@Component({
    selector: 'app-global',
    templateUrl: './global.component.html',
    styleUrls: ['./global.component.scss']
})
export class GlobalComponent implements OnInit {

    theme: boolean = false

    constructor(
        private _apiEmitter: EmitterService,
    ) { }

    ngOnInit(): void {
        this.theme = this._apiEmitter.getTheme();
    }

    changeTheme() {
        this._apiEmitter.setTheme(this.theme);
    }

}
