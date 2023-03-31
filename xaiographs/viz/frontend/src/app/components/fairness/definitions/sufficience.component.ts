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

import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { KatexOptions } from 'ng-katex';

@Component({
    selector: 'app-def-sufficience',
    templateUrl: './sufficience.component.html',
    styleUrls: ['../fairness.component.scss']
})
export class DefSufficienceComponent {

    equation: string = 'sufficiency\\ score= \\left | P\\left ( T=k \\mid Y=k, A=a \\right ) - P\\left ( T=k \\mid Y=k, A=b \\right ) \\right |'

    options: KatexOptions = {
        displayMode: false,
        output: 'mathml',
    };

    constructor(
        public dialogRef: MatDialogRef<DefSufficienceComponent>,
    ) { }
}
