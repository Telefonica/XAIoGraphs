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

import { Injectable, EventEmitter } from '@angular/core';

import { ctsTheme } from '../constants/theme';

@Injectable({
    providedIn: 'root'
})
export class EmitterService {

    currentGlobalTarget;
    currentGlobalFeatures;
    currentGlobalFrencuency;
    currentLocalTarget;
    currentLocalFeatures;

    globalTargetChangeEmitter = new EventEmitter();
    globalFeaturesChangeEmitter = new EventEmitter();
    globalFrecuencyChangeEmitter = new EventEmitter();
    localTargetChangeEmitter = new EventEmitter();
    localFeaturesChangeEmitter = new EventEmitter();
    themeChangeEmitter = new EventEmitter();

    constructor() { }

    setGlobalTarget(target: string) {
        this.currentGlobalTarget = target;
        this.globalTargetChangeEmitter.emit();
    }
    getGlobalTarget() {
        return this.currentGlobalTarget;
    }

    setGlobalFeatures(features: number) {
        this.currentGlobalFeatures = features;
        this.globalFeaturesChangeEmitter.emit();
    }
    getGlobalFeatures() {
        return this.currentGlobalFeatures;
    }

    setGlobalFrecuency(frecuency: number) {
        this.currentGlobalFrencuency = frecuency;
        this.globalFrecuencyChangeEmitter.emit();
    }

    getGlobalFrecuency() {
        return this.currentGlobalFrencuency;
    }

    setAllGlobal(target: any, features: number, frecuency: number) {
        this.currentGlobalTarget = target;
        this.currentGlobalFeatures = features;
        this.currentGlobalFrencuency = frecuency;
        this.globalTargetChangeEmitter.emit();
    }

    setLocalTarget(target: any) {
        this.currentLocalTarget = target;
        this.localTargetChangeEmitter.emit();
    }
    getLocalTarget() {
        return this.currentLocalTarget;
    }

    setLocalFeatures(features: number) {
        this.currentLocalFeatures = features;
        this.localFeaturesChangeEmitter.emit();
    }
    getLocalFeatures() {
        return this.currentLocalFeatures;
    }

    setBothLocal(target: string, features: number) {
        this.currentLocalTarget = target;
        this.currentLocalFeatures = features;
        this.localTargetChangeEmitter.emit();
    }

    setTheme(newColors) {
        localStorage.removeItem(ctsTheme.storageName)
        localStorage.setItem(ctsTheme.storageName, JSON.stringify(newColors));
        this.themeChangeEmitter.emit();
    }
}
