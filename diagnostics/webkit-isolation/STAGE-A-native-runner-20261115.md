# 工程A: native runner堅牢化と合成7分類比較

## A. 判定と範囲

実装・Windows上の合成検証は限定PASS。恒久保全BLOCKEDを分離し、工程全体/総合PARTIAL、native BLOCKED、製品受入FAIL、根本原因UNKNOWN、Draft、マージNO、公開NOを維持する。実GDB接続、実ブラウザ、実signal送信、旧native4枠再実行、dispatch/rerunはすべて0。模擬MI成功はLinux接続許可の証拠ではない。

## B. 基準と開始確認

開始local/remote HEAD `429c2319da69456133f998c9ddfb80a238957016`、tree `773b2ad904a53127de7a270281f8b9af856c7c35`。branch `data/eikyouki-batch13`、originは本repo。最新mainは `3e56d13d77048d056e79c6971e6e7d24ad92b4ff` / tree `bf87c376f7cf86e45cf309feebe1eb15e5684b0f`、Issue34 OPEN、PR35 Draft。開始時未提出変更なし。他作業を破壊せず、この工程内ではfixture/実装/独立レビューのファイル担当を分けた。
AGENTS.md/README、PR本文/Issue34、review5910440446、PLAN-native.md、環境準備文書・レビュー、native-gdb/native-stack/関連検査/3workflowを確認した。今回最終HEAD/treeはPR追補に記録する。旧実験c54a6c2の帰属は変更しない。

## C. 変更範囲

- `native-gdb.cjs`: identity/MI/失敗収録/preflight全体期限を修正。
- `native-evidence.cjs`: exclusive保存、byte上限、原票/summary/完了記録分離。
- `native-lifecycle.cjs`: 単調deadline、所有ChildProcessだけの停止/残存判定、環境command上限。
- `native-stack.cjs`: native保存失敗/不完全をcollectRowで伝播。製品・操作経路・正式timeoutは不変。
- `stage-a-fixtures/`: 固定7入力とbytes/SHA/期待結果台帳。`.gitattributes`でJSON原byteのCRLFをGitでも保持。
- `stage-a-compare.cjs`: 隔離Node CLIの実exitとVM内mock MI/時計/identity比較。各CLI実wall60秒、VM仮想90秒/2万step、初期評価5秒の試験側上限。
- `test-native-stage-a.cjs`: 30合成・故障対照。専用の絶対 `ATLAS_STAGE_A_TEST_ROOT` 必須。
- 本報告と独立レビュー。製品HTML/採録/正式16条件・期待値・timeout/guard/workflow/Pagesは変更なし。

## D. 実装と読み取り規則

全体deadlineは単調時計で開始/待機/終了/最終保存を含め60秒。56秒で未完を中断し、残り4秒をTERM→2秒後必要時KILL→最大2秒のclose確認に予約する。GDB45秒、環境command各5秒/128KiB。所有ChildProcessのオブジェクト以外へのsignalを拒否し、PID全体kill/process.killは使わない。exit/close/各signal要求・成否・残存を記録。停止不能はBLOCKED。

GDB stdout+stderr合計2MiB、小子stdout/stderr各64KiB、root/GDBを通じたイベント合計1MiB、summaryと全receiptを通じた結果記録合計1MiB。結果内にreceipt用32KiBを予約する。上限到達（等号を含む）はBLOCKED。received/retained/discarded/truncatedを記録し、書けたprefixを破棄しない。

PID/PPID/startTicks必須形式、exe path/size/SHA/build ID、必要libraryを照合。attach直前・停止後・SIGABRT要求直前に再照合し、UTC/単調時刻を記録する。startTicksの両側欠測を一致としない。接続拒否でもfinallyでcaptureを概要へ収録し、`gdb/native-result.json`とcompletionを参照する。stack/renderer終了は未取得を明示し、GDB exit0/cleanup signalから推論しない。

原stdout/stderrはbinary prefix保存、到着順/offsetは追記JSONL。`gdb-mi.log`は互換用結合記録で、元の2streamとイベントを一次参照とする。ファイルはすべてexclusive新規作成。既存outDir/重複保存を拒否し、途中書込の部分原票は残して別failure記録にする。原summaryは一度だけ書く。

**summaryの `status:PENDING_FINALIZATION` / proposedStatusだけで成功認定しない。** summary SHAを参照する `*-completion.json`、欠測/部分書込/期限超過記録、原stream counters、呼出元が保存後に取得する最終返値/exitを併せて読む。completion自身も `requiresCallerFinalVerdict:true`。保存後期限超過・失敗は最終返値BLOCKEDとなり、可能なら新規失効記録を残す。summary/receiptの先行値を上書きして過去を隠さない。native-stackもhelper error/不完全を収集成功へ昇格させない。

Node単一プロセスから停止中のOS同期I/Oをhard中断できるとは主張しない。70秒の模擬保存遅延では復帰後BLOCKED、先行summaryはPENDINGを保つ。実LinuxでのI/O・signal・ptraceと絶対wall停止精度は未検証であり、接続許可とともに工程Bで別確認が必要。

