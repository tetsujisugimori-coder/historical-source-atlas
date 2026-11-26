"use strict";

const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const { test } = require("node:test");
const { selectRecords, checkSections } = require("./verify_source_navigation.cjs");
const { records } = require("./hojo_godaiki_records.json");

test("an unknown ID exits with zero attempted checks and no PASS", () => {
  const run = spawnSync(process.execPath, [require.resolve("./verify_source_navigation.cjs")], {
    env: { ...process.env, ONLY_HG_ID: "HG-9999" },
    encoding: "utf8"
  });
  assert.equal(run.status, 1);
  assert.match(run.stderr, /FAIL limited: 0 checks attempted/);
  assert.doesNotMatch(run.stdout, /PASS/);
});

test("limited mode attempts one link and reports 1/1", async () => {
  const onlyId = "HG-0002";
  const visited = [];
  const summary = await checkSections(selectRecords(records, onlyId), onlyId,
    async record => { visited.push(record.id); });
  assert.deepEqual(visited, [onlyId]);
  assert.equal(summary, "PASS limited: 1/1 passed, 1 attempted in Chromium");
});

test("limited and full runs reject a failed click with accurate counts", async t => {
  t.mock.method(console, "error", () => {});
  const onlyId = "HG-0002";
  const check = async record => {
    if (record.id === onlyId) throw new Error("injected click failure");
  };
  await assert.rejects(checkSections(selectRecords(records, onlyId), onlyId, check),
    /FAIL limited: 0\/1 passed, 1 attempted/);
  await assert.rejects(checkSections(records, undefined, check),
    /FAIL full: 11\/12 passed, 12 attempted/);
  assert.equal(console.error.mock.callCount(), 2);
});

test("duplicate IDs and incomplete full runs cannot pass", async () => {
  const duplicate = [...records.slice(0, -1), records[0]];
  assert.throws(() => selectRecords(duplicate), /exactly 12 ordered Hojo articles/);
  await assert.rejects(checkSections(duplicate, undefined, async () => {}),
    /unexpected or duplicate section check: HG-0001/);
  await assert.rejects(checkSections(records.slice(0, -1), undefined, async () => {}),
    /FAIL full: 11\/12 passed, 11 attempted/);
});

test("full mode reports 12/12 after visiting both volumes", async () => {
  const visited = [];
  const summary = await checkSections(selectRecords(records), undefined,
    async record => { visited.push(record.id); });
  assert.deepEqual(visited, records.map(record => record.id));
  assert.equal(summary, "PASS full: 12/12 passed, 12 attempted in Chromium");
});
