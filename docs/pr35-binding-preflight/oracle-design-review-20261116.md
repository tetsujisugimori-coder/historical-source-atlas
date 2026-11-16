版1.2 / 2026-11-16 JST / 基準文書HEAD134c5133d0d04892ec0f0ff0e9d2ee50fedb2f98。内容SHAはmanifest.sha256。以下は新規の独立静的原票掲載（LF表記）。workspace原票の実bytes/SHAは別保全し、旧independent-review.mdを上書きしない。

# 独立設計レビュー最終: oracle・入力・環境成立条件の具体化

担当 /root/oracle_spec_independent_review。新仕様の作成/補訂担当とは別agent/別プロセス。主担当の自己評価を採用せず、AGENTS、文書基準134cと実差分、docs配下全14file、初回案と補訂案を読み、同じ静的反例を再審査した。backend/アプリ/原テスト実行・対象生成/制御・実proc/メモリ照会・GDB/browser/signal・CI/権限操作は0。repo文書編集・commit/push・投稿もこの原票時点で行っていない。

基準HEAD134c5133d0d04892ec0f0ff0e9d2ee50fedb2f98/treeaea16bc285391a21c68934f02c143cb18de30b86。審査実物は independent-final-proposed-source/ と同SHA台帳。これはcommit前提案版の静的レビューで、最終commit/manifest/追加review文書/GitHub実blob/ZIP/投稿は後続別照合が必要。旧independent-review.mdは134c Git blobと全byte不変を独立確認し、旧結論を転用しない。.github/prototype/AGENTSの差分なしも確認。

## 総合判定

**文書仕様は、実装可能性を審査する資料として限定受入可能。総合PARTIAL。** 初回P2-D1/D2とP3-D3、途中のP3-D4について文書補訂を確認した。確認範囲で新規P1なし、未解決の新規文書P2/P3なし。ただし取得機構・TCB/source receipt・死亡policy等の実成立は未検証の必須条件であり、実装/実測/B実証の課題を閉鎖していない。

|判定軸|独立判定|
|---|---|
|文書仕様の限定受入|可能（提案実bytesの静的範囲、最終Git/manifestは後続）|
|oracle設計成立性|O-KはTCB/D境界を限定した条件付き参照設計。O-GはHOLD。TCB自体を含む完全oracleではない|
|oracle実取得可能性|UNKNOWN。通常権限/host/K/O/FD-transfer/read receipt実体が未取得|
|backend実装開始承認|未承認|
|実環境成立性|BLOCKED|
|保証B実証|UNKNOWN、実測0|
|恒久保全|BLOCKED。workspace原票の存在を恒久保全としない|
|実測開始承認|未承認|
|製品受入|FAIL継続|
|PR36マージ|NO、Draft維持|
|PR35マージ|NO、Draft維持/正本取り込みNO|

native BLOCKED / ABA HOLD / Stage A総合PARTIAL / WebKit根本原因UNKNOWN / 追加コードpush HOLDも維持する。

## 初回反例の補訂再確認

### P2-D1: cross-boundary object bridgeと実read由来

初回はO/Dが別々にopenし局所tokenを持つだけで、その同一object性の具体的比較手段がなかった。反例は同じSHA/build IDの別B_objへexecした後にDが旧A_objを保持し、局所token番号や同byteだけを一致とするもの。

