# Azure CLI ComputeDiagnosticRp Extension #
This is an extension to Azure CLI to manage ComputeDiagnosticRp resources.

## How to use ##
### Generate the spot vm placement scores
`az compute diagnostic spot-placement-recommender generate -l eastus --subscription ffffffff-ffff-ffff-ffff-ffffffffffff --availability-zones true --desired-locations '["eastus", "eastus2"]' --desired-count 1 --desired-sizes '[{"sku": "Standard_D2_v2"}]'`
