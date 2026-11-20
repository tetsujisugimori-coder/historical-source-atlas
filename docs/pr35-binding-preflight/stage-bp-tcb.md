Stage B-P / 版1.3 / 2026-11-16 JST / 基準HEAD4297ce68a6ac60ac2e60365c37c649d548dabe8f・tree190adc2c41f394e073664a26e75548d868a7a5f9。内容SHAはmanifest.sha256。設計/静的審査のみ、現640ゲート・実装/実測承認は不変更。

# TCB・独立oracleの実装前成立性（優先工程1）

結論: O-Kを第一候補として必要条件を審査できるが、実read→D derivationの因果対応は未成立、実装開始判定NOT_READY。O-G/GDBは別の完全性証拠が得られるまでHOLD。既存の拒否契約があるので、これは誤PASS実装を新たに再現した報告ではない。

## 主体/書込/取得経路台帳

|主体|責務・書ける原票|独立性の必要証拠|現状|
|---|---|---|---|
|S|出生所有/lifetime/操作許可・親子/wait台帳|host認可、kernel task参照と台帳の連結、Dが変更不可な所有registry|実体/source/権限UNKNOWN|
|K|唯一ptracer、実exe/map_filesの一回open/pin、kernel wait/raw FD交付lane|停止下の正しいtask/generationでkernel objectを開く実境界、原sourceと権限、event完全性。K自己申告だけでK自体を証明しない|trustedと呼ぶのは設計役割、検証済みTCBではない|
|O|kernel proc/FD比較、read/receipt照合、独立ack/期待台帳lane|D parser/更新値を使わない取得経路、K共有TCBとO独立部分の範囲、原票のD書込不能|取得/ACL/隔離の実証なし|
|D|image/M/T/lease追跡、derivation/proofとconsumer結果lane|D instance/state lineage、同じ実入力からのderivation境界、Kへ追跡logicを移さないこと|source未実装、実使用由来UNKNOWN|
|I|固定注入intent/return lane|原recipe/source/hash、owned task/phase、Oのkernel変化で到達を確認。returnだけはackにしない|原入力未生成|
|A|固定source/inputと独立原票からaudit lane|生成者と別担当、原実物の再取得、原票とsummaryの区別|今回文書静的審査だけ実施可能|

同UIDの別processというだけでDからK/Oへの書込・ptrace・FD差替えが不可能とはしない。必要な既存保護の実証がなければNOT_READY。今回新しい保護設定/別UID/namespace/権限を作らない。rawのhashや追記順は保存整合の手段であり、虚偽を出すTCBの真実性を証明しない。

## 10項目の成立可能性

|項目|仕様上要求できること|不足する証拠・現在判定|
|---|---|---|
|1 kernel実object|Sのtask所有とK stop lease内で正しいproc entryをopen|対象/stop/namespace/exec世代とopen実結果の連結UNKNOWN|
|2 一回open/交付|K pinからSCM_RIGHTSで同一open file description(OFD)を複製、実ancillary FD/peer/nonce記録|K取得・transfer source/ABI/端点所有未検証|
|3 O内KCMP_FILE|O保持pinとD返却実FDをO file table内で比較|対応syscall/通常権限未取得。拒否はUNKNOWN/BLOCKED、別方法で救済しない|
|4 OFDと実行object|同OFDならその参照は共有するが、そのopen先が現対象の実行物であることは別|Kの正しい選択とexec/remap排除、version不変性が必要。同inode/同SHAだけ不可|
|5 trusted実read|実OFD・offset/要求/返却長・chunk/fullcopy digestとtask/case/generation/epoch/pinを記録|K/reader source/実I/O経路の独立監査なし|
|6 receipt/payload|一回のreadと固定payload、receipt ID/nonce/sourceとproofを対応付ける|receiptの真正性/改変不能/一意性、実payload交付の境界未成立|
|7 D実使用/計算|actual derivation entryで使ったbyte列をSHA/ELF解析/proofまで結ぶ|下記の識別不能反例によりFD/hash/receipt照合だけでは成立しない。UNKNOWN/NOT_READY|
|8 独立原票|K/OがD event/booleanを期待生成に使用しない|source/IPC/書込分離、TCB正しさは未検証。自己申告同士の一致は禁止|
|9 世代/M/T|kernel exec/clone/exitとOのmapping/thread観測をD更新と独立比較|event取りこぼし/中間B stop/全停止/完全coverageの実証なし|
|10 scope保持|Dの追跡とlease/proofの不具合をDとして検査する|Kに追跡logicを移す/外部正常計算をD成功とするscope縮小は禁止|

