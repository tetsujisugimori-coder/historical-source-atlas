# PR #35 Linux WebKit cause isolation, frozen plan v1

2026-11-13. Review 5885493109. Diagnostic only; product fixes need separate approval.
Remote start HEAD 0338e39629880eab89602abd33e0f44d697f27df / tree 851fff0606d5b66eff2c26b754b3d6b1e680eff4.
Current main 3e56d13d77048d056e79c6971e6e7d24ad92b4ff. Pre-diagnostic 542751d9ac327a3d869d383fe75de373e8aec9d1.
All three fixed commits are materialized by `git show`, not branch names. A new process/browser, isolated HTML file and child-only Temp for every trial. Same Ubuntu 24.04 runner, Node 24, Playwright 1.56.1/browser installation throughout one job. Actual versions/executable hashes recorded. The historical Windows worktree is offline and has not been inspected or modified; a fresh Git clone is used, clean at starting HEAD.

## Frozen sequence

`isolate.cjs` DOC/PLANS are the machine-readable authoritative sequence, saved before launch.
28 trials, one run per row, no adaptive retries or stop-after-success. First two blocks repeat main/pre/current WebKit (6), then each Chromium (3), original current bridge (1), current sampled (1), six reduced fixtures × 2 WebKit (12), tiny/native Chromium (2), no-focus/no-scroll (2), final GDB attachment case (1).
375×1000, no-preference, headless; API/navigation 30s, child 150s watchdog. A watchdog, output overflow, spawn failure or remaining process group stops later planned slots (NOT_RUN). No expectation or timeout changes to formal acceptance.

## Common route and comparison limits

Common route: goto → C01..C05 each search fill → summary native click → clause link native click → hash equality → target reload. No screenshot, timing waits or extra pre-reload state evaluate in ordinary cases. Actions are logged outside the page; DEBUG pw:browser and console/crash listeners are measurement interventions in all cases. Post-reload state is diagnostic, not proof that every formal assertion passed. Sampled case adds process/resource sampling and one pre-reload evaluate, compared with unsampled current rows.

This route is a reduced diagnostic, not the exact previous formal prefix: exact text/summary/focus/overflow checks between clicks are omitted. The bridge adds the previous B13 prelude before the common route (not applicable to main). Differences are reported; if this no longer reproduces, do not claim the old failure disappeared. Both 542751d and 0338e396 have identical product HTML blob6292e2ea4cb1c4bcccae82bab06c78c9ef523603. Main has 129 instead of 131 records and immediate fragment restore, while PR has load-delayed restore, so main/PR is a multi-factor baseline, not proof of a particular cause.

## Reduction graph

Original → one-record retains only EK-0120 in embedded payload/provenance; filters and rendering code retained. one-record → no-css removes style only. no-css → tiny replaces Atlas with standalone synthetic details/5 sections, search rerender, pushState, scroll/focus and load restoration; this large transition is explicitly not one-factor. Tiny → no-restore removes load restoration only. Tiny → no-focus or no-scroll removes the respective call only. Tiny-direct uses goto with C05 fragment and no prior interactions. Native-only uses native anchor navigation, no click interception/rerender/load restoration: combined contrast, not one-factor. Screenshot absent in all cases. Store all exact served HTML hashes; diagnostic fixtures never replace product files/data.

## Native evidence

Ordinary rows preserve native stderr and DEBUG process messages. Sampled/GDB rows additionally capture only own descendants (PID, parent, start time, executable path/hash/build ID), bounded ps/resource/cgroup data. No full environment dump, arbitrary system logs or core dumps. GDB, only if already available, attaches to exactly one observed own WebKitWebProcess; ambiguous/missing candidates mean NOT_OBTAINED. Separate intervention case; bounded 45s / 2MiB debugger, TERM then 2s KILL and close/reap, with 24-frame per-thread stack request, debuginfod disabled. No sudo, ptrace relaxation, sandbox disable or symbol download. Permission refusal remains a blocker; no alternate bypass. Only validated build IDs and actual frames may support symbolized-stack claims. Launcher exit is not renderer exit.

## Classification and evidence

MATCHING_NATIVE_ASSERTION requires optional:479, _M_get, unsigned long, engaged assertion and failed tokens. Matching signature does not prove same root cause. PRE_TARGET_NATIVE_ASSERTION is kept distinct when target reload was not reached. Missing completed/finished fields become INCOMPLETE, never non-reproduction. OTHER_PAGE_CRASH, PRECONDITION_TIMEOUT, NOT_COMPARABLE, LAUNCH_BLOCKED, RELOAD_TIMEOUT, OTHER_ERROR and NO_REPRODUCTION are separate. Missing result/output overflow/watchdog is incomplete evidence, never PASS. Product gate is not replaced by collection status. Native stack/renderer exit remain NOT_OBTAINED unless logs substantiate them.

Store fixed inputs, plan, executed script, actions/results/stdout/stderr/native metadata and manifest in a separate diagnostic artifact. Official API digest/ZIP SHA256/CRC/internal manifest and source are independently read back after CI. Windows historical archive is not overwritten; new evidence uses a new subfolder when reachable, else PENDING with raw artifact handoff. Old evidence remains unchanged. Full formal 16 conditions/data/acceptance workflow/Pages remain byte-identical; only new diagnostic scripts/workflow/docs.
