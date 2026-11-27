// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root.
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { test } = require('node:test');
const vm = require('node:vm');

const html = readFileSync(0, 'utf8');
const renderedBoot = JSON.parse(/const BOOT = (.*);\r?\n/.exec(html)[1]);
const script = /<script nonce="[^"]+">([\s\S]*?)<\/script>/.exec(html)[1]
  .replace(/const BOOT = .*;\r?\n/, 'const BOOT = boot;\n');
const sid = 'target-1';
function schema() {
  const properties = {
    action: { type: 'string', enum: ['Create', 'Validate'], 'x-ms-source': { editable: true, scope: 'Entity' } },
    name: { type: 'string', minLength: 2 },
    resourceId: { type: 'string', pattern: '^/resource/' },
    size: { type: 'integer', minimum: 2 },
    ratio: { type: 'number', minimum: 0 },
    source: { type: 'string', readOnly: true },
    names: { type: 'array', uniqueItems: true, items: { type: 'string', minLength: 2 } }
  };
  return {
    $schema: 'http://json-schema.org/draft-07/schema#', type: 'object',
    properties: {
      $schema: { type: 'string' },
      inputs: { type: 'object', properties: {
        stepInputs: { type: 'object', patternProperties: {
          '^target-1$': { $ref: '#/definitions/step' }
        }, additionalProperties: false }
      }, required: ['stepInputs'], additionalProperties: false }
    }, required: ['inputs'], additionalProperties: false,
    definitions: {
      entity: { type: 'object', properties, required: ['action', 'source'], additionalProperties: false,
        allOf: [
          { if: { properties: { action: { const: 'Create' } }, required: ['action'] },
            then: { required: ['name', 'size'], properties: { resourceId: false } },
            else: { required: ['resourceId'], properties: { name: false } } }
        ]
      },
      step: { type: 'object', properties: {
        ...Object.fromEntries(Object.keys(properties).map(key => [key, { $ref: `#/definitions/entity/properties/${key}` }])),
        workloadOverrides: { type: 'object', additionalProperties: { $ref: '#/definitions/entity' } }
      }, additionalProperties: false }
    }
  };
}
function editor(data = { action: 'Validate', resourceId: '/resource/id', name: null,
  workloadOverrides: { a: { source: 'one' }, b: { source: 'two' } } }, documentSchema = schema(), spec = {}) {
  const root = { $schema: './parameters.schema.json', inputs: { stepInputs: data === null ? {} : { [sid]: data } } };
  const nodes = new Map();
  const element = id => {
    if (!nodes.has(id)) nodes.set(id, {
      textContent: '', innerHTML: '', hidden: false, disabled: false, dataset: {}, style: {}, listeners: {},
      classList: { add() {}, remove() {}, toggle() {} },
      addEventListener(name, fn) { this.listeners[name] = fn; },
      setAttribute() {}, removeAttribute() {}, focus() {},
      querySelector() { return null; }, querySelectorAll() { return []; }
    });
    return nodes.get(id);
  };
  const context = vm.createContext({
    boot: { doc: { schema: {}, stepInputs: root.inputs.stepInputs },
      parameterSchema: documentSchema, inputsRoot: root, spec, meta: {},
      inputlessStepRefs: renderedBoot.inputlessStepRefs },
    document: {
      getElementById: element,
      querySelector(selector) { return selector.startsWith('[data-err=') ? element(selector) : null; },
      querySelectorAll() { return []; },
      addEventListener() {}
    },
    window: { addEventListener() {} }, navigator: {}, URL, setTimeout() {}, clearTimeout() {}
  }, { codeGeneration: { strings: false, wasm: false } });
  vm.runInContext(script, context);
  return { run: code => vm.runInContext(code, context), root, data, nodes };
}

test('Draft-07 references, enum, scope and readOnly drive existing controls', () => {
  const e = editor();
  assert.equal(e.run('uploadBlocked()'), false, e.run('JSON.stringify(allIssues())'));
  assert.deepEqual(Array.from(e.run(`stepFields('${sid}')`)), [
    'action', 'name', 'resourceId', 'size', 'ratio', 'source', 'names'
  ]);
  assert.match(e.nodes.get('form').innerHTML, /<option value="Create"/);
  assert.match(e.nodes.get('ovPane').innerHTML, /data-path="O\|target-1\|a\|source"[^>]+disabled/);
  assert.match(e.nodes.get('form').innerHTML, /data-row="D\|target-1\|name"/);
  assert.equal(e.run(`contextRules('${sid}').action.suggestedValues`), undefined);
});

