# Native stack v1: independent four-slot diagnosis

Start a29b4cecd009c2d76ebb1d51f227b570ad52510a (review-only change from v6 HEAD187810113b4e02de5cd465fb53f6f43cc3d04576). Product/root UNKNOWN and formal WebKit FAIL remain. Existing PR35 branch only. No product, data, formal contract, guard, Pages or old evidence changes.

## Input and intervention
Actual v6 original ZIP14130888601 Library readback supplies B:101900bytes, SHA256d2989329db626bf06f26f3db5bedd951d9cd2edbfeb1da1867c481311508c1d1. Commit these exact bytes; every run also compares preserved Git derivation. No HTML transformation. Playwright1.56.1/WebKit2215, four v6 fixed executable hashes/build IDs required. API/navigation30s, viewport375x1000/no-preference, same preceding20 actions/reference transitions/prior reload/target C05 reload. Debugger intervention only occurs after the preceding20 operations and before target reload.

## Fixed four slots and finite bounds
1 WebKit without debugger;2 WebKit with debugger;3 WebKit without debugger;4 WebKit with debugger. Each fresh worker/browser/context. No pilot browser, repeats, replacement or added slot. Trial wall180s (includes debugger acquisition/collection), GDB total45s, API30s unchanged. Worker stdout4MiB/stderr8MiB/events4MiB; GDB combined2MiB; TERM then KILL after2s. No locals/core/memory collection, core limit0. Reserve2GiB/1024inodes, estimate256MiB diagnostic plus formal artifacts/readbacks3GiB. Dedicated task Temp; no deleting other or older files. Log truncation/timeout/remaining children is not successful stack collection and stops further slots.

## Mandatory non-browser preflight
Before any browser: installed official distribution GDB version; attach to a bounded small Node child created by the same parent as GDB (sibling attach, matching real topology); attach stopped handshake and identity recheck, resume running handshake, induced SIGABRT, bounded raw stack, pass-through continue and actual exit notification. No ptrace_scope/security permission changes, no sudo debugger. Any missing permission, identity or mechanism => BLOCKED and all4 NOT_RUN. GDB availability alone is insufficient. Review and commit precede this run; local unit/fault controls do not launch browsers.

## Identity/signal evidence
Unique WPEWebProcess descendant PID, PPID/ancestor chain, /proc startTicks and executable SHA, loaded WebKit library SHA/build IDs checked before and after attach. Missing/multiple/PID reuse/build mismatch fails closed. MI token response plus stopped notification required; continue ^running and *running before reload. Capture SIGABRT stopped notification separately from pass-through continue and actual exited-signalled/group exit. PID disappearance/launcher exit is not renderer exit signal. Raw frames/offsets/functions/lines and symbol build-ID validation remain separate; stripped/unavailable symbols UNKNOWN. No debugger or symbol-server network lookup in the trial.

## Classification
Preserve pre20 completed,target reached/start/completed,post-state,signature,evidence separately. MATCHING_NATIVE_ASSERTION,PRE_TARGET_NATIVE_ASSERTION,OTHER_PAGE_CRASH,NOT_COMPARABLE,PRECONDITION_TIMEOUT,RELOAD_TIMEOUT,OTHER_ERROR,INCOMPLETE,NO_REPRODUCTION,NOT_RUN/BLOCKED. Native attach/ready/stop/stack/pass/exit each explicit status. NO_REPRODUCTION requires completed reload/post-state and no related errors; intervention nonreproduction is not a fix or proof of root cause. Same signature is not proof of same cause.

## Pre-execution review and controls
Independent review before browser, resolve blockingP1/P2 then commit fixed plan/code. Fault controls: denied attach,wrong/reused PID,build mismatch,missing/invalid JSON/log,early exit,missing stack,output limit,timeout and order/retries. Guard normal and protected-byte rejection. Existing workflow is repurposed to native only so this push cannot rerun v6; formal PR/push and legacy auto jobs remain separate. Result reports use comments not another experiment-triggering push.

## Evidence/stop
Capture actual submitted HEAD/tree, event synthetic merge SHA separately, run/attempt, exact execution source/input/plan, stdout/stderr/MI/events/result/build IDs. Raw artifact ZIP unchanged Library save, actual separate readback, independent bytes/SHA/CRC/manifest. Formal source missing at runtime is post-produced supplement only. Access/retention UNKNOWN unless verified; Windows optional. Native symbols/line info may be NOT_OBTAINED. Root UNKNOWN, Draft, mergeNO, publishNO. Root cause and product fixes require a separate decision.
