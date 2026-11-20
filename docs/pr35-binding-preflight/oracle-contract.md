版1.2 / 2026-11-16 JST / 文書基準HEAD 134c5133d0d04892ec0f0ff0e9d2ee50fedb2f98、tree aea16bc285391a21c68934f02c143cb18de30b86。現640ゲート不変更。内容SHAはmanifest.sha256。設計案と必要条件であり、実装・生成・実測の許可/証拠ではない。

# 独立oracle契約

## 主体・信頼境界（実在/実取得はUNKNOWN）

|主体|責務・入力|禁止する依存|
|---|---|---|
|S: ownership supervisor|許可された生成時からtask handle/親子関係/namespace/bootと所有台帳を保持。操作対象を限定|caller PIDだけで所有を認定しない|
|I: injector|事前固定したprobeの操作recipeを一度だけ要求。別の監査用pipeにintent/returnを出す|そのpipeの「成功」だけをexec/map/threadの到達証拠にしない|
|K: trusted trace broker（TCB候補）|kernelの唯一のptrace所有者。生成時から全task/clone/exec/exitとwait原結果を採取し、全停止barrierを管理|DUTのevent/世代/集合/lease判定を参照して原票を書かない|
|O: oracle observer/recorder|Kの未加工kernel原結果と、停止下のproc kernel object観測を直接取得し、別の原票/比較器で期待を構成|DUTが提供する更新値・capture・parser・caller boolean・同じ可変Bufferをoracleに再利用しない|
|D: DUT（検査対象）|診断controllerのtask/image/mapping/thread追跡・lease状態機械・proof発行/consumer。Kのevent copyを入力に自分のstateを更新|Oの結論を自分の更新の代わりに返さない。O原票に書込不可|
|A: independent auditor|固定入力、K/O原票、D原票を別読取りし、R/V/新証明/cleanupを集約|実装担当のsummaryだけでPASSにしない|

K/Oは検査対象のDから分離した、独立にreviewされる信頼基盤（TCB）である。同じkernelを信頼する点は共有仮定で、悪意kernelやK自体の偽造耐性はこのD検査の保証外。K/Oのsource/版/実file SHA、独立parser、所有IPC/保存先、Dからの書込不能、欠落検出を別審査する。Dの追跡ロジックをKへ移して検査範囲を狭めることは禁止。実backendがK/D分離を提供しない、又は検査対象がGDB/K内部の正しさも含む場合、このoracleでは不足しUNKNOWN/NOT_READY。TCBの宣言だけでfull Bの実証にしない。

## 有限の取得構成

**O-K（参照設計候補）**: 生成時から単一のKがptraceを所有し、exec/clone/exitのkernel eventとwait statusをDへ渡す前にOへ原byte/数値を追記する。Oは別コード経路でkernel procを読み、実object pinの選択/openはKの監査済み取得境界を通す。Oは第二ptracerではない。Kが全thread停止barrierを確認し、O/D双方のsnapshot・proof比較完了までresumeを許さない。通常権限でkernel機能/参照を取得できる場合だけ成立候補。K/backendは未実装・未承認。

O-KとGDBの同時attachは禁止。GDBをsole tracerにする **O-G** は別構成であり、K相当をtrusted GDBと外部raw transport recorderへ置く必要がある。raw MIをDのparserより先に保存し、exec各commitの停止/clone全停止/イベント欠落検出をversion別に裏付けなければならない。GDBのcatch exec/catch load等の存在や単一MI停止だけでは足りず、wait rawを同時に別ptracerで取得できると仮定しない。O-Gの具体的adapterと完全性証拠はUNKNOWN/HOLD。O-Kの設計受入をGDB構成の受入へ転用しない。将来入力manifestは構成を一つに固定し、途中fallbackしない。

O-Kでも現在のC1/B0–5を解除しない。論理順序は所有P1→制御P2→停止下B再検証P3で、診断P4は別承認。今回はいずれも実施しない。

## 識別子・比較値