test('Draft-07 conditional selector choices become dropdowns without becoming validation restrictions', () => {
  const documentSchema = schema();
  delete documentSchema.definitions.entity.properties.action.enum;
  const create = documentSchema.definitions.entity.allOf[0];
  const validate = { if: { properties: { action: { enum: ['Validate'] } }, required: ['action'] },
    then: create.else };
  delete create.else;
  documentSchema.definitions.branches = { allOf: [create, validate] };
  documentSchema.definitions.entity.allOf = [{ $ref: '#/definitions/branches' }];
  const before = JSON.stringify(documentSchema);
  const e = editor(undefined, documentSchema);
  assert.deepEqual(Array.from(e.run(`contextRules('${sid}').action.suggestedValues`)), ['Create', 'Validate']);
  assert.equal(e.run(`contextRules('${sid}').action.allowedValues`), undefined);
  assert.match(e.nodes.get('form').innerHTML, /<select data-path="D\|target-1\|action"/);
  assert.match(e.nodes.get('ovPane').innerHTML, /<select data-path="O\|target-1\|a\|action"/);
  assert.equal(e.run('uploadBlocked()'), false);
  e.run(`setValue('D|${sid}|action', 'Create')`);
  assert.equal(e.run(`stepIssues('${sid}').some(i => i.f === 'name')`), true);
  const custom = editor({ action: 'Custom', workloadOverrides: { a: { source: 'one' } } }, documentSchema);
  assert.match(custom.nodes.get('form').innerHTML, /<option value="Custom" selected>Custom<\/option>/);
  assert.equal(custom.run('uploadBlocked()'), false);
  assert.equal(custom.run('buildInputsJson()'), JSON.stringify(custom.root, null, 2));
  assert.equal(JSON.stringify(documentSchema), before);
});

test('Draft-07 scalar const properties map to dropdowns with SDK numeric coercion', () => {
  const documentSchema = schema();
  documentSchema.definitions.entity.properties.ratio.const = 1.5;
  const e = editor(undefined, documentSchema);
  assert.match(e.nodes.get('form').innerHTML, /<select data-path="D\|target-1\|ratio"/);
  assert.match(e.nodes.get('form').innerHTML, /<option value="1.5"/);
  e.run(`setValue('D|${sid}|ratio', '1.5')`);
  assert.equal(e.data.ratio, 1.5);
  assert.equal(e.run('uploadBlocked()'), false);
  e.run(`setValue('D|${sid}|ratio', '2')`);
  assert.equal(e.run('uploadBlocked()'), true);
});

test('shared controls show workload requirements even when only overrides supply required values', () => {
  const e = editor();
  assert.equal(e.run(`contextRules('${sid}').action.required`), true);
  assert.equal(e.run(`contextRules('${sid}').source.required`), true);
  assert.equal(e.run(`contextRules('${sid}').name.required`), false);
  const required = /data-sec="req"[^>]*>([\s\S]*?)<\/details>/.exec(e.nodes.get('form').innerHTML)[1];
  assert.match(required, /data-row="D\|target-1\|action"/);
  assert.match(required, /data-row="D\|target-1\|source"/);
  assert.doesNotMatch(required, /data-row="D\|target-1\|name"/);
  assert.equal(Object.hasOwn(e.data, 'source'), false);
  assert.equal(e.run('uploadBlocked()'), false, e.run('JSON.stringify(allIssues())'));
});

test('split-schema optional inputs and their descriptions are expanded without a search', () => {
  const documentSchema = schema();
  documentSchema.definitions.entity.properties.name.description = 'Name needed when creating a resource.';
  const e = editor(undefined, documentSchema);
  assert.match(e.nodes.get('form').innerHTML, /<details[^>]*data-sec="opt"\s+open>/);
  assert.match(e.nodes.get('form').innerHTML, /Name needed when creating a resource\./);
  assert.match(e.nodes.get('form').innerHTML, /data-row="D\|target-1\|resourceId"/);
});

