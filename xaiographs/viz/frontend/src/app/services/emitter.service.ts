import { Injectable, EventEmitter } from '@angular/core';

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
}
