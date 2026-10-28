// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root.
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { test } = require('node:test');
const vm = require('node:vm');

const script = /<script nonce="[^"]+">([\s\S]*?)<\/script>/.exec(readFileSync(0, 'utf8'))[1]
  .replace(/const BOOT = .*;\r?\n/, 'const BOOT = boot;\n');
const type = 'storage.target', sid = `${type}-1`;
const createFields = ['targetStorageAccountId', 'targetFileShareName', 'targetFileShareProvisioningModel'];
const optionalCreateFields = ['targetFileShareTier', 'targetFileShareQuotaGiB',
  'targetFileShareProvisionedIops', 'targetFileShareProvisionedBandwidthMibps'];
const shareId = 'targetFileShareId', action = 'targetResourceAction';
const fields = Object.fromEntries([action, shareId, ...createFields, ...optionalCreateFields]
  .map(f => [f, { type: 'string', required: false, scope: 'Entity', isEditable: true }]));
fields[action].allowedValues = ['Create', 'Validate'];
const rules = [
  {
    if: { properties: { [action]: { const: 'Create' } }, required: [action] },
    then: { required: createFields, properties: { [shareId]: false } }
  },
  {
    if: { properties: { [action]: { const: 'Validate' } }, required: [action] },
    then: { required: [shareId], properties: Object.fromEntries(
      [...createFields, ...optionalCreateFields].map(f => [f, false])) }
  }
];
const createValues = Object.fromEntries(createFields.map(f => [f, 'value']));

function editor(data = {}, clauses = { allOf: rules }, extraFields = {}, entities) {
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
  const root = { inputs: { schema: { [type]: { ...fields, ...extraFields, ...clauses } },
    stepInputs: { [sid]: data } } };
  const context = vm.createContext({
    boot: { doc: { schema: root.inputs.schema, stepInputs: root.inputs.stepInputs },
      inputsRoot: root, spec: entities ? { workstreams: [{ steps: [{ stepId: sid, entities }] }] } : {}, meta: {} },
    document: {
      getElementById: element, querySelector() { return null; }, querySelectorAll() { return []; },
      addEventListener() {}
    },
    window: { addEventListener() {} }, navigator: {}, URL, setTimeout() {}, clearTimeout() {}
  }, { codeGeneration: { strings: false, wasm: false } });
  vm.runInContext(script, context);
  return { run: code => vm.runInContext(code, context), nodes, data, root };
}
const exported = e => JSON.parse(e.run('buildInputsJson()')).inputs.stepInputs[sid];

test('Create requires all three inputs, excludes share ID, and gates command preparation', () => {
  const e = editor({ [action]: 'Create', [shareId]: 'stale-id' });
  assert.equal(e.run('uploadBlocked()'), true);
  assert.equal(e.nodes.get('copyBtn').disabled, true);
  assert.equal(e.run(`stepIssues('${sid}').length`), 3);
  assert.doesNotMatch(e.nodes.get('form').innerHTML, /data-row="[^"]+\|targetFileShareId"/);
  assert.equal(Object.hasOwn(exported(e), shareId), false);
  Object.assign(e.data, createValues);
  e.run('refreshValidation()');
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(e.nodes.get('copyBtn').disabled, false);
  assert.equal(e.data[shareId], 'stale-id');
  for (const f of createFields) assert.equal(exported(e)[f], 'value');
});

test('Validate requires share ID and ignores excluded required fields and invalid values', () => {
  const e = editor({ [action]: 'Validate', ...createValues, targetFileShareQuotaGiB: 'invalid',
    workloadOverrides: { a: {} } }, undefined, {
    targetStorageAccountId: { ...fields.targetStorageAccountId, required: true, pattern: '^valid$' },
    targetFileShareQuotaGiB: { type: 'integer', required: true, scope: 'Entity' }
  });
  assert.equal(e.run(`stepIssues('${sid}').length`), 1);
  assert.equal(e.run(`stepIssues('${sid}')[0].f`), shareId);
  for (const f of [...createFields, ...optionalCreateFields]) {
    assert.doesNotMatch(e.nodes.get('form').innerHTML, new RegExp(`data-row="[^"]+\\|${f}"`));
    assert.equal(Object.hasOwn(exported(e), f), false);
  }
  e.data[shareId] = 'id';
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(exported(e)[shareId], 'id');
});

