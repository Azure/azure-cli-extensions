# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azext_automation.generated._client_factory import cf_automation_cl


def cf_automation_account(cli_ctx, *_):
    return cf_automation_cl(cli_ctx).automation_account


def cf_runbook_draft(cli_ctx, *_):
    return cf_automation_cl(cli_ctx).runbook_draft


def cf_job(cli_ctx, *_):
    return cf_automation_cl(cli_ctx).job
