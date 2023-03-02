import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { KatexOptions } from 'ng-katex';

@Component({
    selector: 'app-def-independence',
    templateUrl: './independence.component.html'
})
export class DefIndependenceComponent {

    equation: string = 'independence\\ score = \\left | P(Y=y \\mid A=a) - P(Y=y \\mid A=b) \\right |'

    options: KatexOptions = {
        displayMode: false,
        output: 'mathml',
    };

    constructor(
        public dialogRef: MatDialogRef<DefIndependenceComponent>,
    ) { }

}
