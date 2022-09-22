import { ctsPrdEnvrionment } from '../app/constants/environment';

export const environment = {
    production: ctsPrdEnvrionment.production,
    domain: ctsPrdEnvrionment.domain,
    apiUrl: 'http://' + ctsPrdEnvrionment.domain + '/' + ctsPrdEnvrionment.backend_api
};
