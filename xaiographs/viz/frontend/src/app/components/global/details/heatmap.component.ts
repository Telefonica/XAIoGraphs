import { Component, OnDestroy, OnInit } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { jsonFiles } from '../../../constants/jsonFiles';
import { ctsTheme } from '../../../constants/theme';

@Component({
    selector: 'app-global-heatmap',
    templateUrl: './heatmap.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalHeatmapComponent implements OnInit, OnDestroy {

    currentTarget = '';

    serviceResponse = [];
    serviceResponseExplainability = [];
    orderedFeatures: string[] = [];
    filteredData: any[] = []
    dataSource: any[] = [];

    targetSubscription: any;
    themeSubscription: any;

    displayMap: boolean = false;

    colorTheme: any;
    heatMapLegendStyle: any;
    heatMapDefaultBg: string = ''

    minValue: number = 0
    maxValue: number = 0

    tooltipFeature = ''
    tooltipValue = ''

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.globalTargetChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateMap();
        });
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.generateMap();
        });
    }

    ngOnInit(): void {
        this._apiReader.readJSON(jsonFiles.global_target_explainability).subscribe({
            next: (responseExplainability: any) => {
                this.serviceResponseExplainability = responseExplainability;
            },
            complete: () => {

                this._apiReader.readJSON(jsonFiles.global_heat_map).subscribe({
                    next: (response: any) => {
                        this.serviceResponse = response;
                    },
                    complete: () => {
                        if (this.serviceResponse.length > 0) {
                            this.prepareTheme();
                            this.filterData();
                            this.generateMap();
                            this.displayMap = true;
                        } else {
                            this.displayMap = false;
                        }
                    },
                    error: (err) => {
                        this.displayMap = false;
                        this._apiSnackBar.openSnackBar(JSON.stringify(err));
                    }
                });
            },
            error: (errExplainability) => {
                this._apiSnackBar.openSnackBar(JSON.stringify(errExplainability));
            }
        });
    }

    prepareTheme() {
        this.colorTheme = JSON.parse('' + localStorage.getItem(ctsTheme.storageName))
        this.heatMapLegendStyle = 'linear-gradient(to bottom, ' + this.colorTheme.positiveValue + ',  ' + this.colorTheme.zeroValue + ', ' + this.colorTheme.negativeValue + ')'
    }


    filterData() {
        let orderedFeatExplain: any[] = []

        this.serviceResponseExplainability.forEach((row: any) => {
            if (row.target == this.currentTarget) {
                let valuesArray: any[] = [];
                Object.keys(row).forEach((key) => {
                    if (key != 'target') {
                        valuesArray.push({
                            key: key,
                            value: row[key]
                        })
                    }
                })
                orderedFeatExplain = valuesArray
            }
        });

        orderedFeatExplain.sort((element1: any, element2: any) => {
            return element2.value - element1.value
        })



        orderedFeatExplain.forEach((feature: any) => {
            this.orderedFeatures.push(feature['key'])
        })

        this.filteredData = []

        const listValues: number[] = []

        this.currentTarget = this._apiEmitter.getGlobalTarget();
        this.filteredData = this.serviceResponse.filter((node: any) => {
            if (node.target == this.currentTarget) {
                listValues.push(parseFloat(node.importance))
                return node.target
            } else
                return null
        })

        this.minValue = Math.min(...listValues)
        this.maxValue = Math.max(...listValues)
    }

    generateMap() {
        let featuresList: string[] = []
        this.dataSource = []

        this.orderedFeatures.forEach((featName: string) => {
            this.dataSource.push({
                feature: featName,
                values: []
            })
        })

        this.filteredData.forEach((features: any) => {
            const importance = parseFloat(features.importance)
            const limitTemp = (Math.abs(this.maxValue) > Math.abs(this.minValue)) ? Math.abs(this.maxValue) : Math.abs(this.minValue)
            const tempPercent = Math.floor((Math.abs(importance) / limitTemp) * 255).toString(16)
            const colorBase = (importance > 0) ? this.colorTheme.positiveValue : this.colorTheme.negativeValue

            const dataSourceIndex = this.orderedFeatures.indexOf(features.feature_name)
            this.dataSource[dataSourceIndex].values.push({
                value: features.feature_value,
                importance: features.importance,
                importanceLabeled: importance.toFixed(5),
                frecuency: Math.trunc(parseFloat(features.frequency) * 100),
                colorBase: colorBase + tempPercent
            })
        });

        this.dataSource.forEach((feature:any) => {
            feature.values.sort((element1: any, element2: any) => element2.importance - element1.importance)
        })
    }

    tooltipHover(feature, value) {
        this.tooltipFeature = feature
        this.tooltipValue = value
    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.themeSubscription.unsubscribe();
    }

}
