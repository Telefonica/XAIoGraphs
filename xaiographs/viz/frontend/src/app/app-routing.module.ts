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

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ctsGlobal } from './constants/global'

import { GlobalComponent } from './components/global/global.component';
import { LocalComponent } from './components/local/local.component';
import { FairnessComponent } from './components/fairness/fairness.component';


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
