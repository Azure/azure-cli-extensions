# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines, disable=broad-except
from azext_aks_agent.agent.agent import aks_agent as aks_agent_internal

from knack.log import get_logger


logger = get_logger(__name__)


# pylint: disable=unused-argument
def aks_agent(
    cmd,
    prompt,
    model,
    max_steps,
    config_file,
    resource_group_name=None,
    name=None,
    api_key=None,
    no_interactive=False,
    no_echo_request=False,
    show_tool_output=False,
    refresh_toolsets=False,
):

    aks_agent_internal(
        cmd,
        resource_group_name,
        name,
        prompt,
        model,
        api_key,
        max_steps,
        config_file,
        no_interactive,
        no_echo_request,
        show_tool_output,
        refresh_toolsets,
    )