test('spec-only steps remain visible and selectable without inventing parameter entries', () => {
  const documentSchema = schema();
  const steps = documentSchema.properties.inputs.properties.stepInputs;
  steps.patternProperties['^.+$'] = steps.patternProperties['^target-1$'];
  delete steps.patternProperties['^target-1$'];
  const status = { stepId: 'status-1', displayName: 'Update migration status' };
  const e = editor(undefined, documentSchema, { workstreams: [{ steps: [
    { stepId: 'gate-1', stepRef: 'common.manual', isRequired: true }, status, status,
    { stepId: 'gate-2', stepRef: 'common.approval', isRequired: false }
  ] }] });
  const tabs = [...e.nodes.get('steps').innerHTML.matchAll(/data-sid="([^"]+)"/g)].map(match => match[1]);
  assert.deepEqual(tabs, ['status-1', sid]);
  assert.match(e.nodes.get('form').innerHTML, /Update migration status/);
  assert.match(e.nodes.get('form').innerHTML, /This step has no configurable inputs/);
  assert.doesNotMatch(e.nodes.get('form').innerHTML, /data-path=/);
  assert.equal(e.run('uploadBlocked()'), false, e.run('JSON.stringify(allIssues())'));
  e.run(`selectStep('${sid}')`);
  assert.match(e.nodes.get('form').innerHTML, /data-row="D\|target-1\|action"/);
  e.run("selectStep('status-1')");
  assert.equal(e.run("Object.hasOwn(DOC.stepInputs, 'status-1')"), false);
  assert.equal(e.run('buildInputsJson()'), JSON.stringify(e.root, null, 2));
});

test('shared defaults and nonempty workload values validate independently', () => {
  const e = editor();
  const before = e.run(`JSON.stringify(contextRules('${sid}'))`);
  e.run(`setValue('O|${sid}|a|action', 'Create')`);
  assert.equal(e.run(`entityErrors('${sid}', 'a')`) > 0, true);
  assert.equal(e.run(`entityErrors('${sid}', 'b')`), 0);
  assert.equal(e.run(`JSON.stringify(contextRules('${sid}'))`), before);
  e.run(`setValue('O|${sid}|a|action', 'Validate')`);
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(e.data.action, 'Validate');
});

test('SDK-required groups update for missing and filled values while editing action choices', () => {
  const e = editor();
  const required = field => e.run(`contextRules('${sid}').${field}.required`);
  assert.equal(required('resourceId'), true);
  assert.equal(required('name'), false);
  e.run(`setValue('D|${sid}|action', 'Create')`);
  assert.equal(required('name'), true);
  assert.equal(required('size'), true);
  assert.equal(required('resourceId'), false);
  const group = /data-sec="req"[^>]*>([\s\S]*?)<\/details>/.exec(e.nodes.get('form').innerHTML)[1];
  assert.match(group, /data-row="D\|target-1\|name"/);
  assert.doesNotMatch(group, /data-row="D\|target-1\|resourceId"/);
  e.run(`setValue('D|${sid}|name', 'valid'); setValue('D|${sid}|size', '2')`);
  assert.equal(required('name'), true);
  assert.equal(required('size'), true);
  assert.equal(e.run(`contextRules('${sid}', 'a').name.required`), true);
  e.run(`setValue('D|${sid}|action', 'Validate')`);
  assert.equal(required('name'), false);
  assert.equal(required('size'), false);
  assert.equal(required('resourceId'), true);
});

test('SDK projections follow nested non-const conditions and independent workload values', () => {
  const documentSchema = schema();
  documentSchema.definitions.branch = {
    if: { anyOf: [
      { properties: { ratio: { minimum: 4 } }, required: ['ratio'] },
      { properties: { names: { contains: { const: 'large' } } }, required: ['names'] }
    ] }, then: { required: ['size'] }
  };
  documentSchema.definitions.entity.allOf.push({ $ref: '#/definitions/branch' });
  documentSchema.definitions.entity.dependencies = { size: ['ratio'] };
  const e = editor(undefined, documentSchema);
  assert.equal(e.run(`contextRules('${sid}').size.required`), false);
  e.run(`setValue('D|${sid}|ratio', '5')`);
  assert.equal(e.run(`contextRules('${sid}').size.required`), true);
  e.run(`setValue('D|${sid}|ratio', '0.5')`);
  assert.equal(e.run(`contextRules('${sid}').size.required`), false);
  e.run(`setValue('D|${sid}|names', '["large"]')`);
  assert.equal(e.run(`contextRules('${sid}').size.required`), true);
  e.run(`setValue('O|${sid}|a|names', '["small"]')`);
  assert.equal(e.run(`contextRules('${sid}', 'a').size.required`), false);
  assert.equal(e.run(`contextRules('${sid}', 'b').size.required`), true);
  assert.equal(e.run(`entityErrors('${sid}', 'a')`), 0);
  assert.ok(e.run(`entityErrors('${sid}', 'b')`) > 0);
  e.run(`setValue('D|${sid}|ratio', ''); setValue('D|${sid}|size', '2')`);
  assert.equal(e.run(`contextRules('${sid}').ratio.required`), true);
  assert.equal(e.run(`stepIssues('${sid}').some(i => i.f === 'ratio')`), true);
});

