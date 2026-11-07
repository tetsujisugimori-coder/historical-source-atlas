"""Read-only, type-exact preservation against the reviewed PR #5 merge.

New IDs are permitted; existing IDs and all their fields are immutable here.
Legitimate corrections require a reviewed baseline change, never an allowlist.
"""
import hashlib
import json
from pathlib import Path
from integrity import same_fields
from validation import FIELDS

BASELINE = Path(__file__).with_name('baselines') / 'existing15-pr5.json'
BASELINE_SHA256 = '9f83df390860ef1f801547d383d55666d623184f9335d55afc9dac90fb98dd58'
SOURCE_COMMIT = 'c4c69c1079af74d2dd5fc7ba1b8b6272f0488cbb'


def assert_preserved(records):
    raw = BASELINE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASELINE_SHA256:
        raise ValueError('preservation: baseline hash mismatch; review required')
    baseline = json.loads(raw)
    expected = baseline['records']
    if baseline['source_commit'] != SOURCE_COMMIT or len(expected) != 15:
        raise ValueError('preservation: invalid baseline provenance/count')
    expected_ids = {f'EK-{i:04d}' for i in range(1, 16)}
    if {r['id'] for r in expected} != expected_ids or any(set(r) != set(FIELDS) for r in expected):
        raise ValueError('preservation: invalid baseline IDs/fields')
    seen = set()
    for row in records:
        identifier = row.get('id')
        if type(identifier) is not str or not identifier.strip() or identifier in seen:
            raise ValueError('preservation: invalid/duplicate ID')
        seen.add(identifier)
    actual = [r for r in records if r['id'] in expected_ids]
    same_fields(expected, actual, 'preservation PR5')
    return len(expected) * len(FIELDS)
