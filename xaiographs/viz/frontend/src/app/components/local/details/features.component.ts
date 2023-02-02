import { Component, OnInit, OnDestroy } from '@angular/core';

import { EmitterService } from 'src/app/services/emitter.service';
import { ReaderService } from 'src/app/services/reader.service';
import { SnackbarService } from 'src/app/services/snackbar.service';

import { ChartType } from 'angular-google-charts';

import { jsonFiles } from '../../../constants/jsonFiles';
import { positiveFeaturesGraphStyle0, negativeFeaturesGraphStyle0 } from '../themes/local0';
import { positiveFeaturesGraphStyle1, negativeFeaturesGraphStyle1 } from '../themes/local1';

@Component({
    selector: 'app-local-features',
    templateUrl: './features.component.html',
    styleUrls: ['../local.component.scss']
})
export class LocalFeaturesComponent implements OnInit, OnDestroy {

    currentTarget: any;
    currentFeatures = 0;

    targetSubscription: any;
    featuresSubscription: any;
    themeSubscription: any;

    serviceResponse = [];
    dataSource = []

    type = ChartType.BarChart;
    dataGraph: any[] = [];
    columnNames: any[] = [];
    options: any = {};
    displayGraph: boolean = false;

    positiveFeaturesGraphStyle: any;
    negativeFeaturesGraphStyle: any;

    constructor(
        private _apiEmitter: EmitterService,
        private _apiReader: ReaderService,
        private _apiSnackBar: SnackbarService,
    ) {
        this.targetSubscription = this._apiEmitter.localTargetChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
        });
        this.featuresSubscription = this._apiEmitter.localFeaturesChangeEmitter.subscribe(() => {
            this.filterData();
            this.generateGraph();
        });
        this.themeSubscription = this._apiEmitter.themeChangeEmitter.subscribe(() => {
            this.prepareTheme();
            this.initGraph();
            this.generateGraph();
        })
    }

    ngOnInit() {
        this._apiReader.readJSON(jsonFiles.local_graph_nodes).subscribe({
            next: (response: any) => {
                this.serviceResponse = response;
            },
            complete: () => {
                if (this.serviceResponse.length > 0) {
                    this.prepareTheme();
                    this.initGraph();
                    this.filterData();
                    this.generateGraph();
                    this.displayGraph = true;
                } else {
                    this.displayGraph = false;
                }
            },
            error: (err) => {
                this.displayGraph = false;
                this._apiSnackBar.openSnackBar(JSON.stringify(err));
            }
        });
    }

    prepareTheme() {
        if (!this._apiEmitter.getTheme()) {
            this.positiveFeaturesGraphStyle = positiveFeaturesGraphStyle0
            this.negativeFeaturesGraphStyle = negativeFeaturesGraphStyle0
        } else {
            this.positiveFeaturesGraphStyle = positiveFeaturesGraphStyle1
            this.negativeFeaturesGraphStyle = negativeFeaturesGraphStyle1
        }
    }

    initGraph() {
        this.dataGraph = [];
        this.options = {
            legend: 'none',
            bar: { groupWidth: '90%' },
            chartArea: { right: 20, top: 20, width: '75%', height: '90%' },
            tooltip: { type: 'string', isHtml: true },
        };
    }

    filterData() {
        this.currentTarget = this._apiEmitter.getLocalTarget();
        this.currentFeatures = this._apiEmitter.getLocalFeatures();

        this.dataSource = this.serviceResponse.filter((row: any) => {
            return row.id == this.currentTarget.id;
        }).slice(0, this.currentFeatures);
    }

    generateGraph() {
        let transformDataSet: any[] = [];

        this.columnNames = [
            'Feature',
            'Weight',
            { role: 'style' },
            { 'type': 'string', 'role': 'tooltip', 'p': { 'html': true } },
        ];

        this.dataSource.forEach((data: any, index: number) => {
            let barStyle = '';
            const nodeImportance = parseFloat(data.node_importance);

            if (nodeImportance > 0) {
                const barStyleIndex = (Math.trunc(parseFloat(data.node_weight) / 10) - 1) % this.positiveFeaturesGraphStyle.length;
                barStyle = this.JSONCleaner(this.positiveFeaturesGraphStyle[barStyleIndex]);
            } else {
                const barStyleIndex = (Math.trunc(parseFloat(data.node_weight) / 10) - 1) % this.negativeFeaturesGraphStyle.length;
                barStyle = this.JSONCleaner(this.negativeFeaturesGraphStyle[barStyleIndex]);
            }
            transformDataSet.push([
                data.node_name,
                nodeImportance,
                barStyle,
                '<table style="padding:5px; width:150px;"><tr>' +
                '<td colspan="2" style="font-weight:bold; text-align:center; font-size:13px; color: #019ba9;">' + data.node_name + '</td>' +
                '</tr><tr>' +
                '<td colspan="2" style="border-bottom: 1px solid black; margin:10px;"></td>' +
                '</tr><tr>' +
                '<td style="font-weight:bold; padding-left: 5px">Importance</td>' +
                '<td style="text-align:right; padding-right: 5px">' + nodeImportance.toFixed(5) + '</td>' +
                '</tr></table>',
            ]);
        });

        this.dataGraph = transformDataSet;
    }

    JSONCleaner(value) {
        return JSON.stringify(value)
            .replace('{', '')
            .replace('}', '')
            .replace(/"/g, '')
            .replace(/,/g, ';')
    }

    ngOnDestroy(): void {
        this.targetSubscription.unsubscribe();
        this.featuresSubscription.unsubscribe();
        this.themeSubscription.unsubscribe();
    }

}
