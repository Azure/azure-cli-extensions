# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import List, Tuple

LEGAL_TERMS = '''
LEGAL TERMS

Azure VMware Solution ("AVS") is an Azure Service licensed to you as part of your Azure subscription and subject to the terms and conditions of the agreement under which you obtained your Azure subscription (https://azure.microsoft.com/support/legal/). The following additional terms also apply to your use of AVS:

DATA RETENTION. AVS does not currently support retention or extraction of data stored in AVS Clusters. Once an AVS Cluster is deleted, the data cannot be recovered as it terminates all running workloads, components, and destroys all Cluster data and configuration settings, including public IP addresses.

PROFESSIONAL SERVICES DATA TRANSFER TO VMWARE. In the event that you contact Microsoft for technical support relating to Azure VMware Solution and Microsoft must engage VMware for assistance with the issue, Microsoft will transfer the Professional Services Data and the Personal Data contained in the support case to VMware. The transfer is made subject to the terms of the Support Transfer Agreement between VMware and Microsoft, which establishes Microsoft and VMware as independent processors of the Professional Services Data. Before any transfer of Professional Services Data to VMware will occur, Microsoft will obtain and record consent from you for the transfer.

VMWARE DATA PROCESSING AGREEMENT. Once Professional Services Data is transferred to VMware (pursuant to the above section), the processing of Professional Services Data, including the Personal Data contained the support case, by VMware as an independent processor will be governed by the VMware Data Processing Agreement for Microsoft AVS Customers Transferred for L3 Support (the "VMware Data Processing Agreement") between you and VMware (located at https://www.vmware.com/content/dam/digitalmarketing/vmware/en/pdf/privacy/vmware-data-processing-agreement.pdf). You also give authorization to allow your representative(s) who request technical support for Azure VMware Solution to provide consent on your behalf to Microsoft for the transfer of the Professional Services Data to VMware.

ACCEPTANCE OF LEGAL TERMS. By continuing, you agree to the above additional Legal Terms for AVS. If you are an individual accepting these terms on behalf of an entity, you also represent that you have the legal authority to enter into these additional terms on that entity's behalf.
'''

ROTATE_VCENTER_PASSWORD_TERMS = '''
Any services connected using these credentials will stop working and may cause you to be locked out of your account.

Check if you're using your cloudadmin credentials for any connected services like backup and disaster recovery appliances, VMware HCX, or any vRealize suite products. Verify you're not using cloudadmin credentials for connected services before generating a new password.

If you are using cloudadmin for connected services, learn how you can setup a connection to an external identity source to create and manage new credentials for your connected services: https://docs.microsoft.com/en-us/azure/azure-vmware/configure-identity-source-vcenter

Press Y to confirm no services are using my cloudadmin credentials to connect to vCenter
'''

ROTATE_NSXT_PASSWORD_TERMS = '''
Currently, rotating your NSX-T managed admin credentials isn’t supported.  If you need to rotate your NSX-T manager admin credentials, please submit a support request in the Azure Portal: https://portal.azure.com/#create/Microsoft.Support

Press any key to continue
'''


def privatecloud_listadmincredentials(cmd, resource_group_name, private_cloud):
    from .aaz.latest.vmware.private_cloud import ListAdminCredentials
    return ListAdminCredentials(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "private_cloud": private_cloud
    })


def privatecloud_addidentitysource(cmd, resource_group_name, name, private_cloud, alias, domain, base_user_dn, base_group_dn, primary_server, username, password, secondary_server=None, ssl="Disabled"):
    from .aaz.latest.vmware.private_cloud.identity_source import Create
    command_args = {
        "private_cloud": private_cloud,
        "resource_group": resource_group_name,
        "name": name,
        "alias": alias,
        "domain": domain,
        "base_user_dn": base_user_dn,
        "base_group_dn": base_group_dn,
        "primary_server": primary_server,
        "username": username,
        "password": password,
        "ssl": ssl,
    }
    if secondary_server is not None:
        command_args["secondary_server"] = secondary_server
    return Create(cli_ctx=cmd.cli_ctx)(command_args=command_args)


