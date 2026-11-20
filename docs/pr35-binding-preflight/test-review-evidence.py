"""Fixed synthetic evidence controls. Creates only a new caller-specified directory."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import zlib
from datetime import datetime, timezone


def sha(b):
    return hashlib.sha256(b).hexdigest()


def write(p, b):
    with p.open('xb') as f:
        f.write(b)


def packed(o):
    return (json.dumps(o, indent=2, sort_keys=True) + '\n').encode()


def meta(b):
    return {'bytes': len(b), 'sha256': sha(b), 'crc32': f'{zlib.crc32(b)&0xffffffff:08x}'}


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=False, exist_ok=False)
    verifier = Path(__file__).with_name('verify-review-evidence.py')
    head = '1' * 40
    payload = b'synthetic evidence\n'
    write(out/'payload.txt', payload)
    im = {'files': [{'path': 'payload.txt', **meta(payload)}]}
    with zipfile.ZipFile(out/'original.zip', 'x') as z:
        for name, data in [('payload.txt', payload), ('manifest.json', packed(im))]:
            info = zipfile.ZipInfo(name, (2026, 11, 17, 0, 0, 0))
            z.writestr(info, data)
    def row(aid, path, kind):
        b = (out/path).read_bytes()
        return {'id': aid, 'path': path, 'kind': kind, 'head': head,
                'purpose': 'synthetic test only', 'producer': 'fixture generator',
                'retrieval': 'synthetic, not actual permanent storage',
                'verified_at': '2026-11-17T00:00:00Z', **meta(b)}
    rows = [row('text', 'payload.txt', 'external'), row('zip', 'original.zip', 'zip')]
    with zipfile.ZipFile(out/'original.zip') as z:
        rows[1]['entries'] = [{'path': n, **meta(z.read(n))} for n in z.namelist()]
    rows[1]['internal_manifest'] = 'manifest.json'
    ledger = {'version': 1, 'head': head, 'support_heads': [], 'artifacts': rows,
              'required_closures': ['synthetic-C1'],
              'closures': [{'id': 'synthetic-C1', 'finding': 'synthetic wording',
                            'reason': 'wording narrowed', 'scope': 'static document only',
                            'residual_unknown': 'all runtime properties unknown',
                            'before': ['text'], 'after': ['text'], 'review': ['zip']}]}
    policy = {'approval': {'record': 'synthetic approval: no real permission',
                          'approver': 'test user', 'approved_at': '2026-11-17T00:00:00Z',
                          'reviewer': 'test auditor', 'scope': 'synthetic fixture',
                          'destination': 'synthetic-private', 'privacy': 'synthetic',
                          'decision': 'APPROVED', 'artifacts': ['text', 'zip']}, 'readbacks': []}
    for r in rows:
        name = 'readback-' + r['path']
        write(out/name, (out/r['path']).read_bytes())
        policy['readbacks'].append({'artifact': r['id'], 'destination': 'synthetic-private',
                                   'path': name, 'retrieved_at': '2026-11-17T00:00:00Z',
                                   'acquisition_record': 'synthetic separate retrieval',
                                   'actor': 'synthetic auditor', 'storage_actor': 'synthetic saver'})
    changes = {
        'normal': lambda l, p: None,
        'missing_file': lambda l, p: l['artifacts'][0].update(path='missing'),
        'sha_mismatch': lambda l, p: l['artifacts'][0].update(sha256='0'*64),
        'size_mismatch': lambda l, p: l['artifacts'][0].update(bytes=1),
        'crc_mismatch': lambda l, p: l['artifacts'][0].update(crc32='00000000'),
        'zip_entry_missing': lambda l, p: l['artifacts'][1]['entries'].pop(),
        'required_field_missing': lambda l, p: l['artifacts'][0].pop('bytes'),
        'wrong_head': lambda l, p: l['artifacts'][0].update(head='2'*40),
        'closure_link_missing': lambda l, p: l['closures'][0].update(review=[]),
        'unapproved_destination': lambda l, p: p['approval'].update(decision='UNKNOWN'),
        'readback_missing': lambda l, p: p.update(readbacks=[]),
    }
    results = []
    for name, mutate in changes.items():
        l, p = copy.deepcopy(ledger), copy.deepcopy(policy)
        mutate(l, p)
        lb, pb = packed(l), packed(p)
        lp, pp = out/(name+'.ledger.json'), out/(name+'.policy.json')
        write(lp, lb)
        write(pp, pb)
        command = [sys.executable, '-B', str(verifier), str(out), str(lp), '--head', head,
                   '--ledger-sha256', sha(lb), '--policy', str(pp), '--policy-sha256', sha(pb)]
        started = datetime.now(timezone.utc).isoformat()
        run = subprocess.run(command, capture_output=True, timeout=5)
        write(out/(name+'.stdout'), run.stdout)
        write(out/(name+'.stderr'), run.stderr)
        expected = 0 if name == 'normal' else 1
        report = json.loads(run.stdout)
        ok = run.returncode == expected and ((report['custody_consistency'] == 'PASS') == (name == 'normal'))
        results.append({'case': name, 'input_sha256': sha(lb), 'policy_sha256': sha(pb),
                        'source_sha256': sha(verifier.read_bytes()), 'command': command,
                        'started': started, 'finished': datetime.now(timezone.utc).isoformat(),
                        'exit': run.returncode, 'expected_exit': expected, 'pass': ok,
                        'stdout_sha256': sha(run.stdout), 'stderr_sha256': sha(run.stderr)})
    write(out/'results.json', packed(results))
    print(json.dumps({'controls': len(results), 'passed': sum(x['pass'] for x in results)}))
    return 0 if all(x['pass'] for x in results) else 1


if __name__ == '__main__':
    sys.exit(main())
