# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Required-input completeness for split Draft-07 runbook artifacts."""

import copy
import re

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT7

from azure.cli.core.azclierror import InvalidArgumentValueError

from .config_status import _from_counts, _is_empty
from .constants import INPUTLESS_STEP_REFS


def _values(data, fields):
    if not isinstance(data or {}, dict):
        raise ValueError('Workload inputs must be objects.')
    return {key: value for key, value in (data or {}).items()
            if key != 'workloadOverrides' and not (key in fields and _is_empty(value))}


class SchemaStatus:  # pylint: disable=too-few-public-methods
    """Project active SDK required-property diagnostics into existing statuses."""

    def __init__(self, definition, parameters, schema):
        self.fields = {}
        self.parents = {}
        self.virtual = set()
        try:
            if not isinstance(schema, dict) or schema.get('$schema') not in (
                    'http://json-schema.org/draft-07/schema', 'http://json-schema.org/draft-07/schema#',
                    'https://json-schema.org/draft-07/schema', 'https://json-schema.org/draft-07/schema#'):
                raise ValueError('The parameters schema must declare JSON Schema Draft-07.')
            Draft7Validator.check_schema(schema)
            # An empty registry cannot retrieve remote schemas.
            self.validator = Draft7Validator(schema, registry=Registry())
            self.resolver = Registry().resolver_with_root(Resource.from_contents(
                schema, default_specification=DRAFT7))
            self.schema = schema
            self.document = copy.deepcopy(parameters)
            if not isinstance(self.document, dict) or not isinstance(self.document.get('inputs'), dict):
                raise ValueError('Split parameters must contain an inputs object.')
            if not isinstance(self.document['inputs'].get('stepInputs'), dict):
                raise ValueError('Split parameters must contain a stepInputs object.')
            self._prepare(definition)
        except (SchemaError, Unresolvable, ValueError) as ex:
            raise InvalidArgumentValueError('Invalid parameters schema or inputs: {}'.format(ex)) from ex

    def _resolve(self, rule):
        seen = set()
        while isinstance(rule, dict) and '$ref' in rule:
            reference = rule['$ref']
            if reference in seen:
                raise ValueError('Recursive editor reference: {}'.format(reference))
            seen.add(reference)
            rule = self.resolver.lookup(reference).contents
        return rule if isinstance(rule, dict) else {}

    def _layout(self, sid):
        root = self._resolve(self.schema)
        inputs = self._resolve(root.get('properties', {}).get('inputs', {}))
        steps = self._resolve(inputs.get('properties', {}).get('stepInputs', {}))
        candidates = [steps['properties'][sid]] if sid in steps.get('properties', {}) else []
        candidates.extend(rule for pattern, rule in steps.get('patternProperties', {}).items()
                          if re.search(pattern, sid))
        fields, entities = set(), False
        for candidate in candidates:
            properties = self._resolve(candidate).get('properties', {})
            fields.update(properties)
            if 'workloadOverrides' in properties:
                entities = True
                overrides = self._resolve(properties['workloadOverrides'])
                fields.update(self._resolve(overrides.get('additionalProperties', {})).get('properties', {}))
        fields.discard('workloadOverrides')
        return fields, entities

    def _prepare(self, definition):
        steps = list(definition.get('steps') or [])
        for group in definition.get('workstreams') or []:
            if isinstance(group, dict):
                steps.extend(group.get('steps') or [])
        steps = {step.get('stepId') or step.get('id'): step for step in steps if isinstance(step, dict)}
        inputs = self.document['inputs']['stepInputs']
        for sid in dict.fromkeys([*inputs, *steps]):
            fields, entities = self._layout(sid)
            self.fields[sid] = fields
            if sid not in inputs and not fields:
                continue
            data = inputs.get(sid) or {}
            data = data if isinstance(data, dict) else {}
            shared = _values(data, fields)
            path = ('inputs', 'stepInputs', sid)
            parents = [(shared, path)]
            if entities:
                overrides = data.get('workloadOverrides') or {}
                if not isinstance(overrides, dict):
                    raise ValueError('workloadOverrides must be an object.')
                ids = list(dict.fromkeys([*(steps.get(sid, {}).get('entities') or []), *overrides]))
                if not ids:
                    ids = ['']
                    self.virtual.add(path + ('workloadOverrides', ''))
                shared['workloadOverrides'] = {
                    eid: {**shared, **_values(overrides.get(eid), fields)} for eid in ids}
                parents.extend((value, path + ('workloadOverrides', eid))
                               for eid, value in shared['workloadOverrides'].items())
            inputs[sid] = shared
            self.parents[sid] = parents

    def _errors(self):
        def leaves(errors):
            for error in errors:
                if error.context:
                    yield from leaves(error.context)
                else:
                    yield error
        try:
            return list(leaves(self.validator.iter_errors(self.document)))
        except Unresolvable as ex:
            raise InvalidArgumentValueError('Could not resolve the parameters schema: {}'.format(ex)) from ex

    def compute(self, step):
        """Count required fields satisfied in every context that requires them."""
        if step.get('stepRef') in INPUTLESS_STEP_REFS:
            return _from_counts(0, 0)
        sid = step.get('stepId') or step.get('id')
        parents = self.parents.get(sid, [])
        total = set_count = 0
        unchanged = None
        for field in sorted(self.fields.get(sid, [])):
            saved = [(parent, path, field in parent, parent.pop(field, None)) for parent, path in parents]
            try:
                if any(present for _, _, present, _ in saved):
                    errors = self._errors()
                else:
                    if unchanged is None:
                        unchanged = self._errors()
                    errors = unchanged
                required = {
                    tuple(error.absolute_path) for error in errors
                    if (error.validator == 'required' and field in error.validator_value
                        and field not in error.instance)
                    or (error.validator == 'dependencies'
                        and error.message.startswith(repr(field) + ' is a dependency of '))}
            finally:
                for parent, _, present, value in saved:
                    if present:
                        parent[field] = value
            needed = [(path, value) for _, path, _, value in saved if path in required]
            if needed:
                total += 1
                set_count += all(path not in self.virtual and not _is_empty(value) for path, value in needed)
        return _from_counts(set_count, total)
