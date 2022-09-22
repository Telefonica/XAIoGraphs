import { Injectable, EventEmitter } from '@angular/core';

@Injectable({
    providedIn: 'root'
})
export class EmitterService {

    currentGlobalTarget;
    currentGlobalFeatures;
    currentLocalTarget;
    currentLocalFeatures;

    globalTargetChangeEmitter = new EventEmitter();
    globalFeaturesChangeEmitter = new EventEmitter();
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

    setBothGlobal(target: string, features: number) {
        this.currentGlobalTarget = target;
        this.currentGlobalFeatures = features;
        this.globalTargetChangeEmitter.emit();
    }

    setLocalTarget(target: string) {
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
