# Azure CLI confidentialledger Extension #
This is the extension for confidentialledger

### How to use ###
Install this extension using the below CLI command
```
az extension add --name confidentialledger
```

### Included Features ###
#### confidentialledger ####
##### Create #####
```
az confidentialledger create --location "EastUS" \
    --aad-based-security-principals ledger-role-name="Administrator" principal-id="34621747-6fc8-4771-a2eb-72f31c461f2e" tenant-id="bce123b9-2b7b-4975-8360-5ca0b9b1cd08" \
    --cert-based-security-principals cert="MIIDBTCCAe2gAwIBAgIQXVogj9BAf49IpuOSIvztNDANBgkqhkiG9w0BAQsFADAtMSswKQYDVQQDEyJhY2NvdW50cy5hY2Nlc3Njb250cm9sLndpbmRvd3MubmV0MB4XDTIwMDMxNzAwMDAwMFoXDTI1MDMxNzAwMDAwMFowLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZXNzY29udHJvbC53aW5kb3dzLm5ldDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANfLmdz9yIDskpZzrMXiDeVlCs75ZunrzwzBW5lz7UxdBjHu7Q9iT32otlBp++LOwBcKsVjuQ0GUbulX0FLsfLjEeCe58ZtSn//+6VRFSScg7i+WvDwEUWELR+vMPtCGcXBTpILEnYbSMz0No4+Jpkc1lyMIfDP/KSeqojo74xfW4RKtAgv39uwZ5Yz2hZ/IcWOvaQqMXp1lqhXLFIRWbwjLYYUbmwGwYpQ6++Cml0ucQoMkgYT88HpA/fzXQlLgrHamr3eE/lVp26ZWwfGLAvkdNBabQRSrk8k/c6BmY1mYpUFZo+795PI16mAdp1ioEwH8I5osis+/BR5GhPpwiA8CAwEAAaMhMB8wHQYDVR0OBBYEFF8MDGklOGhGNVJvsHHRCaqtzexcMA0GCSqGSIb3DQEBCwUAA4IBAQCKkegw/mdpCVl1lOpgU4G9RT+1gtcPqZK9kpimuDggSJju6KUQlOCi5/lIH5DCzpjFdmG17TjWVBNve5kowmrhLzovY0Ykk7+6hYTBK8dNNSmd4SK7zY++0aDIuOzHP2Cur+kgFC0gez50tPzotLDtMmp40gknXuzltwJfezNSw3gLgljDsGGcDIXK3qLSYh44qSuRGwulcN2EJUZBI9tIxoODpaWHIN8+z2uZvf8JBYFjA3+n9FRQn51X16CTcjq4QRTbNVpgVuQuyaYnEtx0ZnDvguB3RjGSPIXTRBkLl2x7e8/6uAZ6tchw8rhcOtPsFgJuoJokGjvcUSR/6Eqd" ledger-role-name="Reader" \
    --ledger-type "Public" --tags additionalProps1="additional properties" --name "DummyLedgerName" \
    --resource-group "DummyResourceGroupName" 

az confidentialledger wait --created --name "{myLedger}" --resource-group "{rg}"
```
##### Show #####
```
az confidentialledger show --name "DummyLedgerName" --resource-group "DummyResourceGroupName"
```
##### List #####
```
az confidentialledger list --resource-group "DummyResourceGroupName"
```
##### Update #####
```
az confidentialledger update --location "EastUS" \
    --tags additionProps2="additional property value" additionalProps1="additional properties" \
    --name "DummyLedgerName" --resource-group "DummyResourceGroupName" 
```
##### Delete #####
```
az confidentialledger delete --name "DummyLedgerName" --resource-group "DummyResourceGroupName"
```