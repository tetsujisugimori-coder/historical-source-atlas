版: 1.0 / 作成日: 2026-11-15 JST / 審査基準: 640ce033963837ad0b96ba70830ad7bb4c0f8c2c (tree ee292d4f42fef239ff8ab6dca6d51d08299b51e3)。内容SHA-256は manifest.sha256 を参照。これは設計審査であり実装・実測承認ではない。

# PR35: 保証Bの方式・環境成立性の事前審査

## 判定

設計記録・不足条件の整理は完了候補。実装可能性は条件付き、Bの実証はUNKNOWN、環境成立性BLOCKED、実測承認なし。全体PARTIAL / ABA HOLD / 正本取り込みNO / Draft維持 / 製品受入FAIL / WebKit根本原因UNKNOWN / マージNO。今回は対象生成・制御・メモリ照会、テスト実行、実GDB、ブラウザ、signal、CI実行すべて0。Aの過去限定PASSをBへ昇格しない。

## 基準と参照範囲

|参照|HEAD / tree|今回の確認|
|---|---|---|
|正本PR35|97ce39e8cb9ea38967354aea11cac2282097d7cf / b7370577c706aa70f9eebd80e96ef8ee4f73d93e|APIとlocal、open/Draft、未merge。指定値一致|
|GitHub隔離候補|8ea8d6820abaf14d3deb34beca090ebe771a5981 / 57485fa53465e21fcd3041dae445dcbab92dab08|API、指定値一致|
|既存local基準|2596dbc24078cbb26d473ca949ce8080b1cbf25a / 91114a4e3269e873cdaa16c62a93d747c6cbd4ff|実物あり、未pushを保持|
|ABA最終local|640ce033963837ad0b96ba70830ad7bb4c0f8c2c / ee292d4f42fef239ff8ab6dca6d51d08299b51e3|実物source・計画・試験・独立reviewを読取り。再実行なし|
|文書branch開始main|3e56d13d77048d056e79c6971e6e7d24ad92b4ff / bf87c376f7cf86e45cf309feebe1eb15e5684b0f|mainを変更せず専用worktreeへ分岐|

一次指示: [今回review5911267147](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/35#pullrequestreview-5911267147)、[直前報告6896053371](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/35#issuecomment-6896053371)、[PR本文](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/35)。今回review自体は640のGitHub実物未取得による報告レビュー。今回はlocal640の実物を読めたため、読取りコードレビューも範囲に含む。ただし新しい実行結果ではない。

local640の `diagnostics/webkit-isolation/PLAN-native-ABA.md`、`native-image.cjs`、`native-gdb.cjs`、`native-stack.cjs`、`test-native-aba.cjs`、既存各test/fixture、前回 `REVIEW-final-640ce.md` を参照。実物コピー・SHA・Git帰属は今回workspace証拠に保存。root AGENTS/README適用。既存worktreeは変更しない。

## 文書構成と提出境界

- [Bの主張と失効](claims.md)
- [方式比較・循環・仕様根拠](methods.md)
- [環境適格性台帳](environment.md)
- [次工程の有限計画と回帰](validation-plan.md)
- [証拠契約・保存・提出](evidence.md)
- [独立レビュー](independent-review.md)

文書branchは現mainから作成し、未push2596/640も既存隔離branchも祖先へ取り込まない。差分はこのディレクトリのみ。PR base mainの別Draft PRで文書のみ提出しPR35へリンクする。正本branch/main変更・cherry-pick・mergeなし。追加コードpush HOLD。

GitHub APIの登録workflowは3件で、canonical branchのnative workflowも登録済み。ただし現mainおよび今回文書branchの実ファイルは2件のみ。canonical nativeはpull_requestのdiagnostics/webkit-isolation/**等path対象で、今回文書pathは対象外。登録一覧とbranch実ファイルを区別した。現mainのworkflowはacceptance(push/pull_request/dispatch)とpages(pull_request/dispatch)の2つ。Draftだけでは実行抑止にならないため全提出commitに `[skip ci]`。PR_target/workflow_run等の非対象イベントなしを原文で点検した。[GitHub公式skip仕様](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs)に従いpush/PRを抑止し、実際のrun/jobを読取り確認する。pending/skippedをCI PASSとしない。workflow変更、dispatch/rerunはしない。