test('empty, missing, null, and unrecognized actions do not activate either branch', () => {
  for (const value of [undefined, null, '', 'Unknown']) {
    const data = value === undefined ? {} : { [action]: value };
    const e = editor(data);
    assert.equal(e.run(`inputState('${sid}').required.size`), 0);
    assert.equal(e.run(`inputState('${sid}').excluded.size`), 0);
    assert.equal(e.run('uploadBlocked()'), false);
  }
});

test('conditionally required values reject missing, null and empty input', () => {
  for (const value of [undefined, null, '']) {
    const e = editor({ [action]: 'Validate', [shareId]: value });
    assert.equal(e.run('uploadBlocked()'), true);
    assert.equal(e.run(`stepIssues('${sid}')[0].msg`), 'Required');
  }
});

test('changing action refreshes required markers in both panes without destroying values', () => {
  const e = editor({ [action]: 'Create', [shareId]: 'id', ...createValues, workloadOverrides: { a: {} } });
  const before = JSON.stringify(e.data);
  e.run(`setValue('D|${sid}|${action}', 'Validate')`);
  assert.match(e.nodes.get('form').innerHTML, /targetFileShareId<span class="req"/);
  assert.match(e.nodes.get('ovPane').innerHTML, /targetFileShareId<span class="req"/);
  assert.doesNotMatch(e.nodes.get('form').innerHTML, /data-row="[^"]+\|targetStorageAccountId"/);
  assert.doesNotMatch(e.nodes.get('ovPane').innerHTML, /data-row="[^"]+\|targetStorageAccountId"/);
  assert.doesNotMatch(e.nodes.get('form').innerHTML, /targetStorageAccountId<span class="req"/);
  assert.equal(exported(e)[shareId], 'id');
  e.run(`setValue('D|${sid}|${action}', 'Create')`);
  assert.match(e.nodes.get('form').innerHTML, /targetStorageAccountId<span class="req"/);
  assert.match(e.nodes.get('ovPane').innerHTML, /targetStorageAccountId<span class="req"/);
  assert.equal(Object.hasOwn(exported(e), shareId), false);
  assert.equal(JSON.stringify(e.data), before);
});

test('per-workload conditions use inherited action and honor independent action overrides', () => {
  const e = editor({ [action]: 'Create', ...createValues, [shareId]: 'shared-id',
    workloadOverrides: { a: {}, b: { [action]: 'Validate' } } });
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(e.run(`contextRules('${sid}', 'a').${shareId}`), undefined);
  assert.equal(e.run(`contextRules('${sid}', 'b').targetStorageAccountId`), undefined);
  e.run(`selEntity = 'b'; renderOverrides()`);
  assert.match(e.nodes.get('ovPane').innerHTML, /data-row="[^"]+\|targetFileShareId"/);
  assert.doesNotMatch(e.nodes.get('ovPane').innerHTML, /data-row="[^"]+\|targetStorageAccountId"/);
  assert.doesNotMatch(e.nodes.get('form').innerHTML, /data-row="[^"]+\|targetFileShareId"/);
  for (const f of createFields)
    assert.match(e.nodes.get('form').innerHTML, new RegExp(`${f}<span class="req"`));
  const before = e.nodes.get('form').innerHTML;
  const dataBefore = JSON.stringify(e.data);
  e.run(`setValue('O|${sid}|b|${action}', 'Create')`);
  assert.equal(e.nodes.get('form').innerHTML, before);
  assert.match(e.nodes.get('ovPane').innerHTML, /targetStorageAccountId<span class="req"/);
  assert.equal(e.run(`contextRules('${sid}', 'a').${shareId}`), undefined);
  e.run(`setValue('O|${sid}|b|${action}', 'Validate')`);
  assert.equal(e.nodes.get('form').innerHTML, before);
  assert.equal(JSON.stringify(e.data), dataBefore);
  const out = exported(e);
  assert.equal(Object.hasOwn(out, shareId), false);
  assert.equal(out.workloadOverrides.b[shareId], 'shared-id');
  for (const f of createFields) {
    assert.equal(Object.hasOwn(out, f), false);
    assert.equal(out.workloadOverrides.a[f], 'value');
    assert.equal(Object.hasOwn(out.workloadOverrides.b, f), false);
  }
  assert.equal(Object.hasOwn(out.workloadOverrides.a, shareId), false);
});

