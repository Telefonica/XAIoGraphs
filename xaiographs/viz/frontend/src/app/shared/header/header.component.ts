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

import { Component, OnInit, Input } from '@angular/core';

import { ctsGlobal } from '../../constants/global';
import { ctsHeader } from '../../constants/header';

@Component({
    selector: 'app-header',
    templateUrl: './header.component.html',
    styleUrls: ['./header.component.scss']
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
