import { Component, OnInit } from '@angular/core';
import { EmitterService } from 'src/app/services/emitter.service';

@Component({
    selector: 'app-local',
    templateUrl: './local.component.html',
    styleUrls: ['./local.component.scss']
})
export class LocalComponent implements OnInit {

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
