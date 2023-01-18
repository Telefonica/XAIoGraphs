import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
    selector: 'app-def-sufficience',
    templateUrl: './sufficience.component.html'
})
export class DefSufficienceComponent {

    constructor(
        public dialogRef: MatDialogRef<DefSufficienceComponent>,
    ) { }
}
