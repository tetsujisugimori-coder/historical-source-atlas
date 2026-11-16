版: 1.1 / 作成日: 2026-11-15 JST / 補訂日: 2026-11-16 JST / 審査基準: 640ce033963837ad0b96ba70830ad7bb4c0f8c2c (tree ee292d4f42fef239ff8ab6dca6d51d08299b51e3)。内容SHA-256は manifest.sha256 を参照。これは設計審査であり実装・実測承認ではない。

# 次工程用の有限検証計画（未実行・NOT_READY）

本版は方式と故障到達性の事前登録。実装・実測許可ではない。実行可能な入力binary/backendは未生成、SHA/build IDはUNKNOWN。下記case specificationそのものは本ファイルのSHAで固定するが、実入力の固定完了を偽らない。後工程で実体・SHA・期待結果・source commit・tool/kernel・環境権限・cleanup契約を埋めた新版を独立承認するまでは全case NOT_RUN。成功するまでの再実行、待機追加、期待緩和を禁止。

## 実行前ゲート

G0 別途backend実装/制御取得/対象生成の明示承認。G1 environment全必須欄と通常権限の成立。G2 B0–5の方式・対応kernel/GDBと所有bridgeが独立審査済み。G3 固定実入力manifestとbytes/source帰属、故障注入位置とoracleの独立性。G4 正規保存/実物読戻し/容量が成立。G5 既存guard/製品保護不変、排他controller/復帰責任・hard deadlineを確認。ひとつでもUNKNOWNなら対象を作らずBLOCKED。早期拒否は後段検出成功に計上しない。

## 固定ケース順序と到達oracle

本表の22 case IDを二つの独立系列へ分ける。L系列は19 slot、順序01,02,03,04,05,07,08,09,10,11,12,13,14,15,16,17,18,21,22、各1回。初回01がB0–5へ達しなければL残りはNOT_RUN。各L caseは独立の所有probe（非browser）とfresh epoch。M系列は4 slot、順序M0,06,19,20、各1回。M0は同じadapter契約の完全正常固定bytes/FDとclose確認をPASS/0として受理する正常対照。M0失敗ならM残りNOT_RUN。Mは対象生成なしの合成backend modelで、L正常やlive B達成を前提とせず、その成功をLへ転用しない。全予定は23 slot、うちlive19/model4。通常入力は完全な適格file-backed identityと不変backing。故障は注入前の到達点、注入ack、kernel/controllerの観測、判定を別記する。注入できなければNOT_REACHED（FAILでも検出PASSでもない）。L/Mは別manifest・予算・raw・結果台帳を持つ。Lの13/14は追加のlive安全審査未成立ならその実施ゲートでNOT_READYとし、model結果で代替しない。L/Mいずれもゲート未達を他系列の故障検出へ転用しない。

|順|case/注入|到達確認（最低必要な証拠）|期待|
|---|---|---|---|
|01|正常full identity|所有/全停止/B0–5、全必要mapping、source/copy hash/ID、lease利用と正常close|PASS/0、B証明epoch内だけ|
|02|exec A→B|制御済みowned probeでexec commitイベントとimage世代変化の独立ack|旧lease拒否BLOCKED/1に加え、R/V検査とexec世代・exe対応更新の一致を必須とする|
|03|exec A→B→A|2回のexec commit、同PIDでもepoch2回更新、前後A一致|混合/旧epoch拒否BLOCKED/1に加え、2回のexecの順序・世代更新をV検査で照合。Aへの復帰で世代を巻き戻さない|
|04|exe pathname差替え|同pathの別objectを作成したack、元kernel exe FDとのobject差|元対象の正しい実体を保持/再open混合は拒否。誤正常0件|
|05|PID寿命/再利用|旧owned taskの終了と新owned handleの相違を独立観測|旧handle拒否。実PID再利用を1slot内に観測しなければlive再利用検出NOT_TESTED。PID取得までの反復/任意PID attach禁止|
|06|startTicks不一致|同入力契約の別世代値が比較器へ到達した原票（model限定）|BLOCKED/1。live PID証明と区別|
|07|library pathname差替え|元不変mappingのkernel object参照、pathが別objectへ変わったack|元objectの正しいidentity PASS/0、新pathの混合0件。前提不足はNOT_READY、取得拒否は16/18で別検査|
|08|library unlink|元mappingを残したunlink ackとmapped object参照|元objectの正しいidentity PASS/0、新実体混合0件。前提不足は実行前NOT_READY、取得拒否は16/18で別検査|
|09|library rename/move|rename ackと元mapping range/object不変の証拠|元objectの正しいidentity PASS/0、新実体混合0件。前提不足は実行前NOT_READY。pathname不一致だけで対象切替しない|
|10|library remap/dlclose|旧mapping失効イベントと新range/objectまたはunmap ack|旧lease拒否BLOCKED/1に加え、R/V検査で削除rangeの除外・新range/object/offset等の対応を照合|
|11|dlopen/追加mapping|追加commitとcoverage集合変化|旧lease拒否BLOCKED/1に加え、R/V検査で追加mappingを含むcoverage更新を照合|
|12|thread生成/未追跡thread|新TID/kernel event、controller membership|不完全coverageはBLOCKED/1・B発行0。R/V検査で新TIDのmembership更新と全停止前の新証明発行0を照合|
|13|不完全停止|対象thread一つのstop ack未達を独立確認|STOP_INCOMPLETE、B発行0、BLOCKED/1|
|14|途中resume/step|controllerに届いた実resume/step ackとepoch失効|利用拒否BLOCKED/1|
|15|対象途中終了|owned task exit通知とtask-handle終端|EXITED/BLOCKED/1、debugger exitと分離|
|16|権限不足|事前承認された通常権限の拒否oracle、同操作のerrno|BLOCKED/1、設定緩和なし|
|17|exe FD取得失敗|B取得段階の正確なopen syscall/adapter失敗記録|BLOCKED/1、取得済み原票保持|
|18|mapping FD取得失敗|必要rangeの取得失敗とcoverage欠落|BLOCKED/1|
|19|short read/破損・ID欠測|固定fixture bytes/len/hash、read到達ack（model限定）|A不完全拒否BLOCKED/1、B検出と数えない|
|20|close失敗/遅延|所有FDのclose到達と失敗/未確認ack（model限定）|完了不能BLOCKED/1、遅延結果を追記、上書き0|
|21|偽caller証明|caller boolean/偽leaseがconsumerへ到達、controllerに対応epochなし|拒否BLOCKED/1、偽装を本物oracleに使用しない|
|22|正常full identity再確認|01と同じ固定正常入力、fresh owned task/lease|PASS/0、過剰拒否なし|

04/07/08/09の固定入力は「対象は元の不変backingを実行/mapし続け、pathnameだけを差替え/削除/移動」と定義し、期待は元object/copyの正しいidentityをPASS/0で受理、新pathの実体混合0件。必要な権限/不変性が不足すれば実行前ゲートでNOT_READYとし、この正常期待をBLOCKEDへ変更しない。対応不明の拒否は17/18/権限不足16で別入力として検査する。02/03/10–12は制御した再開の前に旧leaseを失効し、再開中に変化を発生させ、再停止後に旧証明の拒否と下記の変更追跡を別々に確認する。停止lease内でexecできたと装わない。停止不完全/予期外resumeは隔離modelから始め、live制御喪失を起こす試験は別途安全審査なしに行わない。

L上限は1slot全体60秒（起動・待機・close/cleanup込み）、19slot最大1140秒。Mは各5秒、4slot最大20秒。合計最大1160秒、追加試行0。TERM/KILL等は本計画から実行権を与えない。別途許可された所有cleanup契約が全体期限内に収まらなければ開始禁止。GDB合計2MiB、child stdout/stderr各64KiB、events/result各1MiB、環境読取各5秒/128KiBを予定上限とする。上限・timeout・証拠保存失敗・未所有task・controller喪失・cleanup不明で当該系列停止、残りNOT_RUN。保存/所有/権限侵害など共通安全条件の失敗なら両系列停止。原票は取得/破棄bytes・truncated・exit/cleanup/residualの区別を保持。今回は上限を実装変更しない。

## P2-R1補訂: 再開失効と変更追跡を分ける

02/03/10/11/12の各既存slot内でR（resume失効）とV（変更追跡）を別欄に記録する。Rの成功だけではVもcase全体もPASSとしない。slot数・順序・回数・60秒上限・総予算は増やさない。必要な検査を予算内に収める実入力/backendが固定できなければ実行前NOT_READY。

- R: resume要求前に旧leaseが失効し、consumerが旧証明をBLOCKED/1で拒否すること。理由RESUMED/LEASE_REVOKEDはここだけの根拠とし、exec/remap/thread検知の根拠にしない。
- V: 注入側の独立ackとcontrollerのevent原票を、owned task参照・case・sequence・変更前後の世代/集合で照合する。注入ackをcontrollerの更新値やcaller booleanから生成しない。実入力の新版では独立ackの取得主体・取得方法・比較値を固定する。
- 02/03: exec commitごとのcontroller image世代更新、現在exe objectへの対応を照合する。03は2回のcommitと順序を保持し、最終bytesがAと一致しても古いA世代の証明を再利用しない。
- 10/11: 再停止後のkernel mapping観測とcontroller coverageをrange/offset/object/protectionで照合し、削除/追加の集合差を明示する。resumeで旧leaseを拒否しただけ、又は常時空集合を返すだけではV成功にならない。
- 12: 独立した新TID観測に対応するmembership更新を確認する。未追跡/未停止threadが残る間はB発行0。新TIDを含む全停止を改めて確認するまでは新証明を認めない。
- 新しい証明は、再停止後にB0–5を再検証できた場合だけ発行し、そのtask/image世代・mapping集合・thread集合がVの観測と一致することを検査する。旧世代/旧集合を含む証明は拒否する。完全な適格入力として事前固定した再停止状態での正常受理もPASS/0とし、常時拒否を追跡成功にしない。12の不完全停止区間のBLOCKED/1とは別phaseに記録する。
- 独立ack自体が得られず注入到達を証明できない場合はNOT_REACHED。注入到達済みなのにcontroller event/更新が欠落・不一致ならV=FAIL。適格な再停止状態で証明未発行/帰属不一致ならFAIL。R成功でこれらを上書きしない。B未成立の区間で診断を開始しない。

この補訂は文書上の検査契約。変更追跡を実証済みとはせず、実装・対象生成・実測の許可を追加しない。

## 既存回帰は別系列・今回は再走0

|系列|既存640時点の記録|回復の必要条件|
|---|---|---|
|固定7|正常はBLOCKED/1で期待PASS/0に不一致、故障6は早期B gateで未到達|正常PASS/0、故障6は各目的機構到達後BLOCKED/1。capture NOT_STARTEDを取得済みとしない|
|Stage A30|17PASS/13FAIL|同じ正常/故障契約で全期待一致。B未実装を新期待値にしない|
|非browser48|48PASS|同系列の変更影響を後工程で確認|
|純粋関数5|5PASS|schema比較をBの証明にしない|
|候補追加3|2PASS/1FAIL|旧FD mockのopen/read/fstat/close境界を新APIへ追従、正常受理・混合拒否という検査目的を維持。readelf別path取得を成功条件にしない|
|Linux依存8|NOT_TESTED|認可済み通常権限/所有/保存/実行許可を満たすものだけ。実GDB/renderer signal/browserを回帰名目で追加しない|

旧CLI88は今回成功件数へ加算しない。今回は原テスト・期待・fixture・mock一切変更なし。今後mock変更は固定bytes/hashと元の故障機構/成功条件を対照に別差分レビューする。early gateを迂回したstubだけでlive B成立を宣言しない。

## 2026-11-16 入力/oracle具体化の参照

[oracle-contract](oracle-contract.md)が02/03/10–12等の取得主体・kernel原情報・独立比較値を、[input-ledger](input-ledger.md)が全23slotの入力schemaとphase配分を、[evidence-cleanup-contract](evidence-cleanup-contract.md)が終了/close/残存/保存の別判定を定める。既存case ID/順序/期待/上限は不変更。実体/hash/予算成立根拠が未生成のためNOT_READY。静的反例は[別台帳](static-counterexamples.md)で、実行成功件数ではない。