- taskKey = run/case + boot/namespace + S生成台帳ID + 保持kernel task handle参照。PID/PPID/startTicksは補助。数値PIDから別taskへ再bindしない。
- OはDと別にkernel exec eventの連続番号 `g0,g1,g2` を定義する。Dのimage世代をその番号へ一対一に対応付け、execごとに新世代、ABAでg0へ戻らない。thread非leader execの旧TID→現TIDもkernel eventに基づいて対応付け、未対応なら拒否。
- mappingKey = taskKey/generation + start/end/offset/protection(private/shared含む) + kernelから開いたobject参照ID。表示pathnameは比較keyでない。FDを保持する局所object token、mount/namespace/dev/inode、取得時刻、由来proc entry、byte/version証拠を記録する。dev/inodeの一致だけでkernel object対応を認定しない。
- threadKey = taskKey + TID + thread lifetime参照。T集合はKの出生/終了原票とOのproc/task集合を突合。列挙結果一致やtask state文字だけでは全停止barrierにしない。
- leaseKey = taskKey/image generation + fresh epoch + M/T集合digest + B0–5証拠参照。resume要求より前に旧epochを失効。event欠落/不明/切断も失効。時刻だけで因果順を推定せずrun/case/phase、command ID、K seq/O snapshot ID/D seqと原票参照で結ぶ。

## 観測取得レシピ

**E（exec）**: Kが `PTRACE_O_TRACEEXEC` 等の事前有効化を示し、各exec成功のkernel stop/wait原結果・必要なGETEVENTMSG結果をOへ渡す。Oはそのcommit stop中のkernel exe参照を観測し、Kの監査済み取得境界へ `/proc/<owned>/exe` の一回open/pinを要求する。OはK交付FDを受け、固定copyからSHA/build ID、別途不変backingを確認。Dのexec報告は使わない。中間Bもsnapshot完了前に次のresumeを許さない。完全な動的linker状態が整った後の再停止は別phase、exec直後snapshotだけで全library正常を主張しない。

**M（mapping）**: Iのintent/returnは補助。Kの閉じた停止区間で、O自身が `/proc/<owned>/maps` の全必要範囲を観測し、Kの監査済み取得境界へ `map_files/start-end` の実object open/pinを要求する。OはK交付FDを取得し保持する。完全なbefore/after M集合を別parserで作り、必要範囲の欠落・重複・予期しないmappingは拒否。Dの集合をOの入力にしない。kernelに実際の差がないdlclose（参照残り/NODELETE等）は到達ack未完了、NOT_REACHED。到達済みの差とDが不一致ならFAIL。取得拒否ならBLOCKED/観測UNKNOWN、PASSでない。

**T（thread）**: KのTRACECLONE等のkernel新TID/初期stop原結果と、Oの `/proc/<owned>/task` を突合する。新TIDが最初の命令を走る前のstopを含め、全既知threadの個別wait stop ack、出生/終了の未処理0、閉じたbarrierを必要とする。thread1個の停止通知、proc stateのT/t、反復列挙の一致だけは不可。独立observerにkernel原情報が届かなければUNKNOWN。traceイベント設定の意味/版/例外は将来Kの検証義務。

**F（object/content）**: O/Dは以下の同一open file descriptionを参照する別FDから、別のprivate copyを取得し、それぞれの同copyにSHA/build IDを帰属させる。copyを固定しただけでは対象がそのversionを実行/mapしている証明にならない。実対象backingの既存不変性も必要。08/09を満たす候補は、既にfs-verity有効な同じfile objectでdata書換え不能だがdirectory rename/unlinkは通常許可される構成。verity digestはfull-file SHAともGNU build IDとも別field。fs-verityの新規有効化・fs作成・設定変更は本工程で行わない。既存の通常read-only権限や後作成copyは代替証明でない。必要全library/loaderにも同じ条件を課す。

## Object pinの交付と照合（独立指摘D1への補訂）

局所FD番号/token、同path、dev/inode、SHA/build IDだけでO/D objectを同一視しない。参照構成ではKが停止下のkernel exe/map_filesを**一度open**してpinを保持し、同じopen file descriptionをAF_UNIX SCM_RIGHTSでO/Dへ別FDとして交付する。別々のproc openを同じopen descriptionと扱わない。Oの独立性は別copy/parser/照合・raw保存であり、実体選択Kは共有TCBであると明示する。

