import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
    selector: 'app-def-independence',
    templateUrl: './independence.component.html'
})
export class DefIndependenceComponent {

    constructor(
        public dialogRef: MatDialogRef<DefIndependenceComponent>,
    ) { }

}
