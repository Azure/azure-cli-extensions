# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import os
from azext_arcdata.core.constants import ARC_API_V1

AD_CONNECTOR_RESOURCE_KIND = "ActiveDirectoryConnector"
"""
Defines the Kubernetes custom resource kind for active directory connectors
"""
AD_CONNECTOR_RESOURCE_KIND_PLURAL = "activedirectoryconnectors"
"""
Defines the plural name for active directory connectors
"""
AD_CONNECTOR_API_GROUP = "arcdata.microsoft.com"
"""
The Kubernetes group for AD connector
"""
AD_CONNECTOR_API_VERSION = ARC_API_V1
"""
The Kubernetes version for AD connector resources.
"""
ACCOUNT_PROVISIONING_MODE_MANUAL = "manual"
"""
Value indicating that the AD service account will be provisioned manually
"""
ACCOUNT_PROVISIONING_MODE_AUTOMATIC = "automatic"
"""
Value indicating that the AD service account will be provisioned automatically
"""
BASE = os.path.dirname(os.path.realpath(__file__))
"""
Base directory
"""
TEMPLATE_DIR = os.path.join(BASE, "templates")
"""
Custom resource definition directory
"""
AD_CONNECTOR_SPEC = os.path.join(TEMPLATE_DIR, "ad_connector_spec.json")
"""
File location for the Active Directory spec.
"""
