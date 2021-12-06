# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access

import argparse
from azure.cli.core.azclierror import InvalidArgumentValueError
from .vendored_sdks.v2021_11_01_preview.models import KustomizationDefinition, DependsOnDefinition
from .validators import validate_kustomization
from . import consts
from .utils import parse_dependencies, parse_duration


class InternalKustomizationDefinition(KustomizationDefinition):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', "")
        super().__init__(**kwargs)

    def to_KustomizationDefinition(self):
        k_dict = dict(self.__dict__)
        del k_dict['name']
        del k_dict['additional_properties']
        return KustomizationDefinition(**k_dict)


class KustomizationAddAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        validate_kustomization(values)
        model_dependency = []
        sync_interval = None
        retry_interval = None
        timeout = None
        kwargs = {}
        for item in values:
            try:
                key, value = item.split('=', 1)
                if key in consts.DEPENDENCY_KEYS:
                    dependencies = parse_dependencies(value)
                    for dep in dependencies:
                        model_dependency.append(
                            DependsOnDefinition(
                                kustomization_name=dep
                            )
                        )
                elif key in consts.SYNC_INTERVAL_KEYS:
                    sync_interval = value
                elif key in consts.RETRY_INTERVAL_KEYS:
                    retry_interval = value
                elif key in consts.TIMEOUT_KEYS:
                    timeout = value
                else:
                    kwargs[key] = value
            except ValueError as ex:
                raise InvalidArgumentValueError('usage error: {} KEY=VALUE [KEY=VALUE ...]'
                                                .format(option_string)) from ex
        super().__call__(
            parser,
            namespace,
            InternalKustomizationDefinition(
                depends_on=model_dependency,
                sync_interval_in_seconds=parse_duration(sync_interval),
                retry_interval_in_seconds=parse_duration(retry_interval),
                timeout_in_seconds=parse_duration(timeout),
                **kwargs
            ),
            option_string
        )
