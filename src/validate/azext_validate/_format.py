# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def transform_table(result):
    rows = []
    for r in result.get('results', []):
        errors = r.get('errors') or []
        rows.append({
            'Index': r.get('index'),
            'Line': r.get('line'),
            'Status': r.get('status'),
            'Command': r.get('commandName') or '',
            'Problem': errors[0]['code'] if errors else ((r.get('reason') or {}).get('code') or ''),
        })
    return rows