補訂oracle-contract:44–52はKが停止下kernel exe/map_filesを一回openしてpin保持、SCM_RIGHTSで同じopen file descriptionをO/Dへ交付する。Dから実ancillary FDを返し、O内でO保持pinとKCMP_FILE比較、別object/別open/旧FDは不一致FAIL。FD本文整数やtoken自己申告は信用せず、MSG_CTRUNC/欠落/余剰FDは拒否、source/lifetime/nonceを結ぶ。kcmp等の取得不可はUNKNOWN/BLOCKED、事前ならNOT_READY、新capsを付与しない。同inodeでも別open descriptionを同一扱いしない点は[kcmp](https://man7.org/linux/man-pages/man2/kcmp.2.html)と整合する。

単なる返却FD一致では実derivation sourceを証明できない追加懸念も確認した。50はtrusted実read boundaryからsource OFD、各offset/要求/返却length、chunk/fullcopy digest、run/case/task/generation/epoch/pin/nonceのreceiptを発行し、proofと固定payloadを結ぶことを必須にする。新FDを返すだけで旧Bufferへ新receiptを貼る経路は拒否し、その交付/derivation境界が確定・検証されるまでsourceUNKNOWN/正常full受理不可と明示。よって初回反例を文書上成功扱いしない条件は整った。

ただしこれはtrusted reader/adapterをTCBとする設計契約であり、その実装やDの実read経路を今回証明していない。TCB内部の実object取得や任意に虚偽FD/payloadを作るDまで検査したとの主張は禁止。Dの世代/集合/lease追跡をKへ移して範囲を縮小しない注意も維持される。実backendがこの境界を提供しない場合はUNKNOWN/NOT_READYのままである。

### P2-D2: tracer死亡時kernel動作と終了回収

初回の反例はK死亡→kernel自動detach/restartであり、紙上のlease失効だけでは対象の物理的継続を防げなかった。

補訂backend-environment-gates:39–45/evidence-cleanup-contract:46–52は、kernel/ptrace modeの死亡動作、出生所有対象に限定する終了又は復帰policy、その別承認/期限、Sの合法なwait-parent/adoption/reap経路を実行前に要求する。policy/終了確認手段が不明ならNOT_READY。PTRACE_O_EXITKILLは未承認候補であり、設定/実行/承認されていない。K死亡を対象の実死亡とみなさず、pidfd保有/pollをwaitid終了情報取得権に昇格しない。ECHILD等は終了UNKNOWN/cleanup BLOCKEDとする。

[ptrace](https://man7.org/linux/man-pages/man2/ptrace.2.html)のtracer死亡/restartとEXITKILL仕様に対して、起こり得る窓を運用文だけで消したと主張していない。初回反例が実行前NOT_READY又は実行後BLOCKEDとなる条件を明記したため、文書不足は補訂確認。ただし実際の死亡policy/待機/有限cleanupの成立は未証明、実測開始不可を維持する。

### P3-D3: phase returnとD/Kの持続性

oracle-contract:76とcleanup追補で、R consumer return1、新proof consumer return0、D/K OS終了を別fieldにし、R→注入→V→新proofのD instance/state lineage・K lifetime不変を要求。途中再起動/初期化はFAIL又は制御喪失BLOCKEDでslot終了、再試行不可。初回の「RでDを終了し、新Dの初期snapshotを追跡成功へ接続」する反例は成功不可。期待PASS/0/BLOCKED/1は変更していない。

### P3-D4: E/Mに残った別open表現

途中再読で、Kの一回openとE/Mの「Oがopen」の表現が不一致だった。補訂oracle-contract:36/38はOがkernel procを観測→Kの監査済み取得境界へopen/pin要求→K交付FD受領へ統一。局所独立openを同OFD比較へ誤接続しない文言になったことを確認した。

## 指定静的反例と集約

- resumeだけ正常・追跡欠落はK/O到達原票とD event/世代/M/T不一致でV FAIL、Rだけではcase PASS不可。
- 旧exe/ABA巻戻し/旧task・epoch誤帰属はkernel commit別pin、O世代/leaseKeyとの対応でFAIL。
- 常時空mapping、旧tuple残存、追加mapping無視はkernel M_before/after差と属性exact照合でFAIL。
- 新TID未登録/未停止中B発行はK clone/個別stop・O task集合・B発行順序によりFAIL。
- 全case常時拒否、新proof未発行は適格正常phaseのPASS/0条件を満たせずFAIL。
- 注入未到達はNOT_REACHED、oracle取得不能/破損はUNKNOWN/BLOCKED、どちらも故障検出PASSへ昇格しない。
- R/V/newproof/不完全停止中B発行0/原票/予算/cleanupをAND集約しUNKNOWN/PENDINGを真にしない。L/Mを別lane/source/結果へ分け、M成功をL/Bへ転用しない。

これらは机上の論理照合であり、18件の実行成功や実機RED/GREENという集計はしない。静的反例台帳には初回不足→同反例→補訂条件→未証明を保存している。

## 予算・入力・環境・保全の整合

L19/M4のcase ID/順序/各1回、60秒×19+5秒×4=1160秒、追加試行0を維持。Lの8/10/14/18/10秒、Mの0.5/1.5/1.5/1.5秒は配分案で、実現保証でない。追加phase/原票/cleanupを既存slot内に収められないならNOT_READY。同期I/Oやkernel終了にhardな完了保証を仮定していない。

実binary/fixture/source commit/hash/build ID、M/T実体、ack/read receipt、予算実測根拠はUNKNOWN/NOT_GENERATED。null同士を一致にしない。01/22、08/09、R/V後の適格再停止、M0の正常期待を拒否へ緩和していない。固定7正常FAIL/故障6未到達、Stage A30の17PASS/13FAIL等も不変。

通常非root/既存LSM/seccomp/ptrace/proc権限、map_files/kcmp/SCM_RIGHTS/TCB分離/全停止/不変backingは環境gate。使えない機構は不適格/UNKNOWN、root化/caps追加/保護回避なし。fs-verityの内容保護とdirectory操作を分けた08/09候補も、既存file/権限/依存closure未確認の条件付きである。O-G/GDBは独立adapter未成立のままHOLD。

保存は原laneと派生summary、生成state、取得/破棄bytes、停止要求/実終了/controller終了/FDclose/資源/残存/保存を別に記録。Archive過去拒否を保持、Vaultの役割指定を成果物Archiveの自動代替や書込成功にしない。新規workspace文書原票は一時保全であり、恒久保全/B実証は未成立。

## 後続照合

今回の提案sourceに対する静的限定受入である。最終commit後は、旧基準/既存code branch不変、変更path限定、追加review/index/manifest、Git実blobと全byte、全manifest集合/SHA、最新HEADのCOMMENT/本文/状態/受領、文書ZIP実物が生成されるなら独立読戻しを別原票で確認する。未確認項目をPASSにしない。

2026年11月16日 19:59 JST
