# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#!/bin/bash
# LONG=resource-group-name:,elastic-san-name:,volume-group-name:,volume-name:,num-of-sessions:,enable-multi-path::
# while getopts ":resource-group-name:elastic-san-name:volume-group-name:volume-name:num-of-sessions:enable-multi-path" opt; do
#   case $opt in
#      a)
#        echo "argument -a called with parameter $OPTARG" >&2
#        ;;
#      b)
#        echo "argument -b called with parameter $OPTARG" >&2
#        ;;
#      *)
#        echo "invalid command: no parameter included with argument $OPTARG"
#        ;;
#   esac
# done
resource_group_name="test-elasticsan-rg"
elastic_san_name="testsan"
volume_group_name="testvolumegroup"
volume_name="testvolume1"
number_of_sessions=3
enable_multi_path=true
# echo $resource_group_name,$elastic_san_name,$volume_group_name,$volume_name,$number_of_sessions,$enable_multi_path
storage_target=$(az elastic-san volume show -e $elastic_san_name -g $resource_group_name -v $volume_group_name -n $volume_name --query storageTarget 2>/dev/null)
echo $storage_target 
# regex='"targetIqn": "([^"]*)", "targetPortalHostname": "([^"]*)", "targetPortalPort": ([0-9]*)'
# regex='"targetIqn": "([^"]*)", '
# if [[ $storage_target =~ $regex ]];
# then
#     target_iqn="${BASH_REMATCH[1]}"
# fi
# target_iqn=$('{ "provisioningState": "Succeeded", "status": "Running", "targetIqn": "iqn.2023-03.net.windows.core.blob.ElasticSan.es-4qtreagkjzj0:testvolume1", "targetPortalHostname": "es-4qtreagkjzj0.z45.blob.storage.azure.net", "targetPortalPort": 3260 }' | grep -Po '"targetIqn": "([^"]*)",' )
# echo $target_iqn

# target_iqn=$(az elastic-san volume show -e $elastic_san_name -g $resource_group_name -v $volume_group_name -n $volume_name --query storageTarget.targetIqn 2>/dev/null)
# target_portal_hostname=$(az elastic-san volume show -e $elastic_san_name -g $resource_group_name -v $volume_group_name -n $volume_name --query storageTarget.targetPortalHostname 2>/dev/null)
# target_portal_port=$(az elastic-san volume show -e $elastic_san_name -g $resource_group_name -v $volume_group_name -n $volume_name --query storageTarget.targetPortalPort 2>/dev/null)
# echo $target_iqn, $target_portal_hostname, $target_portal_port
# target_iqn=("${storage_target[1]}")
# echo $target_iqn
# for i in ${!storage_target[@]}; do
#   echo "${storage_target[$i]}123"
# done
# for t in ${storage_target[@]}; do
#   echo "$t,"
# done