def privatecloud_deleteidentitysource(cmd, resource_group_name, name, private_cloud, alias, domain, yes=False):
    from .aaz.latest.vmware.private_cloud.identity_source import Delete
    from knack.prompting import prompt_y_n
    msg = 'This will delete the identity source. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return Delete(cli_ctx=cmd.cli_ctx)(command_args={
        "private_cloud": private_cloud,
        "resource_group": resource_group_name,
        "name": name,
    })


def privatecloud_addcmkencryption(cmd, resource_group_name, private_cloud, enc_kv_key_name=None, enc_kv_key_version=None, enc_kv_url=None):
    from .operations.private_cloud import PrivateCloudUpdate
    return PrivateCloudUpdate(cli_ctx=cmd.cli_ctx)(command_args={
        "private_cloud_name": private_cloud,
        "resource_group": resource_group_name,
        "encryption": {
            "status": "Enabled",
            "key_vault_properties": {
                "key_name": enc_kv_key_name,
                "key_version": enc_kv_key_version,
                "key_vault_url": enc_kv_url
            }
        }
    })


def privatecloud_deletecmkenryption(cmd, resource_group_name, private_cloud, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the managed keys encryption. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    from .operations.private_cloud import PrivateCloudUpdate
    return PrivateCloudUpdate(cli_ctx=cmd.cli_ctx)(command_args={
        "private_cloud_name": private_cloud,
        "resource_group": resource_group_name,
        "encryption": {
            "status": "Disabled",
        }
    })


def check_quota_availability(cmd, location):
    from .aaz.latest.vmware.location import CheckQuotaAvailability
    return CheckQuotaAvailability(cli_ctx=cmd.cli_ctx)(command_args={
        "location": location
    })


def check_trial_availability(cmd, location, sku=None):
    from .aaz.latest.vmware.location import CheckTrialAvailability
    return CheckTrialAvailability(cli_ctx=cmd.cli_ctx)(command_args={
        "location": location,
        "sku": sku
    })


def privatecloud_identity_assign(cmd, resource_group_name, private_cloud, system_assigned=False):
    from .operations.private_cloud import PrivateCloudUpdate
    if system_assigned:
        return PrivateCloudUpdate(cli_ctx=cmd.cli_ctx)(command_args={
            "private_cloud_name": private_cloud,
            "resource_group": resource_group_name,
            "identity": {
                "type": "SystemAssigned",
            }
        })


def privatecloud_identity_remove(cmd, resource_group_name, private_cloud, system_assigned=False):
    from .operations.private_cloud import PrivateCloudUpdate
    if system_assigned:
        return PrivateCloudUpdate(cli_ctx=cmd.cli_ctx)(command_args={
            "private_cloud_name": private_cloud,
            "resource_group": resource_group_name,
            "identity": {
                "type": "None",
            }
        })


def privatecloud_identity_get(cmd, resource_group_name, private_cloud):
    from .aaz.latest.vmware.private_cloud import Show
    return Show(cli_ctx=cmd.cli_ctx)(command_args={
        "private_cloud_name": private_cloud,
        "resource_group": resource_group_name,
    }).get("identity")


def privatecloud_rotate_nsxt_password():
    from knack.prompting import prompt
    msg = ROTATE_NSXT_PASSWORD_TERMS
    prompt(msg)
    # return client.private_clouds.begin_rotate_nsxt_password(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def datastore_create():
    print('Please use "az vmware datastore netapp-volume create" or "az vmware datastore disk-pool-volume create" instead.')


def script_execution_create(cmd, resource_group_name, private_cloud, name, timeout, script_cmdlet_id=None, parameters=None, hidden_parameters=None, failure_reason=None, retention=None, out=None, named_outputs: List[Tuple[str, str]] = None):
    from .aaz.latest.vmware.script_execution import Create
    if named_outputs is not None:
        named_outputs = dict(named_outputs)
    return Create(cli_ctx=cmd.cli_ctx)(command_args={
        "private_cloud": private_cloud,
        "resource_group": resource_group_name,
        "script_execution_name": name,
        "timeout": timeout,
        "script_cmdlet_id": script_cmdlet_id,
        "parameters": parameters,
        "hidden_parameters": hidden_parameters,
        "failure_reason": failure_reason,
        "retention": retention,
        "output": out,
        "named_outputs": named_outputs,
    })
