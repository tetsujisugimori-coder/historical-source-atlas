"""Run the historic E1 and E2 inputs against the evidence verifier CLI."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile
import zlib


HERE = Path(__file__).resolve().parent
HEAD = "1" * 40
VERIFIER = HERE.parent / "pr35-binding-preflight" / "verify-review-evidence.py"
FIXTURE_PINS = {
    "e1": (
        "79581a6157a8c5bd3b72ee26633ce8d9ad724ccfc76ea4296b7ac5011d66bc3e",
        "db8a2ac4286b8508f96b93530ac0b4785fb9528ac44a11aad78d9781c0620683",
    ),
    "e2": (
        "4ac0bdc31b7b7fe9c6943060e5745b90a31e74e738980d1db47bde6335ac2bbf",
        "55db27fe25ea1f886c0f74753e5740906b934bb821a0cf3ce612ee1197096eea",
    ),
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def metadata(data):
    return {
        "bytes": len(data),
        "sha256": sha256(data),
        "crc32": f"{zlib.crc32(data):08x}",
    }


def write_json(path, value):
    path.write_bytes((json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8"))


class EvidenceRegressions(unittest.TestCase):
    verifier = VERIFIER

    def run_verifier(self, root, pins=None, error=None):
        ledger_path = root / "ledger.json"
        policy_path = root / "policy.json"
        ledger_pin, policy_pin = pins or (
            sha256(ledger_path.read_bytes()), sha256(policy_path.read_bytes())
        )
        run = subprocess.run(
            [
                sys.executable, "-B", str(self.verifier), str(root), str(ledger_path),
                "--head", HEAD, "--ledger-sha256", ledger_pin,
                "--policy", str(policy_path), "--policy-sha256", policy_pin,
            ],
            capture_output=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(run.stderr, b"", (run.returncode, run.stdout, run.stderr))
        report = json.loads(run.stdout)
        if error is None:
            self.assertEqual(run.returncode, 0, report)
            self.assertEqual(report["content"], "PASS")
            self.assertEqual(report["custody_consistency"], "PASS")
            self.assertNotIn("error", report)
        else:
            self.assertEqual(run.returncode, 1, report)
            self.assertEqual(report, {
                "content": "FAIL", "custody_consistency": "BLOCKED", "error": error,
            })

    def copy_fixture(self, case, directory):
        source = HERE / "fixtures" / case
        for name, expected in zip(("ledger.json", "policy.json"), FIXTURE_PINS[case]):
            self.assertEqual(sha256((source / name).read_bytes()), expected, name)
        return shutil.copytree(source, Path(directory) / case)

    def test_p2_e1_zip_internal_head(self):
        with TemporaryDirectory() as directory:
            root = self.copy_fixture("e1", directory)
            with self.subTest("historical input"):
                self.run_verifier(root, FIXTURE_PINS["e1"], "ZIP internal HEAD mismatch")

            ledger_path = root / "ledger.json"
            ledger = json.loads(ledger_path.read_bytes())
            zip_row = next(row for row in ledger["artifacts"] if row["id"] == "zip")
            zip_path = root / zip_row["path"]
            manifest_path = zip_row["internal_manifest"]
            with ZipFile(zip_path) as archive:
                entries = [(info, archive.read(info)) for info in archive.infolist()]
                manifest = json.loads(archive.read(manifest_path))
            manifest["head"] = HEAD
            manifest_bytes = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")
            with ZipFile(zip_path, "w") as archive:
                for info, data in entries:
                    archive.writestr(info, manifest_bytes if info.filename == manifest_path else data)
            zip_bytes = zip_path.read_bytes()
            (root / "readback-original.zip").write_bytes(zip_bytes)
            zip_row.update(metadata(zip_bytes))
            next(entry for entry in zip_row["entries"] if entry["path"] == manifest_path).update(
                metadata(manifest_bytes)
            )
            write_json(ledger_path, ledger)

            with self.subTest("matching internal HEAD"):
                self.run_verifier(root)
            with self.subTest("stale ledger pin after a byte change"):
                self.run_verifier(root, FIXTURE_PINS["e1"], "unpinned ledger")

    def test_p3_e2_storage_actor(self):
        with TemporaryDirectory() as directory:
            root = self.copy_fixture("e2", directory)
            with self.subTest("historical input"):
                self.run_verifier(root, FIXTURE_PINS["e2"], "independent actor missing")

            policy_path = root / "policy.json"
            policy = json.loads(policy_path.read_bytes())
            receipt = next(row for row in policy["readbacks"] if row["artifact"] == "text")
            del receipt["storage_actor"]
            write_json(policy_path, policy)
            with self.subTest("absent storage actor"):
                self.run_verifier(root, error="'storage_actor'")

            receipt["storage_actor"] = receipt["actor"]
            write_json(policy_path, policy)
            with self.subTest("same actor used for storage and retrieval"):
                self.run_verifier(root, error="independent actor missing")

            receipt["storage_actor"] = "synthetic saver"
            write_json(policy_path, policy)
            with self.subTest("distinct nonempty actors"):
                self.run_verifier(root)
            with self.subTest("stale policy pin after a byte change"):
                self.run_verifier(root, FIXTURE_PINS["e2"], "unpinned approval policy")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verifier", type=Path, default=VERIFIER)
    args = parser.parse_args()
    EvidenceRegressions.verifier = args.verifier.resolve(strict=True)
    unittest.main(argv=[sys.argv[0]], verbosity=2)