test('inherited SDK failures appear once at shared controls, not override-only failures', () => {
  const e = editor();
  e.run(`setValue('D|${sid}|resourceId', '')`);
  const error = e.nodes.get(`[data-err="D|${sid}|resourceId"]`);
  assert.match(error.textContent, /required property "resourceId"/);
  assert.equal((error.textContent.match(/required property/g) || []).length, 1);
  e.run(`setValue('D|${sid}|resourceId', '/resource/id')`);
  assert.equal(error.textContent, '');
  e.run(`setValue('O|${sid}|a|resourceId', 'invalid')`);
  assert.equal(error.textContent, '');
  assert.match(e.nodes.get(`[data-err="O|${sid}|a|resourceId"]`).textContent, /pattern/);
});

test('SDK constraints validate values rather than accepting truncated numbers', () => {
  const e = editor();
  e.run(`setValue('D|${sid}|ratio', '1.25')`);
  assert.equal(e.data.ratio, 1.25);
  e.run(`setValue('D|${sid}|size', '2.5')`);
  assert.equal(e.data.size, 2.5);
  assert.equal(e.run('uploadBlocked()'), true);
  assert.equal(e.run(`stepIssues('${sid}').some(i => i.f === 'size')`), true);
  e.run(`setValue('D|${sid}|size', '3')`);
  assert.equal(e.run('uploadBlocked()'), false);
});

test('new nested conditions, dependencies and array assertions need no CLI evaluator changes', () => {
  const documentSchema = schema();
  documentSchema.definitions.entity.allOf.push({
    if: { properties: { size: { minimum: 4 } }, required: ['size'] },
    then: { anyOf: [{ required: ['ratio'] }, { required: ['names'] }] }
  });
  documentSchema.definitions.entity.dependencies = { ratio: ['size'] };
  const e = editor(undefined, documentSchema);
  e.data.size = 4;
  assert.equal(e.run('uploadBlocked()'), true);
  e.data.names = ['ok', 'ok'];
  assert.equal(e.run('uploadBlocked()'), true);
  e.data.names = ['ok', 'yes'];
  assert.equal(e.run('uploadBlocked()'), false);
});

test('excluded values warn without blocking and save as null without erasing editor values', () => {
  const e = editor();
  e.run(`setValue('D|${sid}|name', 'x')`);
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(e.run(`stepErrors('${sid}')`), 0);
  assert.equal(e.nodes.get('copyBtn').disabled, false);
  const warning = e.nodes.get(`[data-err="D|${sid}|name"]`).textContent;
  assert.match(warning, /not used|ignored/i);
  assert.doesNotMatch(warning, /False boolean schema/);
  let exported = JSON.parse(e.run('buildInputsJson()'));
  assert.equal(exported.inputs.stepInputs[sid].name, null);
  assert.equal(exported.$schema, './parameters.schema.json');
  assert.equal(Object.hasOwn(exported.inputs, 'schema'), false);
  assert.equal(e.data.name, 'x');
  e.run(`setValue('D|${sid}|action', 'Create')`);
  assert.equal(e.run('uploadBlocked()'), true);
  assert.equal(e.run(`stepIssues('${sid}').some(i => i.f === 'name')`), true);
  e.run(`setValue('D|${sid}|name', 'valid'); setValue('D|${sid}|size', '2')`);
  assert.equal(e.run('uploadBlocked()'), false);
  exported = JSON.parse(e.run('buildInputsJson()'));
  assert.equal(exported.inputs.stepInputs[sid].resourceId, null);
  assert.equal(exported.inputs.stepInputs[sid].name, 'valid');
  assert.equal(e.data.resourceId, '/resource/id');
  e.run(`setValue('D|${sid}|action', 'Validate')`);
  assert.equal(e.run('uploadBlocked()'), false);
  exported = JSON.parse(e.run('buildInputsJson()'));
  assert.equal(exported.inputs.stepInputs[sid].resourceId, '/resource/id');
  assert.equal(exported.inputs.stepInputs[sid].name, null);
});

