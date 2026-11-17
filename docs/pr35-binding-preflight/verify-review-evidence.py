"""Read-only byte/lineage audit. Policy approval is an externally reviewed input.

No output files, network calls, extraction, backend, or process control. A PASS
means consistency with pinned inputs, never legal authorization or B evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile
import zlib


def digest(data):
    return hashlib.sha256(data).hexdigest()


def crc(data):
    return f"{zlib.crc32(data) & 0xffffffff:08x}"


def load(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("duplicate JSON key: " + key)
            out[key] = value
        return out
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique)


def local(root, name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or ".." in p.parts or "\\" in name or ":" in name:
        raise ValueError("unsafe relative path")
    out = root.joinpath(*p.parts).resolve(strict=True)
    if not out.is_relative_to(root.resolve()):
        raise ValueError("path outside evidence root")
    return out


def check_bytes(data, record):
    if type(record["bytes"]) is not int or record["bytes"] != len(data):
        raise ValueError("size mismatch")
    if record["sha256"] != digest(data):
        raise ValueError("SHA-256 mismatch")
    if record["crc32"] != crc(data):
        raise ValueError("CRC32 mismatch")


def audit(root, ledger, head, policy=None):
    """policy must be separately reviewed and hash-pinned by the invoking auditor."""
    if ledger["version"] != 1 or ledger["head"] != head:
        raise ValueError("ledger HEAD/version mismatch")
    rows = ledger["artifacts"]
    by_id = {}
    seen = set()
    for row in rows:
        aid, path = row["id"], row["path"]
        if aid in by_id or path in seen:
            raise ValueError("duplicate artifact")
        for field in ("purpose", "producer", "retrieval", "verified_at"):
            if not row[field]:
                raise ValueError("missing artifact attribution")
        if row["head"] != head and row["head"] not in ledger["support_heads"]:
            raise ValueError("unregistered source HEAD")
        data = local(root, path).read_bytes()
        check_bytes(data, row)
        if row["kind"] == "git":
            actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if actual != row["blob"]:
                raise ValueError("Git blob mismatch")
        elif row["kind"] not in ("external", "zip"):
            raise ValueError("unknown artifact kind")
        if row["kind"] == "zip":
            with zipfile.ZipFile(local(root, path)) as archive:
                names = archive.namelist()
                entries = row["entries"]
                if len(names) != len(set(names)) or set(names) != {e["path"] for e in entries} or len(entries) != len(names):
                    raise ValueError("ZIP entry set/duplicates mismatch")
                for entry in entries:
                    payload = archive.read(entry["path"])
                    check_bytes(payload, entry)
                    if archive.getinfo(entry["path"]).CRC != int(entry["crc32"], 16):
                        raise ValueError("ZIP directory CRC mismatch")
                # Existing original ZIPs carry their own exact-set manifest.
                internal = json.loads(archive.read(row["internal_manifest"]))
                if "head" in internal and internal["head"] != row["head"]:
                    raise ValueError("ZIP internal HEAD mismatch")
                if "tree" in row and internal.get("tree") != row["tree"]:
                    raise ValueError("ZIP internal tree mismatch")
                files = internal["files"]
                expected = [f["path"] for f in files]
                if len(expected) != len(set(expected)) or set(names) != set(expected) | {row["internal_manifest"]}:
                    raise ValueError("internal manifest set mismatch")
                for entry in files:
                    check_bytes(archive.read(entry["path"]), entry)
        by_id[aid] = row
        seen.add(path)
    if not rows:
        raise ValueError("empty inventory")
    closed = set()
    for closure in ledger["closures"]:
        if closure["id"] in closed:
            raise ValueError("duplicate closure")
        closed.add(closure["id"])
        for key in ("finding", "reason", "scope", "residual_unknown"):
            if not closure[key]:
                raise ValueError("missing closure rationale/scope")
        for key in ("before", "after", "review"):
            if not closure[key] or not set(closure[key]) <= by_id.keys():
                raise ValueError("missing closure evidence link")
    if closed != set(ledger["required_closures"]):
        raise ValueError("closure inventory mismatch")
    # Never infer permission from a destination name or a ledger's PASS label.
    custody = "BLOCKED"
    if policy is not None:
        approval = policy["approval"]
        if not all(approval[k] for k in ("record", "approver", "approved_at", "reviewer", "scope", "destination", "privacy")):
            raise ValueError("incomplete external approval")
        if approval["decision"] != "APPROVED" or set(approval["artifacts"]) != by_id.keys():
            raise ValueError("unapproved destination/scope")
        stored = policy["readbacks"]
        if {r["artifact"] for r in stored} != by_id.keys() or len(stored) != len(rows):
            raise ValueError("readback missing/duplicate")
        for receipt in stored:
            if receipt["destination"] != approval["destination"] or not receipt["retrieved_at"] or not receipt["acquisition_record"]:
                raise ValueError("readback provenance missing")
            if not receipt["actor"] or not receipt["storage_actor"] or receipt["actor"] == receipt["storage_actor"]:
                raise ValueError("independent actor missing")
            if receipt["artifact"] not in by_id:
                raise ValueError("readback artifact mismatch")
            a = local(root, by_id[receipt["artifact"]]["path"]).read_bytes()
            b = local(root, receipt["path"]).read_bytes()
            if a != b:
                raise ValueError("readback bytes mismatch")
        custody = "PASS"
    return {"content": "PASS", "custody_consistency": custody,
            "artifacts": len(rows), "closures": len(closed),
            "limits": "Policy semantics, approval authenticity, actor independence and retrieval path require external review; no B/implementation/measurement acceptance."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path)
    p.add_argument("ledger", type=Path)
    p.add_argument("--head", required=True)
    p.add_argument("--ledger-sha256", required=True)
    p.add_argument("--policy", type=Path)
    p.add_argument("--policy-sha256")
    args = p.parse_args()
    try:
        if digest(args.ledger.read_bytes()) != args.ledger_sha256:
            raise ValueError("unpinned ledger")
        policy = None
        if args.policy:
            if not args.policy_sha256 or digest(args.policy.read_bytes()) != args.policy_sha256:
                raise ValueError("unpinned approval policy")
            policy = load(args.policy)
        result = audit(args.root, load(args.ledger), args.head, policy)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["custody_consistency"] == "PASS" else 1
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, RuntimeError) as exc:
        print(json.dumps({"content": "FAIL", "custody_consistency": "BLOCKED", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
