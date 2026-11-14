# v5 independent pre-execution review

2026-11-14T11:51:35Z. Reviewed by independent baseline/code auditor, not the implementation author. **Limited pre-browser review PASS; no blocking P1/P2 found.** This is not product acceptance or execution-result approval. Root cause UNKNOWN; formal WebKit acceptance FAIL; Draft/merge NO remain.

## Direct checks
- Read review 5904134358 and the existing Library-refetched v4 original ZIP in a separate process: 307043 bytes, SHA256 `d4ab03426c731e51301e7591fe316dabd121ad16b3f23dd95a2d2d2e19a5f191`, 53 CRC entries, 52 manifest files, HEAD `276161af58b1041fea92eb645f826ab4ab653015` / tree `3d77f8dc814d0412e12e69ed54919a95545f7c33`. This was not a new Library download; previous readback bytes were re-audited.
- All four archived v4 B inputs are byte-identical to v5 A: 101991 bytes, SHA256 `11dc7201c04c2c4fe271f2a64774a5b3a1512de201cb046f5fb58bd7c428da14`.
- Independently derived v5 B by deleting only `[100251,100285)`, the 34-byte expression `target.focus({preventScroll:true})`. B is 101957 bytes, SHA256 `846a8c922565486c61236518a1120d8b3a2de14fbd40e13644905686038a7927`. Semicolon retained deliberately: otherwise `return true` would become conditional and introduce a second change.
- Executed `--check` only (no browser), then compared every one of the eight generated inputs against these independent bytes. Fixed order and condition/engine allocation matched.
- Re-ran all old/new unit tests: 32 PASS, zero fail/skip. Confirmed wrong source, absent/duplicate expression, no-transform prevention, classifier/post-state requirements, four executable hashes, and saved build-mismatch summary with eight NOT_RUN rows.
- Worker function is byte-identical to v4. Existing instrumentation, reference/prior-reload/clauses/target-reload path, 30-second API and 150-second worker limits are unchanged; no retries.
- Guard passed on normal candidate. A separate disposable fault clone with a product-HTML change was rejected with exit 1 and the exact out-of-scope path, not a timeout or launch failure. Actual product files were not mutated.
- Workflow changes only select v5 tests/diagnostic runner/artifact. Formal acceptance, product/data/Pages remain unchanged. Actual workflow source is included in the evidence copy.

## Reviewed byte identities
| File | SHA256 |
|---|---|
| PLAN-v5.md | `0f5c4aae94928fc19b0bf8e4312d763beaed1eda8b45e1ba13ec493e4333f84a` |
| isolate-v5.cjs | `9a1368897f52029a86cc9c477a90ea0161eb8133ef8a7ffddcf2c10811346161` |
| test-v5.cjs | `04160d5df6edbbc2042e8c11603d615ccf97bd65dc7f69cb56542da19822fa6b` |
| .github/workflows/webkit-isolation.yml | `32da81c118c77e28ec03184bc38cdb9e95c7e972be745ebe24b4796e44fdf5c4` |

Commit these reviewed bytes before starting the fixed eight slots. Result/ZIP integrity and current-HEAD formal CI still require post-execution independent audit. Native stack/renderer signal remain NOT_OBTAINED; Library access scope/retention and Windows are not verified here.

Audit logs and JSON are retained separately under the v5 independent-audit evidence directory. A preliminary message had a hand-count typo (33/101958), corrected by byte computation to 34/101957 before this review; it was not a browser failure or changed experimental condition.
