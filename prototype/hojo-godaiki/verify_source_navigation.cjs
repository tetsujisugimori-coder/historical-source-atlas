"use strict";
// Verify the five REAL hyperlinks in the HOJO viewer by clicking them in a
// browser, not by merely comparing href strings or trusting URL fragments.
const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");

const HERE = __dirname;
const data = JSON.parse(fs.readFileSync(path.join(HERE, "hojo_godaiki_records.json"), "utf8"));
const expectedIds = Array.from({ length: 5 }, (_, n) => `HG-${String(n + 1).padStart(4, "0")}`);

function assert(value, message) {
  if (!value) throw new Error(message);
}

async function checkOne(viewer, record, context) {
  const link = viewer.locator(`article[id="${record.id}"] a`, { hasText: "Wikisource原節を読む" });
  assert((await link.count()) === 1, `${record.id}: missing/duplicated viewer link`);
  const href = await link.getAttribute("href");
  const expected = record.source_url.replaceAll("&", "&");
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

(async () => {
  assert(data.records.length === 5 &&
    data.records.every((r, i) => r.id === expectedIds[i]),
    "exactly five ordered Hojo articles required");
  const browser = await chromium.launch({headless: true});
  let failed = 0;
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 780 } });
    const viewer = await context.newPage();
    await viewer.goto(pathToFileURL(path.join(HERE, "index.html")).href);
    for (const record of data.records.filter(r => !process.env.ONLY_HG_ID || r.id === process.env.ONLY_HG_ID)) {
      try { await checkOne(viewer, record, context); }
      catch (err) { failed++; console.error(`FAIL: ${err.stack || err}`); }
    }
    await context.close();
  } finally {
    await browser.close();
  }
  if (failed) throw new Error(`${failed}/5 Wikisource section links did not pass real browser navigation`);
  console.log("All 5/5 external section link clicks verified in Chromium.");
})().catch(err => { console.error(err.stack || err); process.exitCode = 1; });
