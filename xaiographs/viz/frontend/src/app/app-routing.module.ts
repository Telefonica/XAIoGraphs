import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ctsGlobal } from './constants/global'

import { GlobalComponent } from './components/global/global.component';
import { LocalComponent } from './components/local/local.component';
import { FairnessComponent } from './components/fairness/fairness.component';
import { DataComponent } from './components/data/data.component';


const routes: Routes = [
    {
        path: 'global',
        component: GlobalComponent,
    },
    {
        path: 'local',
        component: LocalComponent,
    },
    {
        path: 'fairness',
        component: FairnessComponent,
    },
    {
        path: 'data',
        component: DataComponent,
    },
    {
        path: '**',
        redirectTo: ctsGlobal.initial_component,
        pathMatch: 'full'
    },
];

@NgModule({
    imports: [ RouterModule.forRoot(routes, { initialNavigation: 'disabled' }) ],
    exports: [RouterModule]
})
export class AppRoutingModule { }
