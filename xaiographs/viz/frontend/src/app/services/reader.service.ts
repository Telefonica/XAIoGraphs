import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
    providedIn: 'root'
})
export class ReaderService {
    jsonPath = 'assets/public/';

    constructor(private http: HttpClient) { }

    readJSON(fileName: any) {
        return this.http.get(this.jsonPath + fileName);
    }
}
