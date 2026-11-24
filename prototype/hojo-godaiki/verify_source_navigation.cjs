"use strict";
// Verify the five REAL hyperlinks in the HOJO viewer by clicking them in a
// browser, not by merely comparing href strings or trusting URL fragments.
const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

const HERE = __dirname;
const expectedIds = Array.from({ length: 5 }, (_, n) => `HG-${String(n + 1).padStart(4, "0")}`);

function assert(value, message) {
  if (!value) throw new Error(message);
}

async function checkOne(viewer, record) {
  const link = viewer.locator(`article[id="${record.id}"] a`, { hasText: "Wikisource原節を読む" });
  assert((await link.count()) === 1, `${record.id}: missing/duplicated viewer link`);
  const href = await link.getAttribute("href");
  const expected = record.source_url;
  assert(href === expected, `${record.id}: HTML link != article source_url`);

  const desired = new URL(expected);
  const fragment = decodeURIComponent(desired.hash.substring(1));
  assert(desired.hostname === "ja.wikisource.org" && fragment.length > 0,
    `${record.id}: invalid source domain/fragment`);

  const [popup] = await Promise.all([
    viewer.waitForEvent("popup", { timeout: 20000 }),
    link.click()
  ]);
  try {
    await popup.waitForLoadState("domcontentloaded", { timeout: 30000 });
    await popup.waitForFunction(({ fragment, chapter }) => {
      const target = document.getElementById(fragment);
      if (!target) return false;
      const heading = target.closest("h1,h2,h3,h4,h5,h6");
      const label = heading?.textContent || target.textContent ||
        target.parentElement?.textContent || "";
      return label.includes(chapter) && document.body.textContent.includes(chapter);
    }, { fragment, chapter: record.chapter }, { timeout: 15000 });

    await popup.waitForFunction(fragment => {
      const target = document.getElementById(fragment);
      if (!target) return false;
      const rect = target.getBoundingClientRect();
      return rect.bottom >= -32 && rect.top <= window.innerHeight;
    }, fragment, { timeout: 12000 });

    const state = await popup.evaluate(fragment => {
      const target = document.getElementById(fragment);
      return { href: location.href, title: document.title, fragment,
        targetFound: Boolean(target), targetY: target?.getBoundingClientRect().top,
        viewportHeight: innerHeight, scrollY };
    }, fragment);
    assert(new URL(state.href).hostname === desired.hostname,
      `${record.id}: popup did not land at Wikisource`);
    assert(decodeURIComponent(new URL(state.href).hash.substring(1)) === fragment,
      `${record.id}: popup lost/changed hash`);
    console.log(`PASS ${record.id} ${record.chapter}: ${JSON.stringify(state)}`);
  } catch (error) {
    const state = await popup.evaluate(() => ({
      href: location.href, title: document.title,
      bodyLength: (document.body?.innerText || "").length,
      bodyStart: (document.body?.innerText || "").slice(0, 800),
      targetIDs: [...document.querySelectorAll("[id]")].map(x => x.id)
        .filter(x => /伊豆|早雲|関東|天文|上杉|生捕|小田原|旗馬|犬也|弓馬/.test(x)).slice(0, 30),
      tocLinks: [...document.querySelectorAll('a[href*="#"]')]
        .map(x=>({text:(x.textContent||"").trim().slice(0,75), href:x.getAttribute("href")}))
        .filter(x=>/伊豆|早雲|関東|天文|上杉|生捕|小田原|旗馬|犬也|弓馬/.test(x.text))
        .slice(0, 25),
      headings: [...document.querySelectorAll("h1,h2,h3,h4,h5,h6")]
        .map(x => ({text: (x.textContent || "").trim().slice(0,90),
          ids: [x.id, ...[...x.querySelectorAll("[id]")].map(n=>n.id)]}))
        .filter(x => /伊豆早雲|関東天文|上杉朝成|旗馬じるし|犬也入道/.test(x.text))
        .slice(0, 20)
    })).catch(e => ({diagnosticError: String(e)}));
    throw new Error(`${record.id}: real click/section-position verification FAILED: ${error.message}; ${JSON.stringify(state)}`);
  } finally {
    await popup.close();
  }
}

function selectRecords(records, onlyId) {
  assert(records.length === expectedIds.length &&
    records.every((record, index) => record.id === expectedIds[index]),
    "exactly five ordered Hojo articles required");
  if (onlyId === undefined) return records;
  assert(expectedIds.includes(onlyId),
    `FAIL limited: 0 checks attempted; unknown ONLY_HG_ID ${JSON.stringify(onlyId)}`);
  return records.filter(record => record.id === onlyId);
}

async function checkSections(records, onlyId, check) {
  const mode = onlyId === undefined ? "full" : "limited";
  const expected = new Set(onlyId === undefined ? expectedIds : [onlyId]);
  const attempted = new Set();
  const succeeded = new Set();

  for (const record of records) {
    const id = record.id;
    assert(expected.has(id) && !attempted.has(id), `unexpected or duplicate section check: ${id}`);
    attempted.add(id);
    try {
      await check(record);
      succeeded.add(id);
    } catch (error) {
      console.error(`FAIL ${id}: ${error.stack || error}`);
    }
  }

  const counts = `${succeeded.size}/${expected.size} passed, ${attempted.size} attempted`;
  assert(attempted.size === expected.size && succeeded.size === expected.size,
    `FAIL ${mode}: ${counts}`);
  return `PASS ${mode}: ${counts} in Chromium`;
}

async function main() {
  const data = JSON.parse(fs.readFileSync(path.join(HERE, "hojo_godaiki_records.json"), "utf8"));
  const onlyId = process.env.ONLY_HG_ID;
  const records = selectRecords(data.records, onlyId);
  const { chromium } = require("playwright");
  const browser = await chromium.launch({headless: true});
  let summary;
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 780 } });
    const viewer = await context.newPage();
    await viewer.goto(pathToFileURL(path.join(HERE, "index.html")).href);
    summary = await checkSections(records, onlyId, record => checkOne(viewer, record));
    await context.close();
  } finally {
    await browser.close();
  }
  console.log(summary);
}

if (require.main === module) {
  main().catch(error => { console.error(error.stack || error); process.exitCode = 1; });
}

module.exports = { selectRecords, checkSections };