test('unselected step inputs keep defined fields and required flags regardless of workload conditions', () => {
  const e = editor({ workloadOverrides: { a: { [action]: 'Create' }, b: { [action]: 'Validate' } } },
    undefined,
    { [action]: { ...fields[action], required: true } });
  e.run('const marked = {}; mark = (path, error) => { marked[path] = error; }; refreshValidation();');
  const before = e.nodes.get('form').innerHTML;
  assert.match(before, /targetResourceAction<span class="req"/);
  for (const f of [shareId, ...createFields]) {
    assert.match(before, new RegExp(`data-row="[^"]+\\|${f}"`));
    assert.doesNotMatch(before, new RegExp(`${f}<span class="req"`));
    assert.equal(e.run(`marked['D|${sid}|${f}']`), null);
  }
  assert.equal(e.run('uploadBlocked()'), true);
  e.nodes.get('entSel').listeners.change({ target: { value: 'b' } });
  assert.equal(e.nodes.get('form').innerHTML, before);
  assert.match(e.nodes.get('ovPane').innerHTML, /targetFileShareId<span class="req"/);
  e.nodes.get('entSel').listeners.change({ target: { value: 'a' } });
  assert.equal(e.nodes.get('form').innerHTML, before);
  assert.equal(e.data[action], undefined);
});

test('filtered exports preserve complex inherited values and explicit workload overrides', () => {
  const settings = { folders: ['one', 'two'] };
  const e = editor({ [action]: 'Create', ...createValues, [shareId]: 'id', settings,
    workloadOverrides: { a: {}, b: { [action]: 'Validate' }, c: { settings: { folders: ['custom'] } } } },
    { allOf: [...rules, {
      if: { properties: { [action]: { const: 'Validate' } } }, then: { properties: { settings: false } }
    }] }, { settings: { type: 'object', scope: 'Entity', isEditable: true } });
  const before = JSON.stringify(e.root);
  const out = exported(e);
  assert.equal(Object.hasOwn(out, 'settings'), false);
  assert.deepEqual(out.workloadOverrides.a.settings, settings);
  assert.equal(Object.hasOwn(out.workloadOverrides.b, 'settings'), false);
  assert.deepEqual(out.workloadOverrides.c.settings, { folders: ['custom'] });
  assert.equal(JSON.stringify(e.root), before);
});

test('conditionally required appliance fields are marked and validated in the shared pane', () => {
  const e = editor({ [action]: 'Validate' }, undefined,
    Object.fromEntries(Object.entries(fields).map(([f, rule]) => [f, { ...rule, scope: 'Wave' }])));
  e.run('const marked = {}; mark = (path, error) => { marked[path] = error; }; refreshValidation();');
  assert.match(e.nodes.get('form').innerHTML, /targetFileShareId<span class="req"/);
  assert.equal(e.run(`marked['A|${sid}|${shareId}']`), 'Required');
  assert.equal(e.run('uploadBlocked()'), true);
});

test('shared inputs still show format validation errors', () => {
  const e = editor({ [action]: 'Create', [shareId]: 'invalid', ...createValues,
    workloadOverrides: { a: {}, b: { [action]: 'Validate' } } }, { allOf: [
    { if: { properties: { [action]: { const: 'Validate' } } }, then: { required: [shareId] } }
  ] }, {
    [shareId]: { ...fields[shareId], pattern: '^valid$' }
  });
  e.run('const marked = {}; mark = (path, error) => { marked[path] = error; }; refreshValidation();');
  assert.equal(e.run(`rulesFor('${sid}').${shareId}.required`), false);
  assert.match(e.run(`marked['D|${sid}|${shareId}']`), /Must match/);
  assert.equal(e.run(`entityErrors('${sid}', 'b')`), 1);
});

test('shared conditional errors appear once while retaining each workload issue', () => {
  for (const value of [null, 'invalid']) {
    const e = editor({ [action]: 'Validate', [shareId]: value, workloadOverrides: { a: {}, b: {} } },
      undefined, { [shareId]: { ...fields[shareId], pattern: '^valid$' } });
    e.run('const marked = {}; mark = (path, error) => { marked[path] = error; }; refreshValidation();');
    const expected = value === null ? 'Required' : 'Must match: valid';
    assert.equal(e.run(`marked['D|${sid}|${shareId}']`), expected);
    assert.equal(e.run(`stepIssues('${sid}').length`), 2);
    assert.equal(e.run(`entityErrors('${sid}', 'a')`), 1);
    assert.equal(e.run(`entityErrors('${sid}', 'b')`), 1);
    assert.equal(e.run('uploadBlocked()'), true);
    e.run(`setValue('O|${sid}|b|${shareId}', 'valid')`);
    assert.equal(e.run(`marked['D|${sid}|${shareId}']`), expected);
    assert.equal(e.run(`entityErrors('${sid}', 'b')`), 0);
    e.run(`setValue('D|${sid}|${shareId}', 'valid')`);
    assert.equal(e.run(`marked['D|${sid}|${shareId}']`), null);
    assert.equal(e.run('uploadBlocked()'), false);
  }
});

