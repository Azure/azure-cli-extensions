# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-positional-arguments

import json

from azure.cli.core.util import sdk_no_wait
from azure.mgmt.cloudhealth import models as ch_models


# ── helpers ───────────────────────────────────────────────────────────

def _parse_json(text):
    """Parse a JSON string, returning a dict."""
    if text is None:
        return None
    if isinstance(text, dict):
        return text
    return json.loads(text)


def _parse_datetime(value):
    """Parse ISO 8601 string to datetime if not None."""
    if value is None:
        return None
    from datetime import datetime  # pylint: disable=import-outside-toplevel
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


# ── health-model ──────────────────────────────────────────────────────

def health_model_create(client, resource_group_name, health_model_name,
                        location, tags=None, identity_type=None, no_wait=False):
    resource = ch_models.HealthModel(location=location, tags=tags)
    if identity_type:
        resource.identity = ch_models.ManagedServiceIdentity(type=identity_type)
    return sdk_no_wait(no_wait, client.begin_create,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       resource=resource)


def health_model_show(client, resource_group_name, health_model_name):
    return client.get(resource_group_name=resource_group_name,
                      health_model_name=health_model_name)


def health_model_list(client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def health_model_update(client, resource_group_name, health_model_name,
                        tags=None, identity_type=None, no_wait=False):
    props = ch_models.HealthModelUpdate(tags=tags)
    if identity_type:
        props.identity = ch_models.ManagedServiceIdentity(type=identity_type)
    return sdk_no_wait(no_wait, client.begin_update,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       properties=props)


def health_model_delete(client, resource_group_name, health_model_name, no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name)


# ── entity ────────────────────────────────────────────────────────────

def entity_create(client, resource_group_name, health_model_name, entity_name,
                  display_name=None, impact=None, health_objective=None,
                  icon_name=None, canvas_x=None, canvas_y=None,
                  tags=None, no_wait=False):
    props = ch_models.EntityProperties(
        display_name=display_name,
        impact=impact,
        health_objective=health_objective,
        tags=tags,
    )
    if icon_name:
        props.icon = ch_models.IconDefinition(icon_name=icon_name)
    if canvas_x is not None and canvas_y is not None:
        props.canvas_position = ch_models.EntityCoordinates(x=canvas_x, y=canvas_y)
    resource = ch_models.Entity(properties=props)
    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       entity_name=entity_name,
                       resource=resource)


def entity_show(client, resource_group_name, health_model_name, entity_name):
    return client.get(resource_group_name=resource_group_name,
                      health_model_name=health_model_name,
                      entity_name=entity_name)


def entity_list(client, resource_group_name, health_model_name):
    return client.list_by_health_model(resource_group_name=resource_group_name,
                                       health_model_name=health_model_name)


def entity_delete(client, resource_group_name, health_model_name, entity_name,
                  no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       entity_name=entity_name)


def entity_get_history(client, resource_group_name, health_model_name, entity_name,
                       start_at=None, end_at=None):
    body = ch_models.EntityHistoryRequest(
        start_at=_parse_datetime(start_at),
        end_at=_parse_datetime(end_at),
    )
    return client.get_history(resource_group_name=resource_group_name,
                              health_model_name=health_model_name,
                              entity_name=entity_name,
                              body=body)


def entity_get_signal_history(client, resource_group_name, health_model_name, entity_name,
                              signal_name, start_at=None, end_at=None):
    body = ch_models.SignalHistoryRequest(
        signal_name=signal_name,
        start_at=_parse_datetime(start_at),
        end_at=_parse_datetime(end_at),
    )
    return client.get_signal_history(resource_group_name=resource_group_name,
                                     health_model_name=health_model_name,
                                     entity_name=entity_name,
                                     body=body)


def entity_ingest(client, resource_group_name, health_model_name, entity_name,
                  signal_name, health_state, value=None,
                  expires_in_minutes=None, additional_context=None):
    body = ch_models.HealthReportRequest(
        signal_name=signal_name,
        health_state=health_state,
        value=value,
        expires_in_minutes=expires_in_minutes,
        additional_context=additional_context,
    )
    return client.ingest_health_report(resource_group_name=resource_group_name,
                                       health_model_name=health_model_name,
                                       entity_name=entity_name,
                                       body=body)


# ── signal-definition ─────────────────────────────────────────────────

def signal_definition_create(client, resource_group_name, health_model_name,
                             signal_definition_name, body,
                             signal_kind=None, display_name=None,
                             refresh_interval=None, data_unit=None,
                             no_wait=False):
    # Accept full JSON body for complex polymorphic signal definitions
    resource_dict = _parse_json(body)
    if resource_dict is not None:
        resource = {"properties": resource_dict}
    else:
        resource = {"properties": {
            "signalKind": signal_kind,
            "displayName": display_name,
            "refreshInterval": refresh_interval,
            "dataUnit": data_unit,
        }}
    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       signal_definition_name=signal_definition_name,
                       resource=resource)


