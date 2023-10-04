# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from knack.log import get_logger
from azure.cli.core.azclierror import ValidationError
from msrestazure.tools import is_valid_resource_id, parse_resource_id
from .aaz.latest.netappfiles.volume import Create as _VolumeCreate

logger = get_logger(__name__)


def generate_tags(tag):
    if tag is None:
        return None

    tags = {}
    tag_list = tag.split(" ")
    for tag_item in tag_list:
        parts = tag_item.split("=", 1)
        if len(parts) == 2:
            # two parts, everything after first '=' is the tag's value
            tags[parts[0]] = parts[1]
        elif len(parts) == 1:
            # one part, no tag value
            tags[parts[0]] = ""
    return tags

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
        from azure.cli.core.aaz import AAZStrArg, AAZIntArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        # args_schema.client_auth_config = AAZBoolArg(
        #     options=["--client-auth-configuration", "--client-auth-config"],
        #     help="Client authentication configuration of the application gateway resource.",
        # )
        # args_schema.trusted_client_certs = AAZListArg(
        #     options=["--trusted-client-certificates", "--trusted-client-cert"],
        #     help="Array of references to application gateway trusted client certificates.",
        # )
        # args_schema.trusted_client_certs.Element = AAZResourceIdArg(
        #     fmt=AAZResourceIdArgFormat(
        #         template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network"
        #                  "/applicationGateways/{gateway_name}/trustedClientCertificates/{}",
        #     ),
        # )
        #args_schema.auth_configuration._registered = False
        #args_schema.client_certificates._registered = False

        args_schema.vnet = AAZStrArg(
            options=["--vnet"],
            arg_group="Properties",
            help="Name or Resource ID of the vnet. If you want to use a vnet in other resource group or subscription, please provide the Resource ID instead of the name of the vnet.",
            required=True,
        )
        # args_schema.usage_threshold = AAZIntArg(
        #     options=["--usage-threshold"],
        #     arg_group="Properties",
        #     help="Maximum storage quota allowed for a file system in bytes. This is a soft quota used for alerting only. Minimum size is 100 GiB. Upper limit is 100TiB, 500Tib for LargeVolume. Specified in bytes.",
        #     required=True,
        #     default=100,
        #     fmt=AAZIntArgFormat(
        #         maximum=500,
        #         minimum=100,
        #     ),
        # )

        args_schema.usage_threshold.fmt = AAZIntArgFormat(
                maximum=500,
                minimum=100,
        )

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        # RP expects bytes but CLI allows integer TiBs for ease of use
        # gib_scale = 1024 * 1024 * 1024
        # tib_scale = gib_scale * 1024
        #args.usage_threshold = int(args.usage_threshold) * gib_scale
        # default the resource group of the subnet to the volume's rg unless the subnet is specified by id
        subnet_rg = args.resource_group
        subs_id = self.ctx.subscription_id
        vnetArg = args.vnet.to_serialized_data()
        # determine vnet - supplied value can be name or ARM resource Id
        if is_valid_resource_id(vnetArg):
            resource_parts = parse_resource_id(vnetArg)
            vnetArg = resource_parts['resource_name']
            subnet_rg = resource_parts['resource_group']

        # determine subnet - supplied value can be name or ARM resource Id
        if is_valid_resource_id(args.subnet_id.to_serialized_data()):
            resource_parts = parse_resource_id(args.subnet_id.to_serialized_data())
            subnet = resource_parts['resource_name']
            subnet_rg = resource_parts['resource_group']

        args.subnet_id = f"/subscriptions/{subs_id}/resourceGroups/{subnet_rg}/providers/Microsoft.Network/virtualNetworks/{vnetArg}/subnets/{subnet}"

        # if NFSv4 is specified then the export policy must reflect this
        # the RP ordinarily only creates a default setting NFSv3.
        logger.debug("ANF-Extension log: ProtocolTypes rules len:%s", len(args.protocol_types))

        for protocl in args.protocol_types:
            logger.debug("ANF-Extension log: ProtocolType: %s", protocl)

        logger.debug("ANF-Extension log: exportPolicy rules len:%s", len(args.rules))

        for rule in args.rules:
            logger.debug("ANF-Extension log: rule: %s", rule)

        if (args.protocol_types is not None and any(x in ['NFSv3', 'NFSv4.1'] for x in args.protocol_types) and len(args.rules) ==0)\
                and not ((len(args.protocol_types)==1 and all(elem =="NFSv3" for elem in args.protocol_types)) and len(args.rules) ==0):
            isNfs41 = False
            isNfs3 = False
            cifs=False
            if "NFSv4.1" in args.protocol_types:
                isNfs41 = True
                if args.rules["allowed_clients"] is None:
                    raise ValidationError("Parameter allowed-clients needs to be set when protocol-type is NFSv4.1")
                if rule_index is None:
                    raise ValidationError("Parameter rule-index needs to be set when protocol-type is NFSv4.1")
            if "NFSv3" in args.protocol_types:
                isNfs3 = True
            if "CIFS" in args.protocol_types:
                cifs = True

            rule_index = 1
            logger.debug("ANF-Extension log: Setting exportPolicy rule index: %s, %s, %s, %s", rule_index, isNfs3, isNfs41,cifs )

            args.rules[0]["rule_index"]=rule_index
            args.rules[0]["nfsv3"]=isNfs3
            args.rules[0]["nfsv41"]=isNfs41
            args.rules[0]["cifs"]=cifs
        else:
            logger.debug("Don't create export policy")

# todo create export policy note no longer flatteneded

## check if flattening dataprotection works

## from example keep for reference for now
        # if has_value(args.client_auth_config):
        #     args.auth_configuration.verify_client_cert_issuer_dn = args.client_auth_config
        # args.client_certificates = assign_aaz_list_arg(
        #     args.client_certificates,
        #     args.trusted_client_certs,
        #     element_transformer=lambda _, cert_id: {"id": cert_id}
        # )
# endregion
