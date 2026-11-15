# PR35 工程A runner堅牢化の独立レビュー

対象基準HEAD: `429c2319da69456133f998c9ddfb80a238957016` / tree `773b2ad904a53127de7a270281f8b9af856c7c35`。
担当: 実装担当・7分類ハーネス担当とは別のレビューagent。対象はこの基準からの診断専用working tree差分と、以下の実物source SHAで固定した合成検証。レビュー記録追加後のcommitを実Linux診断の実施HEADとは扱わない。

## 判定

**工程Aの実装・合成検証は限定PASSを支持する。提出コードについて、確認範囲に未解決P1/P2なし。総合PARTIAL、native BLOCKED、製品受入FAIL、根本原因UNKNOWN、Draft・マージNO・公開NOを維持する。**

指定Archiveの保存はPermissionError13でBLOCKEDのまま。実GDB接続・実ブラウザ・実Linuxのプロセス停止/再開/signal引渡しを認定するレビューではない。工程Bの開始承認にはならない。

## 直接確認と独立実行

- AGENTS.md、nativeの計画・準備文書・前回レビュー、native-gdb/native-evidence/native-lifecycle/native-stack、固定fixture/台帳/比較ハーネスと追加テストを読んだ。
- 同じ7fixtureのbyte数/SHAが台帳、修正前、修正後で一致することを別プロセスで再計算した。修正前sourceは基準HEADのGit blobを直接取得して `before-source-exact/native-gdb.cjs` と全byte一致。最終修正後source SHA、同じハーネスSHA、各比較JSONのSHA、原票inventory全ファイルのbyte数/SHAも直接再計算した。
- 正式比較は案件領域の `before-final-isolated/` と `after-final-shared-budget/`。同じ固定入力・同じハーネスを使用し、隔離CLIの実OS exit codeをVM返値から求めたrequested codeと区別して確認した。全14件でOS終了signalはnull。比較ハーネスには実wall 60秒の外枠もある。
- 独立で `node --test diagnostics/webkit-isolation/test-native-stage-a.cjs` を再走し **30/30 PASS、実exit0、stderr0**。対象6sourceのbyte実物を `independent-final-shared-budget/source/` へ保存し、実行中にsource変更がないことを確認した。実プロセスやsignalの操作部分はVM内の模擬実装である。
- root/GDB両Evidenceを通じたevent/resultの各合計1MiB、GDB stdout+stderr合計2MiB、小子各64KiBを、正式7件の実保存byte合計でも検算した。最終7件のeventは1,205〜9,446bytes、result記録は13,952〜27,918bytesで、全件上限内。
- tracked差分はnative-gdb/native-stackの診断コード、追加ファイルも診断配下に限定。製品・記事データ・正式条件・guard・3workflowを緩和する差分は確認していない。自動起動経路は残るので、提出はskip CIを必須とし、実run/job不在はpush後に別途確認する必要がある。

## 同一7入力の独立照合

|入力|修正前 / 実exit|修正後 / 実exit|確認した改善|
|---|---|---|---|
|正常|PASS / 0|PASS / 0|誤拒否なし。既存result上書き2回→0回|
|接続拒否|BLOCKED / 1|BLOCKED / 1|原拒否応答とcapture概要/原票参照を保持|
|PID・同一性不一致|BLOCKED / 1|BLOCKED / 1|不一致拒否と失敗capture概要を保持|
|必須通知欠落|BLOCKED / 1|BLOCKED / 1|応答だけで成功とせず有限停止|
|timeout|BLOCKED / 1|BLOCKED / 1|期限とcleanupを分けて記録|
|出力上限|BLOCKED / 1|BLOCKED / 1|保持/破棄byteとtruncated、不完全性を明示|
|途中終了|BLOCKED / 1|BLOCKED / 1|GDB code7と小子cleanupを分離|

修正前にfault6件で欠落していた概要captureは修正後全件に存在。修正後全件で原票上書き0。正常の仮想経過19ms、通知欠落/timeout各45,004ms、他fault5〜10msで、実時間のGDB接続結果ではない。

## 指摘・同反例による解消確認

P1は検出していない。レビュー中の以下のP2を実装担当へ報告し、修正を確認した。

