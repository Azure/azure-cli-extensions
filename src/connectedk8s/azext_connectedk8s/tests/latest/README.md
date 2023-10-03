# Connectedk8s Testing
Tests need to be configured before running.

1. Make a copy of `config.json.dist` and rename it to `config.json` (the config.json is git ignored).
1. Fill in the details of the newly created `config.json` file:
    - `customLocationsOid`: The custom locations RP service principal object id for enabling the custom locations feature.
    - `rbacAppId`: The RBAC service principal app id for testing RBAC feature.
    - `rbacAppSecret`: The RBAC service principal secret for testing RBAC feature.
    - Querying for apps: Search for required application details via AAD graph with the following `$filter` query in az rest in PowerShell (make sure to fill in the tenant id):
        - Get by starts with:
            ```powershell
            az rest --method get --url "https://graph.windows.net/<tenant id>/servicePrincipals?`$filter=startswith(displayName,'Custom Locations')&api-version=1.6"
            ```
        - Get by exact value:
            ```powershell
            az rest --method get --url "https://graph.windows.net/<tenant id>/servicePrincipals?`$filter=appId eq '<app id>'&api-version=1.6"
            ```
    - For more information about AAD graph queries:
        - https://learn.microsoft.com/en-us/graph/filter-query-parameter?tabs=http
        - https://learn.microsoft.com/en-us/graph/migrate-azure-ad-graph-request-differences