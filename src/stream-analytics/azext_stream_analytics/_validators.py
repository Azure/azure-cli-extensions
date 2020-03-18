# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def validate_streaming_job_start(namespace):
    from knack.util import CLIError
    if namespace.output_start_mode == 'CustomTime' and namespace.output_start_time is None:
        raise CLIError('usage error: --output-start-time is required when --output-start-mode is CustomTime')
