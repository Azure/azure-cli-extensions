# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access,line-too-long

from knack.log import get_logger
from azure.cli.core.azclierror import ValidationError
from azure.cli.core.aaz import has_value
from azure.mgmt.core.tools import is_valid_resource_id, parse_resource_id
from .aaz.latest.netappfiles.volume import Create as _VolumeCreate, Update as _VolumeUpdate


logger = get_logger(__name__)


# def generate_tags(tag):
#     if tag is None:
#         return None

#     tags = {}
#     tag_list = tag.split(" ")
#     for tag_item in tag_list:
#         parts = tag_item.split("=", 1)
#         if len(parts) == 2:
#             # two parts, everything after first '=' is the tag's value
#             tags[parts[0]] = parts[1]
#         elif len(parts) == 1:
#             # one part, no tag value
#             tags[parts[0]] = ""
#     return tags

# def create_volume(cmd, client, account_name, pool_name, volume_name, resource_group_name, location, service_level, creation_token, usage_threshold, subnet_id, tag=None, export_policy=None):
#     rules = build_export_policy_rules(export_policy)
#     volume_export_policy = VolumePropertiesExportPolicy(rules=rules) if rules != [] else None

#     body = Volume(
#         usage_threshold=int(usage_threshold),
#         creation_token=creation_token,
#         service_level=service_level,
#         location=location,
#         subnet_id=subnet_id,
#         tags=generate_tags(tag),
#         export_policy=volume_export_policy)

#     return client.create_or_update(body, resource_group_name, account_name, pool_name, volume_name)

