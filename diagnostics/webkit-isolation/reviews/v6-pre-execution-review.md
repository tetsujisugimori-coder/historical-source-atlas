# v6 independent pre-execution review

2026-11-14 UTC. Separate implementation/review agent. No browser launched by reviewer. **Pre-execution review PASS; no unresolved blocking P1/P2**. Commit plan/code after this review and before the fixed experiment.

## Actual archived baseline
Fresh Library materialization of `libfile_07c96a2e3434819193e1ce51906a309d`, v5 original artifact 14113285605, 367660 bytes, SHA256 `9cdfa210376f3a2d3aaee8991d10048158c707f21b3f5bf6d32337e38f340603`. Independent opening checked all 71 ZIP CRC entries and 70 manifest size/SHA records. Manifest HEAD a2e587b36e4809d0b1f7ac2ea1d56ee7ec075099/tree a404d38fc23a0c52624bc22724017e90d731e7f5. All four saved B inputs are 101957 bytes/SHA846a8c922565486c61236518a1120d8b3a2de14fbd40e13644905686038a7927. New committed baseline equals these actual bytes.

## One-factor/plan review
Read PLAN-v6.md, full runner delta, test-v6.cjs, workflow, unchanged guard. Independent A/B transformation and VM branch checks: 57 expression bytes at [100145,100202) removed, semicolon retained, inverse reinsertion exact. B is 101900 bytes/SHAd2989329db626bf06f26f3db5bedd951d9cd2edbfeb1da1867c481311508c1d1. Both valid/missing article and document-clause/non-clause branches keep return/render behavior; only target scroll callback differs. The alternate document.getElementById(target).scrollIntoView() remains. Worker function is byte-identical to v5, including measurement, 20 actions, timeout and post-state path. Eight slots/order/no retries, four executable hashes, normal motion and viewport unchanged. No product or formal workflow changes.

## Finding V6-P2-01 and same-input correction
Initial collector added unconditional events.jsonl reading. A worker launch failure can save result.json without events: ENOENT would abort the collector; malformed JSON similarly throws. Reported before execution. Implementation added readEvents and preserves classification while marking event loss INCOMPLETE. Independently reused missing-file and malformed-file inputs: initial reading throws ENOENT/SyntaxError; revised reader records INCOMPLETE without throwing. Empty events, previously silently accepted by parsing, now INCOMPLETE. Normal events and pageerror detection remain accepted. Worker timing unchanged.

## Verification
Independent aggregate Node run: 38/38 PASS. Independent mutation copies of order/retry/worker are rejected by intended assertions, not startup errors. Guard normal passes; injected out-of-scope path and protected HTML hash each rejected. Source mismatch, absent/duplicate target, unknown variant, syntax/inverse bytes, missing post-state, pageerror/cleanup errors and each build mismatch have normal/fault contracts. Existing classifier compatibility retained except stricter incomplete-evidence rejection. No browser pilot or retry.

## Limits
This approves the fixed experiment, not its future results or product acceptance. Runtime artifacts, build match, trial completeness and independent Library readback must still be audited. Native stack/renderer signal not obtained; root UNKNOWN. Retention/access UNKNOWN. Formal WebKit failure must remain separate from diagnosis collection success. Local review logs and baseline audit are retained outside Git for later supplemental archive.
