// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root.
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { test } = require('node:test');
const vm = require('node:vm');

const script = /<script nonce="[^"]+">([\s\S]*?)<\/script>/.exec(readFileSync(0, 'utf8'))[1]
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
  workloadOverrides: { a: { source: 'one' }, b: { source: 'two' } } }, documentSchema = schema()) {
  const root = { $schema: './parameters.schema.json', inputs: { stepInputs: { [sid]: data } } };
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
      parameterSchema: documentSchema, inputsRoot: root, spec: {}, meta: {} },
    document: {
      getElementById: element, querySelector() { return null; }, querySelectorAll() { return []; },
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
});

test('shared defaults and nonempty workload values validate independently', () => {
  const e = editor();
  const before = e.nodes.get('form').innerHTML;
  e.run(`setValue('O|${sid}|a|action', 'Create')`);
  assert.equal(e.run(`entityErrors('${sid}', 'a')`) > 0, true);
  assert.equal(e.run(`entityErrors('${sid}', 'b')`), 0);
  assert.equal(e.nodes.get('form').innerHTML, before);
  e.run(`setValue('O|${sid}|a|action', 'Validate')`);
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(e.data.action, 'Validate');
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

test('false schemas reject supplied values but ignore unset service placeholders in the validation view', () => {
  const e = editor();
  e.data.name = 'stale';
  assert.equal(e.run('uploadBlocked()'), true);
  e.run(`setValue('D|${sid}|name', '')`);
  assert.equal(e.run('uploadBlocked()'), false);
  const exported = JSON.parse(e.run('buildInputsJson()'));
  assert.equal(exported.inputs.stepInputs[sid].name, null);
  assert.equal(exported.$schema, './parameters.schema.json');
  assert.equal(Object.hasOwn(exported.inputs, 'schema'), false);
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