Sが出生時から登録したK/O/Dと専用socket端点を結び、peer/lifetime/command/run/case/phase/nonce、Kのsource proc entry/pin/送受信の生kernel結果をO原票に記録する。受信FDは実ancillary dataから取得し、本文のFD整数/tokenは信用しない。MSG_CTRUNC/欠落/余剰FDは拒否。Dのproofには取得source FDをSCM_RIGHTSで返す境界を設け、Oが受け取ったFDとO保持のK交付FDを `kcmp(KCMP_FILE)` で照合する（O自身のfile table内の2FDを比較、Dの可変FD番号を後から読まない）。同じopen file descriptionの複製なので正常は一致、旧exe Aや別open/別objectのFDなら不一致→FAIL。同SHA/build IDの別objectでもこの判定は変えない。kcmpのENOENT/ENOSYS/EPERM等は比較UNKNOWN/BLOCKED、事前不対応ならNOT_READY。新権限を付与しない。

共用open descriptionのfile offset競合はoffset指定のpread等で避け、K/O/Dのcloseは参照別に管理する。取得copyのsourceはKのtrusted read boundaryが発行する実FD/read原結果に基づくread receipt（pin、固定byte SHA/size、generation/epoch、command nonce）と結び、Dが任意の別copyへsource tokenだけ貼ってよい契約にはしない。Dの追跡世代/M/T/lease更新はこのboundaryへ移さず、D原票と独立に照合する。trusted reader/adapterはTCBに属し、Dの申告でなく実際のI/O境界からsource open-description、各offset/要求length/返却length、chunk bytes digest、全copy size/digest、run/case/task/generation/epoch/pin/nonceをreceiptへ固定する。proofはそのreceipt IDと同じ固定payloadのdigestを参照し、Oがsource FD比較結果とreceipt/payloadの対応を独立照合する。新FDだけを返し旧FD/旧Bufferの計算結果へ新receiptを貼る経路は拒否。単なる返却FD一致はderivation sourceの証明ではない。具体的なtrusted reader実装、固定payload交付とD derivationを結ぶ監査可能な境界が確定・検証されるまで、source帰属UNKNOWN、正常full受理不可。このread boundaryを含む実装/相互接続の監査は未実施、Dが実際に用いたread sourceをTCB receiptへ結べないbackendはUNKNOWN/NOT_READYであり完全BのPASSを出さない。

