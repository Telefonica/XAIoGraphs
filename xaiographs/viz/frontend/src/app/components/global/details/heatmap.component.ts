import { Component, OnDestroy, OnInit } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { jsonFiles } from '../../../constants/jsonFiles';
import { heatMapPositiveStyle0, heatMapNegativeStyle0, heatMapDefaultStyle0 } from '../themes/global0';
import { heatMapPositiveStyle1, heatMapNegativeStyle1, heatMapDefaultStyle1 } from '../themes/global1';

@Component({
    selector: 'app-global-heatmap',
    templateUrl: './heatmap.component.html',
    styleUrls: ['../global.component.scss']
})
export class GlobalHeatmapComponent implements OnInit, OnDestroy {

    currentTarget = '';

    serviceResponse = [];
    filteredData: any[] = []
    dataSource: any[] = [];

    targetSubscription: any;
    themeSubscription: any;

    displayMap: boolean = false;

    heatMapPositiveStyle: any;
    heatMapNegativeStyle: any;
    heatMapLegendStyle: any;
    heatMapDefaultBg: string = ''
    heatMapLegendPositive: string = ''
    heatMapLegendNegative: string = ''

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
    }

    prepareTheme() {
        if (!this._apiEmitter.getTheme()) {
            this.heatMapPositiveStyle = heatMapPositiveStyle0
            this.heatMapNegativeStyle = heatMapNegativeStyle0
            this.heatMapDefaultBg = 'rgb(' + heatMapDefaultStyle0.join(', ') + ')'
        } else {
            this.heatMapPositiveStyle = heatMapPositiveStyle1
            this.heatMapNegativeStyle = heatMapNegativeStyle1
            this.heatMapDefaultBg = 'rgb(' + heatMapDefaultStyle1.join(', ') + ')'
        }
        this.heatMapLegendStyle = 'linear-gradient(to bottom, rgb(' + this.heatMapPositiveStyle.join(', ') + '),  ' + this.heatMapDefaultBg + ', rgb(' + this.heatMapNegativeStyle.join(', ') + '))'
        // this.heatMapDefaultBg = 'rgb(' + this.heatMapNegativeStyle.join(', ') + ')'
        this.heatMapLegendPositive = 'rgb(' + this.heatMapNegativeStyle.join(', ') + ')'
        this.heatMapLegendNegative = 'rgb(' + this.heatMapPositiveStyle.join(', ') + ')'
    }

    filterData() {
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

        this.filteredData.forEach((features: any) => {
            const importance = parseFloat(features.importance)
            const limitTemp = (Math.abs(this.maxValue) > Math.abs(this.minValue)) ? Math.abs(this.maxValue) : Math.abs(this.minValue)
            const tempPercent: string = (Math.abs(importance) / limitTemp).toFixed(2)
            let colorBase: string[] = (importance > 0) ? Object.create(this.heatMapPositiveStyle) : Object.create(this.heatMapNegativeStyle)
            colorBase.push(tempPercent)

            const currentTemperature = 'rgba(' + colorBase.join(', ') + ')'
            const fontColor = (Math.abs(importance) < (limitTemp * 0.2)) ? 'rgb(255, 255, 255)' : ((importance > 0) ? 'rgb(' + this.heatMapNegativeStyle.join(',') + ')' : 'rgb(' + this.heatMapPositiveStyle.join(',') + ')')

            if (featuresList.indexOf(features.feature_name) < 0) {
                featuresList.push(features.feature_name)
                this.dataSource.push({
                    feature: features.feature_name,
                    values: [{
                        value: features.feature_value,
                        importance: features.importance,
                        importanceLabeled: importance.toFixed(5),
                        frecuency: Math.trunc(parseFloat(features.frequency) * 100),
                        fontColor: fontColor,
                        temperature: currentTemperature,
                        tempPercent: tempPercent
                    }]
                })
            } else {
                this.dataSource.every((feat: any) => {
                    if (feat.feature == features.feature_name) {
                        feat.values.push({
                            value: features.feature_value,
                            importance: features.importance,
                            importanceLabeled: importance.toFixed(5),
                            frecuency: Math.trunc(parseFloat(features.frequency) * 100),
                            fontColor: fontColor,
                            temperature: currentTemperature,
                            tempPercent: tempPercent
                        })
                        return false
                    }
                    return true
                })
            }
        });
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
