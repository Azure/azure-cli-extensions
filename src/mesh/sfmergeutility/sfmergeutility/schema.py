# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from sfmergeutility.constants import Constants


class Schema(object):  # pylint: disable=too-few-public-methods
    HierarchichalSbzResourceNameBuilderMap = {
        Constants.MicrosoftServiceFabricMesh + "/" + Constants.SecretValues:
        Constants.MicrosoftServiceFabricMesh + "/" + Constants.Secrets + "/{0}/" + Constants.Values + "/{1}"
    }

    SchemaVersionRpApiVersionMap = {
        Constants.SchemaVersion_2018_07_01_preview: Constants.RpApiVersion_2018_07_01_preview,
        Constants.SchemaVersion_1_0_0: Constants.RpApiVersion_2018_07_01_preview,
        Constants.SchemaVersion_1_0_0_preview1: Constants.RpApiVersion_2018_07_01_preview,
        Constants.SchemaVersion_1_0_0_preview2: Constants.RpApiVersion_2018_09_01_preview
    }

    SchemaVersionFabricApiVersionMap = {
        Constants.SchemaVersion_2018_07_01_preview: Constants.FabricApiVersion_6_3_preview,
        Constants.SchemaVersion_1_0_0: Constants.FabricApiVersion_6_3_preview,
        Constants.SchemaVersion_1_0_0_preview1: Constants.FabricApiVersion_6_3_preview,
        Constants.SchemaVersion_1_0_0_preview2: Constants.FabricApiVersion_6_4_preview
    }

    SFSeabreezeResourceMap = {
        Constants.Application: Constants.Applications,
        Constants.Network: Constants.Networks,
        Constants.Volume: Constants.Volumes,
        Constants.Secret: Constants.Secrets,
        Constants.SecretValue: Constants.SecretValues,
        Constants.Gateway: Constants.Gateways,
    }

    SchemaVersionSupportedResourcesTypeMap = {
        Constants.SchemaVersion_2018_07_01_preview:
        {
            Constants.Networks: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Networks,
            Constants.Applications: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Applications,
            Constants.Volumes: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Volumes
        },
        Constants.SchemaVersion_1_0_0:
        {
            Constants.Networks: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Networks,
            Constants.Applications: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Applications,
            Constants.Volumes: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Volumes
        },
        Constants.SchemaVersion_1_0_0_preview1:
        {
            Constants.Networks: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Networks,
            Constants.Applications: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Applications,
            Constants.Volumes: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Volumes,
            Constants.Secrets: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Secrets
        },
        Constants.SchemaVersion_1_0_0_preview2:
        {
            Constants.Networks: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Networks,
            Constants.Applications: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Applications,
            Constants.Volumes: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Volumes,
            Constants.Secrets: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Secrets,
            Constants.SecretValues: Constants.MicrosoftServiceFabricMesh + "/" + Constants.SecretValues,
            Constants.Gateways: Constants.MicrosoftServiceFabricMesh + "/" + Constants.Gateways
        }
    }

    SchemaVersionSupportedResourcesKindMap = {
        Constants.SchemaVersion_2018_07_01_preview: [
            Constants.Network,
            Constants.Application,
            Constants.Volume,
        ],
        Constants.SchemaVersion_1_0_0: [
            Constants.Network,
            Constants.Application,
            Constants.Volume
        ],
        Constants.SchemaVersion_1_0_0_preview1: [
            Constants.Network,
            Constants.Application,
            Constants.Volume,
            Constants.Secret
        ],
        Constants.SchemaVersion_1_0_0_preview2: [
            Constants.Network,
            Constants.Application,
            Constants.Volume,
            Constants.Secret,
            Constants.SecretValue,
            Constants.Gateway,
        ]
    }

