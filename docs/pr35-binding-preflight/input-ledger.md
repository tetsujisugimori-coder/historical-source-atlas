版1.2 / 2026-11-16 JST / 文書基準HEAD 134c5133d0d04892ec0f0ff0e9d2ee50fedb2f98、tree aea16bc285391a21c68934f02c143cb18de30b86。現640ゲート不変更。内容SHAはmanifest.sha256。設計案と必要条件であり、実装・生成・実測の許可/証拠ではない。

# 実入力・故障・予算の事前固定台帳

## 共通schema（設計であり実fixture未作成）

各rowは `spec_version/series/case_id/slot/order/attempt=1`、文書HEAD、将来target/K/O/D/feederのsource commit・Git blobと実file SHA、binary/fixtureのpath・byte数・full SHA256・GNU build ID・verity digestを別fieldに持つ。未生成はstatus=NOT_GENERATED、sha/build ID/size/object=null、reason=UNKNOWN_NOT_CREATED。nullを一致と判定しない。今回固定したのは文書の契約SHAであり実入力hashではない。

object欄はlabelでなくkernel由来FD pin/namespace/mount/dev/inode、version不変性、exe/mapping帰属証拠を要求。必須M集合（range/offset/prot/object/ELF segmentとの関係とdependency closure）とT集合、許容する非対象領域/除外理由を登録。ASLRを無効化しない。動的address/TID/FD値はOのrawから実行時bindingする変数としてschemaと関係を固定し、Dの値で埋めない。expected source labels A/B等を物理inode/addressと偽らない。

各caseに injection recipe/cutpoint、I/Oの別source/hash、ackのkernel原票と比較before/after、必要phase期待exit/意味上判定、必須原票一覧、stop条件、owner/cleanup契約、予算内の完了見積根拠を保存。単に「同じ入力」と書かず全descriptorをimmutable manifestに固定。source/header/fixtureが変われば新版として別承認、同attemptの都合のよい変更・無変更再実行は禁止。

全row共通の現状: target/K/O/D source commit、全実binary/fixtureのSHA/build ID/byte数、kernel object、実M/T、ack実体、予算実測根拠は**UNKNOWN/NOT_GENERATED**。検証器も未実装、入力hashの架空値なし。参照する640は現ゲートの保護基準であり新backendの実装sourceではない。

## 全23 slot（元case ID/順序/期待不変更）

|系列/順|case|予定入力family・cutpoint・oracle|固定期待/停止・cleanup|
|---|---|---|---|
|L01|01|N: 同一予定normal binary、必要file-backed Mと2thread、変化なし。O F/M/T|full正常PASS/0、失敗ならL残りNOT_RUN|
|L02|02|X: 単thread A→B、初期proof後R、exec1 commit stop、再停止。O E/F/M/T|R拒否+V一致+新正常PASS/0、同slot|
|L03|03|X: A→B→A、各commit snapshot、g0/g1/g2別。O E|02と同じ、旧g0再利用不可|
|L04|04|元不変exeを実行したままowned pathだけ別objectへ交換。O F/M/dir|正しい元object PASS/0|
|L05|05|旧owned task終了/新owned task handle、旧寿命参照。O K/S終端|旧handle拒否。実kernel PID再利用はこの1slotで観測できなければNOT_TESTED、取得まで反復しない|
|L06|07|元不変library実map中path別object差替え。O F/M/dir|元object PASS/0、新path混合0|
|L07|08|F: 同元不変libraryをmapしたままunlink。O dir+M/F|元object PASS/0、前提不足は事前NOT_READY|
|L08|09|F: 同元不変libraryをmapしたままrename。O dir+M/F|08と同じ。取得拒否の別機構は16/17/18|
|L09|10|D: 初期L_a→退役→L_b、refcount/NODELETEなしclosure固定。O M差|R+V+新Mの正常PASS/0、削除/追加tupleを両方要求|
|L10|11|D: 未ロードL_b追加。O M差/新object非空|R+V+新proof PASS/0|
|L11|12|T: 初期1thread→1追加、不完全停止と新全停止を別phase。O T|未停止中B0件/BLOCKED、更新後新proof PASS/0|
|L12|13|所有threadのstop ack欠落、事前承認されたsafe fault surface|STOP_INCOMPLETE/BLOCKED、B0件。live安全審査欠落ならNOT_READY|
|L13|14|許可されたresume/step境界の旧lease使用、O K command/ack|BLOCKED/1、live制御喪失は別安全承認なしに作らない|
|L14|15|owned task終了cutpoint、O kernel termination|EXITED/BLOCKED、GDB exit/cleanupと混同0|
|L15|16|通常既存permissionの拒否操作を事前指定、O独立errno|目的操作到達+BLOCKED/1。権限変更しない|
|L16|17|exe acquisition error境界、許可されたfault surfaceとO raw errno|目的open到達+BLOCKED/1。fault injectorが不可ならNOT_READY|
|L17|18|必須mapping acquisition error境界、O coverage/errno|目的到達+BLOCKED/1。正常08/09へ流用不可|
|L18|21|偽caller boolean/旧又は架空epoch、Oに対応leaseなし|到達後拒否BLOCKED/1、fake値はoracleでない|
|L19|22|01と同じ固定N bytes、fresh task/epoch、O F/M/T|full正常PASS/0、過剰拒否検出|
|M01|M0|固定toy bytes/FD/event入力+別の期待台帳|model正常PASS/0、失敗ならM残りNOT_RUN|
|M02|06|固定別startTicks/lifetimeをmodel比較入口へ渡す|拒否BLOCKED/1。LのPID証明ではない|
|M03|19|固定shortread/破損/ID欠測の一つの有限trace内の段階別入力|全必須不完全取得を拒否。subrecordは同一5秒slot内、回数増加でない|
|M04|20|固定FD close失敗/未確認/遅延という有限event trace|完了不能BLOCKED/1、後続close原結果追記。実FD故障注入なし|

