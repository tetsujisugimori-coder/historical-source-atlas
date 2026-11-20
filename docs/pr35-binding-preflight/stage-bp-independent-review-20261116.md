Stage B-P / 版1.3 / 2026-11-16 JST / 基準HEAD4297ce68a6ac60ac2e60365c37c649d548dabe8f・tree190adc2c41f394e073664a26e75548d868a7a5f9。以下は別担当の独立静的原票のLF掲載。原票実bytesはworkspaceへ不変保存、旧原票は不変更。内容SHAはmanifest.sha256。

# Stage B-P 新文書の独立静的最終審査

担当 /root/stage_bp_independent。文書作成・補訂担当とは別agent/別プロセス。主担当の自己評価や旧reviewの受入を採用せず、Stage B-P新4文書全文とREADME追記、基準4297ceのoracle/claims/input/validation/environment/cleanup/methods、一次review5919580472原応答、既存Archive拒否原票を直接読取り照合した。

基準HEAD4297ce68a6ac60ac2e60365c37c649d548dabe8f/tree190adc2c41f394e073664a26e75548d868a7a5f9。審査対象は未commit提案実bytes、snapshotはindependent-stage-bp-final-proposed-source/、SHA台帳はindependent-stage-bp-final-source-ledger.json。最終commit/manifest/追加独立review文書/GitHub/新ZIP/投稿の受領はこの原票後の別照合とする。

backend/アプリ/原テスト実行、対象生成/制御、実proc/メモリ照会、ptrace/GDB/browser/signal、Linux接続/探索/起動、CI/権限変更/導入、repo編集・commit/push・投稿はこの担当から0。新規workspace原票の保存とGit/hash読取りだけを行った。

## 判定

**Stage B-Pは、未成立理由と必要証拠を整理する設計審査として限定完了・文書限定受入可能。総合PARTIAL。** 実装条件の成立はNOT_READY、実装/実測承認は未承認、B実証UNKNOWN。新規P1/P2文書不具合は確認範囲でなし。P3-BP1用語衝突は補訂確認済み、未解決の新規文書P1/P2/P3は確認範囲でなし。BP-U1–6の重要技術ゲートは未成立のままで、文書審査で閉鎖しない。

## P3-BP1: 用語衝突の補訂

初回stage-bp-tcb:39は内容対応をV(value)と略記し、既存R/Vの変更追跡Vと衝突した。stage-bp-inputs:49の「V一致」を単なるbytes値一致へ誤転用する読解リスクがあった。主担当へ独立指摘し、初回実物を独立snapshotとdraft-before-p3-bp1に保持した。

補訂後はB_value（内容整合）とB_use（因果実使用）へ分離し、「既存R/V契約のVは変更追跡のまま」「B_value一致をV成功に転用しない」を明示した。env/inputsの略記もB_useへ整合し、assessmentに履歴を残した。同じ誤転用反例は文書上排除される。case ID、順序、正常/故障期待、1160秒を変えた補訂ではない。

## 優先工程1: TCBと実read/derivation

S/K/O/D/I/Aの責務、書けるlane、所有/取得元、Dの書込・制御分離の必要証拠を台帳化している。Kは実kernel object選択・sole tracerを担う共有TCBで、Oが独立にD更新値を使わず比較する範囲と、K自体の正しさを本D検査で証明できない範囲を分けた。Dの追跡logicをKへ移して検査対象を狭める解決、Dを信頼済みへ再定義する解決を禁止している。

Kの一回open/SCM_RIGHTS同OFD交付/KCMP_FILEは参照同一性の必要条件であり、open先が現在対象の実行objectであること、D userspaceの実入力由来、TCBの正しさまで同時に証明しない。stage-bp-tcbの10項目とBP-U1/U2はこの区別を保っている。

### A/Cの同値旧Buffer反例

Good Dは新交付payload=Xを計算し、Bad Dは別由来の旧Buffer=Xを計算して現在FD/new receipt/current task/epochをproofに載せる。全bytesが同一ならFD/OFD・read digest・payload値・proof値が同じになり得る。hash collisionは不要。現外部観測だけでGood/Badを識別できないという論理を確認した。

新文書はこれを「検出済みFAIL」とせず、B_valueの値整合とB_useの因果実使用を分離し、actual-entry/固定handoff/非迂回derivationから同case/proofまでの独立証拠がなければUNKNOWN/NOT_READYとしている。trusted entry/adapterを候補要件と挙げたことを実現可能・十分・実装検証済みとせず、外部service計算へ移してD成功とするscope弱化も認めない。従って既存のfail-closed契約を緩めない。

