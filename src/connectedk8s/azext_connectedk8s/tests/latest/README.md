# Connectedk8s Testing
Tests need to be configured before running.

1. Make a copy of `config.json.dist` and rename it to `config.json` (the config.json is git ignored).
1. Fill in the details of the newly created `config.json` file:
    - Note that the code doesn't verify that you have a valid RBAC service principal application, so a fake one can be used for testing.
    - `customLocationsOid`: The custom locations RP service principal object ID for enabling the custom locations feature.
    - `rbacAppId`: The RBAC service principal app ID for testing RBAC feature.
    - `rbacAppSecret`: The RBAC service principal secret for testing RBAC feature.
1. Please make sure to test using a service principal with minimal privileges to replicate customer scenarios.
    - Make sure you test with a service principal without Graph API permissions, as some customers don't expect to need it.