全caseの停止/cleanupは[責任契約](evidence-cleanup-contract.md)を参照。未所有/観測破損/共通保存失敗では後続両系列を停止。case05だけの通常完了を除きL caseごとfresh owned probe、L05は同slotに所有確認した旧/新の2寿命、追加slotにはしない。

## 時間・出力・終了条件

L順序 `01,02,03,04,05,07,08,09,10,11,12,13,14,15,16,17,18,21,22`、M順序 `M0,06,19,20`。各1回、追加試行0。L19×60秒=1140秒、M4×5秒=20秒、最大1160秒。L各slotの設計配分は準備/生成8秒・初期proof10秒・R/注入/ack14秒・V/再停止/新proof18秒・保存/cleanup10秒、計60秒。Mは準備0.5・入力/注入1.5・比較1.5・保存/解放1.5秒、計5秒。これは配分案であって間に合う保証や実測ではない。

各slotの単調時計起点を最初のcase準備より前に置き、全phase/原票保存/所有cleanupまで含める。個別phaseの余剰を総期限外へ繰越さない。cleanup予約10秒を侵食するならその時点で正常phaseを停止。TERM後2秒で必要時のみ所有KILLを行う案も別許可されたcleanupに限り、この10秒/60秒内に収める。プロセスが実際に終了/解放されるhard保証は現在ないので、将来controller/OS I/O/cleanupの有限性が裏付けられなければNOT_READY。未終了のままwatchdogが返ったことをcleanup成功にしない。

原入力manifest、global環境確認、証拠容量確認、observer/source固定は実行前の独立設計ゲート。実行時の追加チェックを予算外の隠れたpreflightにせず各slot内へ含める。23slot後に無断の追加対象操作はしない。offlineの文書/ZIP配送は試行や未完了cleanupの延長でなく別作業として明示する。

GDB raw合計2MiB、child stdout/stderr各64KiB、events/result各1MiB、環境読取各5秒/128KiBという既存上限を維持。K/O原票の増加もevents内のlane別事前割当を必要とし、必要分が収まらなければ入力固定不可/NOT_READY。原byte数/取得/破棄/truncatedをbyte単位で記録、超過やtimeoutはBLOCKED。出力抑制で原票消失を成功にしない。ZIPやsourceの文書保存容量は別台帳、ここを理由にruntime上限を緩和しない。

## Source pin/死亡policy/instance固定の追加欄

各descriptorへK/O/D instance lifetime、SCM_RIGHTS source pin/receiver FD transfer receipt、KCMP_FILE oracle照合、trusted read receipt、D/K連続state lineage、K死亡時kernel作用/承認済み終了又は復帰policy、Sのreap/残存責任を追加する。これらも実物/権限/対応sourceはUNKNOWN、同じslotの予算内。R consumerのreturn1をD/K実終了と混同せず、途中再起動でVを正常化しない。
