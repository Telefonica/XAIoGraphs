import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { KatexOptions } from 'ng-katex';

@Component({
    selector: 'app-def-separation',
    templateUrl: './separation.component.html',
    styleUrls: ['../fairness.component.scss']
})
export class DefSeparationComponent {

    equation: string = 'separation\\ score= \\left | P\\left ( Y=k \\mid T=k, A=a \\right ) - P\\left ( Y=k \\mid T=k, A=b \\right ) \\right |'

    options: KatexOptions = {
        displayMode: false,
        output: 'mathml',
    };

    constructor(
        public dialogRef: MatDialogRef<DefSeparationComponent>,
    ) { }

}
