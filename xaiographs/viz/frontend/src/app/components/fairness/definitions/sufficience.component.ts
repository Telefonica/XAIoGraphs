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
