import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FlexLayoutModule } from '@angular/flex-layout';
import { HttpClientModule } from '@angular/common/http';

import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSliderModule } from '@angular/material/slider';
import { MatDialogModule } from '@angular/material/dialog';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatRadioModule } from '@angular/material/radio';
import { MatGridListModule } from '@angular/material/grid-list';

import { GoogleChartsModule } from 'angular-google-charts';
import { TableVirtualScrollModule } from 'ng-table-virtual-scroll';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { GlobalComponent } from './components/global/global.component';
import { LocalComponent } from './components/local/local.component';
import { DataComponent } from './components/data/data.component';
import { FairnessComponent } from './components/fairness/fairness.component';
import { HeaderComponent } from './shared/header/header.component';
import { GlobalFeaturesComponent } from './components/global/details/features.component';
import { GlobalDistributionComponent } from './components/global/details/distribution.component';
import { GlobalTargetComponent } from './components/global/details/target.component';
import { GlobalGraphComponent } from './components/global/details/graph.component';
import { GlobalFeaturesTargetComponent } from './components/global/details/features_target.component';
import { LocalDatasetComponent } from './components/local/details/dataset.component';
import { LocalReasonComponent } from './components/local/details/reason.component';
import { LocalGraphComponent } from './components/local/details/graph.component';
import { LocalFeaturesComponent } from './components/local/details/features.component';
import { DataDatasetComponent } from './components/data/details/dataset.component';
import { CriteriasComponent } from './components/fairness/details/criterias.component';
import { CriteriaFeatureComponent } from './components/fairness/details/criteria-feature.component';
import { ConfMatrixComponent } from './components/fairness/details/conf-matrix.component';
import { DefIndependenceComponent } from './components/fairness/definitions/independence.component';
import { DefSeparationComponent } from './components/fairness/definitions/separation.component';
import { DefSufficienceComponent } from './components/fairness/definitions/sufficience.component';
import { FeatureSufficienceComponent } from './components/fairness/details/feature-sufficience.component';
import { FeatureSeparationComponent } from './components/fairness/details/feature-separation.component';
import { FeatureIndependenceComponent } from './components/fairness/details/feature-independence.component';
import { FeatureCorrelationComponent } from './components/fairness/details/feature-correlation.component';
import { LegendComponent } from './components/fairness/details/legend.component';
import { LocalFilterComponent } from './components/local/details/filter.component';

@NgModule({
    declarations: [
        AppComponent,
        GlobalComponent,
        LocalComponent,
        DataComponent,
        FairnessComponent,
        HeaderComponent,
        GlobalFeaturesComponent,
        GlobalDistributionComponent,
        GlobalTargetComponent,
        GlobalGraphComponent,
        GlobalFeaturesTargetComponent,
        LocalDatasetComponent,
        LocalReasonComponent,
        LocalGraphComponent,
        LocalFeaturesComponent,
        DataDatasetComponent,
        CriteriasComponent,
        CriteriaFeatureComponent,
        ConfMatrixComponent,
        DefIndependenceComponent,
        DefSeparationComponent,
        DefSufficienceComponent,
        FeatureSufficienceComponent,
        FeatureSeparationComponent,
        FeatureIndependenceComponent,
        FeatureCorrelationComponent,
        LegendComponent,
        LocalFilterComponent,
    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        FlexLayoutModule,
        HttpClientModule,
        BrowserAnimationsModule,
        FormsModule,
        ReactiveFormsModule,
        MatIconModule,
        MatTooltipModule,
        MatMenuModule,
        MatSnackBarModule,
        MatFormFieldModule,
        MatInputModule,
        MatExpansionModule,
        MatSelectModule,
        MatCardModule,
        MatSlideToggleModule,
        MatSliderModule,
        MatDialogModule,
        MatProgressBarModule,
        MatButtonModule,
        MatDatepickerModule,
        MatProgressSpinnerModule,
        MatPaginatorModule,
        MatSortModule,
        MatTableModule,
        MatCheckboxModule,
        MatRadioModule,
        MatGridListModule,
        GoogleChartsModule,
        TableVirtualScrollModule,
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule { }
