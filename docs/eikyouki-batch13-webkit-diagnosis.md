# PR #35 Linux WebKit診断計画

2026-11-12の本人追加承認とreview5882861692に基づく診断・証拠保存のみ。開始remote542751d、local112164d。旧4d27bf/112164dのpatch/bundle/失敗原ZIPはWindowsのatlas13-evidenceへ保全。製品・データ・正式browser_acceptance.cjs・その16条件/期待値/timeoutは変更しない。Draft維持、マージNO。

## 実行前に固定する比較

全て375×1000、通常motion。各行1回、順序固定、ケース02だけ明示反復。各ケースは新しいNode/browser、07だけ同一browserに2個のcontextを順番に作る。ケース終了後に次へ進む。診断プロセス240秒watchdogは診断にのみ適用し、発火時は以後未実施として終了（再試行しない）。正式試験のtimeoutを延長しない。

|順|比較|目的|
|---|---|---|
|01|WebKit最小経路、PNGなし|基準|
|02|01と同条件の独立新プロセス|1回の非再現で結論しない|
|03|01に節reload直前のPNG1枚だけ追加|画面取得による介入|
|04a|01に04と同じrouteを登録し、節reloadで無改変HTMLを返す|routingによるHTTP cache無効化の対照|
|04|01の節reload応答だけから初回fragment復元を除外|初期復元競合の反事実比較。先行記事reloadは無改変|
|05|正式経路全体、PNG呼出だけ抑止|前置操作の蓄積（01対05）|
|06|正式経路全体、元のPNG取得順を保持|画面取得負荷（05対06）|
|07|06を同一browserの2contextで実行|contextを跨ぐ資源累積|
|08|06と同経路でChromium|engine差の対照|

最小経路は正式コードのB13年/章/伝聞検索→0131固定リンク→0130参照→記事reload→1461年/堀越章→C01〜C05検索/本文/要約/リンク/focus/overflow→節reloadとその検査をそのまま抽出。前段の131件表示/各章フィルタ/全件export/105件詳細とPNG群、後段Back/Forward以降を省く診断であり正式受入ではない。Fullは正式ファイルを固定SHA-256で検査してメモリ内複製、engine/幅/motionだけ制限し、同一幅反復の証拠ファイル名に連番を付ける。製品HTMLの書換えはしない。04だけrouteで初回fragment処理を省いた診断応答を使い、元HTMLと変種hashを保存する。

A 初期復元は04a/04、routing副作用は01/04a、B PNG負荷は01/03および05/06、C 蓄積は01/05と06/07、D runner差は保存済Windows結果と今回Linux環境情報、E engine差は06/08とraw終了ログで評価。異なるOSの旧結果は同時比較実験ではない。native stackがなければWebKit/Playwrightの根因を断定しない。全9ケースをLinux実行前に固定する。

route登録はHTTP cacheを無効化するため04aを追加した。04と同じ登録・適用タイミングで無改変HTMLを応答する。根拠：[Playwright Page.route](https://playwright.dev/docs/api/class-page#page-route)。応答の試行・fulfilled・errorを別イベントで記録する。

04は節reloadに到達した時だけ変種を応答する。意図的に機能を省くので、reload後のopen/focus検査が失敗し得る。そのassertion失敗とpage crashを区別して記録し、正式受入の期待値は変更しない。

## 計測と限界

HEAD/tree/run/attempt、OS/Node/Playwright/ブラウザversion、限定環境情報、起動要求/起動完了/disconnect、page crash/console/pageerror、既存入力イベント、reload前後fragment/focus/scroll/details、5秒毎および節目のメモリ/空き容量/当該Nodeの子孫process RSS・VSZ・名前、Linux cgroup memory.eventsを保存。stdoutとDEBUG pw:browser stderrは別ファイルへ原保存し、終了code/signalとwatchdogを記録する。native stack・renderer終了が取れない場合はNOT_OBTAINED。生の環境変数全体・認証情報・任意のシステムログやcore dumpは収集しない。

DEBUG、JSONL書込み、resource採取、reload前後evaluateは計測介入である。各比較の共通条件だが無計測時と同一とは断定しない。03のPNGは意図的介入として区別。診断COMPLETED・非再現を技術受入PASSにしない。

診断はPRイベントだけの別job/別runner、正式acceptanceへのneeds依存なし。診断失敗はcontinue-on-errorで証拠保存へ進むが、診断欠測/失敗を結果内に保持する。正式jobの失敗は引き続きworkflow failure。共有acceptance workflowのpermissionsはcontents:readのまま。公開workflowは変更しない。

案件専用Tempを各jobの子プロセス環境に指定し、容量・書込・実際の生成先を確認。共有tmp/cacheの削除はしない。Windowsでも案件Tempと既存browser cacheの読取を明示して検証。原成果はTempではなくevidence artifactと永続Windows workspaceへ保存する。

## 証拠と終了判定

診断原artifactはreload-diagnostics-HEAD-attempt、正式はatlas-HEAD-attemptで分離。内部manifestに全ファイルhashとsource hashを持たせる。API metadata、原ZIP、API digestとSHA-256、CRC/内部manifest照合、HEAD/tree/run対応、別担当読戻しを保存する。転送不能を保存成功にしない。証拠内容は固定の公開用Atlasローカル画面と実験環境に限定し、機密情報の混入を確認する。

停止条件：容量2GiB未満、書込不可、正式ソースhash/抽出anchor不一致、watchdog、push権限拒否。追加の製品修正は次工程に分離し、今回結果はIssue34/PR35に確定度付きで記録する。