test('false properties remove excluded overrides including non-spec keys without mutating editor data', () => {
  const e = editor({ [action]: 'Validate', [shareId]: 'id',
    workloadOverrides: { a: { targetFileShareName: 'stale' }, extra: { targetFileShareName: 'also-stale' } } },
  undefined, {}, ['a']);
  const out = exported(e);
  assert.equal(Object.hasOwn(out.workloadOverrides.a, 'targetFileShareName'), false);
  assert.equal(Object.hasOwn(out.workloadOverrides.extra, 'targetFileShareName'), false);
  assert.equal(e.data.workloadOverrides.a.targetFileShareName, 'stale');
});

test('empty workload overrides still inherit controller and required values', () => {
  const e = editor({ [action]: 'Validate', [shareId]: null,
    workloadOverrides: { a: { [action]: '' }, b: { [shareId]: 'override-id' } } });
  assert.equal(e.run(`entityErrors('${sid}', 'a')`), 1);
  assert.equal(e.run(`entityErrors('${sid}', 'b')`), 0);
  e.data[shareId] = 'shared';
  assert.equal(e.run('uploadBlocked()'), false);
});

test('false exclusion wins over conditional and descriptor required flags', () => {
  const e = editor({ [action]: 'Create', [shareId]: null }, { allOf: [
    { if: { properties: { [action]: { const: 'Create' } } },
      then: { required: [shareId], properties: { [shareId]: false } } }
  ] }, { [shareId]: { ...fields[shareId], required: true } });
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(Object.hasOwn(exported(e), shareId), false);
  assert.doesNotMatch(e.nodes.get('form').innerHTML, /data-row="[^"]+\|targetFileShareId"/);
});

test('allOf remains metadata; malformed and unsupported rules fail visibly', () => {
  for (const clauses of [
    { allOf: 'invalid' }, { allOf: [null] }, { allOf: [{ if: {}, then: { required: 'bad' } }] },
    { allOf: [{ if: { properties: { [action]: { enum: ['Create'] } } }, then: {} }] },
    { allOf: [{ if: {}, then: { properties: { unknown: false } } }] },
    { allOf: [{ if: {}, then: { required: ['unknown'] } }] },
    { allOf: [{ if: {}, then: {}, else: {} }] }, { anyOf: [] }, { $ref: '#/missing' }
  ]) {
    const e = editor({}, clauses);
    assert.equal(e.run('uploadBlocked()'), true);
    assert.match(e.nodes.get('stepConditions').textContent, /rule|allOf/i);
    assert.equal(e.run(`stepFields('${sid}').includes('allOf')`), false);
  }
  assert.equal(editor({}, { allOf: [] }).run('uploadBlocked()'), false);
});

test('legacy schemas retain field checks, keyword-named parameters, exports and partial uploads', () => {
  const e = editor({ description: 'parameter', workloadOverrides: { a: {} } }, {}, {
    description: { type: 'string', required: false, isEditable: true },
    agent: { type: 'string', required: true, scope: 'Entity' }
  });
  assert.equal(e.run(`stepFields('${sid}').includes('description')`), true);
  assert.equal(e.run(`stepErrors('${sid}')`), 1);
  assert.equal(e.run('uploadBlocked()'), false);
  assert.equal(e.nodes.get('copyBtn').disabled, false);
  assert.deepEqual(exported(e), e.data);
});

test('multiple matching rules accumulate and exports preserve schema and never mutate editor data', () => {
  const e = editor({ [action]: 'Validate', [shareId]: 'id', ...createValues }, { allOf: [
    rules[1], { if: { required: [action] }, then: { required: ['extra'] } }
  ] }, { extra: { type: 'string', required: false, scope: 'Entity' } });
  const before = JSON.stringify(e.root);
  assert.equal(e.run('uploadBlocked()'), true);
  e.run('allIssues(); buildInputsJson(); showFile("Saved parameters.json.");');
  assert.equal(JSON.stringify(e.root), before);
  assert.deepEqual(JSON.parse(e.run('buildInputsJson()')).inputs.schema, e.root.inputs.schema);
  assert.match(e.nodes.get('savedNote').textContent, /draft/);
  e.nodes.get('copyBtn').listeners.click({ currentTarget: e.nodes.get('copyBtn') });
  assert.match(e.nodes.get('issueList').innerHTML, /extra/);
});
