# Independent batch09 review: public summary and reproducibility code

This directory contains only REPORT.md, this README, a compact CI summary and two review scripts. Additional local raw logs and large JSON results are not published here. They are not embedded, encoded or repackaged into these files. Official GitHub CI evidence remains in its original Actions artifact.

Verified run URL: https://github.com/tetsujisugimori-coder/historical-source-atlas/actions/runs/42742904125

Verified artifact metadata URL: https://api.github.com/repos/tetsujisugimori-coder/historical-source-atlas/actions/artifacts/13729983277

Artifact name: atlas-6ca200120dfb6731122bb3dc2370ab7c9e2c7703-1. No unverified browser deep link is provided.

Artifact ID: 13729983277. Run ID: 42742904125. Tested HEAD: 6ca200120dfb6731122bb3dc2370ab7c9e2c7703.

Original ZIP SHA-256: b6de7461d48d47d3257a16729f19d5668d86c6087258789f8497f63938973949.

## Reproduce

Use a checkout of the tested HEAD for exact reproduction. `review.py` requires the generated SQLite database, so first run the normal project build. Outputs belong in a fresh local directory, not this published directory.

```sh
python prototype/eikyouki/build.py
python evidence/batch09/review-public/review.py --repo-root . --output /tmp/atlas-independent-new
```

The review scripts are supplied in a later documentation-only commit; when checking out the tested HEAD, retain an external copy of the scripts and adjust their command paths accordingly.

Download the original Actions artifact as `original.zip` and extract it under an `extracted/` subdirectory. Then run:

```sh
python evidence/batch09/review-public/verify_ci.py --artifact-dir /path/to/artifact-directory --repo-root . --head 6ca200120dfb6731122bb3dc2370ab7c9e2c7703 --zip-sha256 b6de7461d48d47d3257a16729f19d5668d86c6087258789f8497f63938973949 --output /tmp/atlas-ci-independent-new/results.json
```

The CI script checks archive bytes, manifest hashes, source identity and recorded operation results. The visual-sample statement reflects the reviewer's original inspection; rerunning the script alone does not perform a new visual inspection. Neither script establishes manuscript accuracy, historical truth, physical Safari behavior or production deployment.
