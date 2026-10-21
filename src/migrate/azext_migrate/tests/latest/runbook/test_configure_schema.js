// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root.
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { test } = require('node:test');
const vm = require('node:vm');

const html = readFileSync(0, 'utf8');
const script = /<script nonce="[^"]+">([\s\S]*?)<\/script>/.exec(html)[1]
  .replace(/const BOOT = .*;\r?\n/, 'const BOOT = boot;\n');
const type = 'storage.validate';
const sid = `${type}-1`;
const fields = {
  vault: { type: 'string', required: false, scope: 'Entity' },
  username: { type: 'string', required: false, scope: 'Entity' },
  action: { type: 'string', required: false, scope: 'Entity' }
};
const condition = {
  if: { required: ['vault'], properties: { vault: { type: 'string', minLength: 1 } } },
  then: { required: ['username'], properties: { username: { type: 'string', minLength: 1 } } }
};

function editor(clauses = {}, data = {}, extraFields = {}) {
  const nodes = new Map();
  const element = id => {
    if (!nodes.has(id)) nodes.set(id, {
      textContent: '', innerHTML: '', hidden: false, disabled: false,
      dataset: {}, style: {}, listeners: {},
      classList: { add() {}, remove() {}, toggle() {} },
      addEventListener(name, fn) { this.listeners[name] = fn; },
      setAttribute() {}, removeAttribute() {}, focus() {},
      querySelector() { return null; }, querySelectorAll() { return []; }
    });
    return nodes.get(id);
  };
  const schema = { ...fields, ...extraFields, ...clauses };
  const root = { inputs: { schema: { [type]: schema }, stepInputs: { [sid]: data } } };
  const context = vm.createContext({
    boot: { doc: { schema: root.inputs.schema, stepInputs: root.inputs.stepInputs },
      inputsRoot: root, spec: {}, meta: {} },
    document: {
      getElementById: element,
      querySelector() { return null; }, querySelectorAll() { return []; },
      addEventListener() {}
    },
    window: { addEventListener() {} }, navigator: {}, URL,
    setTimeout() {}, clearTimeout() {}
  }, { codeGeneration: { strings: false, wasm: false } });
  vm.runInContext(script, context);
  const run = code => vm.runInContext(code, context);
  return { run, nodes, data, root };
}

test('legacy schemas retain fields, validation and partial-upload behavior', () => {
  const e = editor({}, { workloadOverrides: { a: {} } }, {
    agent: { type: 'string', required: true, scope: 'Entity' }
  });
  assert.deepEqual(Array.from(e.run(`stepFields('${sid}')`)), ['vault', 'username', 'action', 'agent']);
  assert.equal(e.run(`preparedSchema('${sid}').validator`), null);
  assert.equal(e.run(`stepErrors('${sid}')`), 1);
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(e.nodes.get('copyBtn').disabled, false);
});

test('allOf is not an input and optional empty vaults do not trigger it', () => {
  for (const data of [{}, { vault: null }, { vault: '' }, { vault: 'v', username: 'u' }]) {
    const e = editor({ allOf: [condition] }, data);
    assert.equal(e.run(`stepFields('${sid}').includes('allOf')`), false);
    assert.equal(e.run('allIssues().length'), 0);
    assert.equal(e.run('uploadBlocked()'), false);
  }
});

test('missing, null and empty conditional values block command preparation', () => {
  for (const data of [{ vault: 'v' }, { vault: 'v', username: null }, { vault: 'v', username: '' }]) {
    const e = editor({ allOf: [condition] }, data);
    assert.equal(e.run('uploadBlocked()'), true);
    assert.equal(e.run(`stepIssues('${sid}').some(i => i.f === 'username')`), true);
    assert.equal(e.nodes.get('copyBtn').disabled, true);
    assert.doesNotMatch(e.nodes.get('cmd').textContent, /az migrate/);
    e.nodes.get('copyBtn').listeners.click({ currentTarget: e.nodes.get('copyBtn') });
    assert.match(e.nodes.get('issueList').innerHTML, /username/);
  }
});

test('effective per-entity values activate and satisfy conditions independently', () => {
  const e = editor({ allOf: [condition] }, {
    vault: null, username: null, workloadOverrides: { a: { vault: 'v' }, b: {} }
  });
  assert.equal(e.run(`entityErrors('${sid}', 'a')`) > 0, true);
  assert.equal(e.run(`entityErrors('${sid}', 'b')`), 0);
  e.data.username = 'shared-user';
  e.run('refreshValidation()');
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(e.nodes.get('copyBtn').disabled, false);
  e.data.username = null;
  e.data.workloadOverrides.a.username = 'override-user';
  assert.equal(e.run('uploadBlocked()'), false);
  e.data.workloadOverrides.a.username = '';
  assert.equal(e.run('uploadBlocked()'), true);
});