1. **stdin errorで原票を失う経路**：模擬GDB stdinへ同じSYNTHETIC_EPIPEを注入。修正前は未処理例外・概要なし、修正後はBLOCKED・概要あり。`independent-review-pass1/` と `pass2/`・`pass3/` に原結果を保持。stdin/stdout/stderr error監視も確認。
2. **最終保存を全体期限に含めない経路**：同じ最終summary書込に仮想70秒の遅延を注入。修正前は経過70,019msなのにPASS、修正後はBLOCKED。ScopeはEvidence作成前に開始し、保存後に解除。summaryはPENDING_FINALIZATION、別completion/最終caller verdictで判定し、summary単独で成功認定しない。completion自体の遅延・途中書込も追加テストで確認した。
3. **cleanup成功と原票完全性の混同、保存上限のスコープ**：cleanupCompleteを分離し、truncated/破棄/保存失敗/下位capture不完全をevidenceCompleteに反映。receipt生成前にも不完全性を反映する。root/GDBのevent/resultは共有budgetとし、summary・completion・failure/deadline receiptを同じresult上限に含める。部分書込/重複保存/両scope合計上限の対照を確認。
4. **native失敗をcollectedへ昇格する経路**：同じ合成JSONでnative.error=SAVE_FAILED、classification BLOCKED、evidenceComplete=falseを与えた。修正前collectRowはevidence COLLECTED、修正後はINCOMPLETE・明示stopReasonとなる。目的reloadの観測分類NO_REPRODUCTION自体と、証拠完全性を区別した。`independent-integration-pass1/`〜`pass3/`。
5. **startTicks欠測同士を同一とする経路**：同じ合成/proc statをPPIDまでで切り詰めた。修正前はstartTicks未取得でもPASS、修正後は `startTicks missing or invalid` でBLOCKED。`independent-stat-pass1/`・`pass2/` には入力を作るprobeとsource実物も保存。PID/PPID/startTicks検査を同期/非同期で共通化したことを確認。

工程Aの30対照（固定7入力を含む）ではTERM後2秒KILL、残存未確認、未所有entryのsignal拒否、環境commandの5秒/128KiB、各stream境界、部分書込・completion失敗、通知欠落、正常受理、PID再利用・path/hash/build不一致も確認した。全反例で実OSのsignalを送ったわけではない。

P3のハーネス外枠停止条件は、case CLIのwall timeout60秒追加と実signal null確認で解消。固定JSONのbyte保持はfixture配下.gitattributesで明示し、実装sourceはLFで最終Git内容と照合できる形にした。

## レビュー対象sourceのSHA-256

|source|SHA-256|
|---|---|
|native-gdb.cjs|c5a2ef943d9306cfcd66e15027d9299929e6d930d4c9ebc4594516e5ecb92498|
|native-evidence.cjs|dddc96e87728907653a056d4d5f2d7a268e7e2f2ed98791a2b5363705f6d2c90|
|native-lifecycle.cjs|a166dfad0a660c42f4ff2ccf957c6c38f2ccc07f30dee6a660aeb87bd845dedb|
|native-stack.cjs|66ae5cd39587d18935202df1b60596e472b0c35f230ea579c21cc655adc15a1b|
|stage-a-compare.cjs|4d9cbac5668a5cc5e016ffa2cf59d345ec060403ba7d2d8375921fa80eb10b45|
|test-native-stage-a.cjs|5cc99d3d8085289a7e0f6e2b9260246f65087a96d5040458ddc0f0ff37d0434a|

独立原票: 案件専用 `../pr35-stage-a-evidence-20261115/independent-final-shared-budget/`、`independent-final-comparison-audit.json`。実装担当の自己再検算と別の担当・別プロセスによる確認である。

## 残る制約・工程B

- 実GDB attach・ブラウザ・旧native4枠は0。Windows上のVM合成試験であり、正規Linux権限、実rendererの祖先/同一性・signal/実終了、WebKit hash/build ID・debug symbolsはNOT_TESTED/NOT_OBTAINED。工程Bは別環境確認・別固定計画・事前独立レビューが必要。
- 同期OS I/O自体が停止した場合の物理的な強制中断を今回保証していない。保存後の単調時計チェックで期限超過をPASSとして返さないことを検証した。summary/receiptはcaller最終判定を要し、欠落・部分保存・deadline-exceededを成功と扱わない。実機の60秒運用は認可済み環境で別検証が必要。
- 指定Archive新規先へのmkdirがPermissionError13となった `final-validation/archive-probe.json` を直接確認した。恒久保存・保存後再取得は未完了/BLOCKED。workspaceのこの検証原票を恒久保存成功へ昇格しない。保全上の既存P2は外部条件として残る。
- 本レビュー時点では最終commit/push・新HEADのrun/job確認・最終ZIP全体の独立保全監査は未実施。親担当の最終報告と、その後の実物監査で補う。旧4原ZIPの再監査はしていない。中間レビューprobeの一部は実行時source SHAのみで、最初のsource全byteを保存したと主張しない。基準before sourceと最終sourceの実物は別途保持している。

2026年11月15日 20:53 JST
