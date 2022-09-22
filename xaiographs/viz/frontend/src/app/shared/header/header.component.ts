/* ANGULAR CORE */
import { Component, OnInit, Input } from '@angular/core';

/* LOCAL FILES */
import { ctsGlobal } from '../../constants/global';
import { ctsHeader } from '../../constants/header';

@Component({
    selector: 'app-header',
    templateUrl: './header.component.html',
})
export class HeaderComponent implements OnInit {

    titleApp = ctsGlobal.titleApp;
    currentLang = ctsGlobal.initial_language;
    optionsMenu = ctsHeader.menu;

    langDictionary: any = {};

    @Input() current = ctsGlobal.initial_component;

    constructor() { }

    ngOnInit(): void { }

}
