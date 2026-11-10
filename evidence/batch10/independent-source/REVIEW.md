# Batch10 independent source review

Result: PASS for the scoped source/data review. No blocking correction requested. This is not a historical-fact certification, base-image collation, or browser acceptance result.

Reviewed implementation HEAD b528a4a against main f823640. Read repository AGENTS.md and the fixed Wikisource chapter ei-10, ending immediately before ei-11. No implementation file, remote state, merge, deployment, or browser session was changed.

## Source and segmentation

All twenty units EK-0083–EK-0102 were read in source order and compared with their summaries. Independent lexical HTML extraction confirms the chapter text and concatenated full_original_text cover the complete narrative without gaps, overlaps, repeated spans, or the next chapter. Heading is correctly excluded from articles. The saved text deliberately preserves variant readings/return marks; this is not a diplomatic transcription verified against scans.

The twenty-unit division is defensible: castle description, encircling dispositions, narrator evaluation, surrender, three distinct consultation speakers, stalemate, order to attack, attack, fire/collapse, three distinct captures, Koga attack, head inspection, arrival, killing, display of heads, and attendants' religious retirement. Captures and undated aftermath are not silently dated from neighboring paragraphs. Alternative finer subdivision is possible but is not required by the current narrative-unit policy.

EK-0086 explicitly identifies the motive inferred by 「とそ見し」 as the narrator's interpretation, not the individual's established intent. EK-0093 preserves uncertainty in 「如何成野心の者のしたりけん」 and does not name a culprit. Its initial wording describes outbreak, while the second sentence preserves the source's arson framing without certifying agency. EK-0098 correctly removes the long 大草紙 textual-boundary annotation from narrative_text, preserves it in full_original_text and annotations, and does not treat it as independent historical corroboration. Page markers and ○〔以下大〕 are independently matched to raw-source annotation spans. Inline variant readings remain visible and are explicitly labeled as retained, not mistaken for separately attested events.

## Dates and preservation

Independent review code imports no application/test modules. Five NAOJ day pairs were parsed from the saved EUC-JP HTML table rows and each response's Julian/Gregorian declaration checked. The six dated records match both endpoints, with 嘉吉元年 and contextual month/year supplementation disclosed. Fourteen remaining records have NULL absolute dates; duration/retrospective expressions are not converted. The source's 永享十三年 / 改元嘉吉 wording and 長の刻 spelling remain visible rather than silently corrected.

All 82 prior records (2,952 values) were compared to git main f823640, not merely the newly committed baseline. All 102 records retain the 36-field schema. Independently reconstructed SQLite chapter/edition joins and HTML payload agree with JSON, including boolean normalization. Existing evidence and prior publication layers are additionally covered by the implementation's seven batch10 tests, which passed when rerun by this reviewer.

Eight independent negative controls rejected joint ledger/source-text tampering, an old-value change, propagated undated dates, wrong dated end, a missing record, duplicate ID, boundary gap, and omitted editorial annotation. Importantly, joint ledger/record corruption is checked against raw HTML, not just against the duplicated ledger record.

## UI and remaining limits

Static UI review confirms separate raw transcription, narrative text, editorial annotation/page-marker labels, unresolved current-view state, and unrecognized historical status. JSON payload and publication rendering code were inspected. Actual browser layout, interaction, responsive screenshots and exports are outside this review; parent is running the serial browser suite.

Wikisource live access was reported 403; this review validates the preserved revision 218476, not a successful present-day fetch. Base scans, variant witnesses, personal identifications, modern locations, and historical recognition remain unverified. NAOJ correspondence does not establish the real historical day of any event.

Non-blocking inherited issue: metadata.transcription_note still says full text was not transcribed, although later batches carry full text for selected articles. This predates batch10 and should be clarified in a separately scoped metadata cleanup rather than rewriting preserved prior article values.

Artifacts: check.py (independent oracle and fault controls), results.json (machine results), test-batch10.log (seven implementation tests rerun).
