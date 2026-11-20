版1.2 / 2026-11-16 JST / 文書基準HEAD 134c5133d0d04892ec0f0ff0e9d2ee50fedb2f98、tree aea16bc285391a21c68934f02c143cb18de30b86。現640ゲート不変更。内容SHAはmanifest.sha256。設計案と必要条件であり、実装・生成・実測の許可/証拠ではない。

# 実装なしの静的反例台帳

基準134cはR/V分離・正常再受理を既に要求した。以下の補足はそれを閉鎖済み実装や実測へ変えず、未指定だった観測主体・source・比較方法・集約を具体化する。RED/GREEN実行結果ではない。全反例は机上のみ、生成/制御/テスト実行0。

|ID / 入力前提・仮想不良実装|134c時点の契約/具体化前の不足|本仕様の排除条件と期待判定|未証明|
|---|---|---|---|
|S01 Oがexec到達を確認、Rだけ正常でV未実装|Rだけcase PASS不可、oracle source未固定|K raw execとO Eにg1/BがありD更新なし→V FAIL、case FAIL|K/O raw実取得|
|S02 exec後Dが旧exe Aを保持、世代だけ更新|現在exe対応要求、object照合手段未指定|Oがcommit stopでpinしたB object/固定bytesとD proofが不一致→FAIL|F権限/不変backing|
|S03 A→B→AでDがg0へ巻戻し|2commit/順序/旧世代不可|O Eのg1/Bとg2/A、fresh epochにg0証明は対応しない→FAIL|中間B stop実現性|
|S04 Dが常時空mapping|空集合不可、coverage実体未固定|O M必要集合非空/追加差とD空がexact不一致→FAIL|map_files通常許可|
|S05 remap後も旧range/object tupleをDに残す|削除/追加差要求|O M_removedにL_a、M_addedにL_b、Dに旧tuple残存→FAIL。同address再利用でもobject差を比較|dlclose実退役/新map到達|
|S06 dlopen後追加をDが無視|coverage更新要求|O added非空、D afterがbeforeのまま→FAIL。I returnだけでaddedを捏造しない|dependency closure|
|S07 新TIDをDがmembershipへ入れない|独立newTID/全停止要求|K TRACECLONE+O task集合にnew、D欠落→V FAIL|kernel thread情報|
|S08 未停止threadありDがB発行|全停止前B0件|K個別stop未達phaseのD proofはFAIL。不完全停止中D BLOCKEDは正しいが、適格再停止後は新proof必須|barrierの安全完全性|
|S09 全caseでD常時BLOCKED|正常再停止PASS/0要求|01/22/M0、02/03/10–12の適格再停止でproof受理0が得られずFAIL。安全拒否を検査成功にしない|正常環境成立|
|S10 Dの新proofが旧task/旧epoch|B0–5現在帰属要求|S taskKey+O generation/M/Tと新leaseKeyを照合、旧lifetime/epoch→FAIL|所有bridge/寿命参照|
|S11 I intentのみ、kernelに変化なし|到達未証明NOT_REACHED|O M/E/Tの到達証拠なし→NOT_REACHED（故障検出PASS0件）、R成功は代替不可|注入recipe到達性|
|S12 O取得拒否/破損、D値をackへcopy|非循環oracle要求|O source/権限不成立→UNKNOWN/BLOCKED、実行前ならNOT_READY。D値からの再生成は禁止、証明成功0|通常アクセス/TCB分離|
|S13 Vは一致するが新proof未発行/誤帰属|適格再停止の発行/帰属要求|正常適格phaseで未発行/旧集合/誤task→FAIL、R/VだけではAND不足|phase別oracle|
|S14 結果UNKNOWNを真にしてcase集約|未確認を成功にしない方針|case ANDの必須欄UNKNOWN/PENDINGならPASS不可、BLOCKED|writer/collector完全性|
|S15 M成功のrawをLへ流用|系列分離|series/run/producer/targetLifetime/source/phase照合が一致せず拒否、live実証には0件|実raw発生なし|
|S16 timeout後追加待機でphaseを完了|slot上限維持|60/5秒超過をBLOCKED、後続NOT_RUN。予算内で終わる裏付けなしは事前NOT_READY|hard deadline/cleanup有限性|
|S17 08/09 permission不足を理由に正常期待BLOCKEDへ変更|正常PASS/0、NOT_READYへ補訂済み|事前不適格なら開始なし、到達済適格の元object拒否はFAIL。権限/取得故障16/17/18へ分離|fs-verity/namespace実条件|
|S18 新仕様を理由にStage A13FAIL/固定7正常FAILを削除|旧回帰別系列|旧判定をvalidation-planに保持、新spec成功と別系列。今回回復実行0|既存不具合継続|

S01–S10はユーザー指定の仮想不良実装。上記判定を動かした試験数として集計しない。O-K/TCB自体を検査対象に含む場合の独立oracleはまだないため、S12によりUNKNOWNを保持する。既存134cで論理排除が求められた事実と、今回の具体化によるsource/境界/集約の追加を区別した。

独立審査で新しい反例が見つかった場合は本台帳を履歴付きで補足し、初回案をworkspace原票として残して最小文書修正する。実入力・原テスト・予算・期待値を変更して反例を消さない。

## 初回独立反例による文書変更前後（実行0）

|独立指摘/同じ反例|初回案の不足|補訂後の論理条件|未証明|
|---|---|---|---|
|P2-D1: 同SHA/build IDの旧別objectをDが保持、O/D局所tokenだけ一致と言う|別々にopenしたFDをcross-boundaryで同一とする手段が欠けた|Kのkernel object一回open/同open descriptionをSCM_RIGHTS交付し、Dから実FDを返却、O保持pinとのKCMP_FILE一致とtrusted read receiptを必須。別object/別openはFAIL、機能/由来不明はNOT_READY/BLOCKED|source pin/receipt/TCB実装・権限|
|P2-D2: K死亡でkernel detach/resume、紙上の失効だけ成功|kernel死亡動作と物理的制御の責任が未指定|承認済み所有対象限定の死亡時終了/復帰policyがなければNOT_READY。死亡/残存/終了原票なしはBLOCKED、EXITKILLは未承認候補|kernel/終了許可/cleanup有限性|
|P3-D3: RでD終了→新Dの初期状態をV成功にする|phaseのexitとD/K OS exit、instance連続性が曖昧|R consumer returnとD/K実終了を分離、同instance lineageを必須、途中再起動はFAIL/BLOCKEDでcase終了、再試行不可|実event/instance原票|

初回文書実物はworkspaceのdraft-before-independent-fixes/と独立初回snapshotに保存し、上書きしない。同じ机上反例を補訂後に独立再審査する。上記は実行RED/GREENの件数でない。

P3-D4（再読時の用語整合）: E/M取得レシピの「Oがopen」という初回表現を、Oのkernel proc観測→K取得境界へのopen/pin要求→K交付FD受領へ統一。同じ別open反例が用語差で復活しないよう、独立観測と単一source pin取得を区別した。
