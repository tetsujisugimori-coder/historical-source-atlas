# PR35 v3: frozen payload-only bridge reduction

2026-11-14 JST. Baseline PR HEAD 7d7a1bd9614c315287fa34ec4e740bc1965b0da5 / tree f416bddf7bb3af9fa9465fa9e4b3669b87ec79cb. This plan is fixed before the new Actions run. It does not reinterpret v1/v2 or their artifacts. Product acceptance remains Chromium8 PASS/WebKit8 FAIL historically; root cause UNKNOWN, Draft, merge NO.

## Input dependency and single changed factor

The reproduced v2 `bridge-no-filters` requires articles EK-0131 and EK-0130, narrative link B13-R01, EK-0120 and its 5 document clauses. `openReference` requires payload membership, search/year/chapter controls, render, details.open, scrollIntoView and (for clauses) focus. `navigateReference` also changes history through pushState. Restoration uses load/hashchange/popstate. Rendering reads publication, article_relationships, document_structures, narrative_references.

A is the unmodified product HTML at the baseline. B changes only the embedded payload array to retain EK-0120, EK-0130 and EK-0131, in original order and with every retained field unchanged. All bytes outside that array are unchanged, including provenance, CSS, DOM-generation code and restoration. Retained provenance may refer to nonrendered records; report that intentional diagnostic inconsistency, do not change product metadata. Reducing payload changes rendered amount/configuration as an effect; this comparison cannot isolate which such effect causes a difference.

The old one-record fixture deletes required bridge articles/references and is NOT_COMPARABLE with this route. It is not reused. CSS, DOM code and restoration reductions are deferred to separately registered later experiments, not changed together here. This plan is not an extreme minimal-HTML claim.

## Frozen execution

Exactly 8 rows in order: WebKit A1,B1,A2,B2,A3,B3, then Chromium A1,B1. New worker/browser/context for every row, no adaptive retries, no repeats until success, no PNG. All use bridge-no-filters:

1. goto origin.
2. goto origin/#EK-0131.
3. click narrative-reference containing EK-0130.
4. prior reload.
5. clear search.
6. For C01 through C05: fill search with clause ID, click article summary, click that clause anchor, verify resulting hash.
7. Final C05 target reload, then record post-state separately.

375x1000, no-preference; API/navigation 30s, worker wall limit150s, retries0. Inherited DEBUG/native stderr, action/crash/console logs and resource snapshots remain measurement interventions in both A/B. No new sampled or debugger intervention case is mixed into these 8 rows. Existing before/after resource observations are retained. Execution-classifier/evidenceState behavior is inherited unchanged from v2; tests include historical counterexamples (pre-target assertion, post-observation timeout, EVENT_LIMIT and truncated collection).

Before launch: static article/reference/clause uniqueness tests, exact input HTML/hash and plan written to new evidence folder. GitHub checkout uses actual PR HEAD and full history; existing guard and old/new unit tests run before any browser experiment. Guard is unchanged. Local connector snapshot unit checks are not represented as a local Git-history guard execution. Remote guard failure prevents the experiment.

## Build identity and native evidence

Ubuntu24.04, Node24, Playwright1.56.1/WebKit2215. Historical v2 original artifact14012381321 (run43369669701) was downloaded again and matched official 1,483,631 bytes and SHA256 49b68ab0b1246da3a236a67da9b00ab72301a9dde351b5702ada6413d5641457; all-entry CRC succeeds. Historical executable identities came from its result.json rows21/22 (ordinary launcher from row01). Pin full-byte SHA256 for pw_run.sh, MiniBrowser, WPEWebProcess and libWPEWebKit-2.0.so.1.7.0 in the runner. A mismatch stops before browser trials; do not claim identical build from revision alone. Record current build IDs/hashes. System libraries/runner image can differ and are not certified identical by these four hashes.

GDB availability is checked using command -v before trials. No spawn gdb ENOENT repetition, ptrace relaxation, sandbox disable, core dump, whole environment dump or symbol downloading. The current preparation environment has no GDB. Native stack and renderer termination remain NOT_OBTAINED in this payload-only experiment; if Actions has GDB, record availability without an unregistered attach. A separate preregistered intervention/nonintervention comparison is still needed for native capture. Launcher exit is never renderer exit.

## Failure and evidence contract

Classify same-signature target assertion, pre-target assertion, other page crash, precondition/reload timeout, not-comparable, incomplete and no-reproduction separately. Target-started/completed are separate fields. A route failure must not overwrite an observed pre-target native assertion with NOT_COMPARABLE. Absence of a signature is not collection success. Watchdog, output limits, spawn failure or remaining descendants stop later slots (NOT_RUN); preserve all raw failures. stdout4MiB/stderr8MiB/events4MiB per row. Native signature does not prove root cause identity.

Use child-only dedicated Temp and new evidence/webkit-isolation-v3. Estimated new output256MiB, including input copies/log headroom, excludes package/browser installation. Before execution require2GiB free and1024 free inodes plus a write probe. Workflow records filesystem capacities; do not delete other Temp/files. Record generated file count/bytes and final capacity. Preserve old runners, tests and artifacts.

Upload a separately named original artifact, with manifest HEAD/tree/source bytes. Afterwards verify API metadata/digest, original ZIP bytes/SHA256, all CRC and internal manifest, input/runner correspondence independently. Windows uses a new folder under existing preservation destination, with independent actual-byte readback; offline means PENDING for new evidence only.

## Interpretation and exit

Three nonreproductions do not establish a fix or universal necessity/sufficiency. If A reproduces and B does not, report a limited dependency on input membership/size/rendered arrangement, not a root cause. If B reproduces, three records are a smaller candidate route; next comparison is removal of only style from that B fixture in a new fixed plan. If A fails to reproduce or either route is incomplete, report the limitation rather than extending trials.

No product HTML/data/schema/formal16 expectations/timeouts/end criteria/acceptance workflow/Pages changes. No merge, Draft removal, publication, main commit or branch deletion. New commit-triggered CI is distinguished from unchanged-CI manual reruns (none requested). Product fix proposals require evidence, and are not applied here.
