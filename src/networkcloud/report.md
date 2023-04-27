# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az networkcloud|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az networkcloud` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az networkcloud baremetalmachine|BareMetalMachines|[commands](#CommandsInBareMetalMachines)|
|az networkcloud baremetalmachinekeyset|BareMetalMachineKeySets|[commands](#CommandsInBareMetalMachineKeySets)|
|az networkcloud bmckeyset|BmcKeySets|[commands](#CommandsInBmcKeySets)|
|az networkcloud cloudservicesnetwork|CloudServicesNetworks|[commands](#CommandsInCloudServicesNetworks)|
|az networkcloud cluster|Clusters|[commands](#CommandsInClusters)|
|az networkcloud clustermanager|ClusterManagers|[commands](#CommandsInClusterManagers)|
|az networkcloud console|Consoles|[commands](#CommandsInConsoles)|
|az networkcloud defaultcninetwork|DefaultCniNetworks|[commands](#CommandsInDefaultCniNetworks)|
|az networkcloud hybridakscluster|HybridAksClusters|[commands](#CommandsInHybridAksClusters)|
|az networkcloud l2network|L2Networks|[commands](#CommandsInL2Networks)|
|az networkcloud l3network|L3Networks|[commands](#CommandsInL3Networks)|
|az networkcloud metricsconfiguration|MetricsConfigurations|[commands](#CommandsInMetricsConfigurations)|
|az networkcloud rack|Racks|[commands](#CommandsInRacks)|
|az networkcloud racksku|RackSkus|[commands](#CommandsInRackSkus)|
|az networkcloud storageappliance|StorageAppliances|[commands](#CommandsInStorageAppliances)|
|az networkcloud trunkednetwork|TrunkedNetworks|[commands](#CommandsInTrunkedNetworks)|
|az networkcloud virtualmachine|VirtualMachines|[commands](#CommandsInVirtualMachines)|
|az networkcloud volume|Volumes|[commands](#CommandsInVolumes)|

## COMMANDS
### <a name="CommandsInBareMetalMachines">Commands in `az networkcloud baremetalmachine` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud baremetalmachine list](#BareMetalMachinesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersBareMetalMachinesListByResourceGroup)|[Example](#ExamplesBareMetalMachinesListByResourceGroup)|
|[az networkcloud baremetalmachine list](#BareMetalMachinesListBySubscription)|ListBySubscription|[Parameters](#ParametersBareMetalMachinesListBySubscription)|[Example](#ExamplesBareMetalMachinesListBySubscription)|
|[az networkcloud baremetalmachine show](#BareMetalMachinesGet)|Get|[Parameters](#ParametersBareMetalMachinesGet)|[Example](#ExamplesBareMetalMachinesGet)|
|[az networkcloud baremetalmachine create](#BareMetalMachinesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersBareMetalMachinesCreateOrUpdate#Create)|[Example](#ExamplesBareMetalMachinesCreateOrUpdate#Create)|
|[az networkcloud baremetalmachine update](#BareMetalMachinesUpdate)|Update|[Parameters](#ParametersBareMetalMachinesUpdate)|[Example](#ExamplesBareMetalMachinesUpdate)|
|[az networkcloud baremetalmachine delete](#BareMetalMachinesDelete)|Delete|[Parameters](#ParametersBareMetalMachinesDelete)|[Example](#ExamplesBareMetalMachinesDelete)|
|[az networkcloud baremetalmachine cordon](#BareMetalMachinesCordon)|Cordon|[Parameters](#ParametersBareMetalMachinesCordon)|[Example](#ExamplesBareMetalMachinesCordon)|
|[az networkcloud baremetalmachine power-off](#BareMetalMachinesPowerOff)|PowerOff|[Parameters](#ParametersBareMetalMachinesPowerOff)|[Example](#ExamplesBareMetalMachinesPowerOff)|
|[az networkcloud baremetalmachine reimage](#BareMetalMachinesReimage)|Reimage|[Parameters](#ParametersBareMetalMachinesReimage)|[Example](#ExamplesBareMetalMachinesReimage)|
|[az networkcloud baremetalmachine replace](#BareMetalMachinesReplace)|Replace|[Parameters](#ParametersBareMetalMachinesReplace)|[Example](#ExamplesBareMetalMachinesReplace)|
|[az networkcloud baremetalmachine restart](#BareMetalMachinesRestart)|Restart|[Parameters](#ParametersBareMetalMachinesRestart)|[Example](#ExamplesBareMetalMachinesRestart)|
|[az networkcloud baremetalmachine run-command](#BareMetalMachinesRunCommand)|RunCommand|[Parameters](#ParametersBareMetalMachinesRunCommand)|[Example](#ExamplesBareMetalMachinesRunCommand)|
|[az networkcloud baremetalmachine run-data-extract](#BareMetalMachinesRunDataExtracts)|RunDataExtracts|[Parameters](#ParametersBareMetalMachinesRunDataExtracts)|[Example](#ExamplesBareMetalMachinesRunDataExtracts)|
|[az networkcloud baremetalmachine run-read-command](#BareMetalMachinesRunReadCommands)|RunReadCommands|[Parameters](#ParametersBareMetalMachinesRunReadCommands)|[Example](#ExamplesBareMetalMachinesRunReadCommands)|
|[az networkcloud baremetalmachine start](#BareMetalMachinesStart)|Start|[Parameters](#ParametersBareMetalMachinesStart)|[Example](#ExamplesBareMetalMachinesStart)|
|[az networkcloud baremetalmachine uncordon](#BareMetalMachinesUncordon)|Uncordon|[Parameters](#ParametersBareMetalMachinesUncordon)|[Example](#ExamplesBareMetalMachinesUncordon)|
|[az networkcloud baremetalmachine validate-hardware](#BareMetalMachinesValidateHardware)|ValidateHardware|[Parameters](#ParametersBareMetalMachinesValidateHardware)|[Example](#ExamplesBareMetalMachinesValidateHardware)|

### <a name="CommandsInBareMetalMachineKeySets">Commands in `az networkcloud baremetalmachinekeyset` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud baremetalmachinekeyset list](#BareMetalMachineKeySetsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersBareMetalMachineKeySetsListByResourceGroup)|[Example](#ExamplesBareMetalMachineKeySetsListByResourceGroup)|
|[az networkcloud baremetalmachinekeyset show](#BareMetalMachineKeySetsGet)|Get|[Parameters](#ParametersBareMetalMachineKeySetsGet)|[Example](#ExamplesBareMetalMachineKeySetsGet)|
|[az networkcloud baremetalmachinekeyset create](#BareMetalMachineKeySetsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersBareMetalMachineKeySetsCreateOrUpdate#Create)|[Example](#ExamplesBareMetalMachineKeySetsCreateOrUpdate#Create)|
|[az networkcloud baremetalmachinekeyset update](#BareMetalMachineKeySetsUpdate)|Update|[Parameters](#ParametersBareMetalMachineKeySetsUpdate)|[Example](#ExamplesBareMetalMachineKeySetsUpdate)|
|[az networkcloud baremetalmachinekeyset delete](#BareMetalMachineKeySetsDelete)|Delete|[Parameters](#ParametersBareMetalMachineKeySetsDelete)|[Example](#ExamplesBareMetalMachineKeySetsDelete)|

### <a name="CommandsInBmcKeySets">Commands in `az networkcloud bmckeyset` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud bmckeyset list](#BmcKeySetsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersBmcKeySetsListByResourceGroup)|[Example](#ExamplesBmcKeySetsListByResourceGroup)|
|[az networkcloud bmckeyset show](#BmcKeySetsGet)|Get|[Parameters](#ParametersBmcKeySetsGet)|[Example](#ExamplesBmcKeySetsGet)|
|[az networkcloud bmckeyset create](#BmcKeySetsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersBmcKeySetsCreateOrUpdate#Create)|[Example](#ExamplesBmcKeySetsCreateOrUpdate#Create)|
|[az networkcloud bmckeyset update](#BmcKeySetsUpdate)|Update|[Parameters](#ParametersBmcKeySetsUpdate)|[Example](#ExamplesBmcKeySetsUpdate)|
|[az networkcloud bmckeyset delete](#BmcKeySetsDelete)|Delete|[Parameters](#ParametersBmcKeySetsDelete)|[Example](#ExamplesBmcKeySetsDelete)|

### <a name="CommandsInCloudServicesNetworks">Commands in `az networkcloud cloudservicesnetwork` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud cloudservicesnetwork list](#CloudServicesNetworksListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersCloudServicesNetworksListByResourceGroup)|[Example](#ExamplesCloudServicesNetworksListByResourceGroup)|
|[az networkcloud cloudservicesnetwork list](#CloudServicesNetworksListBySubscription)|ListBySubscription|[Parameters](#ParametersCloudServicesNetworksListBySubscription)|[Example](#ExamplesCloudServicesNetworksListBySubscription)|
|[az networkcloud cloudservicesnetwork show](#CloudServicesNetworksGet)|Get|[Parameters](#ParametersCloudServicesNetworksGet)|[Example](#ExamplesCloudServicesNetworksGet)|
|[az networkcloud cloudservicesnetwork create](#CloudServicesNetworksCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersCloudServicesNetworksCreateOrUpdate#Create)|[Example](#ExamplesCloudServicesNetworksCreateOrUpdate#Create)|
|[az networkcloud cloudservicesnetwork update](#CloudServicesNetworksUpdate)|Update|[Parameters](#ParametersCloudServicesNetworksUpdate)|[Example](#ExamplesCloudServicesNetworksUpdate)|
|[az networkcloud cloudservicesnetwork delete](#CloudServicesNetworksDelete)|Delete|[Parameters](#ParametersCloudServicesNetworksDelete)|[Example](#ExamplesCloudServicesNetworksDelete)|

### <a name="CommandsInClusters">Commands in `az networkcloud cluster` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud cluster list](#ClustersListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersClustersListByResourceGroup)|[Example](#ExamplesClustersListByResourceGroup)|
|[az networkcloud cluster list](#ClustersListBySubscription)|ListBySubscription|[Parameters](#ParametersClustersListBySubscription)|[Example](#ExamplesClustersListBySubscription)|
|[az networkcloud cluster show](#ClustersGet)|Get|[Parameters](#ParametersClustersGet)|[Example](#ExamplesClustersGet)|
|[az networkcloud cluster create](#ClustersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersClustersCreateOrUpdate#Create)|[Example](#ExamplesClustersCreateOrUpdate#Create)|
|[az networkcloud cluster update](#ClustersUpdate)|Update|[Parameters](#ParametersClustersUpdate)|[Example](#ExamplesClustersUpdate)|
|[az networkcloud cluster delete](#ClustersDelete)|Delete|[Parameters](#ParametersClustersDelete)|[Example](#ExamplesClustersDelete)|
|[az networkcloud cluster deploy](#ClustersDeploy)|Deploy|[Parameters](#ParametersClustersDeploy)|[Example](#ExamplesClustersDeploy)|
|[az networkcloud cluster update-version](#ClustersUpdateVersion)|UpdateVersion|[Parameters](#ParametersClustersUpdateVersion)|[Example](#ExamplesClustersUpdateVersion)|

### <a name="CommandsInClusterManagers">Commands in `az networkcloud clustermanager` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud clustermanager list](#ClusterManagersListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersClusterManagersListByResourceGroup)|[Example](#ExamplesClusterManagersListByResourceGroup)|
|[az networkcloud clustermanager list](#ClusterManagersListBySubscription)|ListBySubscription|[Parameters](#ParametersClusterManagersListBySubscription)|[Example](#ExamplesClusterManagersListBySubscription)|
|[az networkcloud clustermanager show](#ClusterManagersGet)|Get|[Parameters](#ParametersClusterManagersGet)|[Example](#ExamplesClusterManagersGet)|
|[az networkcloud clustermanager create](#ClusterManagersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersClusterManagersCreateOrUpdate#Create)|[Example](#ExamplesClusterManagersCreateOrUpdate#Create)|
|[az networkcloud clustermanager update](#ClusterManagersUpdate)|Update|[Parameters](#ParametersClusterManagersUpdate)|[Example](#ExamplesClusterManagersUpdate)|
|[az networkcloud clustermanager delete](#ClusterManagersDelete)|Delete|[Parameters](#ParametersClusterManagersDelete)|[Example](#ExamplesClusterManagersDelete)|

### <a name="CommandsInConsoles">Commands in `az networkcloud console` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud console list](#ConsolesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersConsolesListByResourceGroup)|[Example](#ExamplesConsolesListByResourceGroup)|
|[az networkcloud console show](#ConsolesGet)|Get|[Parameters](#ParametersConsolesGet)|[Example](#ExamplesConsolesGet)|
|[az networkcloud console create](#ConsolesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersConsolesCreateOrUpdate#Create)|[Example](#ExamplesConsolesCreateOrUpdate#Create)|
|[az networkcloud console update](#ConsolesUpdate)|Update|[Parameters](#ParametersConsolesUpdate)|[Example](#ExamplesConsolesUpdate)|
|[az networkcloud console delete](#ConsolesDelete)|Delete|[Parameters](#ParametersConsolesDelete)|[Example](#ExamplesConsolesDelete)|

### <a name="CommandsInDefaultCniNetworks">Commands in `az networkcloud defaultcninetwork` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud defaultcninetwork list](#DefaultCniNetworksListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDefaultCniNetworksListByResourceGroup)|[Example](#ExamplesDefaultCniNetworksListByResourceGroup)|
|[az networkcloud defaultcninetwork list](#DefaultCniNetworksListBySubscription)|ListBySubscription|[Parameters](#ParametersDefaultCniNetworksListBySubscription)|[Example](#ExamplesDefaultCniNetworksListBySubscription)|
|[az networkcloud defaultcninetwork show](#DefaultCniNetworksGet)|Get|[Parameters](#ParametersDefaultCniNetworksGet)|[Example](#ExamplesDefaultCniNetworksGet)|
|[az networkcloud defaultcninetwork create](#DefaultCniNetworksCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDefaultCniNetworksCreateOrUpdate#Create)|[Example](#ExamplesDefaultCniNetworksCreateOrUpdate#Create)|
|[az networkcloud defaultcninetwork update](#DefaultCniNetworksUpdate)|Update|[Parameters](#ParametersDefaultCniNetworksUpdate)|[Example](#ExamplesDefaultCniNetworksUpdate)|
|[az networkcloud defaultcninetwork delete](#DefaultCniNetworksDelete)|Delete|[Parameters](#ParametersDefaultCniNetworksDelete)|[Example](#ExamplesDefaultCniNetworksDelete)|

### <a name="CommandsInHybridAksClusters">Commands in `az networkcloud hybridakscluster` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud hybridakscluster list](#HybridAksClustersListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersHybridAksClustersListByResourceGroup)|[Example](#ExamplesHybridAksClustersListByResourceGroup)|
|[az networkcloud hybridakscluster list](#HybridAksClustersListBySubscription)|ListBySubscription|[Parameters](#ParametersHybridAksClustersListBySubscription)|[Example](#ExamplesHybridAksClustersListBySubscription)|
|[az networkcloud hybridakscluster show](#HybridAksClustersGet)|Get|[Parameters](#ParametersHybridAksClustersGet)|[Example](#ExamplesHybridAksClustersGet)|
|[az networkcloud hybridakscluster create](#HybridAksClustersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersHybridAksClustersCreateOrUpdate#Create)|[Example](#ExamplesHybridAksClustersCreateOrUpdate#Create)|
|[az networkcloud hybridakscluster update](#HybridAksClustersUpdate)|Update|[Parameters](#ParametersHybridAksClustersUpdate)|[Example](#ExamplesHybridAksClustersUpdate)|
|[az networkcloud hybridakscluster delete](#HybridAksClustersDelete)|Delete|[Parameters](#ParametersHybridAksClustersDelete)|[Example](#ExamplesHybridAksClustersDelete)|
|[az networkcloud hybridakscluster restart-node](#HybridAksClustersRestartNode)|RestartNode|[Parameters](#ParametersHybridAksClustersRestartNode)|[Example](#ExamplesHybridAksClustersRestartNode)|

### <a name="CommandsInL2Networks">Commands in `az networkcloud l2network` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud l2network list](#L2NetworksListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersL2NetworksListByResourceGroup)|[Example](#ExamplesL2NetworksListByResourceGroup)|
|[az networkcloud l2network list](#L2NetworksListBySubscription)|ListBySubscription|[Parameters](#ParametersL2NetworksListBySubscription)|[Example](#ExamplesL2NetworksListBySubscription)|
|[az networkcloud l2network show](#L2NetworksGet)|Get|[Parameters](#ParametersL2NetworksGet)|[Example](#ExamplesL2NetworksGet)|
|[az networkcloud l2network create](#L2NetworksCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersL2NetworksCreateOrUpdate#Create)|[Example](#ExamplesL2NetworksCreateOrUpdate#Create)|
|[az networkcloud l2network update](#L2NetworksUpdate)|Update|[Parameters](#ParametersL2NetworksUpdate)|[Example](#ExamplesL2NetworksUpdate)|
|[az networkcloud l2network delete](#L2NetworksDelete)|Delete|[Parameters](#ParametersL2NetworksDelete)|[Example](#ExamplesL2NetworksDelete)|

### <a name="CommandsInL3Networks">Commands in `az networkcloud l3network` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud l3network list](#L3NetworksListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersL3NetworksListByResourceGroup)|[Example](#ExamplesL3NetworksListByResourceGroup)|
|[az networkcloud l3network list](#L3NetworksListBySubscription)|ListBySubscription|[Parameters](#ParametersL3NetworksListBySubscription)|[Example](#ExamplesL3NetworksListBySubscription)|
|[az networkcloud l3network show](#L3NetworksGet)|Get|[Parameters](#ParametersL3NetworksGet)|[Example](#ExamplesL3NetworksGet)|
|[az networkcloud l3network create](#L3NetworksCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersL3NetworksCreateOrUpdate#Create)|[Example](#ExamplesL3NetworksCreateOrUpdate#Create)|
|[az networkcloud l3network update](#L3NetworksUpdate)|Update|[Parameters](#ParametersL3NetworksUpdate)|[Example](#ExamplesL3NetworksUpdate)|
|[az networkcloud l3network delete](#L3NetworksDelete)|Delete|[Parameters](#ParametersL3NetworksDelete)|[Example](#ExamplesL3NetworksDelete)|

### <a name="CommandsInMetricsConfigurations">Commands in `az networkcloud metricsconfiguration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud metricsconfiguration list](#MetricsConfigurationsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersMetricsConfigurationsListByResourceGroup)|[Example](#ExamplesMetricsConfigurationsListByResourceGroup)|
|[az networkcloud metricsconfiguration show](#MetricsConfigurationsGet)|Get|[Parameters](#ParametersMetricsConfigurationsGet)|[Example](#ExamplesMetricsConfigurationsGet)|
|[az networkcloud metricsconfiguration create](#MetricsConfigurationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersMetricsConfigurationsCreateOrUpdate#Create)|[Example](#ExamplesMetricsConfigurationsCreateOrUpdate#Create)|
|[az networkcloud metricsconfiguration update](#MetricsConfigurationsUpdate)|Update|[Parameters](#ParametersMetricsConfigurationsUpdate)|[Example](#ExamplesMetricsConfigurationsUpdate)|
|[az networkcloud metricsconfiguration delete](#MetricsConfigurationsDelete)|Delete|[Parameters](#ParametersMetricsConfigurationsDelete)|[Example](#ExamplesMetricsConfigurationsDelete)|

### <a name="CommandsInRacks">Commands in `az networkcloud rack` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud rack list](#RacksListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersRacksListByResourceGroup)|[Example](#ExamplesRacksListByResourceGroup)|
|[az networkcloud rack list](#RacksListBySubscription)|ListBySubscription|[Parameters](#ParametersRacksListBySubscription)|[Example](#ExamplesRacksListBySubscription)|
|[az networkcloud rack show](#RacksGet)|Get|[Parameters](#ParametersRacksGet)|[Example](#ExamplesRacksGet)|
|[az networkcloud rack create](#RacksCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersRacksCreateOrUpdate#Create)|[Example](#ExamplesRacksCreateOrUpdate#Create)|
|[az networkcloud rack update](#RacksUpdate)|Update|[Parameters](#ParametersRacksUpdate)|[Example](#ExamplesRacksUpdate)|
|[az networkcloud rack delete](#RacksDelete)|Delete|[Parameters](#ParametersRacksDelete)|[Example](#ExamplesRacksDelete)|

### <a name="CommandsInRackSkus">Commands in `az networkcloud racksku` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud racksku list](#RackSkusListBySubscription)|ListBySubscription|[Parameters](#ParametersRackSkusListBySubscription)|[Example](#ExamplesRackSkusListBySubscription)|
|[az networkcloud racksku show](#RackSkusGet)|Get|[Parameters](#ParametersRackSkusGet)|[Example](#ExamplesRackSkusGet)|

### <a name="CommandsInStorageAppliances">Commands in `az networkcloud storageappliance` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud storageappliance list](#StorageAppliancesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersStorageAppliancesListByResourceGroup)|[Example](#ExamplesStorageAppliancesListByResourceGroup)|
|[az networkcloud storageappliance list](#StorageAppliancesListBySubscription)|ListBySubscription|[Parameters](#ParametersStorageAppliancesListBySubscription)|[Example](#ExamplesStorageAppliancesListBySubscription)|
|[az networkcloud storageappliance show](#StorageAppliancesGet)|Get|[Parameters](#ParametersStorageAppliancesGet)|[Example](#ExamplesStorageAppliancesGet)|
|[az networkcloud storageappliance create](#StorageAppliancesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersStorageAppliancesCreateOrUpdate#Create)|[Example](#ExamplesStorageAppliancesCreateOrUpdate#Create)|
|[az networkcloud storageappliance update](#StorageAppliancesUpdate)|Update|[Parameters](#ParametersStorageAppliancesUpdate)|[Example](#ExamplesStorageAppliancesUpdate)|
|[az networkcloud storageappliance delete](#StorageAppliancesDelete)|Delete|[Parameters](#ParametersStorageAppliancesDelete)|[Example](#ExamplesStorageAppliancesDelete)|
|[az networkcloud storageappliance disable-remote-vendor-management](#StorageAppliancesDisableRemoteVendorManagement)|DisableRemoteVendorManagement|[Parameters](#ParametersStorageAppliancesDisableRemoteVendorManagement)|[Example](#ExamplesStorageAppliancesDisableRemoteVendorManagement)|
|[az networkcloud storageappliance enable-remote-vendor-management](#StorageAppliancesEnableRemoteVendorManagement)|EnableRemoteVendorManagement|[Parameters](#ParametersStorageAppliancesEnableRemoteVendorManagement)|[Example](#ExamplesStorageAppliancesEnableRemoteVendorManagement)|
|[az networkcloud storageappliance run-read-command](#StorageAppliancesRunReadCommands)|RunReadCommands|[Parameters](#ParametersStorageAppliancesRunReadCommands)|[Example](#ExamplesStorageAppliancesRunReadCommands)|
|[az networkcloud storageappliance validate-hardware](#StorageAppliancesValidateHardware)|ValidateHardware|[Parameters](#ParametersStorageAppliancesValidateHardware)|[Example](#ExamplesStorageAppliancesValidateHardware)|

### <a name="CommandsInTrunkedNetworks">Commands in `az networkcloud trunkednetwork` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud trunkednetwork list](#TrunkedNetworksListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersTrunkedNetworksListByResourceGroup)|[Example](#ExamplesTrunkedNetworksListByResourceGroup)|
|[az networkcloud trunkednetwork list](#TrunkedNetworksListBySubscription)|ListBySubscription|[Parameters](#ParametersTrunkedNetworksListBySubscription)|[Example](#ExamplesTrunkedNetworksListBySubscription)|
|[az networkcloud trunkednetwork show](#TrunkedNetworksGet)|Get|[Parameters](#ParametersTrunkedNetworksGet)|[Example](#ExamplesTrunkedNetworksGet)|
|[az networkcloud trunkednetwork create](#TrunkedNetworksCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersTrunkedNetworksCreateOrUpdate#Create)|[Example](#ExamplesTrunkedNetworksCreateOrUpdate#Create)|
|[az networkcloud trunkednetwork update](#TrunkedNetworksUpdate)|Update|[Parameters](#ParametersTrunkedNetworksUpdate)|[Example](#ExamplesTrunkedNetworksUpdate)|
|[az networkcloud trunkednetwork delete](#TrunkedNetworksDelete)|Delete|[Parameters](#ParametersTrunkedNetworksDelete)|[Example](#ExamplesTrunkedNetworksDelete)|

### <a name="CommandsInVirtualMachines">Commands in `az networkcloud virtualmachine` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud virtualmachine list](#VirtualMachinesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersVirtualMachinesListByResourceGroup)|[Example](#ExamplesVirtualMachinesListByResourceGroup)|
|[az networkcloud virtualmachine list](#VirtualMachinesListBySubscription)|ListBySubscription|[Parameters](#ParametersVirtualMachinesListBySubscription)|[Example](#ExamplesVirtualMachinesListBySubscription)|
|[az networkcloud virtualmachine show](#VirtualMachinesGet)|Get|[Parameters](#ParametersVirtualMachinesGet)|[Example](#ExamplesVirtualMachinesGet)|
|[az networkcloud virtualmachine create](#VirtualMachinesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersVirtualMachinesCreateOrUpdate#Create)|[Example](#ExamplesVirtualMachinesCreateOrUpdate#Create)|
|[az networkcloud virtualmachine update](#VirtualMachinesUpdate)|Update|[Parameters](#ParametersVirtualMachinesUpdate)|[Example](#ExamplesVirtualMachinesUpdate)|
|[az networkcloud virtualmachine delete](#VirtualMachinesDelete)|Delete|[Parameters](#ParametersVirtualMachinesDelete)|[Example](#ExamplesVirtualMachinesDelete)|
|[az networkcloud virtualmachine attach-volume](#VirtualMachinesAttachVolume)|AttachVolume|[Parameters](#ParametersVirtualMachinesAttachVolume)|[Example](#ExamplesVirtualMachinesAttachVolume)|
|[az networkcloud virtualmachine detach-volume](#VirtualMachinesDetachVolume)|DetachVolume|[Parameters](#ParametersVirtualMachinesDetachVolume)|[Example](#ExamplesVirtualMachinesDetachVolume)|
|[az networkcloud virtualmachine power-off](#VirtualMachinesPowerOff)|PowerOff|[Parameters](#ParametersVirtualMachinesPowerOff)|[Example](#ExamplesVirtualMachinesPowerOff)|
|[az networkcloud virtualmachine reimage](#VirtualMachinesReimage)|Reimage|[Parameters](#ParametersVirtualMachinesReimage)|[Example](#ExamplesVirtualMachinesReimage)|
|[az networkcloud virtualmachine restart](#VirtualMachinesRestart)|Restart|[Parameters](#ParametersVirtualMachinesRestart)|[Example](#ExamplesVirtualMachinesRestart)|
|[az networkcloud virtualmachine start](#VirtualMachinesStart)|Start|[Parameters](#ParametersVirtualMachinesStart)|[Example](#ExamplesVirtualMachinesStart)|

### <a name="CommandsInVolumes">Commands in `az networkcloud volume` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az networkcloud volume list](#VolumesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersVolumesListByResourceGroup)|[Example](#ExamplesVolumesListByResourceGroup)|
|[az networkcloud volume list](#VolumesListBySubscription)|ListBySubscription|[Parameters](#ParametersVolumesListBySubscription)|[Example](#ExamplesVolumesListBySubscription)|
|[az networkcloud volume show](#VolumesGet)|Get|[Parameters](#ParametersVolumesGet)|[Example](#ExamplesVolumesGet)|
|[az networkcloud volume create](#VolumesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersVolumesCreateOrUpdate#Create)|[Example](#ExamplesVolumesCreateOrUpdate#Create)|
|[az networkcloud volume update](#VolumesUpdate)|Update|[Parameters](#ParametersVolumesUpdate)|[Example](#ExamplesVolumesUpdate)|
|[az networkcloud volume delete](#VolumesDelete)|Delete|[Parameters](#ParametersVolumesDelete)|[Example](#ExamplesVolumesDelete)|


## COMMAND DETAILS
### group `az networkcloud baremetalmachine`
#### <a name="BareMetalMachinesListByResourceGroup">Command `az networkcloud baremetalmachine list`</a>

##### <a name="ExamplesBareMetalMachinesListByResourceGroup">Example</a>
```
az networkcloud baremetalmachine list --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="BareMetalMachinesListBySubscription">Command `az networkcloud baremetalmachine list`</a>

##### <a name="ExamplesBareMetalMachinesListBySubscription">Example</a>
```
az networkcloud baremetalmachine list
```
##### <a name="ParametersBareMetalMachinesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="BareMetalMachinesGet">Command `az networkcloud baremetalmachine show`</a>

##### <a name="ExamplesBareMetalMachinesGet">Example</a>
```
az networkcloud baremetalmachine show --name "bareMetalMachineName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|

#### <a name="BareMetalMachinesCreateOrUpdate#Create">Command `az networkcloud baremetalmachine create`</a>

##### <a name="ExamplesBareMetalMachinesCreateOrUpdate#Create">Example</a>
```
az networkcloud baremetalmachine create --name "bareMetalMachineName" --extended-location \
name="/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ExtendedLocation/customLocatio\
ns/clusterExtendedLocationName" type="CustomLocation" --location "location" --bmc-connection-string \
"bmcconnectionstring" --bmc-credentials password="{password}" username="bmcuser" --bmc-mac-address "00:00:4f:00:57:00" \
--boot-mac-address "00:00:4e:00:58:af" --machine-details "User-provided machine details." --machine-name "r01c001" \
--machine-sku-id "684E-3B16-399E" --rack-id "/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/M\
icrosoft.NetworkCloud/racks/rackName" --rack-slot 1 --serial-number "BM1219XXX" --tags key1="myvalue1" key2="myvalue2" \
--resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--bmc-connection-string**|string|The connection string for the baseboard management controller including IP address and protocol.|bmc_connection_string|bmcConnectionString|
|**--bmc-credentials**|object|The credentials of the baseboard management controller on this bare metal machine.|bmc_credentials|bmcCredentials|
|**--bmc-mac-address**|string|The MAC address of the BMC device.|bmc_mac_address|bmcMacAddress|
|**--boot-mac-address**|string|The MAC address of a NIC connected to the PXE network.|boot_mac_address|bootMacAddress|
|**--machine-details**|string|The custom details provided by the customer.|machine_details|machineDetails|
|**--machine-name**|string|The OS-level hostname assigned to this machine.|machine_name|machineName|
|**--machine-sku-id**|string|The unique internal identifier of the bare metal machine SKU.|machine_sku_id|machineSkuId|
|**--rack-id**|string|The resource ID of the rack where this bare metal machine resides.|rack_id|rackId|
|**--rack-slot**|integer|The rack slot in which this bare metal machine is located, ordered from the bottom up i.e. the lowest slot is 1.|rack_slot|rackSlot|
|**--serial-number**|string|The serial number of the bare metal machine.|serial_number|serialNumber|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="BareMetalMachinesUpdate">Command `az networkcloud baremetalmachine update`</a>

##### <a name="ExamplesBareMetalMachinesUpdate">Example</a>
```
az networkcloud baremetalmachine update --name "bareMetalMachineName" --machine-details "machinedetails" --tags \
key1="myvalue1" key2="myvalue2" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|
|**--machine-details**|string|The details provided by the customer during the creation of rack manifests that allows for custom data to be associated with this machine.|machine_details|machineDetails|

#### <a name="BareMetalMachinesDelete">Command `az networkcloud baremetalmachine delete`</a>

##### <a name="ExamplesBareMetalMachinesDelete">Example</a>
```
az networkcloud baremetalmachine delete --name "bareMetalMachineName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|

#### <a name="BareMetalMachinesCordon">Command `az networkcloud baremetalmachine cordon`</a>

##### <a name="ExamplesBareMetalMachinesCordon">Example</a>
```
az networkcloud baremetalmachine cordon --evacuate "True" --name "bareMetalMachineName" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesCordon">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|
|**--evacuate**|choice|The indicator of whether to evacuate the node workload when the bare metal machine is cordoned.|evacuate|evacuate|

#### <a name="BareMetalMachinesPowerOff">Command `az networkcloud baremetalmachine power-off`</a>

##### <a name="ExamplesBareMetalMachinesPowerOff">Example</a>
```
az networkcloud baremetalmachine power-off --name "bareMetalMachineName" --skip-shutdown "True" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesPowerOff">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|
|**--skip-shutdown**|choice|The indicator of whether to skip the graceful OS shutdown and power off the bare metal machine immediately.|skip_shutdown|skipShutdown|

#### <a name="BareMetalMachinesReimage">Command `az networkcloud baremetalmachine reimage`</a>

##### <a name="ExamplesBareMetalMachinesReimage">Example</a>
```
az networkcloud baremetalmachine reimage --name "bareMetalMachineName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesReimage">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|

#### <a name="BareMetalMachinesReplace">Command `az networkcloud baremetalmachine replace`</a>

##### <a name="ExamplesBareMetalMachinesReplace">Example</a>
```
az networkcloud baremetalmachine replace --name "bareMetalMachineName" --bmc-credentials password="{password}" \
username="bmcuser" --bmc-mac-address "00:00:4f:00:57:ad" --boot-mac-address "00:00:4e:00:58:af" --machine-name "name" \
--serial-number "BM1219XXX" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesReplace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|
|**--bmc-credentials**|object|The credentials of the baseboard management controller on this bare metal machine.|bmc_credentials|bmcCredentials|
|**--bmc-mac-address**|string|The MAC address of the BMC device.|bmc_mac_address|bmcMacAddress|
|**--boot-mac-address**|string|The MAC address of a NIC connected to the PXE network.|boot_mac_address|bootMacAddress|
|**--machine-name**|string|The OS-level hostname assigned to this machine.|machine_name|machineName|
|**--serial-number**|string|The serial number of the bare metal machine.|serial_number|serialNumber|

#### <a name="BareMetalMachinesRestart">Command `az networkcloud baremetalmachine restart`</a>

##### <a name="ExamplesBareMetalMachinesRestart">Example</a>
```
az networkcloud baremetalmachine restart --name "bareMetalMachineName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesRestart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|

#### <a name="BareMetalMachinesRunCommand">Command `az networkcloud baremetalmachine run-command`</a>

##### <a name="ExamplesBareMetalMachinesRunCommand">Example</a>
```
az networkcloud baremetalmachine run-command --name "bareMetalMachineName" --arguments "--argument1" "argument2" \
--limit-time-seconds 60 --script "cHdkCg==" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesRunCommand">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|
|**--limit-time-seconds**|integer|The maximum time the script is allowed to run. If the execution time exceeds the maximum, the script will be stopped, any output produced until then will be captured, and the exit code matching a timeout will be returned (252).|limit_time_seconds|limitTimeSeconds|
|**--script**|string|The base64 encoded script to execute on the bare metal machine.|script|script|
|**--arguments**|array|The list of string arguments that will be passed to the script in order as separate arguments.|arguments|arguments|

#### <a name="BareMetalMachinesRunDataExtracts">Command `az networkcloud baremetalmachine run-data-extract`</a>

##### <a name="ExamplesBareMetalMachinesRunDataExtracts">Example</a>
```
az networkcloud baremetalmachine run-data-extract --name "bareMetalMachineName" --limit-time-seconds 60 --commands \
command="networkInfo" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesRunDataExtracts">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|
|**--commands**|array|The list of curated data extraction commands to be executed directly against the target machine.|commands|commands|
|**--limit-time-seconds**|integer|The maximum time the commands are allowed to run. If the execution time exceeds the maximum, the script will be stopped, any output produced until then will be captured, and the exit code matching a timeout will be returned (252).|limit_time_seconds|limitTimeSeconds|

#### <a name="BareMetalMachinesRunReadCommands">Command `az networkcloud baremetalmachine run-read-command`</a>

##### <a name="ExamplesBareMetalMachinesRunReadCommands">Example</a>
```
az networkcloud baremetalmachine run-read-command --name "bareMetalMachineName" --limit-time-seconds 60 --commands \
arguments="pods" arguments="-A" command="kubectl get" --commands arguments="192.168.0.99" arguments="-c" arguments="3" \
command="ping" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesRunReadCommands">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|
|**--commands**|array|The list of read-only commands to be executed directly against the target machine.|commands|commands|
|**--limit-time-seconds**|integer|The maximum time the commands are allowed to run. If the execution time exceeds the maximum, the script will be stopped, any output produced until then will be captured, and the exit code matching a timeout will be returned (252).|limit_time_seconds|limitTimeSeconds|

#### <a name="BareMetalMachinesStart">Command `az networkcloud baremetalmachine start`</a>

##### <a name="ExamplesBareMetalMachinesStart">Example</a>
```
az networkcloud baremetalmachine start --name "bareMetalMachineName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesStart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|

#### <a name="BareMetalMachinesUncordon">Command `az networkcloud baremetalmachine uncordon`</a>

##### <a name="ExamplesBareMetalMachinesUncordon">Example</a>
```
az networkcloud baremetalmachine uncordon --name "bareMetalMachineName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesUncordon">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|

#### <a name="BareMetalMachinesValidateHardware">Command `az networkcloud baremetalmachine validate-hardware`</a>

##### <a name="ExamplesBareMetalMachinesValidateHardware">Example</a>
```
az networkcloud baremetalmachine validate-hardware --name "bareMetalMachineName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachinesValidateHardware">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--bare-metal-machine-name**|string|The name of the bare metal machine.|bare_metal_machine_name|bareMetalMachineName|

### group `az networkcloud baremetalmachinekeyset`
#### <a name="BareMetalMachineKeySetsListByResourceGroup">Command `az networkcloud baremetalmachinekeyset list`</a>

##### <a name="ExamplesBareMetalMachineKeySetsListByResourceGroup">Example</a>
```
az networkcloud baremetalmachinekeyset list --cluster-name "clusterName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachineKeySetsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|

#### <a name="BareMetalMachineKeySetsGet">Command `az networkcloud baremetalmachinekeyset show`</a>

##### <a name="ExamplesBareMetalMachineKeySetsGet">Example</a>
```
az networkcloud baremetalmachinekeyset show --name "bareMetalMachineKeySetName" --cluster-name "clusterName" \
--resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachineKeySetsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--bare-metal-machine-key-set-name**|string|The name of the bare metal machine key set.|bare_metal_machine_key_set_name|bareMetalMachineKeySetName|

#### <a name="BareMetalMachineKeySetsCreateOrUpdate#Create">Command `az networkcloud baremetalmachinekeyset create`</a>

##### <a name="ExamplesBareMetalMachineKeySetsCreateOrUpdate#Create">Example</a>
```
az networkcloud baremetalmachinekeyset create --name "bareMetalMachineKeySetName" --extended-location \
name="/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ExtendedLocation/customLocatio\
ns/clusterExtendedLocationName" type="CustomLocation" --location "location" --azure-group-id \
"f110271b-XXXX-4163-9b99-214d91660f0e" --expiration "2022-12-31T23:59:59.008Z" --jump-hosts-allowed "192.0.2.1" \
"192.0.2.5" --os-group-name "standardAccessGroup" --privilege-level "Standard" --user-list description="Needs access \
for troubleshooting as a part of the support team" azure-user-name="userABC" key-data="ssh-rsa \
AAtsE3njSONzDYRIZv/WLjVuMfrUSByHp+jfaaOLHTIIB4fJvo6dQUZxE20w2iDHV3tEkmnTo84eba97VMueQD6OzJPEyWZMRpz8UYWOd0IXeRqiFu1lawN\
blZhwNT/ojNZfpB3af/YDzwQCZgTcTRyNNhL4o/blKUmug0daSsSXISTRnIDpcf5qytjs1Xo+yYyJMvzLL59mhAyb3p/cD+Y3/s3WhAx+l0XOKpzXnblrv9\
d3q4c2tWmm/SyFqthaqd0= admin@vm" --user-list description="Needs access for troubleshooting as a part of the support \
team" azure-user-name="userXYZ" key-data="ssh-rsa AAtsE3njSONzDYRIZv/WLjVuMfrUSByHp+jfaaOLHTIIB4fJvo6dQUZxE20w2iDHV3tEk\
mnTo84eba97VMueQD6OzJPEyWZMRpz8UYWOd0IXeRqiFu1lawNblZhwNT/ojNZfpB3af/YDzwQCZgTcTRyNNhL4o/blKUmug0daSsSXISTRnIDpcf5qytjs\
1Xo+yYyJMvzLL59mhAyb3p/cD+Y3/s3WhAx+l0XOKpzXnblrv9d3q4c2tWmm/SyFqthaqd0= admin@vm" --tags key1="myvalue1" \
key2="myvalue2" --cluster-name "clusterName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachineKeySetsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--bare-metal-machine-key-set-name**|string|The name of the bare metal machine key set.|bare_metal_machine_key_set_name|bareMetalMachineKeySetName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--azure-group-id**|string|The object ID of Azure Active Directory group that all users in the list must be in for access to be granted. Users that are not in the group will not have access.|azure_group_id|azureGroupId|
|**--expiration**|date-time|The date and time after which the users in this key set will be removed from the bare metal machines.|expiration|expiration|
|**--jump-hosts-allowed**|array|The list of IP addresses of jump hosts with management network access from which a login will be allowed for the users.|jump_hosts_allowed|jumpHostsAllowed|
|**--privilege-level**|choice|The access level allowed for the users in this key set.|privilege_level|privilegeLevel|
|**--user-list**|array|The unique list of permitted users.|user_list|userList|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--os-group-name**|string|The name of the group that users will be assigned to on the operating system of the machines.|os_group_name|osGroupName|

#### <a name="BareMetalMachineKeySetsUpdate">Command `az networkcloud baremetalmachinekeyset update`</a>

##### <a name="ExamplesBareMetalMachineKeySetsUpdate">Example</a>
```
az networkcloud baremetalmachinekeyset update --name "bareMetalMachineKeySetName" --expiration \
"2022-12-31T23:59:59.008Z" --jump-hosts-allowed "192.0.2.1" "192.0.2.5" --user-list description="Needs access for \
troubleshooting as a part of the support team" azure-user-name="userABC" key-data="ssh-rsa \
AAtsE3njSONzDYRIZv/WLjVuMfrUSByHp+jfaaOLHTIIB4fJvo6dQUZxE20w2iDHV3tEkmnTo84eba97VMueQD6OzJPEyWZMRpz8UYWOd0IXeRqiFu1lawN\
blZhwNT/ojNZfpB3af/YDzwQCZgTcTRyNNhL4o/blKUmug0daSsSXISTRnIDpcf5qytjs1Xo+yYyJMvzLL59mhAyb3p/cD+Y3/s3WhAx+l0XOKpzXnblrv9\
d3q4c2tWmm/SyFqthaqd0= admin@vm" --user-list description="Needs access for troubleshooting as a part of the support \
team" azure-user-name="userXYZ" key-data="ssh-rsa AAtsE3njSONzDYRIZv/WLjVuMfrUSByHp+jfaaOLHTIIB4fJvo6dQUZxE20w2iDHV3tEk\
mnTo84eba97VMueQD6OzJPEyWZMRpz8UYWOd0IXeRqiFu1lawNblZhwNT/ojNZfpB3af/YDzwQCZgTcTRyNNhL4o/blKUmug0daSsSXISTRnIDpcf5qytjs\
1Xo+yYyJMvzLL59mhAyb3p/cD+Y3/s3WhAx+l0XOKpzXnblrv9d3q4c2tWmm/SyFqthaqd0= admin@vm" --tags key1="myvalue1" \
key2="myvalue2" --cluster-name "clusterName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachineKeySetsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--bare-metal-machine-key-set-name**|string|The name of the bare metal machine key set.|bare_metal_machine_key_set_name|bareMetalMachineKeySetName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|
|**--expiration**|date-time|The date and time after which the users in this key set will be removed from the bare metal machines.|expiration|expiration|
|**--jump-hosts-allowed**|array|The list of IP addresses of jump hosts with management network access from which a login will be allowed for the users.|jump_hosts_allowed|jumpHostsAllowed|
|**--user-list**|array|The unique list of permitted users.|user_list|userList|

#### <a name="BareMetalMachineKeySetsDelete">Command `az networkcloud baremetalmachinekeyset delete`</a>

##### <a name="ExamplesBareMetalMachineKeySetsDelete">Example</a>
```
az networkcloud baremetalmachinekeyset delete --name "bareMetalMachineKeySetName" --cluster-name "clusterName" \
--resource-group "resourceGroupName"
```
##### <a name="ParametersBareMetalMachineKeySetsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--bare-metal-machine-key-set-name**|string|The name of the bare metal machine key set.|bare_metal_machine_key_set_name|bareMetalMachineKeySetName|

### group `az networkcloud bmckeyset`
#### <a name="BmcKeySetsListByResourceGroup">Command `az networkcloud bmckeyset list`</a>

##### <a name="ExamplesBmcKeySetsListByResourceGroup">Example</a>
```
az networkcloud bmckeyset list --cluster-name "clusterName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBmcKeySetsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|

#### <a name="BmcKeySetsGet">Command `az networkcloud bmckeyset show`</a>

##### <a name="ExamplesBmcKeySetsGet">Example</a>
```
az networkcloud bmckeyset show --name "bmcKeySetName" --cluster-name "clusterName" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersBmcKeySetsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--bmc-key-set-name**|string|The name of the baseboard management controller key set.|bmc_key_set_name|bmcKeySetName|

#### <a name="BmcKeySetsCreateOrUpdate#Create">Command `az networkcloud bmckeyset create`</a>

##### <a name="ExamplesBmcKeySetsCreateOrUpdate#Create">Example</a>
```
az networkcloud bmckeyset create --name "bmcKeySetName" --extended-location name="/subscriptions/subscriptionId/resourc\
eGroups/resourceGroupName/providers/Microsoft.ExtendedLocation/customLocations/clusterExtendedLocationName" \
type="CustomLocation" --location "location" --azure-group-id "f110271b-XXXX-4163-9b99-214d91660f0e" --expiration \
"2022-12-31T23:59:59.008Z" --privilege-level "Administrator" --user-list description="Needs access for troubleshooting \
as a part of the support team" azure-user-name="userABC" key-data="ssh-rsa AAtsE3njSONzDYRIZv/WLjVuMfrUSByHp+jfaaOLHTII\
B4fJvo6dQUZxE20w2iDHV3tEkmnTo84eba97VMueQD6OzJPEyWZMRpz8UYWOd0IXeRqiFu1lawNblZhwNT/ojNZfpB3af/YDzwQCZgTcTRyNNhL4o/blKUm\
ug0daSsSXISTRnIDpcf5qytjs1Xo+yYyJMvzLL59mhAyb3p/cD+Y3/s3WhAx+l0XOKpzXnblrv9d3q4c2tWmm/SyFqthaqd0= admin@vm" \
--user-list description="Needs access for troubleshooting as a part of the support team" azure-user-name="userXYZ" \
key-data="ssh-rsa AAtsE3njSONzDYRIZv/WLjVuMfrUSByHp+jfaaOLHTIIB4fJvo6dQUZxE20w2iDHV3tEkmnTo84eba97VMueQD6OzJPEyWZMRpz8U\
YWOd0IXeRqiFu1lawNblZhwNT/ojNZfpB3af/YDzwQCZgTcTRyNNhL4o/blKUmug0daSsSXISTRnIDpcf5qytjs1Xo+yYyJMvzLL59mhAyb3p/cD+Y3/s3W\
hAx+l0XOKpzXnblrv9d3q4c2tWmm/SyFqthaqd0= admin@vm" --tags key1="myvalue1" key2="myvalue2" --cluster-name "clusterName" \
--resource-group "resourceGroupName"
```
##### <a name="ParametersBmcKeySetsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--bmc-key-set-name**|string|The name of the baseboard management controller key set.|bmc_key_set_name|bmcKeySetName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--azure-group-id**|string|The object ID of Azure Active Directory group that all users in the list must be in for access to be granted. Users that are not in the group will not have access.|azure_group_id|azureGroupId|
|**--expiration**|date-time|The date and time after which the users in this key set will be removed from the baseboard management controllers.|expiration|expiration|
|**--privilege-level**|choice|The access level allowed for the users in this key set.|privilege_level|privilegeLevel|
|**--user-list**|array|The unique list of permitted users.|user_list|userList|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="BmcKeySetsUpdate">Command `az networkcloud bmckeyset update`</a>

##### <a name="ExamplesBmcKeySetsUpdate">Example</a>
```
az networkcloud bmckeyset update --name "bmcKeySetName" --expiration "2022-12-31T23:59:59.008Z" --user-list \
description="Needs access for troubleshooting as a part of the support team" azure-user-name="userABC" \
key-data="ssh-rsa AAtsE3njSONzDYRIZv/WLjVuMfrUSByHp+jfaaOLHTIIB4fJvo6dQUZxE20w2iDHV3tEkmnTo84eba97VMueQD6OzJPEyWZMRpz8U\
YWOd0IXeRqiFu1lawNblZhwNT/ojNZfpB3af/YDzwQCZgTcTRyNNhL4o/blKUmug0daSsSXISTRnIDpcf5qytjs1Xo+yYyJMvzLL59mhAyb3p/cD+Y3/s3W\
hAx+l0XOKpzXnblrv9d3q4c2tWmm/SyFqthaqd0= admin@vm" --user-list description="Needs access for troubleshooting as a part \
of the support team" azure-user-name="userXYZ" key-data="ssh-rsa AAtsE3njSONzDYRIZv/WLjVuMfrUSByHp+jfaaOLHTIIB4fJvo6dQU\
ZxE20w2iDHV3tEkmnTo84eba97VMueQD6OzJPEyWZMRpz8UYWOd0IXeRqiFu1lawNblZhwNT/ojNZfpB3af/YDzwQCZgTcTRyNNhL4o/blKUmug0daSsSXI\
STRnIDpcf5qytjs1Xo+yYyJMvzLL59mhAyb3p/cD+Y3/s3WhAx+l0XOKpzXnblrv9d3q4c2tWmm/SyFqthaqd0= admin@vm" --tags \
key1="myvalue1" key2="myvalue2" --cluster-name "clusterName" --resource-group "resourceGroupName"
```
##### <a name="ParametersBmcKeySetsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--bmc-key-set-name**|string|The name of the baseboard management controller key set.|bmc_key_set_name|bmcKeySetName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|
|**--expiration**|date-time|The date and time after which the users in this key set will be removed from the baseboard management controllers.|expiration|expiration|
|**--user-list**|array|The unique list of permitted users.|user_list|userList|

#### <a name="BmcKeySetsDelete">Command `az networkcloud bmckeyset delete`</a>

##### <a name="ExamplesBmcKeySetsDelete">Example</a>
```
az networkcloud bmckeyset delete --name "bmcKeySetName" --cluster-name "clusterName" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersBmcKeySetsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--bmc-key-set-name**|string|The name of the baseboard management controller key set.|bmc_key_set_name|bmcKeySetName|

### group `az networkcloud cloudservicesnetwork`
#### <a name="CloudServicesNetworksListByResourceGroup">Command `az networkcloud cloudservicesnetwork list`</a>

##### <a name="ExamplesCloudServicesNetworksListByResourceGroup">Example</a>
```
az networkcloud cloudservicesnetwork list --resource-group "resourceGroupName"
```
##### <a name="ParametersCloudServicesNetworksListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="CloudServicesNetworksListBySubscription">Command `az networkcloud cloudservicesnetwork list`</a>

##### <a name="ExamplesCloudServicesNetworksListBySubscription">Example</a>
```
az networkcloud cloudservicesnetwork list
```
##### <a name="ParametersCloudServicesNetworksListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="CloudServicesNetworksGet">Command `az networkcloud cloudservicesnetwork show`</a>

##### <a name="ExamplesCloudServicesNetworksGet">Example</a>
```
az networkcloud cloudservicesnetwork show --name "cloudServicesNetworkName" --resource-group "resourceGroupName"
```
##### <a name="ParametersCloudServicesNetworksGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cloud-services-network-name**|string|The name of the cloud services network.|cloud_services_network_name|cloudServicesNetworkName|

#### <a name="CloudServicesNetworksCreateOrUpdate#Create">Command `az networkcloud cloudservicesnetwork create`</a>

##### <a name="ExamplesCloudServicesNetworksCreateOrUpdate#Create">Example</a>
```
az networkcloud cloudservicesnetwork create --name "cloudServicesNetworkName" --extended-location \
name="/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ExtendedLocation/customLocatio\
ns/clusterExtendedLocationName" type="CustomLocation" --location "location" --additional-egress-endpoints \
"[{\\"category\\":\\"azure-resource-management\\",\\"endpoints\\":[{\\"domainName\\":\\"https://storageaccountex.blob.c\
ore.windows.net\\",\\"port\\":443}]}]" --enable-default-egress-endpoints "False" --tags key1="myvalue1" \
key2="myvalue2" --resource-group "resourceGroupName"
```
##### <a name="ParametersCloudServicesNetworksCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cloud-services-network-name**|string|The name of the cloud services network.|cloud_services_network_name|cloudServicesNetworkName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--additional-egress-endpoints**|array|The list of egress endpoints. This allows for connection from a Hybrid AKS cluster to the specified endpoint.|additional_egress_endpoints|additionalEgressEndpoints|
|**--enable-default-egress-endpoints**|choice|The indicator of whether the platform default endpoints are allowed for the egress traffic.|enable_default_egress_endpoints|enableDefaultEgressEndpoints|

#### <a name="CloudServicesNetworksUpdate">Command `az networkcloud cloudservicesnetwork update`</a>

##### <a name="ExamplesCloudServicesNetworksUpdate">Example</a>
```
az networkcloud cloudservicesnetwork update --name "cloudServicesNetworkName" --additional-egress-endpoints \
"[{\\"category\\":\\"azure-resource-management\\",\\"endpoints\\":[{\\"domainName\\":\\"https://storageaccountex.blob.c\
ore.windows.net\\",\\"port\\":443}]}]" --enable-default-egress-endpoints "False" --tags key1="myvalue1" \
key2="myvalue2" --resource-group "resourceGroupName"
```
##### <a name="ParametersCloudServicesNetworksUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cloud-services-network-name**|string|The name of the cloud services network.|cloud_services_network_name|cloudServicesNetworkName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|
|**--additional-egress-endpoints**|array|The list of egress endpoints. This allows for connection from a Hybrid AKS cluster to the specified endpoint.|additional_egress_endpoints|additionalEgressEndpoints|
|**--enable-default-egress-endpoints**|choice|The indicator of whether the platform default endpoints are allowed for the egress traffic.|enable_default_egress_endpoints|enableDefaultEgressEndpoints|

#### <a name="CloudServicesNetworksDelete">Command `az networkcloud cloudservicesnetwork delete`</a>

##### <a name="ExamplesCloudServicesNetworksDelete">Example</a>
```
az networkcloud cloudservicesnetwork delete --name "cloudServicesNetworkName" --resource-group "resourceGroupName"
```
##### <a name="ParametersCloudServicesNetworksDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cloud-services-network-name**|string|The name of the cloud services network.|cloud_services_network_name|cloudServicesNetworkName|

### group `az networkcloud cluster`
#### <a name="ClustersListByResourceGroup">Command `az networkcloud cluster list`</a>

##### <a name="ExamplesClustersListByResourceGroup">Example</a>
```
az networkcloud cluster list --resource-group "resourceGroupName"
```
##### <a name="ParametersClustersListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="ClustersListBySubscription">Command `az networkcloud cluster list`</a>

##### <a name="ExamplesClustersListBySubscription">Example</a>
```
az networkcloud cluster list
```
##### <a name="ParametersClustersListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="ClustersGet">Command `az networkcloud cluster show`</a>

##### <a name="ExamplesClustersGet">Example</a>
```
az networkcloud cluster show --name "clusterName" --resource-group "resourceGroupName"
```
##### <a name="ParametersClustersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|

#### <a name="ClustersCreateOrUpdate#Create">Command `az networkcloud cluster create`</a>

##### <a name="ExamplesClustersCreateOrUpdate#Create">Example</a>
```
az networkcloud cluster create --name "clusterName" --extended-location name="/subscriptions/subscriptionId/resourceGro\
ups/resourceGroupName/providers/Microsoft.ExtendedLocation/customLocations/clusterManagerExtendedLocationName" \
type="CustomLocation" --location "location" --bare-metal-machine-configuration-data "[{\\"bmcCredentials\\":{\\"passwor\
d\\":\\"{password}\\",\\"username\\":\\"username\\"},\\"bmcMacAddress\\":\\"AA:BB:CC:DD:EE:FF\\",\\"bootMacAddress\\":\
\\"00:BB:CC:DD:EE:FF\\",\\"machineDetails\\":\\"extraDetails\\",\\"machineName\\":\\"bmmName1\\",\\"rackSlot\\":1,\\"se\
rialNumber\\":\\"BM1219XXX\\"},{\\"bmcCredentials\\":{\\"password\\":\\"{password}\\",\\"username\\":\\"username\\"},\\\
"bmcMacAddress\\":\\"AA:BB:CC:DD:EE:00\\",\\"bootMacAddress\\":\\"00:BB:CC:DD:EE:00\\",\\"machineDetails\\":\\"extraDet\
ails\\",\\"machineName\\":\\"bmmName2\\",\\"rackSlot\\":2,\\"serialNumber\\":\\"BM1219YYY\\"}]" --network-rack-id \
"/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ManagedNetworkFabric/networkRacks/n\
etworkRackName" --rack-location "Foo Datacenter, Floor 3, Aisle 9, Rack 2" --rack-serial-number "AA1234" --rack-sku-id \
"/subscriptions/subscriptionId/providers/Microsoft.NetworkCloud/rackSkus/rackSkuName" --storage-appliance-configuration\
-data "[{\\"adminCredentials\\":{\\"password\\":\\"{password}\\",\\"username\\":\\"username\\"},\\"rackSlot\\":1,\\"ser\
ialNumber\\":\\"BM1219XXX\\",\\"storageApplianceName\\":\\"vmName\\"}]" --analytics-workspace-id \
"/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/microsoft.operationalInsights/workspaces/logA\
nalyticsWorkspaceName" --cluster-location "Foo Street, 3rd Floor, row 9" --cluster-service-principal \
application-id="12345678-1234-1234-1234-123456789012" password="{password}" principal-id="00000008-0004-0004-0004-00000\
0000012" tenant-id="80000000-4000-4000-4000-120000000000" --cluster-type "SingleRack" --cluster-version "1.0.0" \
--compute-deployment-threshold type="PercentSuccess" grouping="PerCluster" value=90 --compute-rack-definitions \
"[{\\"bareMetalMachineConfigurationData\\":[{\\"bmcCredentials\\":{\\"password\\":\\"{password}\\",\\"username\\":\\"us\
ername\\"},\\"bmcMacAddress\\":\\"AA:BB:CC:DD:EE:FF\\",\\"bootMacAddress\\":\\"00:BB:CC:DD:EE:FF\\",\\"machineDetails\\\
":\\"extraDetails\\",\\"machineName\\":\\"bmmName1\\",\\"rackSlot\\":1,\\"serialNumber\\":\\"BM1219XXX\\"},{\\"bmcCrede\
ntials\\":{\\"password\\":\\"{password}\\",\\"username\\":\\"username\\"},\\"bmcMacAddress\\":\\"AA:BB:CC:DD:EE:00\\",\
\\"bootMacAddress\\":\\"00:BB:CC:DD:EE:00\\",\\"machineDetails\\":\\"extraDetails\\",\\"machineName\\":\\"bmmName2\\",\
\\"rackSlot\\":2,\\"serialNumber\\":\\"BM1219YYY\\"}],\\"networkRackId\\":\\"/subscriptions/subscriptionId/resourceGrou\
ps/resourceGroupName/providers/Microsoft.ManagedNetworkFabric/networkRacks/networkRackName\\",\\"rackLocation\\":\\"Foo\
 Datacenter, Floor 3, Aisle 9, Rack 2\\",\\"rackSerialNumber\\":\\"AA1234\\",\\"rackSkuId\\":\\"/subscriptions/subscrip\
tionId/providers/Microsoft.NetworkCloud/rackSkus/rackSkuName\\",\\"storageApplianceConfigurationData\\":[{\\"adminCrede\
ntials\\":{\\"password\\":\\"{password}\\",\\"username\\":\\"username\\"},\\"rackSlot\\":1,\\"serialNumber\\":\\"BM1219\
XXX\\",\\"storageApplianceName\\":\\"vmName\\"}]}]" --managed-resource-group-configuration name="my-managed-rg" \
location="East US" --network-fabric-id "/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Micros\
oft.ManagedNetworkFabric/networkFabrics/fabricName" --tags key1="myvalue1" key2="myvalue2" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersClustersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster manager associated with the cluster.|extended_location|extendedLocation|
|**--analytics-workspace-id**|string|The resource ID of the Log Analytics Workspace that will be used for storing relevant logs.|analytics_workspace_id|analyticsWorkspaceId|
|**--cluster-type**|choice|The type of rack configuration for the cluster.|cluster_type|clusterType|
|**--cluster-version**|string|The current runtime version of the cluster.|cluster_version|clusterVersion|
|**--network-fabric-id**|string|The resource ID of the Network Fabric associated with the cluster.|network_fabric_id|networkFabricId|
|**--network-rack-id**|string|The resource ID of the network rack that matches this rack definition.|network_rack_id|networkRackId|
|**--rack-serial-number**|string|The unique identifier for the rack within Network Cloud cluster. An alternate unique alphanumeric value other than a serial number may be provided if desired.|rack_serial_number|rackSerialNumber|
|**--rack-sku-id**|string|The resource ID of the sku for the rack being added.|rack_sku_id|rackSkuId|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--cluster-location**|string|The customer-provided location information to identify where the cluster resides.|cluster_location|clusterLocation|
|**--cluster-service-principal**|object|The service principal to be used by the cluster during Arc Appliance installation.|cluster_service_principal|clusterServicePrincipal|
|**--compute-deployment-threshold**|object|The validation threshold indicating the allowable failures of compute machines during environment validation and deployment.|compute_deployment_threshold|computeDeploymentThreshold|
|**--compute-rack-definitions**|array|The list of rack definitions for the compute racks in a multi-rack cluster, or an empty list in a single-rack cluster.|compute_rack_definitions|computeRackDefinitions|
|**--managed-resource-group-configuration**|object|The configuration of the managed resource group associated with the resource.|managed_resource_group_configuration|managedResourceGroupConfiguration|
|**--availability-zone**|string|The zone name used for this rack when created.|availability_zone|availabilityZone|
|**--bare-metal-machine-configuration-data**|array|The unordered list of bare metal machine configuration.|bare_metal_machine_configuration_data|bareMetalMachineConfigurationData|
|**--rack-location**|string|The free-form description of the rack's location.|rack_location|rackLocation|
|**--storage-appliance-configuration-data**|array|The list of storage appliance configuration data for this rack.|storage_appliance_configuration_data|storageApplianceConfigurationData|

#### <a name="ClustersUpdate">Command `az networkcloud cluster update`</a>

##### <a name="ExamplesClustersUpdate">Example</a>
```
az networkcloud cluster update --name "clusterName" --bare-metal-machine-configuration-data \
"[{\\"bmcCredentials\\":{\\"password\\":\\"{password}\\",\\"username\\":\\"username\\"},\\"bmcMacAddress\\":\\"AA:BB:CC\
:DD:EE:FF\\",\\"bootMacAddress\\":\\"00:BB:CC:DD:EE:FF\\",\\"machineDetails\\":\\"extraDetails\\",\\"machineName\\":\\"\
bmmName1\\",\\"rackSlot\\":1,\\"serialNumber\\":\\"BM1219XXX\\"},{\\"bmcCredentials\\":{\\"password\\":\\"{password}\\"\
,\\"username\\":\\"username\\"},\\"bmcMacAddress\\":\\"AA:BB:CC:DD:EE:00\\",\\"bootMacAddress\\":\\"00:BB:CC:DD:EE:00\\\
",\\"machineDetails\\":\\"extraDetails\\",\\"machineName\\":\\"bmmName2\\",\\"rackSlot\\":2,\\"serialNumber\\":\\"BM121\
9YYY\\"}]" --network-rack-id "/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.Manage\
dNetworkFabric/networkRacks/networkRackName" --rack-location "Foo Datacenter, Floor 3, Aisle 9, Rack 2" \
--rack-serial-number "newSerialNumber" --rack-sku-id "/subscriptions/subscriptionId/providers/Microsoft.NetworkCloud/ra\
ckSkus/rackSkuName" --storage-appliance-configuration-data "[{\\"adminCredentials\\":{\\"password\\":\\"{password}\\",\
\\"username\\":\\"username\\"},\\"rackSlot\\":1,\\"serialNumber\\":\\"BM1219XXX\\",\\"storageApplianceName\\":\\"vmName\
\\"}]" --compute-deployment-threshold type="PercentSuccess" grouping="PerCluster" value=90 --tags key1="myvalue1" \
key2="myvalue2" --resource-group "resourceGroupName"
az networkcloud cluster update --name "clusterName" --cluster-location "Foo Street, 3rd Floor, row 9" --tags \
key1="myvalue1" key2="myvalue2" --resource-group "resourceGroupName"
```
##### <a name="ParametersClustersUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|
|**--cluster-location**|string|The customer-provided location information to identify where the cluster resides.|cluster_location|clusterLocation|
|**--cluster-service-principal**|object|The service principal to be used by the cluster during Arc Appliance installation.|cluster_service_principal|clusterServicePrincipal|
|**--compute-deployment-threshold**|object|The validation threshold indicating the allowable failures of compute machines during environment validation and deployment.|compute_deployment_threshold|computeDeploymentThreshold|
|**--compute-rack-definitions**|array|The list of rack definitions for the compute racks in a multi-rack cluster, or an empty list in a single-rack cluster.|compute_rack_definitions|computeRackDefinitions|
|**--availability-zone**|string|The zone name used for this rack when created.|availability_zone|availabilityZone|
|**--bare-metal-machine-configuration-data**|array|The unordered list of bare metal machine configuration.|bare_metal_machine_configuration_data|bareMetalMachineConfigurationData|
|**--network-rack-id**|string|The resource ID of the network rack that matches this rack definition.|network_rack_id|networkRackId|
|**--rack-location**|string|The free-form description of the rack's location.|rack_location|rackLocation|
|**--rack-serial-number**|string|The unique identifier for the rack within Network Cloud cluster. An alternate unique alphanumeric value other than a serial number may be provided if desired.|rack_serial_number|rackSerialNumber|
|**--rack-sku-id**|string|The resource ID of the sku for the rack being added.|rack_sku_id|rackSkuId|
|**--storage-appliance-configuration-data**|array|The list of storage appliance configuration data for this rack.|storage_appliance_configuration_data|storageApplianceConfigurationData|

#### <a name="ClustersDelete">Command `az networkcloud cluster delete`</a>

##### <a name="ExamplesClustersDelete">Example</a>
```
az networkcloud cluster delete --name "clusterName" --resource-group "resourceGroupName"
```
##### <a name="ParametersClustersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|

#### <a name="ClustersDeploy">Command `az networkcloud cluster deploy`</a>

##### <a name="ExamplesClustersDeploy">Example</a>
```
az networkcloud cluster deploy --name "clusterName" --resource-group "resourceGroupName"
az networkcloud cluster deploy --skip-validations-for-machines "bmmName1" --name "clusterName" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersClustersDeploy">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--skip-validations-for-machines**|array|The names of bare metal machines in the cluster that should be skipped during environment validation.|skip_validations_for_machines|skipValidationsForMachines|

#### <a name="ClustersUpdateVersion">Command `az networkcloud cluster update-version`</a>

##### <a name="ExamplesClustersUpdateVersion">Example</a>
```
az networkcloud cluster update-version --name "clusterName" --target-cluster-version "2.0" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersClustersUpdateVersion">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--target-cluster-version**|string|The version to be applied to the cluster during update.|target_cluster_version|targetClusterVersion|

### group `az networkcloud clustermanager`
#### <a name="ClusterManagersListByResourceGroup">Command `az networkcloud clustermanager list`</a>

##### <a name="ExamplesClusterManagersListByResourceGroup">Example</a>
```
az networkcloud clustermanager list --resource-group "resourceGroupName"
```
##### <a name="ParametersClusterManagersListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="ClusterManagersListBySubscription">Command `az networkcloud clustermanager list`</a>

##### <a name="ExamplesClusterManagersListBySubscription">Example</a>
```
az networkcloud clustermanager list
```
##### <a name="ParametersClusterManagersListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="ClusterManagersGet">Command `az networkcloud clustermanager show`</a>

##### <a name="ExamplesClusterManagersGet">Example</a>
```
az networkcloud clustermanager show --name "clusterManagerName" --resource-group "resourceGroupName"
```
##### <a name="ParametersClusterManagersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-manager-name**|string|The name of the cluster manager.|cluster_manager_name|clusterManagerName|

#### <a name="ClusterManagersCreateOrUpdate#Create">Command `az networkcloud clustermanager create`</a>

##### <a name="ExamplesClusterManagersCreateOrUpdate#Create">Example</a>
```
az networkcloud clustermanager create --name "clusterManagerName" --location "location" --analytics-workspace-id \
"/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/microsoft.operationalInsights/workspaces/logA\
nalyticsWorkspaceName" --fabric-controller-id "/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers\
/Microsoft.ManagedNetworkFabric/networkFabricControllers/fabricControllerName" --managed-resource-group-configuration \
name="my-managed-rg" location="East US" --tags key1="myvalue1" key2="myvalue2" --resource-group "resourceGroupName"
```
##### <a name="ParametersClusterManagersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-manager-name**|string|The name of the cluster manager.|cluster_manager_name|clusterManagerName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--fabric-controller-id**|string|The resource ID of the fabric controller that has one to one mapping with the cluster manager.|fabric_controller_id|fabricControllerId|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--analytics-workspace-id**|string|The resource ID of the Log Analytics workspace that is used for the logs collection.|analytics_workspace_id|analyticsWorkspaceId|
|**--availability-zones**|array|Field deprecated, this value will no longer influence the cluster manager allocation process and will be removed in a future version. The Azure availability zones within the region that will be used to support the cluster manager resource.|availability_zones|availabilityZones|
|**--managed-resource-group-configuration**|object|The configuration of the managed resource group associated with the resource.|managed_resource_group_configuration|managedResourceGroupConfiguration|
|**--vm-size**|string|Field deprecated, this value will no longer influence the cluster manager allocation process and will be removed in a future version. The size of the Azure virtual machines to use for hosting the cluster manager resource.|vm_size|vmSize|

#### <a name="ClusterManagersUpdate">Command `az networkcloud clustermanager update`</a>

##### <a name="ExamplesClusterManagersUpdate">Example</a>
```
az networkcloud clustermanager update --name "clusterManagerName" --tags key1="myvalue1" key2="myvalue2" \
--resource-group "resourceGroupName"
```
##### <a name="ParametersClusterManagersUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-manager-name**|string|The name of the cluster manager.|cluster_manager_name|clusterManagerName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|

#### <a name="ClusterManagersDelete">Command `az networkcloud clustermanager delete`</a>

##### <a name="ExamplesClusterManagersDelete">Example</a>
```
az networkcloud clustermanager delete --name "clusterManagerName" --resource-group "resourceGroupName"
```
##### <a name="ParametersClusterManagersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-manager-name**|string|The name of the cluster manager.|cluster_manager_name|clusterManagerName|

### group `az networkcloud console`
#### <a name="ConsolesListByResourceGroup">Command `az networkcloud console list`</a>

##### <a name="ExamplesConsolesListByResourceGroup">Example</a>
```
az networkcloud console list --resource-group "resourceGroupName" --virtual-machine-name "virtualMachineName"
```
##### <a name="ParametersConsolesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|

#### <a name="ConsolesGet">Command `az networkcloud console show`</a>

##### <a name="ExamplesConsolesGet">Example</a>
```
az networkcloud console show --name "default" --resource-group "resourceGroupName" --virtual-machine-name \
"virtualMachineName"
```
##### <a name="ParametersConsolesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|
|**--console-name**|string|The name of the virtual machine console.|console_name|consoleName|

#### <a name="ConsolesCreateOrUpdate#Create">Command `az networkcloud console create`</a>

##### <a name="ExamplesConsolesCreateOrUpdate#Create">Example</a>
```
az networkcloud console create --name "default" --extended-location name="/subscriptions/subscriptionId/resourceGroups/\
resourceGroupName/providers/Microsoft.ExtendedLocation/customLocations/clusterManagerExtendedLocationName" \
type="CustomLocation" --location "location" --enabled "True" --expiration "2022-06-01T01:27:03.008Z" --key-data \
"ssh-rsa AAtsE3njSONzDYRIZv/WLjVuMfrUSByHp+jfaaOLHTIIB4fJvo6dQUZxE20w2iDHV3tEkmnTo84eba97VMueQD6OzJPEyWZMRpz8UYWOd0IXeR\
qiFu1lawNblZhwNT/ojNZfpB3af/YDzwQCZgTcTRyNNhL4o/blKUmug0daSsSXISTRnIDpcf5qytjs1Xo+yYyJMvzLL59mhAyb3p/cD+Y3/s3WhAx+l0XOK\
pzXnblrv9d3q4c2tWmm/SyFqthaqd0= admin@vm" --tags key1="myvalue1" key2="myvalue2" --resource-group "resourceGroupName" \
--virtual-machine-name "virtualMachineName"
```
##### <a name="ParametersConsolesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|
|**--console-name**|string|The name of the virtual machine console.|console_name|consoleName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster manager associated with the cluster this virtual machine is created on.|extended_location|extendedLocation|
|**--enabled**|choice|The indicator of whether the console access is enabled.|enabled|enabled|
|**--key-data**|string|The public ssh key of the user.|key_data|keyData|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--expiration**|date-time|The date and time after which the key will be disallowed access.|expiration|expiration|

#### <a name="ConsolesUpdate">Command `az networkcloud console update`</a>

##### <a name="ExamplesConsolesUpdate">Example</a>
```
az networkcloud console update --name "default" --enabled "True" --expiration "2022-06-01T01:27:03.008Z" --key-data \
"ssh-rsa AAtsE3njSONzDYRIZv/WLjVuMfrUSByHp+jfaaOLHTIIB4fJvo6dQUZxE20w2iDHV3tEkmnTo84eba97VMueQD6OzJPEyWZMRpz8UYWOd0IXeR\
qiFu1lawNblZhwNT/ojNZfpB3af/YDzwQCZgTcTRyNNhL4o/blKUmug0daSsSXISTRnIDpcf5qytjs1Xo+yYyJMvzLL59mhAyb3p/cD+Y3/s3WhAx+l0XOK\
pzXnblrv9d3q4c2tWmm/SyFqthaqd0= admin@vm" --tags key1="myvalue1" key2="myvalue2" --resource-group "resourceGroupName" \
--virtual-machine-name "virtualMachineName"
```
##### <a name="ParametersConsolesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|
|**--console-name**|string|The name of the virtual machine console.|console_name|consoleName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|
|**--enabled**|choice|The credentials used to login to the image repository that has access to the specified image.|enabled|enabled|
|**--expiration**|date-time|The date and time after which the key will be disallowed access.|expiration|expiration|
|**--key-data**|string|The public ssh key of the user.|key_data|keyData|

#### <a name="ConsolesDelete">Command `az networkcloud console delete`</a>

##### <a name="ExamplesConsolesDelete">Example</a>
```
az networkcloud console delete --name "default" --resource-group "resourceGroupName" --virtual-machine-name \
"virtualMachineName"
```
##### <a name="ParametersConsolesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|
|**--console-name**|string|The name of the virtual machine console.|console_name|consoleName|

### group `az networkcloud defaultcninetwork`
#### <a name="DefaultCniNetworksListByResourceGroup">Command `az networkcloud defaultcninetwork list`</a>

##### <a name="ExamplesDefaultCniNetworksListByResourceGroup">Example</a>
```
az networkcloud defaultcninetwork list --resource-group "resourceGroupName"
```
##### <a name="ParametersDefaultCniNetworksListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DefaultCniNetworksListBySubscription">Command `az networkcloud defaultcninetwork list`</a>

##### <a name="ExamplesDefaultCniNetworksListBySubscription">Example</a>
```
az networkcloud defaultcninetwork list
```
##### <a name="ParametersDefaultCniNetworksListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="DefaultCniNetworksGet">Command `az networkcloud defaultcninetwork show`</a>

##### <a name="ExamplesDefaultCniNetworksGet">Example</a>
```
az networkcloud defaultcninetwork show --name "defaultCniNetworkName" --resource-group "resourceGroupName"
```
##### <a name="ParametersDefaultCniNetworksGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--default-cni-network-name**|string|The name of the default CNI network.|default_cni_network_name|defaultCniNetworkName|

#### <a name="DefaultCniNetworksCreateOrUpdate#Create">Command `az networkcloud defaultcninetwork create`</a>

##### <a name="ExamplesDefaultCniNetworksCreateOrUpdate#Create">Example</a>
```
az networkcloud defaultcninetwork create --name "defaultCniNetworkName" --extended-location \
name="/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ExtendedLocation/customLocatio\
ns/clusterExtendedLocationName" type="CustomLocation" --location "location" --bgp-peers as-number=64497 \
peer-ip="203.0.113.254" --community-advertisements communities="64512:100" subnet-prefix="192.0.2.0/27" \
--service-external-prefixes "192.0.2.0/28" --service-load-balancer-prefixes "192.0.2.16/28" --ip-allocation-type \
"DualStack" --ipv4-connected-prefix "203.0.113.0/24" --ipv6-connected-prefix "2001:db8:0:3::/64" \
--l3-isolation-domain-id "/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ManagedNet\
workFabric/l3IsolationDomains/l3IsolationDomainName" --vlan 12 --tags key1="myvalue1" key2="myvalue2" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersDefaultCniNetworksCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--default-cni-network-name**|string|The name of the default CNI network.|default_cni_network_name|defaultCniNetworkName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--l3-isolation-domain-id**|string|The resource ID of the Network Fabric l3IsolationDomain.|l3_isolation_domain_id|l3IsolationDomainId|
|**--vlan**|integer|The VLAN from the l3IsolationDomain that is used for this network.|vlan|vlan|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--ip-allocation-type**|choice|The type of the IP address allocation.|ip_allocation_type|ipAllocationType|
|**--ipv4-connected-prefix**|string|The IPV4 prefix (CIDR) assigned to this default CNI network. It is required when the IP allocation type is IPV4 or DualStack.|ipv4_connected_prefix|ipv4ConnectedPrefix|
|**--ipv6-connected-prefix**|string|The IPV6 prefix (CIDR) assigned to this default CNI network. It is required when the IP allocation type is IPV6 or DualStack.|ipv6_connected_prefix|ipv6ConnectedPrefix|
|**--bgp-peers**|array|The list of BgpPeer entities that the Hybrid AKS cluster will peer with in addition to peering that occurs automatically with the switch fabric.|bgp_peers|bgpPeers|
|**--community-advertisements**|array|The list of prefix community advertisement properties. Each prefix community specifies a prefix, and the communities that should be associated with that prefix when it is announced.|community_advertisements|communityAdvertisements|
|**--node-mesh-password**|string|The password of the Calico node mesh. It defaults to a randomly-generated string when not provided.|node_mesh_password|nodeMeshPassword|
|**--service-external-prefixes**|array|The subnet blocks in CIDR format for Kubernetes service external IPs to be advertised over BGP.|service_external_prefixes|serviceExternalPrefixes|
|**--service-load-balancer-prefixes**|array|The subnet blocks in CIDR format for Kubernetes load balancers. Load balancer IPs will only be advertised if they are within one of these blocks.|service_load_balancer_prefixes|serviceLoadBalancerPrefixes|

#### <a name="DefaultCniNetworksUpdate">Command `az networkcloud defaultcninetwork update`</a>

##### <a name="ExamplesDefaultCniNetworksUpdate">Example</a>
```
az networkcloud defaultcninetwork update --tags key1="myvalue1" key2="myvalue2" --name "defaultCniNetworkName" \
--resource-group "resourceGroupName"
```
##### <a name="ParametersDefaultCniNetworksUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--default-cni-network-name**|string|The name of the default CNI network.|default_cni_network_name|defaultCniNetworkName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|

#### <a name="DefaultCniNetworksDelete">Command `az networkcloud defaultcninetwork delete`</a>

##### <a name="ExamplesDefaultCniNetworksDelete">Example</a>
```
az networkcloud defaultcninetwork delete --name "defaultCniNetworkName" --resource-group "resourceGroupName"
```
##### <a name="ParametersDefaultCniNetworksDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--default-cni-network-name**|string|The name of the default CNI network.|default_cni_network_name|defaultCniNetworkName|

### group `az networkcloud hybridakscluster`
#### <a name="HybridAksClustersListByResourceGroup">Command `az networkcloud hybridakscluster list`</a>

##### <a name="ExamplesHybridAksClustersListByResourceGroup">Example</a>
```
az networkcloud hybridakscluster list --resource-group "resourceGroupName"
```
##### <a name="ParametersHybridAksClustersListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="HybridAksClustersListBySubscription">Command `az networkcloud hybridakscluster list`</a>

##### <a name="ExamplesHybridAksClustersListBySubscription">Example</a>
```
az networkcloud hybridakscluster list
```
##### <a name="ParametersHybridAksClustersListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="HybridAksClustersGet">Command `az networkcloud hybridakscluster show`</a>

##### <a name="ExamplesHybridAksClustersGet">Example</a>
```
az networkcloud hybridakscluster show --name "hybridAksClusterName" --resource-group "resourceGroupName"
```
##### <a name="ParametersHybridAksClustersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--hybrid-aks-cluster-name**|string|The name of the Hybrid AKS cluster.|hybrid_aks_cluster_name|hybridAksClusterName|

#### <a name="HybridAksClustersCreateOrUpdate#Create">Command `az networkcloud hybridakscluster create`</a>

##### <a name="ExamplesHybridAksClustersCreateOrUpdate#Create">Example</a>
```
az networkcloud hybridakscluster create --name "hybridAksClusterName" --extended-location \
name="/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ExtendedLocation/customLocatio\
ns/clusterExtendedLocationName" type="CustomLocation" --location "location" --associated-network-ids \
"/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.NetworkCloud/l3Networks/l3NetworkNa\
me" --control-plane-count 4 --hybrid-aks-provisioned-cluster-id "/subscriptions/subscriptionId/resourceGroups/resourceG\
roupName/providers/Microsoft.HybridContainerService/provisionedClusters/hybridAksClusterName" --worker-count 8 --tags \
key1="myvalue1" key2="myvalue2" --resource-group "resourceGroupName"
```
##### <a name="ParametersHybridAksClustersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--hybrid-aks-cluster-name**|string|The name of the Hybrid AKS cluster.|hybrid_aks_cluster_name|hybridAksClusterName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--associated-network-ids**|array|The list of resource IDs for the workload networks associated with the Hybrid AKS cluster. It can be any of l2Networks, l3Networks, or trunkedNetworks resources. This field will also contain one cloudServicesNetwork and one defaultCniNetwork.|associated_network_ids|associatedNetworkIds|
|**--control-plane-count**|integer|The number of control plane node VMs.|control_plane_count|controlPlaneCount|
|**--hybrid-aks-provisioned-cluster-id**|string|The resource ID of the Hybrid AKS cluster that this additional information is for.|hybrid_aks_provisioned_cluster_id|hybridAksProvisionedClusterId|
|**--worker-count**|integer|The number of worker node VMs.|worker_count|workerCount|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="HybridAksClustersUpdate">Command `az networkcloud hybridakscluster update`</a>

##### <a name="ExamplesHybridAksClustersUpdate">Example</a>
```
az networkcloud hybridakscluster update --name "hybridAksClusterName" --tags key1="myvalue1" key2="myvalue2" \
--resource-group "resourceGroupName"
```
##### <a name="ParametersHybridAksClustersUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--hybrid-aks-cluster-name**|string|The name of the Hybrid AKS cluster.|hybrid_aks_cluster_name|hybridAksClusterName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|

#### <a name="HybridAksClustersDelete">Command `az networkcloud hybridakscluster delete`</a>

##### <a name="ExamplesHybridAksClustersDelete">Example</a>
```
az networkcloud hybridakscluster delete --name "hybridAksClusterName" --resource-group "resourceGroupName"
```
##### <a name="ParametersHybridAksClustersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--hybrid-aks-cluster-name**|string|The name of the Hybrid AKS cluster.|hybrid_aks_cluster_name|hybridAksClusterName|

#### <a name="HybridAksClustersRestartNode">Command `az networkcloud hybridakscluster restart-node`</a>

##### <a name="ExamplesHybridAksClustersRestartNode">Example</a>
```
az networkcloud hybridakscluster restart-node --name "hybridAksClusterName" --node-name "nodeName" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersHybridAksClustersRestartNode">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--hybrid-aks-cluster-name**|string|The name of the Hybrid AKS cluster.|hybrid_aks_cluster_name|hybridAksClusterName|
|**--node-name**|string|The name of the node to restart.|node_name|nodeName|

### group `az networkcloud l2network`
#### <a name="L2NetworksListByResourceGroup">Command `az networkcloud l2network list`</a>

##### <a name="ExamplesL2NetworksListByResourceGroup">Example</a>
```
az networkcloud l2network list --resource-group "resourceGroupName"
```
##### <a name="ParametersL2NetworksListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="L2NetworksListBySubscription">Command `az networkcloud l2network list`</a>

##### <a name="ExamplesL2NetworksListBySubscription">Example</a>
```
az networkcloud l2network list
```
##### <a name="ParametersL2NetworksListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="L2NetworksGet">Command `az networkcloud l2network show`</a>

##### <a name="ExamplesL2NetworksGet">Example</a>
```
az networkcloud l2network show --name "l2NetworkName" --resource-group "resourceGroupName"
```
##### <a name="ParametersL2NetworksGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--l2-network-name**|string|The name of the L2 network.|l2_network_name|l2NetworkName|

#### <a name="L2NetworksCreateOrUpdate#Create">Command `az networkcloud l2network create`</a>

##### <a name="ExamplesL2NetworksCreateOrUpdate#Create">Example</a>
```
az networkcloud l2network create --name "l2NetworkName" --extended-location name="/subscriptions/subscriptionId/resourc\
eGroups/resourceGroupName/providers/Microsoft.ExtendedLocation/customLocations/clusterExtendedLocationName" \
type="CustomLocation" --location "location" --hybrid-aks-plugin-type "DPDK" --interface-name "eth0" \
--l2-isolation-domain-id "/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ManagedNet\
workFabric/l2IsolationDomains/l2IsolationDomainName" --tags key1="myvalue1" key2="myvalue2" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersL2NetworksCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--l2-network-name**|string|The name of the L2 network.|l2_network_name|l2NetworkName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--l2-isolation-domain-id**|string|The resource ID of the Network Fabric l2IsolationDomain.|l2_isolation_domain_id|l2IsolationDomainId|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--hybrid-aks-plugin-type**|choice|The network plugin type for Hybrid AKS.|hybrid_aks_plugin_type|hybridAksPluginType|
|**--interface-name**|string|The default interface name for this L2 network in the virtual machine. This name can be overridden by the name supplied in the network attachment configuration of that virtual machine.|interface_name|interfaceName|

#### <a name="L2NetworksUpdate">Command `az networkcloud l2network update`</a>

##### <a name="ExamplesL2NetworksUpdate">Example</a>
```
az networkcloud l2network update --name "l2NetworkName" --tags key1="myvalue1" key2="myvalue2" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersL2NetworksUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--l2-network-name**|string|The name of the L2 network.|l2_network_name|l2NetworkName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|

#### <a name="L2NetworksDelete">Command `az networkcloud l2network delete`</a>

##### <a name="ExamplesL2NetworksDelete">Example</a>
```
az networkcloud l2network delete --name "l2NetworkName" --resource-group "resourceGroupName"
```
##### <a name="ParametersL2NetworksDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--l2-network-name**|string|The name of the L2 network.|l2_network_name|l2NetworkName|

### group `az networkcloud l3network`
#### <a name="L3NetworksListByResourceGroup">Command `az networkcloud l3network list`</a>

##### <a name="ExamplesL3NetworksListByResourceGroup">Example</a>
```
az networkcloud l3network list --resource-group "resourceGroupName"
```
##### <a name="ParametersL3NetworksListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="L3NetworksListBySubscription">Command `az networkcloud l3network list`</a>

##### <a name="ExamplesL3NetworksListBySubscription">Example</a>
```
az networkcloud l3network list
```
##### <a name="ParametersL3NetworksListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="L3NetworksGet">Command `az networkcloud l3network show`</a>

##### <a name="ExamplesL3NetworksGet">Example</a>
```
az networkcloud l3network show --name "l3NetworkName" --resource-group "resourceGroupName"
```
##### <a name="ParametersL3NetworksGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--l3-network-name**|string|The name of the L3 network.|l3_network_name|l3NetworkName|

#### <a name="L3NetworksCreateOrUpdate#Create">Command `az networkcloud l3network create`</a>

##### <a name="ExamplesL3NetworksCreateOrUpdate#Create">Example</a>
```
az networkcloud l3network create --name "l3NetworkName" --extended-location name="/subscriptions/subscriptionId/resourc\
eGroups/resourceGroupName/providers/Microsoft.ExtendedLocation/customLocations/clusterExtendedLocationName" \
type="CustomLocation" --location "location" --hybrid-aks-ipam-enabled "True" --hybrid-aks-plugin-type "DPDK" \
--interface-name "eth0" --ip-allocation-type "DualStack" --ipv4-connected-prefix "198.51.100.0/24" \
--ipv6-connected-prefix "2001:db8::/64" --l3-isolation-domain-id "/subscriptions/subscriptionId/resourceGroups/resource\
GroupName/providers/Microsoft.ManagedNetworkFabric/l3IsolationDomains/l3IsolationDomainName" --vlan 12 --tags \
key1="myvalue1" key2="myvalue2" --resource-group "resourceGroupName"
```
##### <a name="ParametersL3NetworksCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--l3-network-name**|string|The name of the L3 network.|l3_network_name|l3NetworkName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--l3-isolation-domain-id**|string|The resource ID of the Network Fabric l3IsolationDomain.|l3_isolation_domain_id|l3IsolationDomainId|
|**--vlan**|integer|The VLAN from the l3IsolationDomain that is used for this network.|vlan|vlan|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--hybrid-aks-ipam-enabled**|choice|The indicator of whether or not to disable IPAM allocation on the network attachment definition injected into the Hybrid AKS Cluster.|hybrid_aks_ipam_enabled|hybridAksIpamEnabled|
|**--hybrid-aks-plugin-type**|choice|The network plugin type for Hybrid AKS.|hybrid_aks_plugin_type|hybridAksPluginType|
|**--interface-name**|string|The default interface name for this L3 network in the virtual machine. This name can be overridden by the name supplied in the network attachment configuration of that virtual machine.|interface_name|interfaceName|
|**--ip-allocation-type**|choice|The type of the IP address allocation, defaulted to "DualStack".|ip_allocation_type|ipAllocationType|
|**--ipv4-connected-prefix**|string|The IPV4 prefix (CIDR) assigned to this L3 network. Required when the IP allocation type is IPV4 or DualStack.|ipv4_connected_prefix|ipv4ConnectedPrefix|
|**--ipv6-connected-prefix**|string|The IPV6 prefix (CIDR) assigned to this L3 network. Required when the IP allocation type is IPV6 or DualStack.|ipv6_connected_prefix|ipv6ConnectedPrefix|

#### <a name="L3NetworksUpdate">Command `az networkcloud l3network update`</a>

##### <a name="ExamplesL3NetworksUpdate">Example</a>
```
az networkcloud l3network update --name "l3NetworkName" --tags key1="myvalue1" key2="myvalue2" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersL3NetworksUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--l3-network-name**|string|The name of the L3 network.|l3_network_name|l3NetworkName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|

#### <a name="L3NetworksDelete">Command `az networkcloud l3network delete`</a>

##### <a name="ExamplesL3NetworksDelete">Example</a>
```
az networkcloud l3network delete --name "l3NetworkName" --resource-group "resourceGroupName"
```
##### <a name="ParametersL3NetworksDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--l3-network-name**|string|The name of the L3 network.|l3_network_name|l3NetworkName|

### group `az networkcloud metricsconfiguration`
#### <a name="MetricsConfigurationsListByResourceGroup">Command `az networkcloud metricsconfiguration list`</a>

##### <a name="ExamplesMetricsConfigurationsListByResourceGroup">Example</a>
```
az networkcloud metricsconfiguration list --cluster-name "clusterName" --resource-group "resourceGroupName"
```
##### <a name="ParametersMetricsConfigurationsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|

#### <a name="MetricsConfigurationsGet">Command `az networkcloud metricsconfiguration show`</a>

##### <a name="ExamplesMetricsConfigurationsGet">Example</a>
```
az networkcloud metricsconfiguration show --cluster-name "clusterName" --name "default" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersMetricsConfigurationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--metrics-configuration-name**|string|The name of the metrics configuration for the cluster.|metrics_configuration_name|metricsConfigurationName|

#### <a name="MetricsConfigurationsCreateOrUpdate#Create">Command `az networkcloud metricsconfiguration create`</a>

##### <a name="ExamplesMetricsConfigurationsCreateOrUpdate#Create">Example</a>
```
az networkcloud metricsconfiguration create --cluster-name "clusterName" --name "default" --extended-location \
name="/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ExtendedLocation/customLocatio\
ns/clusterExtendedLocationName" type="CustomLocation" --location "location" --collection-interval 15 --enabled-metrics \
"metric1" "metric2" --tags key1="myvalue1" key2="myvalue2" --resource-group "resourceGroupName"
```
##### <a name="ParametersMetricsConfigurationsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--metrics-configuration-name**|string|The name of the metrics configuration for the cluster.|metrics_configuration_name|metricsConfigurationName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--collection-interval**|integer|The interval in minutes by which metrics will be collected.|collection_interval|collectionInterval|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--enabled-metrics**|array|The list of metric names that have been chosen to be enabled in addition to the core set of enabled metrics.|enabled_metrics|enabledMetrics|

#### <a name="MetricsConfigurationsUpdate">Command `az networkcloud metricsconfiguration update`</a>

##### <a name="ExamplesMetricsConfigurationsUpdate">Example</a>
```
az networkcloud metricsconfiguration update --cluster-name "clusterName" --name "default" --collection-interval 15 \
--enabled-metrics "metric1" "metric2" --tags key1="myvalue1" key2="myvalue2" --resource-group "resourceGroupName"
```
##### <a name="ParametersMetricsConfigurationsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--metrics-configuration-name**|string|The name of the metrics configuration for the cluster.|metrics_configuration_name|metricsConfigurationName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|
|**--collection-interval**|integer|The interval in minutes by which metrics will be collected.|collection_interval|collectionInterval|
|**--enabled-metrics**|array|The list of metric names that have been chosen to be enabled in addition to the core set of enabled metrics.|enabled_metrics|enabledMetrics|

#### <a name="MetricsConfigurationsDelete">Command `az networkcloud metricsconfiguration delete`</a>

##### <a name="ExamplesMetricsConfigurationsDelete">Example</a>
```
az networkcloud metricsconfiguration delete --cluster-name "clusterName" --name "default" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersMetricsConfigurationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the cluster.|cluster_name|clusterName|
|**--metrics-configuration-name**|string|The name of the metrics configuration for the cluster.|metrics_configuration_name|metricsConfigurationName|

### group `az networkcloud rack`
#### <a name="RacksListByResourceGroup">Command `az networkcloud rack list`</a>

##### <a name="ExamplesRacksListByResourceGroup">Example</a>
```
az networkcloud rack list --resource-group "resourceGroupName"
```
##### <a name="ParametersRacksListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="RacksListBySubscription">Command `az networkcloud rack list`</a>

##### <a name="ExamplesRacksListBySubscription">Example</a>
```
az networkcloud rack list
```
##### <a name="ParametersRacksListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="RacksGet">Command `az networkcloud rack show`</a>

##### <a name="ExamplesRacksGet">Example</a>
```
az networkcloud rack show --name "rackName" --resource-group "resourceGroupName"
```
##### <a name="ParametersRacksGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--rack-name**|string|The name of the rack.|rack_name|rackName|

#### <a name="RacksCreateOrUpdate#Create">Command `az networkcloud rack create`</a>

##### <a name="ExamplesRacksCreateOrUpdate#Create">Example</a>
```
az networkcloud rack create --name "rackName" --extended-location name="/subscriptions/subscriptionId/resourceGroups/re\
sourceGroupName/providers/Microsoft.ExtendedLocation/customLocations/clusterExtendedLocationName" \
type="CustomLocation" --location "location" --availability-zone "1" --rack-location "Rack 28" --rack-serial-number \
"RACK_SERIAL_NUMBER" --rack-sku-id "RACK-TYPE-1" --tags key1="myvalue1" key2="myvalue2" --resource-group \
"resourceGroupName"
```
##### <a name="ParametersRacksCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--rack-name**|string|The name of the rack.|rack_name|rackName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--availability-zone**|string|The value that will be used for machines in this rack to represent the availability zones that can be referenced by Hybrid AKS Clusters for node arrangement.|availability_zone|availabilityZone|
|**--rack-location**|string|The free-form description of the rack location. (e.g. “DTN Datacenter, Floor 3, Isle 9, Rack 2B”)|rack_location|rackLocation|
|**--rack-serial-number**|string|The unique identifier for the rack within Network Cloud cluster. An alternate unique alphanumeric value other than a serial number may be provided if desired.|rack_serial_number|rackSerialNumber|
|**--rack-sku-id**|string|The SKU for the rack.|rack_sku_id|rackSkuId|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="RacksUpdate">Command `az networkcloud rack update`</a>

##### <a name="ExamplesRacksUpdate">Example</a>
```
az networkcloud rack update --name "rackName" --rack-location "Rack 2B" --rack-serial-number "RACK_SERIAL_NUMBER" \
--tags key1="myvalue1" key2="myvalue2" --resource-group "resourceGroupName"
```
##### <a name="ParametersRacksUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--rack-name**|string|The name of the rack.|rack_name|rackName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|
|**--rack-location**|string|The free-form description of the rack location. (e.g. “DTN Datacenter, Floor 3, Isle 9, Rack 2B”)|rack_location|rackLocation|
|**--rack-serial-number**|string|The globally unique identifier for the rack.|rack_serial_number|rackSerialNumber|

#### <a name="RacksDelete">Command `az networkcloud rack delete`</a>

##### <a name="ExamplesRacksDelete">Example</a>
```
az networkcloud rack delete --name "rackName" --resource-group "resourceGroupName"
```
##### <a name="ParametersRacksDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--rack-name**|string|The name of the rack.|rack_name|rackName|

### group `az networkcloud racksku`
#### <a name="RackSkusListBySubscription">Command `az networkcloud racksku list`</a>

##### <a name="ExamplesRackSkusListBySubscription">Example</a>
```
az networkcloud racksku list
```
##### <a name="ParametersRackSkusListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="RackSkusGet">Command `az networkcloud racksku show`</a>

##### <a name="ExamplesRackSkusGet">Example</a>
```
az networkcloud racksku show --name "rackSkuName"
```
##### <a name="ParametersRackSkusGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--rack-sku-name**|string|The name of the rack SKU.|rack_sku_name|rackSkuName|

### group `az networkcloud storageappliance`
#### <a name="StorageAppliancesListByResourceGroup">Command `az networkcloud storageappliance list`</a>

##### <a name="ExamplesStorageAppliancesListByResourceGroup">Example</a>
```
az networkcloud storageappliance list --resource-group "resourceGroupName"
```
##### <a name="ParametersStorageAppliancesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="StorageAppliancesListBySubscription">Command `az networkcloud storageappliance list`</a>

##### <a name="ExamplesStorageAppliancesListBySubscription">Example</a>
```
az networkcloud storageappliance list
```
##### <a name="ParametersStorageAppliancesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="StorageAppliancesGet">Command `az networkcloud storageappliance show`</a>

##### <a name="ExamplesStorageAppliancesGet">Example</a>
```
az networkcloud storageappliance show --resource-group "resourceGroupName" --name "storageApplianceName"
```
##### <a name="ParametersStorageAppliancesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-appliance-name**|string|The name of the storage appliance.|storage_appliance_name|storageApplianceName|

#### <a name="StorageAppliancesCreateOrUpdate#Create">Command `az networkcloud storageappliance create`</a>

##### <a name="ExamplesStorageAppliancesCreateOrUpdate#Create">Example</a>
```
az networkcloud storageappliance create --resource-group "resourceGroupName" --name "storageApplianceName" \
--extended-location name="/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ExtendedLo\
cation/customLocations/clusterExtendedLocationName" type="CustomLocation" --location "location" \
--administrator-credentials password="{password}" username="adminUser" --rack-id "/subscriptions/subscriptionId/resourc\
eGroups/resourceGroupName/providers/Microsoft.NetworkCloud/racks/rackName" --rack-slot 1 --serial-number "BM1219XXX" \
--storage-appliance-sku-id "684E-3B16-399E" --tags key1="myvalue1" key2="myvalue2"
```
##### <a name="ParametersStorageAppliancesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-appliance-name**|string|The name of the storage appliance.|storage_appliance_name|storageApplianceName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--administrator-credentials**|object|The credentials of the administrative interface on this storage appliance.|administrator_credentials|administratorCredentials|
|**--rack-id**|string|The resource ID of the rack where this storage appliance resides.|rack_id|rackId|
|**--rack-slot**|integer|The slot the storage appliance is in the rack based on the BOM configuration.|rack_slot|rackSlot|
|**--serial-number**|string|The serial number for the storage appliance.|serial_number|serialNumber|
|**--storage-appliance-sku-id**|string|The SKU for the storage appliance.|storage_appliance_sku_id|storageApplianceSkuId|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="StorageAppliancesUpdate">Command `az networkcloud storageappliance update`</a>

##### <a name="ExamplesStorageAppliancesUpdate">Example</a>
```
az networkcloud storageappliance update --resource-group "resourceGroupName" --name "storageApplianceName" \
--serial-number "BM1219XXX" --tags key1="myvalue1" key2="myvalue2"
```
##### <a name="ParametersStorageAppliancesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-appliance-name**|string|The name of the storage appliance.|storage_appliance_name|storageApplianceName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|
|**--serial-number**|string|The serial number for the storage appliance.|serial_number|serialNumber|

#### <a name="StorageAppliancesDelete">Command `az networkcloud storageappliance delete`</a>

##### <a name="ExamplesStorageAppliancesDelete">Example</a>
```
az networkcloud storageappliance delete --resource-group "resourceGroupName" --name "storageApplianceName"
```
##### <a name="ParametersStorageAppliancesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-appliance-name**|string|The name of the storage appliance.|storage_appliance_name|storageApplianceName|

#### <a name="StorageAppliancesDisableRemoteVendorManagement">Command `az networkcloud storageappliance disable-remote-vendor-management`</a>

##### <a name="ExamplesStorageAppliancesDisableRemoteVendorManagement">Example</a>
```
az networkcloud storageappliance disable-remote-vendor-management --resource-group "resourceGroupName" --name \
"storageApplianceName"
```
##### <a name="ParametersStorageAppliancesDisableRemoteVendorManagement">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-appliance-name**|string|The name of the storage appliance.|storage_appliance_name|storageApplianceName|

#### <a name="StorageAppliancesEnableRemoteVendorManagement">Command `az networkcloud storageappliance enable-remote-vendor-management`</a>

##### <a name="ExamplesStorageAppliancesEnableRemoteVendorManagement">Example</a>
```
az networkcloud storageappliance enable-remote-vendor-management --resource-group "resourceGroupName" \
--support-endpoints "10.0.0.0/24" --name "storageApplianceName"
```
##### <a name="ParametersStorageAppliancesEnableRemoteVendorManagement">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-appliance-name**|string|The name of the storage appliance.|storage_appliance_name|storageApplianceName|
|**--support-endpoints**|array|Field Deprecated. This field is not used and will be rejected if provided. The list of IPv4 subnets (in CIDR format), IPv6 subnets (in CIDR format), or hostnames that the storage appliance needs accessible in order to turn on the remote vendor management.|support_endpoints|supportEndpoints|

#### <a name="StorageAppliancesRunReadCommands">Command `az networkcloud storageappliance run-read-command`</a>

##### <a name="ExamplesStorageAppliancesRunReadCommands">Example</a>
```
az networkcloud storageappliance run-read-command --resource-group "resourceGroupName" --name "storageApplianceName" \
--limit-time-seconds 60 --commands command="AlertList"
```
##### <a name="ParametersStorageAppliancesRunReadCommands">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-appliance-name**|string|The name of the storage appliance.|storage_appliance_name|storageApplianceName|
|**--commands**|array|The list of read-only commands to run.|commands|commands|
|**--limit-time-seconds**|integer|The maximum time the commands are allowed to run. If the execution time exceeds the maximum, the script will be stopped, any output produced until then will be captured, and the exit code matching a timeout will be returned (252).|limit_time_seconds|limitTimeSeconds|

#### <a name="StorageAppliancesValidateHardware">Command `az networkcloud storageappliance validate-hardware`</a>

##### <a name="ExamplesStorageAppliancesValidateHardware">Example</a>
```
az networkcloud storageappliance validate-hardware --resource-group "resourceGroupName" --name "storageApplianceName"
```
##### <a name="ParametersStorageAppliancesValidateHardware">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-appliance-name**|string|The name of the storage appliance.|storage_appliance_name|storageApplianceName|

### group `az networkcloud trunkednetwork`
#### <a name="TrunkedNetworksListByResourceGroup">Command `az networkcloud trunkednetwork list`</a>

##### <a name="ExamplesTrunkedNetworksListByResourceGroup">Example</a>
```
az networkcloud trunkednetwork list --resource-group "resourceGroupName"
```
##### <a name="ParametersTrunkedNetworksListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="TrunkedNetworksListBySubscription">Command `az networkcloud trunkednetwork list`</a>

##### <a name="ExamplesTrunkedNetworksListBySubscription">Example</a>
```
az networkcloud trunkednetwork list
```
##### <a name="ParametersTrunkedNetworksListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="TrunkedNetworksGet">Command `az networkcloud trunkednetwork show`</a>

##### <a name="ExamplesTrunkedNetworksGet">Example</a>
```
az networkcloud trunkednetwork show --resource-group "resourceGroupName" --name "trunkedNetworkName"
```
##### <a name="ParametersTrunkedNetworksGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--trunked-network-name**|string|The name of the trunked network.|trunked_network_name|trunkedNetworkName|

#### <a name="TrunkedNetworksCreateOrUpdate#Create">Command `az networkcloud trunkednetwork create`</a>

##### <a name="ExamplesTrunkedNetworksCreateOrUpdate#Create">Example</a>
```
az networkcloud trunkednetwork create --resource-group "resourceGroupName" --name "trunkedNetworkName" \
--extended-location name="/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ExtendedLo\
cation/customLocations/clusterExtendedLocationName" type="CustomLocation" --location "location" \
--hybrid-aks-plugin-type "DPDK" --interface-name "eth0" --isolation-domain-ids "/subscriptions/subscriptionId/resourceG\
roups/resourceGroupName/providers/Microsoft.ManagedNetworkFabric/l2IsolationDomains/l2IsolationDomainName" \
"/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ManagedNetworkFabric/l3IsolationDom\
ains/l3IsolationDomainName" --vlans 12 14 --tags key1="myvalue1" key2="myvalue2"
```
##### <a name="ParametersTrunkedNetworksCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--trunked-network-name**|string|The name of the trunked network.|trunked_network_name|trunkedNetworkName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--isolation-domain-ids**|array|The list of resource IDs representing the Network Fabric isolation domains. It can be any combination of l2IsolationDomain and l3IsolationDomain resources.|isolation_domain_ids|isolationDomainIds|
|**--vlans**|array|The list of vlans that are selected from the isolation domains for trunking.|vlans|vlans|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--hybrid-aks-plugin-type**|choice|The network plugin type for Hybrid AKS.|hybrid_aks_plugin_type|hybridAksPluginType|
|**--interface-name**|string|The default interface name for this trunked network in the virtual machine. This name can be overridden by the name supplied in the network attachment configuration of that virtual machine.|interface_name|interfaceName|

#### <a name="TrunkedNetworksUpdate">Command `az networkcloud trunkednetwork update`</a>

##### <a name="ExamplesTrunkedNetworksUpdate">Example</a>
```
az networkcloud trunkednetwork update --resource-group "resourceGroupName" --name "trunkedNetworkName" --tags \
key1="myvalue1" key2="myvalue2"
```
##### <a name="ParametersTrunkedNetworksUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--trunked-network-name**|string|The name of the trunked network.|trunked_network_name|trunkedNetworkName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|

#### <a name="TrunkedNetworksDelete">Command `az networkcloud trunkednetwork delete`</a>

##### <a name="ExamplesTrunkedNetworksDelete">Example</a>
```
az networkcloud trunkednetwork delete --resource-group "resourceGroupName" --name "trunkedNetworkName"
```
##### <a name="ParametersTrunkedNetworksDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--trunked-network-name**|string|The name of the trunked network.|trunked_network_name|trunkedNetworkName|

### group `az networkcloud virtualmachine`
#### <a name="VirtualMachinesListByResourceGroup">Command `az networkcloud virtualmachine list`</a>

##### <a name="ExamplesVirtualMachinesListByResourceGroup">Example</a>
```
az networkcloud virtualmachine list --resource-group "resourceGroupName"
```
##### <a name="ParametersVirtualMachinesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="VirtualMachinesListBySubscription">Command `az networkcloud virtualmachine list`</a>

##### <a name="ExamplesVirtualMachinesListBySubscription">Example</a>
```
az networkcloud virtualmachine list
```
##### <a name="ParametersVirtualMachinesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="VirtualMachinesGet">Command `az networkcloud virtualmachine show`</a>

##### <a name="ExamplesVirtualMachinesGet">Example</a>
```
az networkcloud virtualmachine show --resource-group "resourceGroupName" --name "virtualMachineName"
```
##### <a name="ParametersVirtualMachinesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|

#### <a name="VirtualMachinesCreateOrUpdate#Create">Command `az networkcloud virtualmachine create`</a>

##### <a name="ExamplesVirtualMachinesCreateOrUpdate#Create">Example</a>
```
az networkcloud virtualmachine create --resource-group "resourceGroupName" --name "virtualMachineName" \
--virtual-machine-parameters "{\\"extendedLocation\\":{\\"name\\":\\"/subscriptions/subscriptionId/resourceGroups/resou\
rceGroupName/providers/Microsoft.ExtendedLocation/customLocations/clusterExtendedLocationName\\",\\"type\\":\\"CustomLo\
cation\\"},\\"location\\":\\"location\\",\\"tags\\":{\\"key1\\":\\"myvalue1\\",\\"key2\\":\\"myvalue2\\"},\\"adminUsern\
ame\\":\\"username\\",\\"bootMethod\\":\\"UEFI\\",\\"cloudServicesNetworkAttachment\\":{\\"attachedNetworkId\\":\\"/sub\
scriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.NetworkCloud/cloudServicesNetworks/cloud\
ServicesNetworkName\\",\\"ipAllocationMethod\\":\\"Dynamic\\"},\\"cpuCores\\":2,\\"memorySizeGB\\":8,\\"networkAttachme\
nts\\":[{\\"attachedNetworkId\\":\\"/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.\
NetworkCloud/l3Networks/l3NetworkName\\",\\"defaultGateway\\":\\"True\\",\\"ipAllocationMethod\\":\\"Dynamic\\",\\"ipv4\
Address\\":\\"198.51.100.1\\",\\"ipv6Address\\":\\"2001:0db8:0000:0000:0000:0000:0000:0000\\",\\"networkAttachmentName\
\\":\\"netAttachName01\\"}],\\"networkData\\":\\"bmV0d29ya0RhdGVTYW1wbGU=\\",\\"placementHints\\":[{\\"hintType\\":\\"A\
ffinity\\",\\"resourceId\\":\\"/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.Netwo\
rkCloud/racks/rackName\\",\\"schedulingExecution\\":\\"Hard\\",\\"scope\\":\\"\\"}],\\"sshPublicKeys\\":[{\\"keyData\\"\
:\\"ssh-rsa AAtsE3njSONzDYRIZv/WLjVuMfrUSByHp+jfaaOLHTIIB4fJvo6dQUZxE20w2iDHV3tEkmnTo84eba97VMueQD6OzJPEyWZMRpz8UYWOd0I\
XeRqiFu1lawNblZhwNT/ojNZfpB3af/YDzwQCZgTcTRyNNhL4o/blKUmug0daSsSXISTRnIDpcf5qytjs1Xo+yYyJMvzLL59mhAyb3p/cD+Y3/s3WhAx+l0\
XOKpzXnblrv9d3q4c2tWmm/SyFqthaqd0= admin@vm\\"}],\\"storageProfile\\":{\\"osDisk\\":{\\"createOption\\":\\"Ephemeral\\"\
,\\"deleteOption\\":\\"Delete\\",\\"diskSizeGB\\":120},\\"volumeAttachments\\":[\\"/subscriptions/subscriptionId/resour\
ceGroups/resourceGroupName/providers/Microsoft.NetworkCloud/volumes/volumeName\\"]},\\"userData\\":\\"dXNlckRhdGVTYW1wb\
GU=\\",\\"vmDeviceModel\\":\\"T2\\",\\"vmImage\\":\\"myacr.azurecr.io/foobar:latest\\",\\"vmImageRepositoryCredentials\
\\":{\\"password\\":\\"{password}\\",\\"registryUrl\\":\\"myacr.azurecr.io\\",\\"username\\":\\"myuser\\"}}"
```
##### <a name="ParametersVirtualMachinesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|
|**--virtual-machine-parameters**|object|The request body.|virtual_machine_parameters|virtualMachineParameters|

#### <a name="VirtualMachinesUpdate">Command `az networkcloud virtualmachine update`</a>

##### <a name="ExamplesVirtualMachinesUpdate">Example</a>
```
az networkcloud virtualmachine update --resource-group "resourceGroupName" --name "virtualMachineName" \
--vm-image-repository-credentials password="{password}" registry-url="myacr.azurecr.io" username="myuser" --tags \
key1="myvalue1" key2="myvalue2"
```
##### <a name="ParametersVirtualMachinesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|
|**--vm-image-repository-credentials**|object|The credentials used to login to the image repository that has access to the specified image.|vm_image_repository_credentials|vmImageRepositoryCredentials|

#### <a name="VirtualMachinesDelete">Command `az networkcloud virtualmachine delete`</a>

##### <a name="ExamplesVirtualMachinesDelete">Example</a>
```
az networkcloud virtualmachine delete --resource-group "resourceGroupName" --name "virtualMachineName"
```
##### <a name="ParametersVirtualMachinesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|

#### <a name="VirtualMachinesAttachVolume">Command `az networkcloud virtualmachine attach-volume`</a>

##### <a name="ExamplesVirtualMachinesAttachVolume">Example</a>
```
az networkcloud virtualmachine attach-volume --resource-group "resourceGroupName" --volume-id \
"/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.NetworkCloud/volumes/volumeName" \
--name "virtualMachineName"
```
##### <a name="ParametersVirtualMachinesAttachVolume">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|
|**--volume-id**|string|The resource ID of the volume.|volume_id|volumeId|

#### <a name="VirtualMachinesDetachVolume">Command `az networkcloud virtualmachine detach-volume`</a>

##### <a name="ExamplesVirtualMachinesDetachVolume">Example</a>
```
az networkcloud virtualmachine detach-volume --resource-group "resourceGroupName" --volume-id \
"/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.NetworkCloud/volumes/volumeName" \
--name "virtualMachineName"
```
##### <a name="ParametersVirtualMachinesDetachVolume">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|
|**--volume-id**|string|The resource ID of the volume.|volume_id|volumeId|

#### <a name="VirtualMachinesPowerOff">Command `az networkcloud virtualmachine power-off`</a>

##### <a name="ExamplesVirtualMachinesPowerOff">Example</a>
```
az networkcloud virtualmachine power-off --resource-group "resourceGroupName" --name "virtualMachineName" \
--skip-shutdown "True"
```
##### <a name="ParametersVirtualMachinesPowerOff">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|
|**--skip-shutdown**|choice|The indicator of whether to skip the graceful OS shutdown and power off the virtual machine immediately.|skip_shutdown|skipShutdown|

#### <a name="VirtualMachinesReimage">Command `az networkcloud virtualmachine reimage`</a>

##### <a name="ExamplesVirtualMachinesReimage">Example</a>
```
az networkcloud virtualmachine reimage --resource-group "resourceGroupName" --name "virtualMachineName"
```
##### <a name="ParametersVirtualMachinesReimage">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|

#### <a name="VirtualMachinesRestart">Command `az networkcloud virtualmachine restart`</a>

##### <a name="ExamplesVirtualMachinesRestart">Example</a>
```
az networkcloud virtualmachine restart --resource-group "resourceGroupName" --name "virtualMachineName"
```
##### <a name="ParametersVirtualMachinesRestart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|

#### <a name="VirtualMachinesStart">Command `az networkcloud virtualmachine start`</a>

##### <a name="ExamplesVirtualMachinesStart">Example</a>
```
az networkcloud virtualmachine start --resource-group "resourceGroupName" --name "virtualMachineName"
```
##### <a name="ParametersVirtualMachinesStart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-machine-name**|string|The name of the virtual machine.|virtual_machine_name|virtualMachineName|

### group `az networkcloud volume`
#### <a name="VolumesListByResourceGroup">Command `az networkcloud volume list`</a>

##### <a name="ExamplesVolumesListByResourceGroup">Example</a>
```
az networkcloud volume list --resource-group "resourceGroupName"
```
##### <a name="ParametersVolumesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="VolumesListBySubscription">Command `az networkcloud volume list`</a>

##### <a name="ExamplesVolumesListBySubscription">Example</a>
```
az networkcloud volume list
```
##### <a name="ParametersVolumesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="VolumesGet">Command `az networkcloud volume show`</a>

##### <a name="ExamplesVolumesGet">Example</a>
```
az networkcloud volume show --resource-group "resourceGroupName" --name "volumeName"
```
##### <a name="ParametersVolumesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--volume-name**|string|The name of the volume.|volume_name|volumeName|

#### <a name="VolumesCreateOrUpdate#Create">Command `az networkcloud volume create`</a>

##### <a name="ExamplesVolumesCreateOrUpdate#Create">Example</a>
```
az networkcloud volume create --resource-group "resourceGroupName" --name "volumeName" --extended-location \
name="/subscriptions/subscriptionId/resourceGroups/resourceGroupName/providers/Microsoft.ExtendedLocation/customLocatio\
ns/clusterExtendedLocationName" type="CustomLocation" --location "location" --size-mi-b 10000 --tags key1="myvalue1" \
key2="myvalue2"
```
##### <a name="ParametersVolumesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--volume-name**|string|The name of the volume.|volume_name|volumeName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--extended-location**|object|The extended location of the cluster associated with the resource.|extended_location|extendedLocation|
|**--size-mi-b**|integer|The size of the allocation for this volume in Mebibytes.|size_mi_b|sizeMiB|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="VolumesUpdate">Command `az networkcloud volume update`</a>

##### <a name="ExamplesVolumesUpdate">Example</a>
```
az networkcloud volume update --resource-group "resourceGroupName" --name "volumeName" --tags key1="myvalue1" \
key2="myvalue2"
```
##### <a name="ParametersVolumesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--volume-name**|string|The name of the volume.|volume_name|volumeName|
|**--tags**|dictionary|The Azure resource tags that will replace the existing ones.|tags|tags|

#### <a name="VolumesDelete">Command `az networkcloud volume delete`</a>

##### <a name="ExamplesVolumesDelete">Example</a>
```
az networkcloud volume delete --resource-group "resourceGroupName" --name "volumeName"
```
##### <a name="ParametersVolumesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--volume-name**|string|The name of the volume.|volume_name|volumeName|