[kcmp](https://man7.org/linux/man-pages/man2/kcmp.2.html)と[SCM_RIGHTS](https://man7.org/linux/man-pages/man7/unix.7.html)はOFD比較/参照転送の仕様根拠。これらはD userspaceのどのBufferがderivationへ入ったかを観測するAPIではない。

## 実read receiptとderivationの識別限界

要求を二つに分け、本補足の識別子をB_value（内容整合）とB_use（因果実使用）にする。B_valueは現在objectの不変byte列とpayload/結果の内容が整合すること。B_useはDがその交付payloadを実際に計算へ使ったこと。既存R/V契約のVは変更追跡のままで、B_value一致をV成功に転用しない。A/B契約をB_valueだけへ弱めたり、B_useを不要と決めたりする承認は本工程にない。

机上のGood Dは新payload=Xから計算する。Bad Dは由来が別の旧Buffer=Xから計算し、正しい現在FD、receipt r_new、現在task/epochをproofに付ける。両者のFD/OFD、read chunk/full digest、payload値、proof値は全て同じになり得る。hash collisionは不要。従って現観測だけではGood/Badを識別できず、BadをFAIL検出できたとは言えない。値が一致することと、実使用の由来が確認できたことは別である。

この限界は4297ce oracle-contractの「具体的な交付/derivation境界が確定・検証されるまでsourceUNKNOWN/正常full不可」というゲートを具体化する。常時拒否のDを正常受理したものではない。現在はcase開始前NOT_READYであり、実行済み正常試験のPASSでもFAILでもない。

## B_useを主張するための追加証拠（未取得）

独立して信頼根拠のある境界が、(a)kernel pin→実read、(b)改変/alias不能な固定input capsuleの交付、(c)actual derivation invocationがそのcapsuleを入力にした事実、(d)同じbyte列がSHAとELF解析へ入ること、(e)その出力と同case/task/epoch/proof、を非迂回の一本道として証拠化する必要がある。Buffer label、Dのentry log、caller boolean、Dが作るreceipt、hashが一致するだけでは(c)を証明しない。

候補はTCBを含むtrusted derivation-entry/adapterの実sourceと固定input handoff、実際の呼出/入力/出力を観測する独立経路を別審査する方式。ただし現在その具体的実体・独立性・改変不能性・通常権限での取得方法はUNKNOWN。文書で要件を列挙しただけで実現可能又は十分としない。sourceレビューだけでもruntimeの実使用証拠を自動的には得られない。

外部trusted serviceへderivationそのものを移す方式は「Dが実際に計算した」証明ではなく、検査対象の変更となるため本工程では採用しない。KへDの追跡logicを移す案、Dを信頼済みと再定義する案も不可。通常権限で必要な独立境界を成立させられなければO-Kの当該B_use保証はNOT_READYのまま。TCB/kernel自体の悪意や未審査readerの正しさは今回の保証対象外、TCBのsource・実行物・設定・監査が得られるまでTCBは未検証の仮定である。

## A–H 静的反例

|反例/入力前提|独立した根拠・期待判定|現在の成立性/不足|
|---|---|---|
|A 正FD、新receipt、旧Bufferで計算|OFD返却とread値だけでは不十分。旧bytesが異なりoutputが不一致ならFAIL、同値ならactual-entry由来証拠が必要|同値の場合の識別はUNKNOWN/NOT_READY。FAILを検出済みとしない|
|B 別objectを同SHAだけで受理|K pin由来とOの実返却FD比較、停止下object帰属。別OFD不一致はFAIL|K pin選択/権限未検証。同SHAは代替根拠でない|
|C 新receiptを旧payloadへ貼付|run/case/pin/generation/epoch/nonceと固定payload/actual-entryを突合。値差/ID差はFAIL|旧payloadが同値で再labelされる場合はAと同じ識別限界|
|D 別case receipt再利用|AがI/K/O原票のcase/series/run/sourceとproof tupleを照合|不一致はFAILの契約、真正性/重複拒否の実証なし|
|E 旧task/epoch proof流用|S lifetime、O現在generation/M/T、fresh lease epochの照合|不一致はFAIL、実task handle/instance境界未取得|
|F D更新値をoracle期待に使用|O source lane/独立parser/取得元を監査。期待をDから作るのは禁止|循環する方式は不採用、源が不明ならUNKNOWN/NOT_READY|
|G 常時拒否|適格な01/22/M0とR/V後の正常受理はPASS/0が必要|適格状態でDが常時拒否ならFAIL。現在の事前NOT_READYと混同しない|
|H exec A→B→Aの世代巻戻し|K原exec2commit+O中間B/最終A、D g0→g1→g2/current proofを照合|旧g0利用はFAILの契約。中間B停止/原票の実取得はUNKNOWN|

これは机上審査で、コード/対象を使ったRED/GREENや機構検出PASSの件数ではない。A/Cを含め未取得の観測を真としてcase ANDへ投入せず、B_use保証が必須のまま未成立ならfull identity/実装開始判定はNOT_READYを保持する。