test('the SDK handles nested boolean combinations, else and dependencies', () => {
  const clauses = {
    allOf: [
      { if: { properties: { action: { const: 'Create' } }, required: ['action'] },
        then: { anyOf: [{ required: ['vault'] }, { required: ['username'] }] },
        else: { not: { required: ['action'] } } },
      { oneOf: [{ required: ['vault'] }, { required: ['username'] }] }
    ],
    dependencies: { username: ['vault'] }
  };
  assert.equal(editor(clauses, { vault: 'v', action: 'Create' }).run('uploadBlocked()'), false);
  for (const data of [{ action: 'Create' }, { username: 'u', action: 'Create' },
    { vault: 'v', username: 'u', action: 'Create' }, { vault: 'v', action: 'Reuse' }]) {
    assert.equal(editor(clauses, data).run('uploadBlocked()'), true);
  }
});

test('false schemas, array assertions and local references use the SDK', () => {
  const clauses = {
    definitions: { nonempty: { type: 'string', minLength: 1 } },
    allOf: [{ properties: { username: { $ref: '#/definitions/nonempty' }, action: false,
      shares: { type: 'array', contains: { const: 'ready' }, uniqueItems: true } } }]
  };
  const valid = editor(clauses, { username: 'u', shares: ['ready'] });
  assert.equal(valid.run('uploadBlocked()'), false, valid.run('JSON.stringify(allIssues())'));
  for (const data of [{ username: '' }, { action: 'Create' }, { shares: ['pending'] },
    { shares: ['ready', 'ready'] }]) {
    assert.equal(editor(clauses, data).run('uploadBlocked()'), true);
  }
});

test('schema errors, bad dialects and unresolved references fail visibly', () => {
  for (const clauses of [{ allOf: [] }, { allOf: 'invalid' },
    { properties: false }, { properties: null }, { properties: [] }, { properties: 'invalid' },
    { allOf: [{ properties: { vault: { pattern: '[' } } }] },
    { definitions: { value: true }, allOf: [{ $ref: '#/definitions/value', $id: 'https://example.invalid/other' }] },
    { $schema: 'https://json-schema.org/draft/2020-12/schema', allOf: [true] },
    { allOf: [{ $ref: 'https://example.invalid/missing-schema' }] }]) {
    const e = editor(clauses, { vault: 'v' });
    assert.equal(e.run('uploadBlocked()'), true);
    assert.match(e.nodes.get('stepConditions').textContent, /schema|ref/i);
  }
});

test('additionalProperties recognizes parameters and metadata is not rendered', () => {
  const e = editor({ additionalProperties: false, $comment: 'test' }, { vault: 'v' });
  assert.equal(e.run('uploadBlocked()'), false, e.run('JSON.stringify(allIssues())'));
  assert.equal(e.run(`stepFields('${sid}').includes('$comment')`), false);
  e.data.unknown = 'x';
  assert.equal(e.run('uploadBlocked()'), true);
});

test('legacy inputs named after schema keywords remain inputs', () => {
  const e = editor({}, { description: 'input' }, {
    description: { type: 'string', required: false, isEditable: true }
  });
  assert.equal(e.run(`stepFields('${sid}').includes('description')`), true);
  assert.equal(e.run(`preparedSchema('${sid}').validator`), null);
});

test('required and nested properties cannot be satisfied by inherited prototype values', () => {
  const e = editor({ allOf: [{ required: ['constructor', 'toString', '__proto__'] }] });
  assert.equal(e.run('uploadBlocked()'), true);
  assert.equal(e.run(`schemaIssues('${sid}', null).filter(i => /required property/.test(i.msg)).length`), 3);
  const nested = editor({ allOf: [{ properties: { config: { properties: { constructor: { type: 'string' } } } } }] },
    { config: {} });
  assert.equal(nested.run('uploadBlocked()'), false);
});

test('validation does not modify exported schemas or inputs and saves invalid work as a draft', () => {
  const e = editor({ allOf: [condition] }, { vault: 'v', username: null });
  const before = JSON.stringify(e.root);
  e.run('allIssues(); allIssues(); showFile("Saved parameters.json.");');
  assert.equal(JSON.stringify(e.root), before);
  assert.equal(e.run('buildInputsJson()'), JSON.stringify(e.root, null, 2));
  assert.match(e.nodes.get('savedNote').textContent, /draft/);
  assert.equal(e.nodes.get('savedNote').hidden, false);
});
