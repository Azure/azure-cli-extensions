from azure.cli.core.commands.parameters import Completer


# def get_test_id_completion_list():

#     @Completer
#     def completer(cmd, prefix, namespace, **kwargs):  # pylint: disable=unused-argument
#         load_test_resource = getattr(namespace, 'load_test_resource', None)
#         resource_group = getattr(namespace, 'resource_group', None)
        
#             return [r.name for r in get_resources_in_resource_group(cmd.cli_ctx, rg, resource_type=resource_type)]
#         return [r.name for r in get_resources_in_subscription(cmd.cli_ctx, resource_type)]

#     return completer