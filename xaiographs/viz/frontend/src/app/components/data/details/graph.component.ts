import { Component, OnInit, Input } from '@angular/core';

import { ChartType } from 'angular-google-charts';

@Component({
    selector: 'app-dataset-graph',
    templateUrl: './graph.component.html',
    styleUrls: ['../data.component.scss']
})
export class DatasetGraphComponent implements OnInit {

    @Input() dataSource: any[] = [];
    @Input() columnName: string = '';

    groupData
    type = ChartType.ColumnChart;
    dataGraph: any[] = [];
    columnNames = ['Value', 'Count'];;
    options: any = {};
    displayGraph: boolean = false;

    constructor() { }

    ngOnInit(): void {
        const graphSource: any[] = [];

        this.dataSource.forEach((row: any) => {
            let element = {}
            element[this.columnName] = row[this.columnName]
            graphSource.push(element)
        })

        this.groupData = graphSource.reduce((p, c) => {
            let name = c[this.columnName];
            if (!p.hasOwnProperty(name)) {
                p[name] = 0;
            }
            p[name]++;
            return p;
        }, {})

        this.initGraph();
        this.createGraph();
    }

    initGraph() {
        this.dataGraph = [];
        this.options = {
            legend: 'none',
            bar: { groupWidth: '90%' },
            chartArea: { right: 20, top: 20, width: '80%', height: '75%' },
            tooltip: { type: 'string', isHtml: true },
        };
    }

    createGraph() {
        Object.keys(this.groupData).sort().forEach((name) => {
            this.dataGraph.push([name, this.groupData[name]])
        })
        this.displayGraph = true
    }

}