def signal_definition_show(client, resource_group_name, health_model_name,
                           signal_definition_name):
    return client.get(resource_group_name=resource_group_name,
                      health_model_name=health_model_name,
                      signal_definition_name=signal_definition_name)


def signal_definition_list(client, resource_group_name, health_model_name):
    return client.list_by_health_model(resource_group_name=resource_group_name,
                                       health_model_name=health_model_name)


def signal_definition_delete(client, resource_group_name, health_model_name,
                             signal_definition_name, no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       signal_definition_name=signal_definition_name)


# ── relationship ──────────────────────────────────────────────────────

def relationship_create(client, resource_group_name, health_model_name,
                        relationship_name, parent_entity_name, child_entity_name,
                        display_name=None, tags=None, no_wait=False):
    resource = ch_models.Relationship(
        properties=ch_models.RelationshipProperties(
            parent_entity_name=parent_entity_name,
            child_entity_name=child_entity_name,
            display_name=display_name,
            tags=tags,
        )
    )
    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       relationship_name=relationship_name,
                       resource=resource)


def relationship_show(client, resource_group_name, health_model_name,
                      relationship_name):
    return client.get(resource_group_name=resource_group_name,
                      health_model_name=health_model_name,
                      relationship_name=relationship_name)


def relationship_list(client, resource_group_name, health_model_name):
    return client.list_by_health_model(resource_group_name=resource_group_name,
                                       health_model_name=health_model_name)


def relationship_delete(client, resource_group_name, health_model_name,
                        relationship_name, no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       relationship_name=relationship_name)


# ── auth-setting ──────────────────────────────────────────────────────

def auth_setting_create(client, resource_group_name, health_model_name,
                        authentication_setting_name,
                        authentication_kind, managed_identity_name,
                        display_name=None, no_wait=False):
    if authentication_kind == 'ManagedIdentity':
        props = ch_models.ManagedIdentityAuthenticationSettingProperties(
            managed_identity_name=managed_identity_name,
            display_name=display_name,
        )
    else:
        from knack.util import CLIError
        raise CLIError(f"Unsupported authentication kind: {authentication_kind}. "
                       "Supported: ManagedIdentity.")
    resource = ch_models.AuthenticationSetting(properties=props)
    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       authentication_setting_name=authentication_setting_name,
                       resource=resource)


def auth_setting_show(client, resource_group_name, health_model_name,
                      authentication_setting_name):
    return client.get(resource_group_name=resource_group_name,
                      health_model_name=health_model_name,
                      authentication_setting_name=authentication_setting_name)


def auth_setting_list(client, resource_group_name, health_model_name):
    return client.list_by_health_model(resource_group_name=resource_group_name,
                                       health_model_name=health_model_name)


def auth_setting_delete(client, resource_group_name, health_model_name,
                        authentication_setting_name, no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       authentication_setting_name=authentication_setting_name)


# ── discovery-rule ────────────────────────────────────────────────────

def discovery_rule_create(client, resource_group_name, health_model_name,
                          discovery_rule_name,
                          authentication_setting, discover_relationships,
                          add_recommended_signals, specification_kind,
                          resource_graph_query=None,
                          display_name=None, no_wait=False):
    if specification_kind == 'ResourceGraphQuery':
        specification = ch_models.ResourceGraphQuerySpecification(
            resource_graph_query=resource_graph_query,
        )
    elif specification_kind == 'ApplicationInsightsTopology':
        specification = ch_models.ApplicationInsightsTopologySpecification()
    else:
        from knack.util import CLIError
        raise CLIError(f"Unsupported specification kind: {specification_kind}. "
                       "Supported: ResourceGraphQuery, ApplicationInsightsTopology.")

    resource = ch_models.DiscoveryRule(
        properties=ch_models.DiscoveryRuleProperties(
            authentication_setting=authentication_setting,
            discover_relationships=discover_relationships,
            add_recommended_signals=add_recommended_signals,
            specification=specification,
            display_name=display_name,
        )
    )
    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       discovery_rule_name=discovery_rule_name,
                       resource=resource)


def discovery_rule_show(client, resource_group_name, health_model_name,
                        discovery_rule_name):
    return client.get(resource_group_name=resource_group_name,
                      health_model_name=health_model_name,
                      discovery_rule_name=discovery_rule_name)


def discovery_rule_list(client, resource_group_name, health_model_name):
    return client.list_by_health_model(resource_group_name=resource_group_name,
                                       health_model_name=health_model_name)


def discovery_rule_delete(client, resource_group_name, health_model_name,
                          discovery_rule_name, no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete,
                       resource_group_name=resource_group_name,
                       health_model_name=health_model_name,
                       discovery_rule_name=discovery_rule_name)
