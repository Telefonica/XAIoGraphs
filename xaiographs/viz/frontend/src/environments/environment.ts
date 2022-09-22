import { ctsDevEnvrionment } from '../app/constants/environment';

export const environment = {
    production: ctsDevEnvrionment.production,
    domain: ctsDevEnvrionment.domain,
    apiUrl: 'http://' + ctsDevEnvrionment.domain + '/' + ctsDevEnvrionment.backend_api
};
