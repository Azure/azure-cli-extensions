# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import math
import os
import re
from pathlib import Path
from unittest.mock import patch
from uuid import UUID


CONFIG_DIR = Path(__file__).parent


def _merge(settings, overrides):
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(settings.get(key), dict):
            _merge(settings[key], value)
        else:
            settings[key] = value


def load_test_config():
    with (CONFIG_DIR / 'config.json').open(encoding='utf-8') as stream:
        settings = json.load(stream)
    override_path = os.environ.get('AZURE_CDN_TEST_CONFIG')
    local_path = Path(override_path) if override_path else CONFIG_DIR / 'config.local.json'
    if override_path or local_path.exists():
        with local_path.open(encoding='utf-8') as stream:
            _merge(settings, json.load(stream))
    for key in ('subscription_id', 'cloud', 'arm_endpoint'):
        value = os.environ.get('AZURE_CDN_TEST_' + key.upper())
        if value:
            settings[key] = value
    return settings


def fixture(name, playback_subscription=None):
    value = load_test_config()['fixtures'][name]
    if playback_subscription is not None:
        value = re.sub(r'^/subscriptions/[^/]+', '/subscriptions/' + playback_subscription,
                       value, flags=re.IGNORECASE)
    return value


def timeout_settings(mode):
    values = load_test_config()['timeouts'][mode]
    for name in ('case_seconds', 'suite_seconds'):
        value = values[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f'{mode}.{name} must be a positive, finite number')
    return values


def configure_test_environment(scenario):
    if not scenario.in_recording:
        return

    from azure.cli.core._profile import Profile

    settings = load_test_config()
    subscription_fixture = getattr(scenario, 'subscription_fixture_by_test', {}).get(
        getattr(scenario, '_testMethodName', None))
    if subscription_fixture:
        settings['subscription_id'] = settings['fixtures'][subscription_fixture].split('/')[2]
    subscription = str(UUID(settings['subscription_id']))
    original = Profile.load_cached_subscriptions

    def selected_subscriptions(profile, all_clouds=False):
        if (profile.cli_ctx.cloud.name != settings['cloud'] or
                profile.cli_ctx.cloud.endpoints.resource_manager.rstrip('/') != settings['arm_endpoint'].rstrip('/')):
            raise ValueError('The Azure CLI cloud does not match the configured CDN test environment')
        subscriptions = copy.deepcopy(original(profile, all_clouds=all_clouds))
        if not any(item['id'].lower() == subscription for item in subscriptions):
            raise ValueError('The configured CDN test subscription is absent from the Azure CLI account cache')
        for item in subscriptions:
            item['isDefault'] = item['id'].lower() == subscription
        return subscriptions

    patcher = patch.object(Profile, 'load_cached_subscriptions', selected_subscriptions)
    patcher.start()
    scenario.addCleanup(patcher.stop)
    Profile(cli_ctx=scenario.cli_ctx).load_cached_subscriptions()