# region volume
class VolumeCreate(_VolumeCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZIntArgFormat, AAZBoolArg, AAZArgEnum
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.vnet = AAZStrArg(
            options=["--vnet"],
            arg_group="Properties",
            help="Name or Resource ID of the vnet. If you want to use a vnet in other resource group or subscription, please provide the Resource ID instead of the name of the vnet.",
            required=True,
        )

        # old export policy params, for backwards compatibility
        args_schema.rule_index = AAZStrArg(
            options=["--rule-index"],
            arg_group="ExportPolicy backwards compatibility",
            help="Order index. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False
        )
        args_schema.unix_read_only = AAZBoolArg(
            options=["--unix-read-only"],
            arg_group="ExportPolicy backwards compatibility",
            help="Read only access. Exists for backwards compatibility, please use --export-policy-rules (--rules) instead.",
            required=False
        )
        args_schema.unix_read_write = AAZBoolArg(
            options=["--unix-read-write"],
            arg_group="ExportPolicy backwards compatibility",
            help="Read and write access. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False
        )
        args_schema.cifs = AAZBoolArg(
            options=["--cifs"],
            arg_group="ExportPolicy backwards compatibility",
            help="Allows CIFS protocol. Enable only for CIFS type volumes. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False
        )
        args_schema.allowed_clients = AAZStrArg(
            options=["--allowed-clients"],
            arg_group="ExportPolicy backwards compatibility",
            help="Client ingress specification as comma separated string with IPv4 CIDRs, IPv4 host addresses and host names. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False
        )
        args_schema.kerberos5_read_only = AAZBoolArg(
            options=["--kerberos5-r"],
            arg_group="ExportPolicy backwards compatibility",
            help="Kerberos5 Read only access. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False
        )
        args_schema.kerberos5_read_write = AAZBoolArg(
            options=["--kerberos5-rw"],
            arg_group="ExportPolicy backwards compatibility",
            help="Kerberos5 Read and write access. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False
        )
        args_schema.kerberos5_i_read_only = AAZBoolArg(
            options=["--kerberos5i-r"],
            arg_group="ExportPolicy backwards compatibility",
            help="Kerberos5i Readonly access. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False
        )
        args_schema.kerberos5_i_read_write = AAZBoolArg(
            options=["--kerberos5i-rw"],
            arg_group="ExportPolicy backwards compatibility",
            help="Kerberos5i Read and write access. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False
        )
        args_schema.kerberos5_p_read_only = AAZBoolArg(
            options=["--kerberos5p-r"],
            arg_group="ExportPolicy backwards compatibility",
            help="Kerberos5p Readonly access. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False
        )
        args_schema.kerberos5_p_read_write = AAZBoolArg(
            options=["--kerberos5p-rw"],
            arg_group="ExportPolicy backwards compatibility",
            help="Kerberos5p Read and write access. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False
        )
        args_schema.has_root_access = AAZBoolArg(
            options=["--has-root-access"],
            arg_group="ExportPolicy backwards compatibility",
            help="Has root access to volume. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False
        )
        args_schema.chown_mode = AAZBoolArg(
            options=["--chown-mode"],
            arg_group="ExportPolicy backwards compatibility",
            help="This parameter specifies who is authorized to change the ownership of a file. restricted - Only root user can change the ownership of the file. unrestricted - Non-root users can change ownership of files that they own. Possible values include- Restricted, Unrestricted. Exists for backwards compatibility, please use --export-policy-rules --rules instead.",
            required=False,
            enum={"Restricted": "Restricted", "Unrestricted": "Unrestricted"}
        )

        args_schema.usage_threshold._fmt = AAZIntArgFormat(
            maximum=2457600,
            minimum=100,
        )

        # The API does only support setting Basic and Standard
        args_schema.network_features.enum = AAZArgEnum({"Basic": "Basic", "Standard": "Standard"}, case_sensitive=False)

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        # RP expects bytes but CLI allows integer TiBs for ease of use
        logger.debug("ANF-Extension log: usage_threshold: %s", args.usage_threshold)
        if args.usage_threshold is not None:
            gib_scale = 1024 * 1024 * 1024
            args.usage_threshold = int(args.usage_threshold.to_serialized_data()) * gib_scale

        # default the resource group of the subnet to the volume's rg unless the subnet is specified by id
        subnet = args.subnet_id
        subnet_rg = args.resource_group
        subs_id = self.ctx.subscription_id
        vnetArg = args.vnet.to_serialized_data()
        if not is_valid_resource_id(args.subnet_id.to_serialized_data()):
            if is_valid_resource_id(vnetArg):
                # determine vnet - supplied value can be name or ARM resource Id
                resource_parts = parse_resource_id(vnetArg)
                vnetArg = resource_parts['resource_name']
                subnet_rg = resource_parts['resource_group']
            args.subnet_id = f"/subscriptions/{subs_id}/resourceGroups/{subnet_rg}/providers/Microsoft.Network/virtualNetworks/{vnetArg}/subnets/{subnet}"

        # if NFSv4 is specified then the export policy must reflect this
        # the RP ordinarily only creates a default setting NFSv3.
        logger.debug("ANF-Extension log: ProtocolTypes rules len:%s", len(args.protocol_types))

        for protocol in args.protocol_types:
            logger.debug("ANF-Extension log: ProtocolType: %s", protocol)

        logger.debug("ANF-Extension log: exportPolicy rules len:%s", len(args.export_policy_rules))

        for rule in args.export_policy_rules:
            logger.debug("ANF-Extension log: rule: %s", rule)

        if (has_value(args.protocol_types) and any(x in ['NFSv3', 'NFSv4.1'] for x in args.protocol_types) and len(args.export_policy_rules) == 0)\
                and not ((len(args.protocol_types) == 1 and all(elem == "NFSv3" for elem in args.protocol_types)) and len(args.export_policy_rules) == 0):
            isNfs41 = False
            isNfs3 = False
            cifs = False

            if not has_value(args.rule_index):
                rule_index = 1
            else:
                rule_index = int(args.rule_index.to_serialized_data()) or 1
            if "NFSv4.1" in args.protocol_types:
                isNfs41 = True
                if not has_value(args.allowed_clients):
                    raise ValidationError("Parameter allowed-clients needs to be set when protocol-type is NFSv4.1")
            if "NFSv3" in args.protocol_types:
                isNfs3 = True
            if "CIFS" in args.protocol_types:
                cifs = True

            logger.debug("ANF log: Setting exportPolicy rule index: %s, isNfs3: %s, isNfs4: %s, cifs: %s", rule_index, isNfs3, isNfs41, cifs)

            logger.debug("ANF log: Before exportPolicy rule => : rule_index: %s, nfsv3: %s, nfsv4: %s, cifs: %s", args.export_policy_rules[0]["rule_index"], args.export_policy_rules[0]["nfsv3"], args.export_policy_rules[0]["nfsv41"], args.export_policy_rules[0]["cifs"])
            logger.debug("ANF log: args.rule_index %s,  rule_index: %s", args.rule_index, rule_index)
            args.export_policy_rules[0]["rule_index"] = rule_index
            args.export_policy_rules[0]["nfsv3"] = isNfs3
            args.export_policy_rules[0]["nfsv41"] = isNfs41
            args.export_policy_rules[0]["cifs"] = cifs
            args.export_policy_rules[0]["allowed_clients"] = args.allowed_clients
            args.export_policy_rules[0]["unix_read_only"] = args.unix_read_only
            args.export_policy_rules[0]["unix_read_write"] = args.unix_read_write
            args.export_policy_rules[0]["cifs"] = args.cifs
            args.export_policy_rules[0]["kerberos5_read_only"] = args.kerberos5_read_only
            args.export_policy_rules[0]["kerberos5_read_write"] = args.kerberos5_read_write
            args.export_policy_rules[0]["kerberos5i_read_only"] = args.kerberos5_i_read_only
            args.export_policy_rules[0]["kerberos5i_read_write"] = args.kerberos5_i_read_write
            args.export_policy_rules[0]["kerberos5p_read_only"] = args.kerberos5_p_read_only
            args.export_policy_rules[0]["kerberos5p_read_write"] = args.kerberos5_p_read_write
            args.export_policy_rules[0]["has_root_access"] = args.has_root_access
            args.export_policy_rules[0]["chown_mode"] = args.chown_mode

            logger.debug("ANF-Extension log: after exportPolicy rule => : %s, %s, %s, %s", args.export_policy_rules[0]["rule_index"], args.export_policy_rules[0]["nfsv3"], args.export_policy_rules[0]["nfsv41"], args.export_policy_rules[0]["cifs"])

        else:
            logger.debug("Don't create export policy")

# todo create export policy note no longer flatteneded

# check if flattening dataprotection works


class VolumeUpdate(_VolumeUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZIntArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.vnet = AAZStrArg(
            options=["--vnet"],
            arg_group="Properties",
            help="Name or Resource ID of the vnet. If you want to use a vnet in other resource group or subscription, please provide the Resource ID instead of the name of the vnet.",
            required=False,
        )
        args_schema.usage_threshold._fmt = AAZIntArgFormat(
            maximum=500,
            minimum=100,
        )

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        # RP expects bytes but CLI allows integer TiBs for ease of use
        logger.debug("ANF-Extension log: VolumeUpdate")
        logger.debug("ANF-Extension log: usage_threshold: %s", args.usage_threshold)
        if has_value(args.usage_threshold) and args.usage_threshold.to_serialized_data() is not None:
            gib_scale = 1024 * 1024 * 1024
            args.usage_threshold = int(args.usage_threshold.to_serialized_data()) * gib_scale

# endregion
