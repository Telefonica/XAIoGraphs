import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
    selector: 'app-def-separation',
    templateUrl: './separation.component.html'
})
export class DefSeparationComponent {

    constructor(
        public dialogRef: MatDialogRef<DefSeparationComponent>,
    ) { }

}
