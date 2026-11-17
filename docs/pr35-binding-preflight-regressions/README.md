# 審査証拠検査器の E1／E2 回帰試験

基準は PR #36 の `0e74fde6b99300122a33561b838458d45ccb1169`、tree `952e5ccba917d0d45deb10ffcfbc0c0e3206bc49`。試験は既存検査器の CLI を呼び出す。fixture 内の承認・保存・再取得は合成入力。原定義と判定根拠は[独立レビュー](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#pullrequestreview-5937669837)と[提出報告](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#issuecomment-6946887909)に記録されている。

| 試験 ID | 固定反例 | 期待結果 |
| --- | --- | --- |
| P2-E1 | `fixtures/e1/`。ZIP のサイズ・SHA-256・CRC と各 entry が台帳に一致する一方、内部 manifest の HEAD が台帳の ZIP 行の HEAD と異なる。 | `ZIP internal HEAD mismatch`、`FAIL`／`BLOCKED`、exit 1 |
| P3-E2 | `fixtures/e2/`。有効な合成承認と全 byte が一致する読戻しを用意し、先頭の読戻し票の `storage_actor` を空文字列にする。 | `independent actor missing`、`FAIL`／`BLOCKED`、exit 1 |

履歴上の負対照の ledger・policy・ZIP・payload・読戻し入力を同じ byte 列で収録した。CLI に渡す ledger と policy の SHA-256 は試験内に固定している。対照では一時ディレクトリに入力をコピーする。E1 は内部 HEAD の一致、E2 は別々の非空の保存者と再取得者で `PASS`／`PASS`、exit 0 を要求する。変更後の入力に旧 SHA-256 を渡す場合、E2 で保存者が欠落する場合、保存者と再取得者が同じ場合も拒否を確認する。各拒否は exit code と構造化された判定・理由の一致を合格条件とする。

リポジトリのルートから実行する。

```sh
python -B docs/pr35-binding-preflight-regressions/test_evidence_regressions.py
```

歴史的な修正前の検査器（SHA-256 `bef369cb9163966eeefcf90f9c110218327f37a1a4e21a7882e3354c8446bf68`）を手元に持つ場合は、`--verifier <path>` で指定できる。旧版は両方の固定反例を `PASS`／`PASS`、exit 0 と判定するため、本試験は両反例で失敗する。基準版の検査器（SHA-256 `fbb2662e516eff5883c6636af6c766875e2ae48a0a2309bbbbb2157bee81bba4`）は同じ入力を期待どおりに拒否する。
