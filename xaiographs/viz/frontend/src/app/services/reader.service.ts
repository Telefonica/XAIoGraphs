import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
    providedIn: 'root'
})
export class ReaderService {
    assetsPath = 'assets/'
    jsonPath = 'public/';
    colors = 'colors.json';

    orderedTarget: string[] = []

    constructor(private http: HttpClient) { }

    setOrderedTarget(targets: string[]) {
        this.orderedTarget = targets
    }

    getOrderedTarget(target: string) {
        return this.orderedTarget.indexOf(target)
    }

    readJSON(fileName: any) {
        return this.http.get(this.assetsPath + this.jsonPath + fileName);
    }
    readColors() {
        return this.http.get(this.assetsPath + this.colors);
    }
}