test('ignored shared values remain available to workloads that still use them', () => {
  const e = editor({ action: 'Validate', resourceId: '/resource/id', workloadOverrides: {
    a: { action: 'Create', source: 'one', name: 'valid', size: 2 }, b: { source: 'two' }
  } });
  assert.equal(e.run('uploadBlocked()'), false);
  const output = JSON.parse(e.run('buildInputsJson()')).inputs.stepInputs[sid];
  assert.equal(output.resourceId, null);
  assert.equal(output.workloadOverrides.a.resourceId, null);
  assert.equal(output.workloadOverrides.b.resourceId, '/resource/id');
  assert.equal(e.data.resourceId, '/resource/id');
  assert.equal(Object.hasOwn(e.data.workloadOverrides.b, 'resourceId'), false);
  assert.equal(editor(output).run('uploadBlocked()'), false);
  e.run(`setValue('O|${sid}|a|action', 'Validate')`);
  const restored = JSON.parse(e.run('buildInputsJson()')).inputs.stepInputs[sid];
  assert.equal(restored.resourceId, '/resource/id');
  assert.equal(restored.workloadOverrides.a.name, null);
  assert.equal(e.data.workloadOverrides.a.name, 'valid');
});

test('referenced false property schemas are exclusions, not false branches of alternatives', () => {
  const documentSchema = schema();
  documentSchema.definitions.excluded = false;
  documentSchema.definitions.entity.allOf[0].else.properties.name = { $ref: '#/definitions/excluded' };
  documentSchema.definitions.entity.properties.ratio.anyOf = [
    { $ref: '#/definitions/excluded' }, { minimum: 4 }
  ];
  const e = editor(undefined, documentSchema);
  e.run(`setValue('D|${sid}|name', 'ignored')`);
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(JSON.parse(e.run('buildInputsJson()')).inputs.stepInputs[sid].name, null);
  e.run(`setValue('D|${sid}|ratio', '2')`);
  assert.equal(e.run('uploadBlocked()'), true);
  assert.equal(JSON.parse(e.run('buildInputsJson()')).inputs.stepInputs[sid].ratio, 2);
  e.run(`setValue('D|${sid}|ratio', '4')`);
  assert.equal(e.run('uploadBlocked()'), false);
  delete documentSchema.definitions.entity.properties.ratio.anyOf;
  documentSchema.definitions.entity.anyOf = [
    { properties: { ratio: { $ref: '#/definitions/excluded' } } },
    { properties: { ratio: { minimum: 4 } } }
  ];
  const ambiguous = editor(undefined, documentSchema);
  ambiguous.run(`setValue('D|${sid}|ratio', '2')`);
  assert.equal(ambiguous.run('uploadBlocked()'), true);
  assert.equal(JSON.parse(ambiguous.run('buildInputsJson()')).inputs.stepInputs[sid].ratio, 2);
});

test('optional invalid values, unknown properties and nested false schemas still block', () => {
  const e = editor();
  e.run(`setValue('D|${sid}|ratio', '0.5')`);
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(JSON.parse(e.run('buildInputsJson()')).inputs.stepInputs[sid].ratio, 0.5);
  assert.equal(e.nodes.get(`[data-err="D|${sid}|ratio"]`).textContent, '');
  e.run(`setValue('D|${sid}|ratio', '-1')`);
  assert.equal(e.run('uploadBlocked()'), true);
  e.run(`setValue('D|${sid}|ratio', '')`);
  e.data.unknown = 'invalid';
  assert.equal(e.run('uploadBlocked()'), true);
  const documentSchema = schema();
  documentSchema.definitions.entity.properties.names.items = false;
  const nested = editor(undefined, documentSchema);
  nested.run(`setValue('D|${sid}|names', '["invalid"]')`);
  assert.equal(nested.run('uploadBlocked()'), true);
  assert.deepEqual(JSON.parse(nested.run('buildInputsJson()')).inputs.stepInputs[sid].names, ['invalid']);
});

