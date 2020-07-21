#!/bin/sh -e
# swagger validation
# https://github.com/Azure/azure-rest-api-specs/blob/master/documentation/swagger-checklist.md#validation-tools-for-swagger-checklist
spec=/azure-rest-api-specs/specification/vmware/resource-manager/Microsoft.AVS/stable/2020-03-20/vmware.json
autorest --input-file=$spec --azure-validator --openapi-type=arm
oav validate-spec $spec -p
oav validate-example $spec -p
rm -rf azext_vmware/vendored_sdks/
autorest --input-file=$spec --python --output-folder=azext_vmware --namespace=vendored_sdks --azure-arm=true --override-client-name=AVSClient --use=@microsoft.azure/autorest.python@3.0.62