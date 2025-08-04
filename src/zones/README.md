# Microsoft Azure CLI 'zones' Extension

This package is for the 'zones' extension.
i.e. 'az zones'

This CLI Extension helps validate the zone redundancy status of resources within a specific scope.
For each resource, one of the following statuses will be returned:
    Unknown             # Unable to verify status. You'll need to check the resource manually.
    Yes                 # Resource is configured for zone redundancy
    Always              # Resource is always zone redundant, no configuration needed
    No                  # Resource is not configured for zone redundancy, but could be in another configuration
    Never               # Resource cannot be configured for zone redundancy
    Dependent           # Resource is zone redundant if parent or related resource is zone redundant
    NoZonesInRegion     # The region the resource is deployed in does not have Availability Zones

> [!NOTE]  
> This extension is in active development. While an effort has been made to include the most common resource types and their zone redundancy configuration, there are still plenty of resource types missing. More will be added in future releases. In the meantime, if you need specific resources added or have found errors, please raise a Github issue.

## When should you use this?

In order to build a fully zone redundant application, you need to satisfy three criteria:

1) Enable zone redundancy on all PaaS resources in the application
2) Ensure zonal resources are spread across all zones. These are the resources that take a 'zones' attribute in their definition.
3) Validate that your application code is able to handle the loss of a zone, e.g. that connections are retried properly when a dependency is unreachable.

The _zones_ CLI extension can help with the first two steps. By running this against a specific resource group that contains your production resources, you can be sure that you have not overlooked any resources in your quest for zone redundancy. If the results show 'No' on one of your resources, that means that you need to change the configuration to enable ZR. If it shows 'Never', that probably means you need to deploy multiple of those resources to the different zones manually.

The third step can be validated using Chaos Engineering practices. On Azure, look into Chaos Studio to get started with that.

Suggested use for this extension:
- Manually run this against the production subscription or resource group(s) to validate that all resources have zone redundanct enabled
- Run this as part of your CI/CD pipelines, validating zone redundancy of the resources after deployment in the (pre-)production environment. Consider failing the pipeline if any of the resource results contains _No_ as the result. Note that _no_ only occurs in cases where zone redundancy was not enabled, but could be if the resource was configured differently. 

## USAGE

Validate all resources in current scope to which you have read access:

```bash
az zones validate
```

Get the results in human-readable table format:

```bash
az zones validate --output table
```

Validate all resources in specific resource groups to which you have read access:

```bash
az zones validate --resource-groups <resource_group1>,<resource_group2>,...
```

Omit 'dependent' resources from the output. These are resources that by themselves cannot be zone redundant, but take on the status of their parent or related resource. This can be useful for improving readability of the results:

```bash
az zones validate --omit-dependent-resources
```

Validate all resources with specific tags. Resources that have ALL specified tags will be returned. Tags are case-sensitive.

```bash
az zones validate --tags env=prod,criticality=high
```

## Important Notes

- The extension still has missing resource types. These are shown as _Unknown_ in the results. It is essential that you validate zone redundancy of these resources yourself, since your whole application is only zone redundant is all resources are zone redundant. 

- The _zones_ CLI extension can only help with resources you can view, i.e. for which you have read access. You must ensure that all relevant resources are indeed listed in the results.

- While this extension is a useful tool in validating zone redundancy on resources, you are still responsible for reviewing the [Reliability Guides](https://learn.microsoft.com/azure/reliability/overview-reliability-guidance) for all the services you use in your applications, as these may contain important information regarding operation in high availability scenarios. Ultimately, the product reliability guides are the authoritative source for zone redundancy guidance. 

- Zonal services are considered to be Zone Redundant if they are deployed to at least 2 zones. 