import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class ReaderService {
    apiUrl = environment.apiUrl + '/reader';

    constructor(private http: HttpClient) { }

    readCSV(body: any) {
        return this.http.post(`${this.apiUrl}/readCSV`, body);
    }

    listGlobalTarget(body: any) {
        return this.http.post(`${this.apiUrl}/listGlobalTarget`, body);
    }

    readGlobalNodesWeights(body: any) {
        return this.http.post(`${this.apiUrl}/readGlobalNodesWeights`, body);
    }

    readGlobalEdgesWeights(body: any) {
        return this.http.post(`${this.apiUrl}/readGlobalEdgesWeights`, body);
    }

    readLocalDataset(body: any) {
        return this.http.post(`${this.apiUrl}/readLocalDataset`, body);
    }

    readLocalNodesWeights(body: any) {
        return this.http.post(`${this.apiUrl}/readLocalNodesWeights`, body);
    }

    readLocalEdgesWeights(body: any) {
        return this.http.post(`${this.apiUrl}/readLocalEdgesWeights`, body);
    }

    readLocalReasonWhy(body: any) {
        return this.http.post(`${this.apiUrl}/readLocalReasonWhy`, body);
    }


    listDatasetHeaders(body: any) {
        return this.http.post(`${this.apiUrl}/listDatasetHeaders`, body);
    }
    readDatasetSelected(body: any) {
        return this.http.post(`${this.apiUrl}/readDatasetSelected`, body);
    }
}
