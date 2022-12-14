from ..generated._client_factory import cf_devcenter_cl

#To do regional host name customization
#Get all projects from ARG - find dev_center from devCenterId property
#Take devcenterUri property from found project
def get_endpoint(cmd, dev_center):
    cf_controlplane = cf_devcenter_cl(cmd.cli_ctx)
    return ""