## E. 同一7入力のbefore/after

入力は実装変更前に固定、全SHAは `stage-a-fixtures/ledger.json`。基準ソースはGit blobからbyte exact取得。同じ確定harnessで `before-final-isolated` / `after-final-shared-budget` に保存し、各caseを隔離Node CLIで実行した。以下のexitはその実OS exit code（模擬targetのexitと別）。時間は仮想時計である。

|分類|bytes|before/exit|after/exit|after仮想ms|修正差|
|---|---:|---|---|---:|---|
|正常|731|PASS/0|PASS/0|19|受理維持、結果原票上書き2回→0|
|接続拒否|742|BLOCKED/1|BLOCKED/1|10|原拒否応答+概要capture+原票参照|
|PID不一致|795|BLOCKED/1|BLOCKED/1|9|不一致拒否+概要capture|
|必須running通知欠落|775|BLOCKED/1|BLOCKED/1|45004|応答だけで成功にしない+概要|
|timeout|765|BLOCKED/1|BLOCKED/1|45004|有限停止+概要|
|出力上限|786|BLOCKED/1|BLOCKED/1|5|truncated/取得/破棄byte+概要|
|途中終了|774|BLOCKED/1|BLOCKED/1|5|GDB exit7とrenderer未取得を分離|

旧6故障は既にBLOCKEDだったが概要captureが全欠落。修正後は全件収録、全件上書き0。上限入力はreceived2097169 / retained2097152 / discarded17。最終比較の全fixture SHA/harness SHA/原票inventory SHA/比較結果SHAを照合した。隔離CLIの実signalは全null、wall timeout発火なし。初期harness整備中のbefore/afterも削除せず、正式対称比較とは別扱いで保存する。

## F–G. 対照・停止・保存検証

最終追加30/30 PASS。正常受理、6故障、PID再利用/欠測、SIGABRT直前の不一致で送信しない、通知欠落、環境5秒/128KiB、小子64KiB、GDB2MiB、イベント/共有結果上限、所有外signal拒否、TERM→2000ms→KILL、残存未確認、EPIPE、summary/原stream/completion途中書込、重複作成、保存遅延、native不完全の後段伝播を検査。
既存の非ブラウザ48件とnative-gdb純粋関数選択5件もPASS。旧Linux `/proc`・sleep・signalに依存する8検査は今回NOT_TESTED（選択対象外）で、旧61検査全PASSとは報告しない。CI未実施。

## H. 独立レビュー

別担当が同反例でstdin例外・遅延保存の誤PASS・stat欠測の誤一致・collectRow誤昇格をRED再現し、修正後同じ反例でGREEN確認。P1なし。コードP2を解消した範囲と未検証の実Linux/恒久保全を独立レビューに記す。追加30検査と7分類の独立再検算も別原票として保全。担当自身の照合と独立照合を区別する。

## I. 保全

今回の案件領域は実在cwdと同じ綴りの `C:/Users/tetsu/Dev-Workspace/historical-source-atras/pr35-stage-a-evidence-20261115/`。以前の原票を上書きしない新規領域。原票/fixture/source/差分/RED・GREEN/レビューを保存する。Windows指定恒久先の新規 `C:/Users/tetsu/Dev-Artifact-Archive/historical-source-atlas/PR35/native-stage-a-20261115T115500Z` は容量確認後のmkdirで **PermissionError13**、directoryCreated=false。回避せず恒久保存・保存後読戻しはBLOCKED。
workspaceで最終source ZIP/Git履歴bundleと全原票を新規ZIP化し、別ファイルへ実読戻し、byte/SHA/CRC/manifest/fixture/sourceとcommit一致を自己/独立照合する。最終ZIPのbyte/SHA/件数と実提出HEADはPR追補に記載し、workspace照合を指定Archive移管完了としない。旧原4ZIPの既存完了状態を変更しない。

## J. GitHub提出・CI抑止

3workflowのpush/pull_request条件と、pull_request_target/workflow_run等の別起動経路がないことを確認。GitHub公式skip規則 https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs に従い、全提出commitへ `[skip ci]` を付ける。push前にremoteとstage/メッセージを再確認、通常pushだけを使う。確認不能ならpushせず提出BLOCKED。push後PR HEAD/Draft・run/jobを読取確認し最終追補に報告。CI未実行はCI PASSではない。workflow/guard緩和なし。

## K–L. 残件とマージ判断

工程Bは認可済みLinux・一般ユーザーの正規sibling attach許可、同Playwright/WebKit実行物4SHA/build ID、書込/再取得先、有限な非ブラウザ計画と事前独立レビューを別途確認してから判断する。今回の模擬成功から実rendererや再現性を断定しない。正式既存Chromium8PASS/WebKit8FAILを変更していない。**マージNO**。

2026年11月15日 20:55 JST
