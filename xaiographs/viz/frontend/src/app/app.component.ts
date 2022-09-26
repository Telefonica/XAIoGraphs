/* ANGULAR CORE */
import { Component, OnInit, HostListener } from '@angular/core';
import { Router, RoutesRecognized } from '@angular/router';

/* ANGULAR SERVICES */
import { SnackbarService } from './services/snackbar.service';

/* LOCAL FILES */
import { ctsGlobal } from './constants/global';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    title = ctsGlobal.titleApp;
    currentModule = ctsGlobal.initial_component;

    constructor(
        private router: Router,
    ) {
        this.router.navigate(['/global'], {skipLocationChange: true});
    }

    ngOnInit() {
        this.router.events.subscribe(val => {
            if (val instanceof RoutesRecognized) {
                if (val.state.root.firstChild) {
                    this.currentModule = val.state.root.firstChild.url[0].path;
                }
            }
        });
    }
}
