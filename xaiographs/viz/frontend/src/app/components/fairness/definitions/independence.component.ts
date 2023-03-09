import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { KatexOptions } from 'ng-katex';

@Component({
    selector: 'app-def-independence',
    templateUrl: './independence.component.html',
    styleUrls: ['../fairness.component.scss']
})
export class DefIndependenceComponent {

    equation: string = 'independence\\ score= \\left | P\\left ( Y=k \\mid A=a \\right ) - P\\left ( Y=k \\mid A=b \\right ) \\right |'

    options: KatexOptions = {
        displayMode: false,
        output: 'mathml',
    };

    constructor(
        public dialogRef: MatDialogRef<DefIndependenceComponent>,
    ) { }

}
