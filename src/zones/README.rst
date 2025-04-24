Microsoft Azure CLI 'zones' Extension
==========================================

This package is for the 'zones' extension.
i.e. 'az zones'

This CLI Extension helps validate the zone redundancy status of resources within a specific scope. 
For each resource, one of the following statuses will be returned:
    Unknown         # Unable to verify status. You'll need to check the resource manually.
    Yes             # Resource is configured for zone redundancy
    Always          # Resource is always zone redundant, no configuration needed
    No              # Resource is not configured for zone redundancy, but could be in another configuration
    Never           # Resource cannot be configured for zone redundancy
    Dependent       # Resource is zone redundant if parent or related resource is zone redundant
    NoZonesInRegion # The region the resource is deployed in does not have Availability Zones

USAGE

Validate all resources in current scope to which you have read access:
az zones validate

Validate all resources in specific resource groups to which you have read access:
az zones validate [--resource-groups <resource_group1>,<resource_group2> ...]

Omit 'dependent' resources from the output:
az zones validate --omit-dependent-resources