test('SDK revalidates the actual saved projection instead of merely suppressing false errors', () => {
  const documentSchema = schema();
  documentSchema.definitions.step.allOf = [
    { required: ['resourceId'], properties: { resourceId: false } }
  ];
  const e = editor(undefined, documentSchema);
  assert.equal(e.run('uploadBlocked()'), true);
  assert.equal(e.run(`stepIssues('${sid}').some(i => i.f === 'resourceId' && /required/.test(i.msg))`), true);
});

test('missing conditional required fields are attributed to their workload controls', () => {
  const e = editor({ action: 'Create', workloadOverrides: { a: { source: 'one' } } });
  const issues = Array.from(e.run(`stepIssues('${sid}')`));
  assert.deepEqual(issues.map(i => i.f).sort(), ['name', 'size'], JSON.stringify(issues));
  assert.equal(issues.every(i => i.eid === 'a'), true);
  e.run(`setValue('D|${sid}|name', 'valid'); setValue('D|${sid}|size', '2')`);
  assert.equal(e.run('uploadBlocked()'), false);
});

test('full-document root assertions are also evaluated by the SDK', () => {
  const documentSchema = schema();
  documentSchema.required.push('approval');
  const e = editor(undefined, documentSchema);
  assert.equal(e.run('uploadBlocked()'), true);
  assert.match(e.nodes.get('stepConditions').textContent, /approval/);
});

test('empty parameter documents retain all SDK failures and document-level review feedback', () => {
  for (const change of [
    s => { s.required.push('approval'); },
    s => { s.properties.inputs.properties.stepInputs.required = [sid]; },
    s => { s.definitions.entity.allOf = 'invalid'; }
  ]) {
    const documentSchema = schema();
    change(documentSchema);
    for (const spec of [{}, { workstreams: [{ steps: [{ stepId: 'status-1' }] }] }]) {
      const e = editor(null, documentSchema, spec);
      assert.equal(e.run('uploadBlocked()'), true);
      assert.ok(e.run('allIssues().length') > 0);
      assert.equal(e.nodes.get('copyBtn').disabled, true);
      assert.doesNotMatch(e.nodes.get('vsummary').textContent, /All required inputs set/);
      assert.match(e.nodes.get('vsummary').innerHTML, /document/i);
      e.run('showIssues()');
      assert.match(e.nodes.get('issueList').innerHTML, /approval|target-1|schema/i);
      assert.match(e.nodes.get('issueList').innerHTML, /Parameters document/);
    }
  }
  const valid = editor(null);
  assert.equal(valid.run('uploadBlocked()'), false);
  assert.equal(valid.run('buildInputsJson()'), JSON.stringify(valid.root, null, 2));
});

test('all matching named and pattern schemas contribute controls and workload metadata', () => {
  const documentSchema = schema();
  const steps = documentSchema.properties.inputs.properties.stepInputs;
  steps.properties = { [sid]: { type: 'object', properties: {
    sharedLabel: { type: 'string', 'x-ms-source': { scope: 'Wave' } }
  }, required: ['sharedLabel'] } };
  delete documentSchema.definitions.step.additionalProperties;
  delete documentSchema.definitions.entity.additionalProperties;
  steps.patternProperties['^target-'] = { type: 'object', properties: {
    workloadOverrides: { type: 'object', additionalProperties: {
      type: 'object', properties: { extra: { type: 'integer', minimum: 2 } }, required: ['extra']
    } }
  } };
  const before = JSON.stringify(documentSchema);
  const e = editor(undefined, documentSchema);
  assert.equal(e.run(`stepFields('${sid}').includes('sharedLabel')`), true);
  assert.equal(e.run(`entityFields('${sid}').includes('extra')`), true);
  assert.match(e.nodes.get('form').innerHTML, /data-path="A\|target-1\|sharedLabel"/);
  assert.match(e.nodes.get('ovPane').innerHTML, /data-path="O\|target-1\|a\|extra"/);
  assert.equal(e.run('uploadBlocked()'), true);
  e.run(`setValue('A|${sid}|sharedLabel', 'shared'); setValue('D|${sid}|extra', '2')`);
  assert.equal(e.run('uploadBlocked()'), false, e.run('JSON.stringify(allIssues())'));
  e.run(`setValue('O|${sid}|a|extra', '1')`);
  assert.equal(e.run('uploadBlocked()'), true);
  assert.equal(JSON.stringify(documentSchema), before);
});

