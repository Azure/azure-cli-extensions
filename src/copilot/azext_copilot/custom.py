# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from knack.util import CLIError
from .response_utils import process_prompt

logger = get_logger(__name__)

def create_copilot(cmd, prompt):
    payload = process_prompt(prompt)

    logger.warning(payload)


def list_copilot(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `copilot list`')


# def update_copilot(cmd, instance, tags=None):
#     with cmd.update_context(instance) as c:
#         c.set_param('tags', tags)
#     return instance