[kcmp仕様](https://man7.org/linux/man-pages/man2/kcmp.2.html)はopen file descriptionを比較し、一般の「同一inode」比較ではない。[SCM_RIGHTS仕様](https://man7.org/linux/man-pages/man7/unix.7.html)のFD参照転送を前提とする。必要syscall/ancillary/正規アクセス/送受信元と生存参照の対応は未確認。単に同UIDの別processであることやsocket上のcaller文字列を認証としない。DがK/Oのメモリ・原票・FD選択を改変できる既存環境ではTCB分離未成立としてNOT_READY（今回新しい隔離設定を作らない）。悪意kernel/TCBや任意にFDとcopyの由来を偽装できるDまでをこの設計で実証したとはしない。

## 各caseのA–J契約

下表のE/M/T/Fは上記のO取得方法/信頼境界を参照。全行のH判定は末尾の共通規則、IはK/OとD分離、Jは[環境ゲート](backend-environment-gates.md)全充足を要す。独立ackのsourceはIの自己申告でなくOのkernel観測である。

|case|A 観測状態 / B 発生主体|C/D 独立ack主体・方法|E/F 照合・世代/集合|G 正常/故障期待、個別J|
|---|---|---|---|---|
|01/22|正常owned probe、Iは変化注入なし|O:F/M/T、K全停止・S所有記録|task/g0/新epoch、全必要Mと全T、B0–5参照。22は01と同一固定入力だがfresh task/epoch|正しいfull identity PASS/0。常時BLOCKEDはFAIL。実体/hash未生成、現状NOT_READY|
|02|単一thread exec A→B。Iは1 execを要求|O:Eでkernel commit1とexe Bを直接取得|g0→g1、task寿命同じ、現exe object B、loader準備後M/Tを再取得|R旧証明BLOCKED/1、Vの追跡一致+新証明PASS/0を両方要求。B snapshot未完なら次resume禁止|
|03|A→B→A。Iは順に2 exec|O:Eを2回、g1/Bとg2/Aの別snapshotを保持|kernel commit順・個数2、D世代対応がg0,g1,g2で非巻戻し。最終A bytes同一でもg2新epoch|RとV、新証明PASS/0。中間Bを観測できない構成はNOT_READY、観測欠落はUNKNOWN/BLOCKED|
|10|library L_aを退役しL_bをmapする固定recipe（dlclose後dlopen、参照残りなし）。I/owned probeが操作|O:Mの前後差で旧tuple除外/新tuple追加を確認、I returnだけ不可|M_removed/addedをrange/offset/object/protection全部で比較。同range再利用時も旧object tupleは消え、新tupleへ。その他required mappingを消さない|R、V、新Mに対する新証明PASS/0。実際unmap未達ならNOT_REACHED、D差分欠落はFAIL|
|11|I/probeが未ロードのL_bを1回dlopen|O:Mで新objectに属する非空tuple追加とbefore保持を確認|追加closureはinputで固定、DのM_afterとOのexact required set比較|追加無視/空coverageはFAIL、適格再停止proof PASS/0|
|12|I/probeが新threadを1個生成し生存させる|O:Tのkernel clone child IDと新TIDの実在・stop ack|T_after=T_before+new、全member/barrierとB発行順序。未停止区間→完全再停止区間を別記|R、V、未停止中B発行0/BLOCKED/1、全停止再検証後新proof PASS/0。両phase必須|
|08|Iがowned directory内の元library pathnameをunlink。元map存続|Oがdirectory操作結果/元entry消失を直接取得しF/Mで同元objectをpin|M/object/bytes/versionはbefore同一、path消失を理由に別実体へ切替えない|元object PASS/0。事前permission/不変性不足はNOT_READY、実行後の正常期待変更禁止|
|09|Iが同directory内で元pathを新pathへrename、元map存続|Oが旧entry消失/新entry→元objectとF/M不変を直接確認|task/generation、M元object/version保持。pathだけ変化|08と同じPASS/0、新path別実体混合0|
|M0|非実行toy bytes/FD/event traceを固定した合成正常入力。model feederが供給|独立に手書き/レビューした期待台帳と固定入力bytes。kernel/実threadは存在しない|期待台帳はD更新で生成しない。別parserでM/T/世代/closeを比較|model正常PASS/0、M0失敗はM後続NOT_RUN。L/B実証へ昇格禁止|

## 判定/集約（H/Iの共通契約）

- `NOT_READY`: 実行前にhost認可、入力実体/hash、独立oracle手段/権限、予算等が欠ける。生成しない。
- `NOT_REACHED`: 正常に観測できた範囲で目的の事象への到達を証明できない。Iのintent/returnだけは到達でない。故障検出PASSにしない。oracle取得不能/破損は別途UNKNOWN/BLOCKEDも記録してNOT_REACHEDへ隠さない。
- `FAIL`: 到達をOで確認したのにD event/世代/M/Tが欠落・不一致、誤証明/早期B発行、又は事前固定した適格な再停止状態の正常受理未発行/拒否。単なる拒否exit1は検査成功でない。
- `BLOCKED`: 実行後の権限拒否/timeout/上限/保存/観測/cleanup不確定など、安全に完了できない状態。故障case16等では、この分類を期待する機構へ到達した証拠があって初めて検査期待一致と別記。`UNKNOWN` は未確認の事実属性でありPASSの別名ではない。
- R/V対象caseの意味上PASS条件は、R一致 AND O到達確認 AND V event/世代/集合一致 AND 全停止B0–5新証明の正しい帰属/正常受理 AND 不完全停止区間B発行0（12） AND 全必須原票/予算/cleanupの確認。UNKNOWN/欠落を真にしない。R phaseのconsumerコマンド/意味上return1と、新proof consumerのreturn0、case/harness判定、D/KのOS終了を別fieldにする。R→注入→V→新proofのD instance/state lineage・K lifetimeは不変で、途中再起動/状態初期化で追跡欠落を隠してはならない。予期しないD/K実終了はFAIL又は制御喪失BLOCKEDで当該slot終了、再試行不可（対象終了を検査する15もD再起動で正常へ接続しない）。
- LとMのraw/期待/集計を分離。旧固定7・Stage A30の未達結果は不変。実測0の現時点でこのAND式の評価済みPASSを作らない。
