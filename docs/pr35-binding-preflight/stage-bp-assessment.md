Stage B-P / 版1.3 / 2026-11-16 JST / 基準HEAD4297ce68a6ac60ac2e60365c37c649d548dabe8f・tree190adc2c41f394e073664a26e75548d868a7a5f9。内容SHAはmanifest.sha256。設計/静的審査のみ、現640ゲート・実装/実測承認は不変更。

# Stage B-P 成立性審査・残余条件

一次指示: [レビュー5919580472](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#pullrequestreview-5919580472)とStage B-P依頼。工程成功の範囲は、未成立理由と必要証拠を確定し次の独立審査へ提出できること。実装開始を承認する工程ではない。

- [TCB/receipt/derivationと反例A–H](stage-bp-tcb.md)
- [Linux/権限/死亡/cleanup](stage-bp-environment.md)
- [23slot入力・1160秒](stage-bp-inputs.md)

## 開始版と調査範囲

GitHub/localのHEAD4297ce68a6ac60ac2e60365c37c649d548dabe8f/tree190adc2c41f394e073664a26e75548d868a7a5f9が一致、branch docs/pr35-binding-feasibility-20261115、base main3e56を確認して開始。PR36/35はDraft/未merge。Git blobとlocalの既存15fileを全byte照合し、AGENTS/既存差分/レビューを読取り。既存未pushコード/隔離branch/正本/mainを変更しない。過去原票は別物として保存し、未読の原証拠を再監査済みとしない。

TCB仕様と一次API資料、既存環境/アクセス拒否記録を照合したが、新しいhostへ接続・探索していない。文書審査/原票hash・ZIP保存処理以外のアプリ/原テスト/診断実行、対象生成/制御、ptrace/GDB/実proc/メモリ、browser、CI dispatch/rerun、権限/capability/root取得・保護緩和・導入は0。

## 技術未成立台帳（新規の確定製品不具合と区別）

|ID/分類|再現条件・根拠|影響/必要証拠・現在判定|
|---|---|---|
|BP-U1 C因果対応|正FD/new receipt/新payload=Xと、旧Buffer=Xから計算したDは現外部観測が同じ。oracle-contractの未確定entry gateを具体化|read receipt/hashだけでA/C不良を検出したとは言えない。非迂回trusted actual-entry/handoff/derivationの独立証拠が必要。UNKNOWN/NOT_READY|
|BP-U2 TCB根拠|K/Oのsource/実物/設定・書込/制御分離が未取得|TCBと命名したことをTCB正しさとしない。D追跡logic移動によるscope縮小不可。UNKNOWN|
|BP-U3 host/通常権限|認可host/ABI/ptrace/map_files/SCM_RIGHTS/kcmp/fs-verity等の同時成立証拠なし|当該方式は必要通常権限がなければ不成立。新権限で解決しない。環境BLOCKED|
|BP-U4 死亡/回収|K死亡auto-resume、孤児化、S wait権限/終了status、有限cleanup未確定|承認済み所有限定policyと合法adoption/reap、実終了/FD/残存/保存の別証拠。NOT_READY|
|BP-U5 入力/時間|全23slotの実source/bytes/hash/ID/ackが未生成、phase/cleanup上限根拠なし|NOT_GENERATED/UNKNOWN、予算NOT_READY。追加試行/期限緩和なし|
|BP-U6 恒久保全|Archive過去拒否、Vault実保存未確認、代替先認可なし|workspace読戻しだけでは完了不可。恒久保全BLOCKED|

これらは残余の技術ゲートであり、新規の実行でP1/P2/P3を再現した件数ではない。既存のB/正常回帰/保全の未達は継続。独立審査で新規文書P1/P2/P3が出た場合は、初回sourceと同じ反例を保存して補訂し、結果を新規独立原票へ分離する。

## 保管・実物照合

|先/役割|既存証拠/今回の扱い|判定|
|---|---|---|
|Dev-Artifact-Archive/正式成果物|2026-11-15の専用mkdir errno13/WinError5原票を読取り保持、今回再試行/変更/迂回なし|恒久成果物保全BLOCKED|
|Hachibei-Evidence-Vault/承認証拠|指定された役割と実書込/retention/再取得能力を区別。今回は未使用|実アクセス/保存UNKNOWN。Archiveの無断代替にしない|
|案件workspace|pr36-stage-bp-evidence-20261116T2118JSTへ新規保存、旧原票不変|一時保全のみ。独立照合結果は後続受領原票へ|
|Library/Space候補|利用権限・保存範囲・原実物再取得の証拠なし。探索/転送しない|UNKNOWN/未採用、代替保全PASSにしない|

今回の新文書をZIP化する場合はdesign-onlyでsource Git blob/実file/manifestの集合とSHA、原ZIPのbyte数/SHA、全entry CRCを保存する。別担当が保存済み実物を別新規先へ再取得して全byte/CRC/exact manifest/source帰属を再計算するまで独立監査PENDING。生成者自身の再読だけでは独立監査でない。旧368371byte ZIP等の照合を新版に流用しない。投稿受領は原ZIPを変えず別追補へ保存する。実測raw/TCB実体/fixtureはNOT_GENERATEDで、文書保存を実証証拠としない。

## 次工程・判定

TCB/独立oracleの設計条件整理は可能、ただし因果実使用の独立境界も含めた成立性はPARTIAL/UNKNOWN。認可済みLinuxと通常権限、死亡/回収/cleanup、実入力/時間、恒久保存を成立させる証拠が不足し、実装開始判断はNOT_READY。実装開始承認・実測開始承認は未承認のまま。O-K第一候補、O-G/GDB HOLD、C2 HOLD、現640ゲート不変更。

進めるのはBP-U1–6の資料/設計/既存証拠の整理と独立審査まで。実装/実測/対象生成で不足を埋める工程には本依頼だけで進まない。未知を成功と偽る、既存証拠破壊、文書範囲逸脱、未所有操作、未承認実行/予算変更を必要とするなら停止する。未成立として記録できる限り文書審査は限定完了可能。

文書提出は同PR36文書branchのみ、workflow原文/変更path/イベント/commitを点検し[skip ci]を併用。skip文字列だけを安全性証明にしない。通常push後も実run/checkと最新head/Draftを読取り、CI未実施をPASSにしない。新しい独立COMMENTは最新HEADへ帰属させ、APPROVE/マージ/Draft解除なし。旧レビューの受入は履歴として保持。

最終状態: 総合PARTIAL、native BLOCKED、ABA HOLD、保証B UNKNOWN、WebKit根本原因UNKNOWN、製品受入FAIL、追加コードpush HOLD、PR35/36 Draft・マージNO。文書限定完了と実装/実測/B PASSを分離する。

独立審査P3-BP1の補訂履歴: 初回案で内容対応をVと略記し既存R/Vの変更追跡Vと衝突したため、B_value/B_useへ名称分離した。B_value一致を既存V成功へ転用しない。ケース/期待/保証を変更した補訂ではなく、同じ誤転用反例を再審査する。初回4文書はworkspace draft-before-p3-bp1/へ不変保存。
