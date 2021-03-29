# Azure CLI quota Extension #
This is the extension for quota

### How to use ###
Install this extension using the below CLI command
```
az extension add --name quota
```

### Included Features ###
#### quota reservation ####
##### List #####
```
az quota reservation list --reservation-order-id "276e7ae4-84d0-4da6-ab4b-d6b94f3557da"
```
##### Show #####
```
az quota reservation show --expand "renewProperties" --reservation-id "6ef59113-3482-40da-8d79-787f823e34bc" \
    --reservation-order-id "276e7ae4-84d0-4da6-ab4b-d6b94f3557da" 
```
##### Update #####
```
az quota reservation update --applied-scope-type "Shared" --instance-flexibility "Off" \
    --reservation-id "6ef59113-3482-40da-8d79-787f823e34bc" \
    --reservation-order-id "276e7ae4-84d0-4da6-ab4b-d6b94f3557da" 
```
##### Available-scope #####
```
az quota reservation available-scope --properties scopes="/subscriptions/efc7c997-7700-4a74-b731-55aec16c15e9" \
    --reservation-id "356e7ae4-84d0-4da6-ab4b-d6b94f3557da" \
    --reservation-order-id "276e7ae4-84d0-4da6-ab4b-d6b94f3557da" 
```
##### List-revision #####
```
az quota reservation list-revision --reservation-id "6ef59113-3482-40da-8d79-787f823e34bc" \
    --reservation-order-id "276e7ae4-84d0-4da6-ab4b-d6b94f3557da" 
```
##### Merge #####
```
az quota reservation merge \
    --sources "/providers/Microsoft.Capacity/reservationOrders/c0565a8a-4491-4e77-b07b-5e6d66718e1c/reservations/cea04232-932e-47db-acb5-e29a945ecc73" "/providers/Microsoft.Capacity/reservationOrders/c0565a8a-4491-4e77-b07b-5e6d66718e1c/reservations/5bf54dc7-dacd-4f46-a16b-7b78f4a59799" \
    --reservation-order-id "276e7ae4-84d0-4da6-ab4b-d6b94f3557da" 
```
##### Split #####
```
az quota reservation split --quantities 1 2 \
    --reservation-id "/providers/Microsoft.Capacity/reservationOrders/276e7ae4-84d0-4da6-ab4b-d6b94f3557da/reservations/bcae77cd-3119-4766-919f-b50d36c75c7a" \
    --reservation-order-id "276e7ae4-84d0-4da6-ab4b-d6b94f3557da" 
```
#### quota ####
##### Show-applied-reservation-list #####
```
az quota show-applied-reservation-list --subscription-id "23bc208b-083f-4901-ae85-4f98c0c3b4b6"
```
##### Show-catalog #####
```
az quota show-catalog --location "eastus" --reserved-resource-type "VirtualMachines" \
    --subscription-id "23bc208b-083f-4901-ae85-4f98c0c3b4b6" 
```
#### quota reservation-order ####
##### Purchase #####
```
az quota reservation-order purchase --location "westus" --applied-scope-type "Shared" --billing-plan "Monthly" \
    --billing-scope-id "/subscriptions/ed3a1871-612d-abcd-a849-c2542a68be83" --display-name "TestReservationOrder" \
    --quantity 1 --renew false --instance-flexibility "On" --reserved-resource-type "VirtualMachines" --term "P1Y" \
    --name "standard_D1" --reservation-order-id "a075419f-44cc-497f-b68a-14ee811d48b9" 
```
##### Show #####
```
az quota reservation-order show --reservation-order-id "a075419f-44cc-497f-b68a-14ee811d48b9"
```
##### Show #####
```
az quota reservation-order show --expand "schedule" --reservation-order-id "a075419f-44cc-497f-b68a-14ee811d48b9"
```
##### Calculate #####
```
az quota reservation-order calculate --location "westus" --applied-scope-type "Shared" --billing-plan "Monthly" \
    --billing-scope-id "/subscriptions/ed3a1871-612d-abcd-a849-c2542a68be83" --display-name "TestReservationOrder" \
    --quantity 1 --instance-flexibility "On" --reserved-resource-type "VirtualMachines" --term "P1Y" \
    --name "standard_D1" 
```
##### List #####
```
az quota reservation-order list
```
#### quota operation ####
##### List #####
```
az quota operation list
```
#### quota calculate-exchange ####
##### Post #####
```
az quota calculate-exchange post \
    --reservations-to-exchange quantity=1 reservation-id="/providers/microsoft.capacity/reservationOrders/1f14354c-dc12-4c8d-8090-6f295a3a34aa/reservations/c8c926bd-fc5d-4e29-9d43-b68340ac23a6" \
    --reservations-to-purchase location="westus" reserved-resource-type="VirtualMachines" billing-scope-id="/subscriptions/ed3a1871-612d-abcd-a849-c2542a68be83" term="P1Y" billing-plan="Upfront" quantity=1 display-name="testDisplayName" applied-scope-type="Shared" applied-scopes=null renew=false instance-flexibility="On" name="Standard_B1ls" 
```
#### quota exchange ####
##### Post #####
```
az quota exchange post --session-id "66e2ac8f-439e-4345-8235-6fef07608081"
```
#### quota ####
##### Create #####
```
az quota create \
    --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":200,\\"unit\\":\\"Count\\"}" \
    --location "eastus" --provider-id "Microsoft.Compute" --resource-name "standardFSv2Family" \
    --subscription-id "D7EC67B3-7657-4966-BFFC-41EFD36BAAB3" 
```
##### Create #####
```
az quota create \
    --properties "{\\"name\\":{\\"value\\":\\"StandardDv2Family\\"},\\"limit\\":200,\\"resourceType\\":\\"dedicated\\",\\"unit\\":\\"Count\\"}" \
    --location "eastus" --provider-id "Microsoft.MachineLearningServices" --resource-name "StandardDv2Family" \
    --subscription-id "D7EC67B3-7657-4966-BFFC-41EFD36BAAB3" 
```
##### Create #####
```
az quota create \
    --properties "{\\"name\\":{\\"value\\":\\"TotalLowPriorityCores\\"},\\"limit\\":200,\\"resourceType\\":\\"lowPriority\\",\\"unit\\":\\"Count\\"}" \
    --location "eastus" --provider-id "Microsoft.MachineLearningServices" --resource-name "TotalLowPriorityCores" \
    --subscription-id "D7EC67B3-7657-4966-BFFC-41EFD36BAAB3" 
```
##### List #####
```
az quota list --location "eastus" --provider-id "Microsoft.Compute" \
    --subscription-id "00000000-0000-0000-0000-000000000000" 
```
##### List #####
```
az quota list --location "eastus" --provider-id "Microsoft.MachineLearningServices" \
    --subscription-id "00000000-0000-0000-0000-000000000000" 
```
##### Show #####
```
az quota show --location "eastus" --provider-id "Microsoft.Compute" --resource-name "standardNDSFamily" \
    --subscription-id "00000000-0000-0000-0000-000000000000" 
```
##### Update #####
```
az quota update \
    --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":200,\\"unit\\":\\"Count\\"}" \
    --location "eastus" --provider-id "Microsoft.Compute" --resource-name "standardFSv2Family" \
    --subscription-id "D7EC67B3-7657-4966-BFFC-41EFD36BAAB3" 
```
#### quota quota-request-status ####
##### List #####
```
az quota quota-request-status list --location "eastus" --provider-id "Microsoft.Compute" \
    --subscription-id "3f75fdf7-977e-44ad-990d-99f14f0f299f" 
```
##### Show #####
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --location "eastus" \
    --provider-id "Microsoft.Compute" --subscription-id "00000000-0000-0000-0000-000000000000" 
```
##### Show #####
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --location "eastus" \
    --provider-id "Microsoft.Compute" --subscription-id "00000000-0000-0000-0000-000000000000" 
```
##### Show #####
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --location "eastus" \
    --provider-id "Microsoft.Compute" --subscription-id "00000000-0000-0000-0000-000000000000" 
```