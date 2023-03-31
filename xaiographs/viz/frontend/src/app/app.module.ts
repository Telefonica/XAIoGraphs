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

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';
import { FlexLayoutModule } from '@angular/flex-layout';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatDialogModule } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatMenuModule } from '@angular/material/menu';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelectModule } from '@angular/material/select';
import { MatSliderModule } from '@angular/material/slider';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSortModule } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';

import { ColorPickerModule } from 'ngx-color-picker';
import { GoogleChartsModule } from 'angular-google-charts';
import { KatexModule } from 'ng-katex';
import { NgApexchartsModule } from 'ng-apexcharts'
import { TableVirtualScrollModule } from 'ng-table-virtual-scroll';

import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { ConfMatrixComponent } from './components/fairness/details/conf-matrix.component';
import { CriteriaFeatureComponent } from './components/fairness/details/criteria-feature.component';
import { CriteriasComponent } from './components/fairness/details/criterias.component';
import { DefIndependenceComponent } from './components/fairness/definitions/independence.component';
import { DefSeparationComponent } from './components/fairness/definitions/separation.component';
import { DefSufficienceComponent } from './components/fairness/definitions/sufficience.component';
import { FairnessComponent } from './components/fairness/fairness.component';
import { FeatureCorrelationComponent } from './components/fairness/details/feature-correlation.component';
import { FeatureIndependenceComponent } from './components/fairness/details/feature-independence.component';
import { FeatureSeparationComponent } from './components/fairness/details/feature-separation.component';
import { FeatureSufficienceComponent } from './components/fairness/details/feature-sufficience.component';
import { GlobalComponent } from './components/global/global.component';
import { GlobalDistributionComponent } from './components/global/details/distribution.component';
import { GlobalFeaturesComponent } from './components/global/details/features.component';
import { GlobalFeaturesTargetComponent } from './components/global/details/features_target.component';
import { GlobalGraphComponent } from './components/global/details/graph.component';
import { GlobalHeatmapComponent } from './components/global/details/heatmap.component';
import { GlobalTargetComponent } from './components/global/details/target.component';
import { GlobalTargetExplainabilityComponent } from './components/global/details/target-explainability.component';
import { HeaderComponent } from './shared/header/header.component';
import { LegendComponent } from './components/fairness/details/legend.component';
import { LocalComponent } from './components/local/local.component';
import { LocalDatasetComponent } from './components/local/details/dataset.component';
import { LocalFeaturesComponent } from './components/local/details/features.component';
import { LocalFilterComponent } from './components/local/details/filter.component';
import { LocalGraphComponent } from './components/local/details/graph.component';
import { LocalReasonComponent } from './components/local/details/reason.component';
import { PaletteComponent } from './shared/palette/palette.component';

@NgModule({
    declarations: [
        AppComponent,
        ConfMatrixComponent,
        CriteriaFeatureComponent,
        CriteriasComponent,
        DefIndependenceComponent,
        DefSeparationComponent,
        DefSufficienceComponent,
        FairnessComponent,
        FeatureCorrelationComponent,
        FeatureIndependenceComponent,
        FeatureSeparationComponent,
        FeatureSufficienceComponent,
        GlobalComponent,
        GlobalDistributionComponent,
        GlobalFeaturesComponent,
        GlobalFeaturesTargetComponent,
        GlobalGraphComponent,
        GlobalHeatmapComponent,
        GlobalTargetComponent,
        GlobalTargetExplainabilityComponent,
        HeaderComponent,
        LegendComponent,
        LocalComponent,
        LocalDatasetComponent,
        LocalFeaturesComponent,
        LocalFilterComponent,
        LocalGraphComponent,
        LocalReasonComponent,
        PaletteComponent,
    ],
    imports: [
        AppRoutingModule,
        BrowserAnimationsModule,
        BrowserModule,
        ColorPickerModule,
        FlexLayoutModule,
        FormsModule,
        GoogleChartsModule,
        HttpClientModule,
        KatexModule,
        MatButtonModule,
        MatCardModule,
        MatCheckboxModule,
        MatDatepickerModule,
        MatDialogModule,
        MatExpansionModule,
        MatFormFieldModule,
        MatGridListModule,
        MatIconModule,
        MatInputModule,
        MatMenuModule,
        MatPaginatorModule,
        MatProgressBarModule,
        MatProgressSpinnerModule,
        MatRadioModule,
        MatSelectModule,
        MatSliderModule,
        MatSlideToggleModule,
        MatSnackBarModule,
        MatSortModule,
        MatTableModule,
        MatTooltipModule,
        NgApexchartsModule,
        ReactiveFormsModule,
        TableVirtualScrollModule,
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule { }
