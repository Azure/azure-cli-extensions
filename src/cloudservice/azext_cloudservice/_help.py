# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.help_files import helps

helps['cloud-service create'] = """
    type: command
    short-summary: "Create a cloud service (extended support). Please note some properties can be set only during cloud service creation."
    examples:
      - name: Create a cloud service with 2 roles, 2 load balancers (one has a public IP and another has a private IP), secrets and extensions.
        text: |-
               az cloud-service create -g ResourceGroup -n CloudService --roles ContosoFrontend:Standard_D1_v2:1:Standard ContosoBackend:Standard_D1_v2:1:Standard --package-url PackageURL --configuration Config --load-balancer-configurations MyLoadBalancer:MyFe:PublicIP:: MyLoadBalancer2:MyFe2::SubnetIDd:PrivateIPID --secrets Vault0:Cert0:Cert1 Vault1:Cert2:Cert3:Cert4 --extensions "@extensions.json"
"""
