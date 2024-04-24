# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from .vendored_sdks.appplatform.v2024_05_01_preview import models
from azure.cli.core.azclierror import ArgumentUsageError
from ._utils import convert_argument_to_parameter_list

import shlex


class BaseSource:
    def fulfilled_options_from_original_source_info(self, **_):
        return {}

    def validate_source(self, **_):
        pass


class JarSource(BaseSource):
    def validate_source(self, **kwargs):
        invalid_input = {k: v for k, v in kwargs.items() if k in ['main_entry', 'target_module'] and v is not None}
        if any(invalid_input):
            invalid_input_str = convert_argument_to_parameter_list(invalid_input.keys())
            runtime_version = kwargs.get('runtime_version') or kwargs.get('deployment_resource').properties.source.runtime_version
            raise ArgumentUsageError('{} cannot be set when --runtime-version is {}.'
                                     .format(invalid_input_str, runtime_version))

    def format_source(self, deployable_path=None, runtime_version=None, version=None, jvm_options=None, **_):
        if all(x is None for x in [deployable_path, runtime_version, version, jvm_options]):
            return
        return models.JarUploadedUserSourceInfo(
            relative_path=deployable_path,
            jvm_options=jvm_options,
            runtime_version=runtime_version or 'Java_11',
            version=version
        )

    def fulfilled_options_from_original_source_info(self, deployment_resource,
                                                    jvm_options=None, runtime_version=None, **_):
        if all(x is None for x in [jvm_options, runtime_version]):
            return {}
        original_source = deployment_resource.properties.source
        return {
            'jvm_options': jvm_options if jvm_options is not None else original_source.jvm_options,
            'runtime_version': runtime_version or original_source.runtime_version,
            'version': original_source.version,
            'deployable_path': original_source.relative_path
        }


class WarSource(BaseSource):
    def validate_source(self, **kwargs):
        invalid_input = {k: v for k, v in kwargs.items() if k in ['main_entry', 'target_module'] and v is not None}
        if any(invalid_input):
            invalid_input_str = convert_argument_to_parameter_list(invalid_input.keys())
            runtime_version = kwargs.get('runtime_version') or kwargs.get('deployment_resource').properties.source.runtime_version
            raise ArgumentUsageError('{} cannot be set when --runtime-version is {}.'
                                     .format(invalid_input_str, runtime_version))

    def format_source(self, deployable_path=None, runtime_version=None, server_version=None, version=None, jvm_options=None, **_):
        if all(x is None for x in [deployable_path, runtime_version, server_version, version, jvm_options]):
            return
        return models.WarUploadedUserSourceInfo(
            relative_path=deployable_path,
            jvm_options=jvm_options,
            runtime_version=runtime_version or 'Java_11',
            server_version=server_version or 'Tomcat_9',
            version=version
        )

    def fulfilled_options_from_original_source_info(self, deployment_resource,
                                                    jvm_options=None, runtime_version=None, server_version=None, **_):
        if all(x is None for x in [jvm_options, runtime_version]):
            return {}
        original_source = deployment_resource.properties.source
        return {
            'jvm_options': jvm_options if jvm_options is not None else original_source.jvm_options,
            'runtime_version': runtime_version or original_source.runtime_version,
            'server_version': server_version or original_source.server_version,
            'version': original_source.version,
            'deployable_path': original_source.relative_path
        }


class NetCoreZipSource(BaseSource):
    def validate_source(self, **kwargs):
        invalid_input = {k: v for k, v in kwargs.items() if k in ['jvm_options'] and v is not None}
        if any(invalid_input):
            invalid_input_str = convert_argument_to_parameter_list(invalid_input.keys())
            runtime_version = kwargs.get('runtime_version') or kwargs.get('deployment_resource').properties.source.runtime_version
            raise ArgumentUsageError('{} cannot be set when --runtime-version is {}.'
                                     .format(invalid_input_str, runtime_version))

    def format_source(self, deployable_path=None, main_entry=None, version=None, runtime_version=None, **_):
        if all(x is None for x in [deployable_path, main_entry, version]):
            return None
        return models.NetCoreZipUploadedUserSourceInfo(
            relative_path=deployable_path,
            net_core_main_entry_path=main_entry,
            runtime_version=runtime_version or 'NetCore_31',
            version=version
        )

    def fulfilled_options_from_original_source_info(self, deployment_resource,
                                                    main_entry=None, runtime_version=None, **_):
        if all(x is None for x in [main_entry, runtime_version]):
            return {}
        original_source = deployment_resource.properties.source
        return {
            'main_entry': main_entry or original_source.net_core_main_entry_path,
            'runtime_version': runtime_version or original_source.runtime_version,
            'version': original_source.version,
            'deployable_path': original_source.relative_path
        }


class CustomContainerSource(BaseSource):
    def validate_source(self, **kwargs):
        invalid_input = {k: v for k, v in kwargs.items() if k in ['jvm_options', 'main_entry', 'target_module'] and v is not None}
        if any(invalid_input):
            invalid_input_str = convert_argument_to_parameter_list(invalid_input.keys())
            raise ArgumentUsageError('{} cannot be set when --container-image is set.'
                                     .format(invalid_input_str))

    def format_source(self, version=None, **kwargs):
        container = self._format_container(**kwargs)
        if all(x is None for x in [container, version]):
            return None
        return models.CustomContainerUserSourceInfo(
            custom_container=container,
            version=version
        )

    def _format_container(self, container_registry=None, container_image=None,
                          container_command=None, container_args=None,
                          registry_username=None, registry_password=None, language_framework=None, **_):
        if all(x is None for x in [container_image,
                                   container_command, container_args,
                                   registry_username, registry_password]):
            return None
        if container_command is not None:
            container_command = shlex.split(container_command)
        if container_args is not None:
            container_args = shlex.split(container_args)
        credential = models.ImageRegistryCredential(
            username=registry_username,
            password=registry_password      # [SuppressMessage("Microsoft.Security", "CS001:SecretInline", Justification="false positive")]
        ) if registry_username or registry_password else None
        return models.CustomContainer(
            server=container_registry,
            container_image=container_image,
            command=container_command,
            args=container_args,
            image_registry_credential=credential,
            language_framework=language_framework
        )


class BuildResult(BaseSource):
    def format_source(self, deployable_path=None, version=None, **_):
        if all(x is None for x in [deployable_path, version]):
            return None
        return models.BuildResultUserSourceInfo(
            build_result_id=deployable_path,
            version=version
        )


class SourceBuild(BaseSource):
    def validate_source(self, **kwargs):
        invalid_input = {k: v for k, v in kwargs.items() if k in ['jvm_options', 'main_entry'] and v is not None}
        if any(invalid_input):
            invalid_input_str = convert_argument_to_parameter_list(invalid_input.keys())
            raise ArgumentUsageError('{} cannot be set when built from source.'
                                     .format(invalid_input_str))

    def format_source(self, deployable_path=None, target_module=None, runtime_version=None, version=None, **_):
        if all(x is None for x in [deployable_path, target_module, runtime_version, version]):
            return None
        return models.SourceUploadedUserSourceInfo(
            relative_path=deployable_path,
            version=version,
            artifact_selector=target_module,
            runtime_version=runtime_version
        )


def source_selector(source_type=None, **_):
    if source_type == 'Container':
        return CustomContainerSource()
    if source_type == 'Source':
        return SourceBuild()
    if source_type == 'NetCoreZip':
        return NetCoreZipSource()
    if source_type == 'BuildResult':
        return BuildResult()
    if source_type == 'War':
        return WarSource()
    return JarSource()