test('untyped scalar enum and const dropdowns preserve their JSON value types on edit and Save', () => {
  const documentSchema = schema();
  const properties = documentSchema.definitions.entity.properties;
  properties.ratio = { const: 1.5 };
  properties.enabled = { enum: [false, true] };
  documentSchema.definitions.step.properties.enabled = { $ref: '#/definitions/entity/properties/enabled' };
  const e = editor(undefined, documentSchema);
  for (const [prefix, target] of [
    [`D|${sid}`, e.data], [`O|${sid}|a`, e.data.workloadOverrides.a]
  ]) {
    e.run(`setValue('${prefix}|ratio', '1.5'); setValue('${prefix}|enabled', 'false')`);
    assert.equal(target.ratio, 1.5);
    assert.equal(target.enabled, false);
    assert.equal(e.run('uploadBlocked()'), false, e.run('JSON.stringify(allIssues())'));
  }
  const output = JSON.parse(e.run('buildInputsJson()')).inputs.stepInputs[sid];
  assert.equal(output.ratio, 1.5);
  assert.equal(output.enabled, false);
  assert.equal(output.workloadOverrides.a.ratio, 1.5);
  assert.equal(output.workloadOverrides.a.enabled, false);
  e.run(`setValue('O|${sid}|a|enabled', 'true')`);
  assert.equal(e.data.workloadOverrides.a.enabled, true);
  e.run(`setValue('D|${sid}|ratio', '2')`);
  assert.equal(e.run('uploadBlocked()'), true);
});

test('undeclared and nested workloadOverrides survive projection and remain SDK errors', () => {
  const documentSchema = schema();
  delete documentSchema.definitions.step.properties.workloadOverrides;
  const e = editor({ action: 'Validate', workloadOverrides: {} }, documentSchema);
  assert.equal(e.run('uploadBlocked()'), true);
  assert.match(e.run('JSON.stringify(allIssues())'), /workloadOverrides/);
  assert.deepEqual(JSON.parse(e.run('buildInputsJson()')).inputs.stepInputs[sid].workloadOverrides, {});
  const nested = editor();
  nested.data.workloadOverrides.a.workloadOverrides = { hidden: 'invalid' };
  assert.equal(nested.run('uploadBlocked()'), true);
  assert.match(nested.run('JSON.stringify(allIssues())'), /workloadOverrides/);
  assert.deepEqual(JSON.parse(nested.run('buildInputsJson()')).inputs.stepInputs[sid]
    .workloadOverrides.a.workloadOverrides, { hidden: 'invalid' });
});

test('mixed-scope provider fields stay shared and inherited-only in workload validation and Save', () => {
  const documentSchema = schema();
  const shared = { type: 'string', minLength: 2, 'x-ms-source': { scope: 'Wave', editable: true } };
  documentSchema.definitions.step.properties.entityName = shared;
  documentSchema.definitions.step.required = ['entityName'];
  documentSchema.definitions.entity.patternProperties = { '^entityName$': shared };
  const e = editor(undefined, documentSchema);
  assert.equal(e.run(`contextRules('${sid}').entityName.scope`), 'Wave');
  assert.equal(e.run(`entityFields('${sid}').includes('entityName')`), false);
  assert.equal(e.run(`applianceFields('${sid}').includes('entityName')`), true);
  assert.match(e.nodes.get('form').innerHTML, /data-path="A\|target-1\|entityName"/);
  assert.doesNotMatch(e.nodes.get('ovPane').innerHTML, /O\|target-1\|a\|entityName/);
  e.run(`setValue('A|${sid}|entityName', 'x')`);
  assert.equal(e.run('uploadBlocked()'), true);
  assert.ok(e.nodes.get(`[data-err="A|${sid}|entityName"]`).textContent);
  e.run(`setValue('A|${sid}|entityName', 'Shared wave'); setValue('O|${sid}|a|ratio', '1.5')`);
  assert.equal(e.run('uploadBlocked()'), false, e.run('JSON.stringify(allIssues())'));
  const output = JSON.parse(e.run('buildInputsJson()')).inputs.stepInputs[sid];
  assert.equal(output.entityName, 'Shared wave');
  assert.equal(output.workloadOverrides.a.ratio, 1.5);
  for (const workload of Object.values(output.workloadOverrides))
    assert.equal(Object.hasOwn(workload, 'entityName'), false);
  // Explicit scope also wins if a compatible schema lists a shared property in both places.
  documentSchema.definitions.entity.properties.entityName = shared;
  const compatible = editor(undefined, documentSchema);
  assert.equal(compatible.run(`contextRules('${sid}').entityName.scope`), 'Wave');
  assert.equal(compatible.run(`entityFields('${sid}').includes('entityName')`), false);
});

