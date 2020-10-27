# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from importlib import import_module

'''
Since the method get_models()/get_sdk() in azure-cli-core is bound to resourceType, the method _sdk_get_versioned_sdk() will be called, so only the multi-api SDK is supported.
If we add a version directory to the path of the SDK folder, because there is no required client (specific to the multiple version SDK) outside of the version directory, the client_factory will have a load problem.
So write a separate method to load the model.
'''


def get_model(sdk_path, mod_attr_path, checked=True):
    try:
        attr_mod, attr_path = mod_attr_path.split('#') \
            if '#' in mod_attr_path else (mod_attr_path, '')
        full_mod_path = '{}.{}'.format(sdk_path, attr_mod) if attr_mod else sdk_path
        op = import_module(full_mod_path)
        if attr_path:
            # Only load attributes if needed
            for part in attr_path.split('.'):
                op = getattr(op, part)
        return op
    except (ImportError, AttributeError) as ex:
        if checked:
            return None
        raise ex
