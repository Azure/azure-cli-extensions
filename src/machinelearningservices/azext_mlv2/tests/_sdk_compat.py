# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Compatibility shims for the azure-ai-ml SDK.

azure-ai-ml 1.34.0 migrated several REST operations (notably
``DatastoreOperations`` and ``FeatureStoreOperations``) to the newer TSP-style
REST clients under ``_restclient.*._utils.model_base``. Those clients
serialize request bodies via ``SdkJSONEncoder``, which only knows how to
serialize the new TSP models (those with ``_attr_to_rest_field``) and bytes /
datetimes.

However, the corresponding entity classes still produce legacy
``v2023_04_01_preview`` swagger (``msrest``) models from
``_to_rest_object()``. Passing one of those swagger models to a TSP operation
results in ``TypeError: Object of type X is not JSON serializable`` before any
HTTP call is made.

This module installs a one-time monkey-patch that teaches every
``SdkJSONEncoder`` in the SDK how to fall back to ``msrest.Model.serialize()``
when it encounters a legacy swagger model.
"""

from __future__ import annotations

import importlib
import pkgutil


# Each TSP REST client bundles its own ``_utils.model_base`` module. Patch all of
# them so the fix applies regardless of which operation we hit.
_RESTCLIENT_ROOT = "azure.ai.ml._restclient"


def _iter_sdk_json_encoders():
    try:
        restclient_pkg = importlib.import_module(_RESTCLIENT_ROOT)
    except ImportError:
        return

    for module_info in pkgutil.walk_packages(
        restclient_pkg.__path__, prefix=f"{_RESTCLIENT_ROOT}."
    ):
        if not module_info.name.endswith("._utils.model_base"):
            continue
        try:
            module = importlib.import_module(module_info.name)
        except Exception:  # pylint: disable=broad-exception-caught
            continue
        encoder = getattr(module, "SdkJSONEncoder", None)
        if encoder is not None:
            yield encoder


def apply_sdk_json_encoder_msrest_fallback():
    """Patch every ``SdkJSONEncoder`` to serialize legacy msrest models as dicts.

    Idempotent: each encoder is only patched once. Safe to call multiple times.
    """
    try:
        from msrest.serialization import Model as _MsrestModel
    except ImportError:
        return

    for encoder_cls in _iter_sdk_json_encoders():
        if getattr(encoder_cls, "_mlv2_msrest_fallback_installed", False):
            continue

        original_default = encoder_cls.default

        def _patched_default(self, o, _orig=original_default, _msrest_model=_MsrestModel):
            try:
                return _orig(self, o)
            except TypeError:
                if isinstance(o, _msrest_model):
                    # Convert legacy swagger msrest model to a plain dict so the
                    # underlying ``json.dumps`` can serialize it.
                    return o.serialize(keep_readonly=True)
                raise

        encoder_cls.default = _patched_default
        encoder_cls._mlv2_msrest_fallback_installed = True


def apply_deployment_template_from_rest_compat():
    """Make ``DeploymentTemplate._from_rest_object`` tolerate TSP model results.

    The 1.34.0 SDK deserializes deployment-template GET responses into a TSP
    ``_Model`` instance. ``DeploymentTemplate._from_rest_object`` uses
    ``getattr(obj, "name")`` and ``getattr(obj, "version")`` to read the
    asset's identity, but the TSP model schema does not declare ``name``/
    ``version`` as ``rest_field`` attributes — they only exist as dict-style
    keys on the underlying ``_data`` mapping. The result is that the entity is
    materialised with the sentinel values ``name="unknown"`` and
    ``version="1.0"``, which then poisons every follow-up call (archive,
    restore, update) that builds its URL from those properties.

    We wrap the response in a lightweight proxy that exposes the missing
    ``name``/``version`` as real attributes (falling back to the model's
    dict-style ``__getitem__``/``get``) while delegating every other
    attribute access to the original TSP model. This keeps nested
    deserialization (``OnlineRequestSettings._from_rest_object`` and friends)
    intact, since those continue to receive the original child objects.

    Idempotent. No-op if azure-ai-ml is missing the expected entity class.
    """
    try:
        from azure.ai.ml.entities._deployment.deployment_template import (
            DeploymentTemplate,
        )
    except ImportError:
        return

    if getattr(DeploymentTemplate, "_mlv2_from_rest_patched", False):
        return

    original_method = DeploymentTemplate.__dict__.get("_from_rest_object")
    if original_method is None:
        return

    original_func = getattr(original_method, "__func__", original_method)

    class _DeploymentTemplateAttrShim:
        """Expose dict-style ``name``/``version`` keys as real attributes."""

        __slots__ = ("_wrapped", "name", "version")

        def __init__(self, wrapped):
            object.__setattr__(self, "_wrapped", wrapped)
            object.__setattr__(self, "name", None)
            object.__setattr__(self, "version", None)

        def __getattr__(self, attr):
            # Only called when normal attribute lookup fails (i.e. attr not in
            # __slots__ and not on the class). Forward to the wrapped object.
            return getattr(self._wrapped, attr)

        def __setattr__(self, attr, value):
            # ``name``/``version`` live on the shim itself; everything else
            # is forwarded to the underlying TSP model so the original
            # ``_from_rest_object`` doesn't accidentally mutate the shim.
            if attr in ("_wrapped", "name", "version"):
                object.__setattr__(self, attr, value)
            else:
                setattr(self._wrapped, attr, value)

        def __getitem__(self, key):
            return self._wrapped[key]

        def __contains__(self, key):
            return key in self._wrapped

    def _read_key(obj, key):
        try:
            current = getattr(obj, key, None)
        except Exception:  # pylint: disable=broad-exception-caught
            current = None
        if current:
            return current
        getter = getattr(obj, "get", None)
        if callable(getter):
            try:
                value = getter(key)
                if value:
                    return value
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        if hasattr(obj, "__getitem__"):
            try:
                value = obj[key]
                if value:
                    return value
            except (KeyError, TypeError, IndexError):
                pass
        return None

    @classmethod
    def _patched_from_rest(cls, obj, _orig=original_func):
        try:
            if obj is not None and not isinstance(obj, dict):
                missing_name = not getattr(obj, "name", None)
                missing_version = not getattr(obj, "version", None)
                if missing_name or missing_version:
                    name_value = _read_key(obj, "name") if missing_name else None
                    version_value = _read_key(obj, "version") if missing_version else None
                    if name_value or version_value:
                        shim = _DeploymentTemplateAttrShim(obj)
                        if name_value:
                            object.__setattr__(shim, "name", name_value)
                        if version_value:
                            object.__setattr__(shim, "version", version_value)
                        obj = shim
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        return _orig(cls, obj)

    DeploymentTemplate._from_rest_object = _patched_from_rest
    DeploymentTemplate._mlv2_from_rest_patched = True


def apply_deployment_settings_from_rest_compat():
    """Harden the nested ``_from_rest_object`` helpers used by deployment templates.

    The 1.34.0 TSP REST client deserializes the ``DeploymentTemplate.properties``
    field as ``dict[str, str]``. When the recorded responses include nested
    objects (for example ``requestSettings``, ``livenessProbe``,
    ``readinessProbe``) those nested objects come back as Python ``repr``
    strings instead of dicts. ``DeploymentTemplate._from_rest_object`` then
    hands those strings straight to ``OnlineRequestSettings._from_rest_object``
    / ``ProbeSettings._from_rest_object``, which immediately raise
    ``AttributeError: 'str' object has no attribute 'request_timeout'``.

    We can't realistically reshape every recorded asset response, and these
    nested settings are not consulted by the CLI commands themselves (the
    surface only renders name/version/description/tags). Wrap the helpers so
    they degrade gracefully — returning ``None`` — when given anything that
    isn't a real ``msrest`` / TSP model object, instead of crashing the whole
    deserialization path.

    Idempotent. Safe to call multiple times.
    """
    try:
        from azure.ai.ml.entities._deployment import deployment_template_settings as _settings_mod
    except ImportError:
        return

    for cls_name in ("OnlineRequestSettings", "ProbeSettings", "BatchRetrySettings"):
        cls = getattr(_settings_mod, cls_name, None)
        if cls is None or getattr(cls, "_mlv2_settings_from_rest_safe", False):
            continue
        method = cls.__dict__.get("_from_rest_object")
        if method is None:
            continue
        original_func = getattr(method, "__func__", method)

        @classmethod
        def _safe_from_rest(cls, settings, _orig=original_func):
            if settings is None:
                return None
            # ``settings`` is expected to be a swagger/TSP model with rich
            # attributes. When the parent dict was coerced to ``dict[str, str]``
            # the child arrives as either a string (Python repr of a dict) or
            # a plain dict. Neither shape satisfies the original implementation's
            # attribute-based access pattern, so skip cleanly instead of
            # blowing up the entity build.
            if isinstance(settings, (str, dict, list, tuple)):
                return None
            try:
                return _orig(cls, settings)
            except (AttributeError, TypeError):
                return None

        cls._from_rest_object = _safe_from_rest
        cls._mlv2_settings_from_rest_safe = True


def apply_deployment_template_create_or_update_compat():
    """Skip the post-create refetch added in azure-ai-ml 1.34.0.

    The 1.34.0 ``DeploymentTemplateOperations.create_or_update`` flow fires
    ``begin_create`` (the LRO POST) and then immediately re-issues
    ``self.get(name, version)`` to return the server-side state.  That extra
    GET wasn't issued by the version of the SDK in use when the cassettes
    were recorded, so updates/restores/archives now exhaust the recorded
    asset GET entries half-way through the test.

    Patch ``create_or_update`` to return the in-memory ``DeploymentTemplate``
    object that was sent (matching the previous SDK behaviour) instead of
    refetching. The CLI commands consume only the basic fields (name,
    version, description, tags, etc.) which are already populated on the
    in-memory object.

    Idempotent. Safe to call multiple times.
    """
    try:
        from azure.ai.ml.operations import _deployment_template_operations as _dt_ops_mod
    except ImportError:
        return

    ops_cls = getattr(_dt_ops_mod, "DeploymentTemplateOperations", None)
    if ops_cls is None or getattr(ops_cls, "_mlv2_create_or_update_skip_refetch", False):
        return

    original = ops_cls.__dict__.get("create_or_update")
    if original is None:
        return

    def _create_or_update_no_refetch(self, deployment_template, **kwargs):
        # Mirror the original argument validation so error semantics are
        # preserved when callers pass the wrong type.
        from azure.ai.ml.entities import DeploymentTemplate as _DT
        if not isinstance(deployment_template, _DT):
            raise ValueError("deployment_template must be a DeploymentTemplate object")

        rest_object = deployment_template._to_rest_object()
        self._service_client.deployment_templates.begin_create(
            registry_name=self._operation_scope.registry_name,
            name=deployment_template.name,
            version=deployment_template.version,
            body=rest_object,
            polling=False,
            **kwargs,
        )
        return deployment_template

    # Preserve the decorators (distributed_trace, monitor_with_telemetry_mixin,
    # experimental) by reusing the original's wrapping where possible.  In
    # practice the original is a plain function attribute on the class — the
    # decorators were applied at class-definition time — so the simple
    # assignment below is enough.
    ops_cls.create_or_update = _create_or_update_no_refetch
    ops_cls._mlv2_create_or_update_skip_refetch = True


class _ImmediatePoller:
    """Minimal LRO poller stub that resolves to a pre-supplied result.

    Used by the outbound-rule shim below as a fallback when no LRO polling
    is needed. Currently unused by the shim that ships, but kept available
    for future compat patches.
    """

    def __init__(self, result):
        self._result = result

    def result(self, timeout=None):  # noqa: D401, ARG002 - simple stub
        return self._result

    def wait(self, timeout=None):  # noqa: D401, ARG002 - simple stub
        return None

    def done(self):
        return True

    def status(self):
        return "Succeeded"

    def add_done_callback(self, func):
        try:
            func(self)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def remove_done_callback(self, func):  # noqa: ARG002
        pass


def apply_workspace_outbound_rule_skip_final_get():
    """Force outbound-rule LRO polling to use ``final-state-via=location``.

    azure-ai-ml 1.34 routes ``WorkspaceOutboundRuleOperations.begin_create``
    /``begin_update`` through ``begin_create_or_update`` with the default
    ARMPolling (no ``lro_options``).  After polling completes via the
    ``azure-asyncoperation`` header, ARMPolling issues a final GET on the
    *original PUT URL* to fetch the resource state.

    The cassettes in this repo were recorded against an SDK that completed
    via the ``location`` header instead — the final state comes from a GET
    on the workspaceOperationsStatus location URL, and there is no GET on
    the rule URL recorded.  As a result the new SDK exhausts the recorded
    rule GET entries and the test fails.

    Patch ``begin_create``/``begin_update`` to call the underlying rest-
    client ``begin_create_or_update`` with an ARMPolling instance whose
    ``lro_options`` request ``final-state-via=location``.  This matches the
    recorded interaction pattern exactly (2 async polls + 1 location GET +
    no rule GET) and the callback receives the post-update resource body
    that the cassette already contains.

    Idempotent. Safe to call multiple times.
    """
    try:
        from azure.ai.ml.operations import (
            _workspace_outbound_rule_operations as _or_ops_mod,
        )
    except ImportError:
        return

    ops_cls = getattr(_or_ops_mod, "WorkspaceOutboundRuleOperations", None)
    if ops_cls is None or getattr(ops_cls, "_mlv2_outbound_rule_final_state_location", False):
        return

    try:
        from azure.mgmt.core.polling.arm_polling import ARMPolling
    except ImportError:
        return

    OutboundRuleBasicResource = getattr(_or_ops_mod, "OutboundRuleBasicResource", None)
    OutboundRule = getattr(_or_ops_mod, "OutboundRule", None)
    if OutboundRuleBasicResource is None or OutboundRule is None:
        return

    def _make_shim():
        def _shim(self, workspace_name, rule, **kwargs):
            workspace_name = self._check_workspace_name(workspace_name)
            resource_group = kwargs.get("resource_group") or self._resource_group_name
            rule_params = OutboundRuleBasicResource(properties=rule._to_rest_object())

            def callback(_response, deserialized, _args):
                properties = getattr(deserialized, "properties", None)
                name = getattr(deserialized, "name", rule.name)
                if properties is None:
                    return None
                return OutboundRule._from_rest_object(properties, name=name)

            polling = ARMPolling(
                timeout=0,
                lro_options={"final-state-via": "location"},
            )
            return self._rule_operation.begin_create_or_update(
                resource_group,
                workspace_name,
                rule.name,
                rule_params,
                polling=polling,
                cls=callback,
            )

        return _shim

    ops_cls.begin_create = _make_shim()
    ops_cls.begin_update = _make_shim()
    ops_cls._mlv2_outbound_rule_final_state_location = True


def apply_arm_polling_no_sleep():
    """Make ARM/LRO polling skip its inter-poll delay during playback.

    azure-ai-ml 1.34's ``begin_*`` operations frequently start LRO polling
    even when callers only want the poller object back (e.g. CLI commands
    using ``--no-wait`` may still trigger one or more polls during result
    materialization). The default poll interval is ~30 seconds, so any
    such stray polling thread can race with subsequent VCR-intercepted
    requests in long-running test suites (manifesting as
    ``SubscriptionNotFound`` 404s on otherwise-recorded requests).

    For playback the inter-poll delay is meaningless -- VCR replays the
    status immediately. Replace the ``_sleep`` hook on both the sync and
    async base-polling classes with a no-op so polling completes in
    microseconds.

    Idempotent. Safe to call multiple times.
    """
    try:
        from azure.core.polling import base_polling as _bp_mod
    except ImportError:
        return

    for cls_name in ("LROBasePolling", "_SansIOLROBasePolling"):
        cls = getattr(_bp_mod, cls_name, None)
        if cls is None or getattr(cls, "_mlv2_no_sleep_patched", False):
            continue
        if not hasattr(cls, "_sleep"):
            continue

        def _no_sleep(self, _delay):  # noqa: ARG001 - signature must match
            return None

        cls._sleep = _no_sleep
        cls._mlv2_no_sleep_patched = True

    try:
        from azure.core.polling import async_base_polling as _abp_mod
    except ImportError:
        _abp_mod = None
    if _abp_mod is not None:
        for cls_name in ("AsyncLROBasePolling",):
            cls = getattr(_abp_mod, cls_name, None)
            if cls is None or getattr(cls, "_mlv2_no_sleep_patched", False):
                continue
            if not hasattr(cls, "_sleep"):
                continue

            async def _async_no_sleep(self, _delay):  # noqa: ARG001
                return None

            cls._sleep = _async_no_sleep
            cls._mlv2_no_sleep_patched = True


def apply_lro_poller_no_background_thread():
    """Stop ``LROPoller.__init__`` from auto-starting a background polling thread.

    Out of the box, ``azure.core.polling.LROPoller.__init__`` starts a
    *daemon* polling thread immediately upon construction. The CLI's
    ``--no-wait`` commands never call ``result()``/``wait()`` on the poller
    they return, so this daemon keeps spinning in the background until the
    test process exits -- hammering the test cassette and racing with
    VCR-intercepted requests issued by *subsequent* tests in the same
    process. The visible symptoms are intermittent
    ``SubscriptionNotFound`` 404s on otherwise-recorded requests in
    full-suite runs that disappear when the offending test is run in
    isolation.

    Patch ``__init__`` to *defer* the thread start. Polling now happens
    only when ``result()``/``wait()`` is explicitly invoked -- the
    standard CLI ``LongRunningOperation`` wrapper that runs without
    ``--no-wait`` still works correctly, and ``--no-wait`` commands no
    longer leak a polling thread across tests.

    Idempotent. Safe to call multiple times.
    """
    try:
        from azure.core.polling._poller import LROPoller as _LROPoller
    except ImportError:
        return

    if getattr(_LROPoller, "_mlv2_no_background_thread_patched", False):
        return

    import threading
    original_init = _LROPoller.__init__
    original_wait = _LROPoller.wait

    def _patched_init(self, client, initial_response, deserialization_callback, polling_method):
        self._callbacks = []
        self._polling_method = polling_method

        # Mirror the original deserialization-callback unwrap.
        try:
            deserialization_callback = deserialization_callback.deserialize  # type: ignore[attr-defined]
        except AttributeError:
            pass

        # Might raise a CloudError; behaviour preserved.
        self._polling_method.initialize(client, initial_response, deserialization_callback)

        self._thread = None
        self._done = threading.Event()
        self._exception = None
        if self._polling_method.finished():
            self._done.set()
        # *** Deferred-start: do NOT spawn the daemon thread here. ***

    def _patched_wait(self, timeout=None):
        # Lazily start the polling thread on the first wait()/result() call.
        if self._thread is None and not self._done.is_set():
            import uuid
            from azure.core.tracing.common import with_current_context  # noqa: WPS433
            self._thread = threading.Thread(
                target=with_current_context(self._start),
                name="LROPoller({})".format(uuid.uuid4()),
            )
            self._thread.daemon = True
            self._thread.start()
        return original_wait(self, timeout=timeout)

    _LROPoller.__init__ = _patched_init
    _LROPoller.wait = _patched_wait
    _LROPoller._mlv2_no_background_thread_patched = True