### A–Hの机上判定

|反例|独立根拠と審査結果|
|---|---|
|A 正FD＋旧Buffer|FD/read値だけでは不足。同値旧BufferはB_use識別未成立UNKNOWN/NOT_READY、PASSにも検出FAILにも計上しない|
|B 別object＋同SHA|K kernel pinと実ancillary FD/OFD比較が必要。同SHAだけは代替不可、機構未確認はUNKNOWN|
|C 新receipt＋旧payload|case/pin/generation/epoch/nonceとactual-entryを結ぶ必要。同値再labelはAの識別限界を保持|
|D 別case receipt|独立原票とcase/series/run/source/proof tuple不一致ならFAILの契約。真正性/重複拒否は未実証|
|E 旧task/epoch|S kernel lifetime、O現在M/T/世代、fresh epochへの対応が必要、PID/同bytesで代替しない|
|F D更新をoracle期待へ|独立source/書込分離/別parserが必要、循環方式不採用、源不明NOT_READY|
|G 常時拒否|適格01/22/M0およびR/V後適格正常phaseでPASS/0必須。現入力未生成の早期NOT_READYを故障検出成功としない|
|H ABA巻戻し|Kの2execとO中間B/最終A/世代順、D新proofを対応付ける必要。中間B/K完全性未取得はUNKNOWN|

## 環境・安全終了・予算

stage-bp-environmentはinstalled/callable/authorized/measuredを別欄とし、candidate Linux全機構の実体/許可未取得をUNKNOWN/NOT_TESTEDで記録する。APIの資料上存在やWindows過去版をLinux適格性へ昇格しない。通常権限でmap_files等が足りなければ方式不適格とし、新capability/root/保護緩和で補わない。

K死亡auto-detach/resume、target孤児化、Sが合法wait親でない/exit status取得不能、要求ackだけ成功、期限内cleanup不能を別反例にした。EXITKILL/subreaperは候補のみで未有効化。pidfd終端をwait権限へ昇格せず、実終了/controller終了/FD/資源/残存/保存は別状態で、有限性根拠なしはNOT_READYのまま。

入力台帳はL19/M4の全23caseを各1回・元順で保持。共通descriptor Uを各rowに適用し、実source/binary/SHA/build ID/verity/object/M/T/ack、phase/終了時間根拠をNOT_GENERATED/UNKNOWNにしている。L各60秒、M各5秒、1140+20=1160秒、追加0、従来8/10/14/18/10秒とM0.5/1.5/1.5/1.5秒配分を維持。追加B_use観測も予算内、根拠未成立で全slot NOT_READY。01/22/M0および08/09の正常PASS/0を維持し、権限不足や事後期待変更で成功にしない。

独立にrow順序23件を読取り照合し、既存15fileはREADME追記を除き全byte不変（現manifestはまだ旧版、最終受入未実施）、READMEも既存全文prefixを保持。.github/prototype/AGENTSのtracked差分0を確認した。

## 保全・残余条件

Archiveの2026-11-15 errno13/WinError5原票を読取り、歴史的拒否と今回未再試行を区別。Vaultは承認証拠役割であり実保存/retention/独立再取得UNKNOWN、Library/Spaceは権限/保存範囲未確認で未採用。workspace保存を恒久保全へ昇格せず、新ZIPの実物独立読戻しまでPENDINGとする契約は妥当。旧368371byte ZIP監査は新版へ流用しない。

BP-U1因果対応、U2 TCB、U3 host/通常権限、U4死亡/回収、U5入力/時間、U6恒久保全は技術未成立ゲートで、新規の実行再現P1/P2/P3件数ではない。既存B/正常回帰/保全の未達を閉鎖しない。

文書限定完了は可、oracle全体成立PARTIAL/UNKNOWN、実取得UNKNOWN、実環境/恒久保全BLOCKED、実装開始NOT_READY/承認なし、実測承認なし、B UNKNOWN、native BLOCKED/ABA HOLD/製品FAIL/根本原因UNKNOWN、両PR Draft/マージNOを維持する。

後続の最終Git HEAD/追加review/index/manifest、原ZIP実物、GitHub最新source・run/check・COMMENT/読戻しは別監査が必要。この原票をその代わりにしない。

2026年11月16日 21:29 JST
