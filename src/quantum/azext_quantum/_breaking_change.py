# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.breaking_change import register_argument_deprecate

register_argument_deprecate('quantum execute', '--location', target_version="May 2026")
register_argument_deprecate('quantum run', '--location', target_version="May 2026")
register_argument_deprecate('quantum job submit', '--location', target_version="May 2026")
register_argument_deprecate('quantum job cancel', '--location', target_version="May 2026")
register_argument_deprecate('quantum job list', '--location', target_version="May 2026")
register_argument_deprecate('quantum job output', '--location', target_version="May 2026")
register_argument_deprecate('quantum job show', '--location', target_version="May 2026")
register_argument_deprecate('quantum job wait', '--location', target_version="May 2026")
register_argument_deprecate('quantum target list', '--location', target_version="May 2026")
register_argument_deprecate('quantum workspace set', '--location', target_version="May 2026")
register_argument_deprecate('quantum workspace quotas', '--location', target_version="May 2026")