test('live requiredness also honors full-document conditions on non-workload inputs', () => {
  const documentSchema = schema();
  delete documentSchema.definitions.step.properties.workloadOverrides;
  documentSchema.allOf = [{
    if: { properties: { inputs: { properties: { stepInputs: { properties: {
      [sid]: { properties: { action: { const: 'Create' } } }
    } } } } } },
    then: { properties: { inputs: { properties: { stepInputs: { properties: {
      [sid]: { required: ['name'] }
    } } } } } }
  }];
  const e = editor({ action: 'Validate' }, documentSchema);
  assert.equal(e.run(`contextRules('${sid}').name.required`), false);
  e.run(`setValue('A|${sid}|action', 'Create')`);
  assert.equal(e.run(`contextRules('${sid}').name.required`), true);
  assert.equal(e.run('uploadBlocked()'), true);
  e.run(`setValue('A|${sid}|name', 'valid')`);
  assert.equal(e.run(`contextRules('${sid}').name.required`), true);
  assert.equal(e.run('uploadBlocked()'), false);
});

test('step instance schemas are not conflated by their common step type', () => {
  const documentSchema = schema();
  documentSchema.properties.inputs.properties.stepInputs.patternProperties['^target-2$'] = {
    type: 'object', properties: { label: { type: 'string' } }, required: ['label']
  };
  const e = editor(undefined, documentSchema);
  e.root.inputs.stepInputs['target-2'] = { label: 'second' };
  assert.deepEqual(Array.from(e.run("stepFields('target-2')")), ['label']);
  assert.equal(e.run('uploadBlocked()'), false);
  e.root.inputs.stepInputs['target-2'].label = null;
  assert.equal(e.run("stepIssues('target-2').some(i => i.f === 'label')"), true);
  assert.equal(e.run(`stepIssues('${sid}').length`), 0);
});

test('inherited Object.prototype names cannot satisfy schema required properties', () => {
  const documentSchema = schema();
  documentSchema.definitions.entity.required.push('constructor', 'toString');
  const e = editor(undefined, documentSchema);
  assert.equal(e.run('uploadBlocked()'), true);
  assert.match(e.nodes.get('stepConditions').textContent, /constructor/);
});

test('unknown properties, malformed schemas, dialects and unresolved references fail visibly', () => {
  const unknown = editor();
  unknown.data.unknown = null;
  assert.equal(unknown.run('uploadBlocked()'), true);
  for (const change of [
    s => { s.$schema = 'https://json-schema.org/draft/2020-12/schema'; },
    s => { s.definitions.entity.allOf = 'bad'; },
    s => { s.definitions.step.properties.action = { $ref: '#/definitions/missing' }; },
    s => { s.definitions.entity.allOf = [{ $ref: 'https://example.invalid/missing' }]; }
  ]) {
    const documentSchema = schema();
    change(documentSchema);
    const e = editor(undefined, documentSchema);
    assert.equal(e.run('uploadBlocked()'), true);
    assert.ok(e.nodes.get('stepConditions').textContent);
  }
});

test('schemas and original parameters are not mutated and invalid drafts can still be saved', () => {
  const e = editor({ action: 'Create', workloadOverrides: { a: { source: 'one' } } });
  const before = JSON.stringify(e.root);
  e.run('allIssues(); buildInputsJson(); showFile("Saved parameters.json.");');
  assert.equal(JSON.stringify(e.root), before);
  assert.equal(e.run('buildInputsJson()'), JSON.stringify(e.root, null, 2));
  assert.match(e.nodes.get('savedNote').textContent, /draft/);
});
