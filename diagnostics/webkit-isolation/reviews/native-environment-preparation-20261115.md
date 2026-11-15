# PR35 native環境準備の独立レビュー

対象: PR35、開始HEAD `c29cfcc2c130c65cb4cc93eac859aac2dc025139` / tree `193227045ec328d556ef5d45b05e56952eb8625e`。
担当: 実装・調査担当と別のレビューagent。確認日時: 2026年11月15日 20:11 JST。

## 判定

文書だけの環境調査・未実施条件の報告として受入可。今回の新規文書に確認範囲でP1/P2なし。**総合PARTIAL、native診断BLOCKED、製品受入FAIL、根本原因UNKNOWN、Draft維持・マージNO・公開NO**を支持する。接続許可・診断成功・次回実ブラウザ開始の承認ではない。

## 直接確認した範囲

- AGENTS.md、新規 `ENVIRONMENT-native-preparation-20261115.md`、既存PLAN-native.md、native-gdb.cjs、native-stack.cjsのpreflight gate/実行物固定値、acceptance/native/Pagesの3workflowを読んだ。
- Git HEAD/treeを独立取得し開始値と一致。開始HEADに対するprototype、workflow、native実行コード、guardのtracked差分なし。新調査文書はuntrackedの状態でレビューした。既存実験HEAD c54a6c2から開始HEADまでのtracked差分が既存レビュー文書1件であることも確認した。
- checkout外案件領域のinventory.jsonと22件のstdout/stderr原票を読み、全原票の実byte数が台帳と一致することを別プロセスで確認。PRのHEAD/branch/Draft、repo runnerのtotal_count0、過去jobのubuntu-24.04/GitHub Actions runner名、WSL未導入案内を原票から照合した。SSH設定なし等は調査担当の取得記録の範囲で、別ホスト走査をしていない。
- Windows通常実行やMSYS readelfをLinux ptrace診断と同等扱いしていない。CLIや接続toolの不在からホスト全体・組織全体のLinux不在を断定していない。過去hosted runnerを現在接続可能な候補に数えていない。
- 固定4SHAはnative-stack.cjsと一致し、新測定値でないと明示されている。preflight/ブラウザ0件、7分類のbefore/after未実施、既存61検査を今回の結果にしない記載は妥当。
- 次回非ブラウザ仕様は対象のsibling/共通祖先関係、1候補1回、全体60秒・GDB45秒等、出力上限、個別通知と実終了判定、失敗時BLOCKED、非既存案件保存先・容量・移管条件を定義している。実rendererの中間launcherとの差を明示し、小子PASSをrenderer成功へ昇格させない。
- 3workflowは変更していないが、無印pushなら正式/legacy/nativeブラウザが自動起動し得る。文書commitに`[skip ci]`を指定し、push前メッセージ・remote整合確認、push後run/job読取確認を行う方針は必須。今回レビュー時点ではcommit/pushは未実施で、その結果までは確認していない。

## 未解決・開始前の必須条件

1. 認可済みLinux候補、一般ユーザー権限、正規sibling attach許可、実行物hash/build ID、保存・転送先は未確保。候補の具体的ID/出力絶対パスを記入した固定計画・コードの再レビュー前にpreflightを開始できない。
2. 既存native-gdb.cjsは新仕様の全体60秒watchdog、小子出力上限、環境採取、単調時刻・残存確認・保存失敗処理を全て実装したrunnerではない。SIGABRT送信直前の同一性再確認も次回実装・反例で明確にする必要がある。
3. 接続拒否で`capture.ready`がrejectするとpreflight.jsonへのcapture収録を通らず、別gdb/native-result.json参照が必要になる。文書はこの不足を正しく残している。今後修正する場合は成功/拒否/PID不一致/通知欠落/timeout/上限/途中終了の同一7入力を別保存先でbefore/after比較すること。今回この挙動を実行再現していない。
4. 既存コードは同一outDir内のnative-result.jsonを複数回書くため、次回の「原票非上書き」要件は新規出力ディレクトリの確保だけで満たしたとせず、追記イベントや段階別snapshotと最終派生summaryを区別する設計が必要。今回既存ファイルや旧原票を変更した証拠はない。
5. `archive-destination-probe.json`を追加で直接読み、指定Archive配下の新規案件先作成がPermissionError13・directoryCreated=falseで失敗した原結果を確認した。Windows恒久保存・保存後別再取得はBLOCKED/未実施であり、workspace ZIP/readbackの自己照合では解消しない。原結果の確認であり、別担当がmkdirを再試行したわけではない。最終HEAD/tree、skip CIのpush後確認はレビュー時点未完了で、担当の最終追補が必要。

これらは次回の実行を止める条件であり、今回の文書提出を実ブラウザ実行許可へ読み替えない。正規接続確認前のため別ブラウザ計画を未作成/開始不可とする判断は適切。

## 限界

ブラウザ・GDB・native preflight・Linux依存テストを実行していない。workflow dispatch/rerun、commit/push、権限変更、製品変更なし。旧原4ZIPやLibrary実物、今回の最終保全ZIPを再取得・SHA/CRC/manifest監査していない。22原票のbyte数照合は旧原証拠の再監査・Windows恒久保全の独立監査ではない。GitHub connector失敗・CIM拒否・証明書取得の経緯は調査担当の説明と継承文脈であり、その初回原ログを今回別取得したとは主張しない。

2026年11月15日 20:11 JST
