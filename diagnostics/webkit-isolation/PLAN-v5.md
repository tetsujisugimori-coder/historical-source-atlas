# v5: focus call only, fixed before execution

Diagnostic only; product acceptance FAIL and root cause UNKNOWN remain. PR #35 stays Draft, merge NO. Baseline v4 HEAD 276161af58b1041fea92eb645f826ab4ab653015 / tree 3d77f8dc814d0412e12e69ed54919a95545f7c33. Latest remote at start matches; clean baseline checkout. Original v4 ZIP is independently checked, not regenerated.

## Exact input contract
A is exactly archived v4 B (three articles EK-0120/EK-0130/EK-0131, sole style element removed): 101991 bytes, SHA256 11dc7201c04c2c4fe271f2a64774a5b3a1512de201cb046f5fb58bd7c428da14.
B removes the unique 34-byte expression `target.focus({preventScroll:true})` at byte range [100251,100285). The semicolon is retained as the empty conditional statement: deleting it would accidentally make `return true` conditional, a second factor. B: 101957 bytes, SHA256 846a8c922565486c61236518a1120d8b3a2de14fbd40e13644905686038a7927. Reinsert removed bytes and compare the entire input. Wrong source hash, absent/duplicate expression stop, no automatic repair. Product HTML remains untouched. Retain article order/provenance/DOM/restoration/scrollIntoView and all other bytes. No focus compensation.

## Frozen slots
1 WebKit A1; 2 WebKit B1; 3 WebKit A2; 4 WebKit B2; 5 WebKit A3; 6 WebKit B3; 7 Chromium A1; 8 Chromium B1.
Each slot separate worker/browser/context. Retries 0; no replacement/addition. Stop leaves remaining slots NOT_RUN. No local browser pilot. CI runs this one fixed comparison, not v3/v4 again.

## Environment and procedure
Reuse byte-identical v4 worker. Playwright1.56.1, viewport375x1000, normal motion, API/navigation30000ms, worker150000ms. Preserve reference navigation/prior reload, 5 clauses, target C05 reload, post-state. All four WebKit executable hashes unchanged from v4 (EXPECTED_WEBKIT in source); mismatch prevents all trials and records actual identity. Ubuntu24.04 image version, Node, OS, HEAD/tree/run/attempt recorded; equal four hashes do not prove entire environment equality. No new screenshot/sampling/debugger. Native stack and renderer exit signal remain NOT_OBTAINED.

## Classification and collection
Record pre-actions complete; target reload started/completed; signature match; post-state obtained; collection independently. Categories MATCHING_NATIVE_ASSERTION, PRE_TARGET_NATIVE_ASSERTION, OTHER_PAGE_CRASH, NOT_COMPARABLE, PRECONDITION_TIMEOUT, RELOAD_TIMEOUT, OTHER_ERROR, INCOMPLETE, NO_REPRODUCTION, LAUNCH_BLOCKED. Preserve v4 signatures/error ordering, but explicitly reject absent post-state as INCOMPLETE (previous classifier allowed finished without post-state). No reproduction requires completed reload, post-state, no error; not product PASS. Inoperable input is NOT_COMPARABLE or appropriate precondition timeout, not success. Same native signature does not establish same cause; removing focus may affect focus/scroll/event ordering/WebKit internals.

## Stops and protection
Existing guard unchanged; formal16 tests/expectations/timeouts/Pages/data/product untouched. Independent pre-execution review, all blocking P1/P2 resolved, commit plan/code before browser. Wrong source/build/unknown scope, permission/capacity failure stop safely. Minimum2GiB/1024inodes; dedicated nonshared Temp; no old-file cleanup. Estimate256MiB diagnostic, about600MiB new formal ZIPs plus separate readbacks (allow3GiB). Initial workspace38GiB free; measure before/after in runner. Output/watchdog/descendant limits retained; do not retry stopped trials.

## Evidence
Save actual inputs, transformation offsets/removed bytes/hash, source copies including imported runners, plan/results/events/stderr, resource and run identity. Manifest every file. Preserve raw diagnostic and new PR/push formal ZIPs unmodified, official digest/size/SHA/CRC/internal manifest, save Library then fresh bytes independently verified. Access range/retention/Windows separate UNKNOWN or NOT_TESTED. Previous evidence remains immutable. Formal acceptance separate, evaluated at submitted HEAD, never inferred from diagnostic collection success.
