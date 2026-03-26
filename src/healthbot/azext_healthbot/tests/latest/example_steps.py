# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


# EXAMPLE: /Bots/put/BotCreate
def step_create_with_sku(test, rg, sku, checks=None):
    if checks is None:
        checks = []
    test.cmd(f'az healthbot create '
             f'--name "{{myBot}}" '
             f'--location "eastus" '
             f'--sku "{sku}" '
             f'--resource-group "{{rg}}"',
             checks=checks)


# EXAMPLE: /Bots/get/List Bots by Resource Group
def step_list(test, rg, checks=None):
    if checks is None:
        checks = []
    test.cmd('az healthbot list '
             '--resource-group "{rg}"',
             checks=checks)


# EXAMPLE: /Bots/get/List Bots by Subscription
def step_list2(test, rg, checks=None):
    if checks is None:
        checks = []
    test.cmd('az healthbot list',
             checks=checks)


# EXAMPLE: /Bots/get/ResourceInfoGet
def step_show(test, rg, checks=None):
    if checks is None:
        checks = []
    test.cmd('az healthbot show '
             '--name "{myBot}" '
             '--resource-group "{rg}"',
             checks=checks)


# EXAMPLE: /Bots/patch/BotUpdate
def step_update_with_sku(test, rg, sku, checks=None):
    if checks is None:
        checks = []
    test.cmd(f'az healthbot update '
             f'--name "{{myBot}}" '
             f'--sku "{sku}" '
             f'--resource-group "{{rg}}"',
             checks=checks)


# EXAMPLE: /Bots/delete/BotDelete
def step_delete(test, rg, checks=None):
    if checks is None:
        checks = []
    test.cmd('az healthbot delete -y '
             '--name "{myBot}" '
             '--resource-group "{rg}"',
             checks=checks)


# Boundary value: update with tags only, no --sku (sku=None)
def step_update_tags_only(test, rg, checks=None):
    if checks is None:
        checks = []
    test.cmd('az healthbot update '
             '--name "{myBot}" '
             '--tags testkey=testvalue '
             '--resource-group "{rg}"',
             checks=checks)


# Boundary value: update with empty tags (tags='')
def step_update_empty_tags(test, rg, checks=None):
    if checks is None:
        checks = []
    test.cmd('az healthbot update '
             '--name "{myBot}" '
             '--tags '
             '--resource-group "{rg}"',
             checks=checks)


# Boundary value: create with empty bot name (bot_name='')
def step_create_empty_name(test, rg, checks=None):
    if checks is None:
        checks = []
    test.cmd('az healthbot create '
             '--name "" '
             '--location "eastus" '
             '--sku "F0" '
             '--resource-group "{rg}"',
             checks=checks,
             expect_failure=True)


# Boundary value: create with tags
def step_create_with_tags(test, rg, sku, checks=None):
    if checks is None:
        checks = []
    test.cmd(f'az healthbot create '
             f'--name "{{myBot}}" '
             f'--location "eastus" '
             f'--sku "{sku}" '
             f'--tags env=test '
             f'--resource-group "{{rg}}"',
             checks=checks)


# Boundary value: list with empty resource group (boundary: empty string)
def step_list_empty_rg(test, rg, checks=None):
    if checks is None:
        checks = []
    test.cmd('az healthbot list '
             '-g ""',
             checks=checks)


# Wait for provisioning to complete
def step_wait_for_provisioned(test, rg):
    test.cmd('az healthbot wait '
             '--name "{myBot}" '
             '--resource-group "{rg}" '
             '--updated')


# Boundary value: delete with --no-wait (no_wait=True)
def step_delete_no_wait(test, rg, checks=None):
    if checks is None:
        checks = []
    test.cmd('az healthbot delete -y '
             '--name "{myBot}" '
             '--resource-group "{rg}" '
             '--no-wait',
             checks=checks)
