# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

DEFAULT_MOCK_ALIAS_STRING = '''
[mn]
command = monitor

[diag]
command = diagnostic-settings create

[ac]
command = account

[ls]
command = list -otable

[create-grp]
command = group create -n test --tags tag1=$tag1 tag2=$tag2 tag3=$non-existing-env-var

[create-vm]
command = vm create -g test-group -n test-vm

[pos-arg-1 {{ 0 }} {{ 1 }}]
command = iot {{ 0 }}test {{ 1 }}test

[pos-arg-2 {{ 0 }} {{ arg_1 }}]
command = sf {{ 0 }} {{ 0 }} {{ arg_1 }} {{ arg_1 }}

[pos-arg-json {{ 0 }}]
command = test --json {{ 0 }}

[cp {{ arg_1 }} {{ arg_2 }}]
command = storage blob copy start-batch --source-uri {{ arg_1 }} --destination-container {{ arg_2 }}

[ac-ls]
command = ac ls

[-h]
command = account

[storage-connect {{ arg_1 }} {{ arg_2 }}]
command = az storage account connection-string -g {{ arg_1 }} -n {{ arg_2 }} -otsv

[storage-ls {{ arg_1 }}]
command = storage blob list --account-name {{ arg_1.split(".")[0] }} --container-name {{ arg_1.split("/")[1] }}

[storage-ls-2 {{ arg_1 }}]
command = storage blob list --account-name {{ arg_1.replace('https://', '').split('.')[0] }} --container-name {{ arg_1.replace("https://", "").split("/")[1] }}
'''

COLLISION_MOCK_ALIAS_STRING = '''
[account]
command = monitor

[list-locations]
command = diagnostic-settings create

[dns]
command = network dns
'''

DUP_SECTION_MOCK_ALIAS_STRING = '''
[mn]
command = monitor

[mn]
command = account
'''

DUP_OPTION_MOCK_ALIAS_STRING = '''
[mn]
command = monitor
command = account
'''

MALFORMED_MOCK_ALIAS_STRING = '''
[mn]
command = monitor

aodfgojadofgjaojdfog
'''

TEST_RESERVED_COMMANDS = ['account list-locations',
                          'network dns',
                          'storage account']
