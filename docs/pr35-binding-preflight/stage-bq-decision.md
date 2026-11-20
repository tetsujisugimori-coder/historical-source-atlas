Stage B-Q / 版1.4 / 2026-11-17 JST / 基準HEAD1273d288fc30bce9e176f1a7e917d354ae650e13、tree1592f45dd641e59dc6f264d67019a6e39b22849f、親4297ce68a6ac60ac2e60365c37c649d548dabe8f。内容SHAはmanifest.sha256。設計・静的判定のみ。

# 実現可能性と実装開始の決定記録

**現条件のbackend実装開始=NO（NOT_READY/未承認）、実測開始=NO（NOT_READY/未承認）。一般的な実現可能性はUNKNOWN。** 未成立条件と排除/保留の理由を独立審査できれば設計審査は限定完了可能だが、保証B PASSではない。採用決定できる完成方式は現時点でない。

従来の役割/23slot台帳を再作成せず、[Stage B-P TCB](stage-bp-tcb.md)、[環境](stage-bp-environment.md)、[入力](stage-bp-inputs.md)、[残余条件](stage-bp-assessment.md)を不変の根拠として参照し、今回の決定だけを記録する。一次指示は[review5922091789](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#pullrequestreview-5922091789)。文書/レビューの受入と実在するsource・実物・実測の証拠は別である。

## 0. 固定/証拠の索引

|ID|今回利用した根拠・観測主体|示せること/限界|
|---|---|---|
|E1|GitHub PR35/36・commit/tree/parent・変更file API、local Git/実fileを主担当/独立担当が読取り|開始PR36=1273/tree1592/親4297、base main3e56、Draft/未merge。基準20file全byte/Git一致。実TCBの証明でない|
|E2|基準のoracle-contract/Stage B-P/validation/input/cleanup/既存reviewを静的読取り|保証B、B_value/B_use、R/V、正常PASS/0、L19/M4/順序/1160秒は不変。旧独立原票も不変|
|E3|Linux kcmp/ptrace/wait等の一次仕様、Valgrind core/tool公式資料|API/一般instrumentationの意味と追加観測の可能性。特定版の設置/呼出/認可/実測は示さない|
|E4|保存済みArchive拒否原票（2026-11-15 errno13/WinError5）、Vault/Library/Spaceの既存状態|過去拒否と実保存未確認を区別。新しい書込試行/代替先探索なし|
|E5|過去Stage B-P workspace ZIP469215byteの独立監査原票/receiptを参照|過去のdesign-only保全範囲の参照のみ。旧ZIPの再監査やB-Q恒久保全へ転用しない|

開始HEAD/branchは指定版と一致、worktreeはclean。main/PR35/隔離8ea/未push2596・640の状態を原票に固定した。差異を解消するためのreset/force/正本選び直しなし。Linux/対象の調査を重複せず、現在のhost状況を新観測したとはしない。

## 1. BP-U1: 何を排除し、何を保留するか

Xは同じbyte列。Good Dは新handoffのpayload Xを計算し、Bad Dは別由来の旧Buffer Xを使い現在FD/receipt/task/epochを付ける。現観測集合（OFD、read receipt、digest、proof値）が等しい実行があり、hash衝突は不要。従ってその観測集合だけの判定関数は二者を区別できない。この限定方式の不適格は論理上判断できる。全ての将来方式が不可能だという結論ではない。

|候補|追加観測・実行境界と必要source|同値旧Bufferへの耐性/通常権限・未取得|決定|
|---|---|---|---|
|Q0 現FD/OFD/receipt/digest/proof一致のみ|K/O原票の既存観測のまま|同値XのGood/Badが観測等価。追加の署名/nonceが同じpayload値をbindしても実使用を強制しない|**方式不適格（B_use用途）**。B_value/参照整合の必要条件には残す|
|Q1 trusted入口hook・Buffer ID・引数記録だけ|D入口/adapterのsourceとinput handoffを観測|入口は新Xでも内部SHA/ELFが旧global/aliasを読む、又は新Xをreadして捨て旧Xで計算する反例を排除しない。単にhookをtrusted化しても不足|**この限定方式は不適格**。必要条件の一部であって完成oracleに採用しない|
|Q2 同じDの実operand/provenanceを非迂回に観測するO-monitor|D全体・runtime/native/JIT/libs、monitor/実行engine、input-origin交付、独立trace検証器の正確source/build/実行物。actual read/writeからSHA/ELF/proof sinkまで観測|新/旧originと実output依存を区別できるなら観測等価性を破る候補。ただし具体engine/tool、完全coverage、Dから改変不能、通常権限/ABI/時間/出力量の証拠なし|**条件付き成立候補（仮説）**。実在の適格構成は未立証UNKNOWN、採用/実装開始不可|
|Q3 全D因果性の形式的排除証明と実artifact/runtime結合|全経路D/adapter/crypto/parser/proofのモデル、証明artifact/独立checker/source、compiler/JIT/build/loaderのprovenance保持refinementと実行物/設定の結合|許容される実行からBad Dを排除できる証明が必要。sourceの値意味の正しさ/hash/ビルド測定だけでは因果由来を保存しない。実source/モデル/証明器/証明/chainが未取得|**未立証・UNKNOWN**。名称だけで候補採用やsource codeをtrustedへ昇格しない|
|Q4 外部trusted serviceへ計算移転・KへD追跡logic移動・B_valueへ保証縮小|独立計算結果又は縮小したDを検査|元のDの実使用/追跡を検査した証拠にならず本依頼の禁止条件に抵触|**方式不適格**。契約変更で成功を作らない|

### Q2が仮説のまま残るための厳密な条件

O-monitorはS/K/O/D/I/Aを置き換える新権威ではなく、O側の観測機構として審査する。Kはtargetのsole ptracerを維持し、追加の同一target attachやprivileged観測を前提にしない。元のDの追跡/crypto/ELF/proof命令を実行・検査対象に残し、外部サービスが代算した正常値をDへ返す方式はQ4である。

必要な追加証拠は、(i)K pin→trusted read→新input origin、(ii)actual instructionのread-from/write/copyとorigin、(iii)SHA/ELFが実際に消費したoperandと範囲、(iv)実proof出力までの依存経路、(v)現在task/case/epoch/世代/集合への帰属、の全体である。新payloadを一度読んだtrace、関数名/入口だけ、単純な過大近似taintタグの付与だけでは足りない。新Xを読んで捨て、旧Xで計算したBad DをFAILにできるactual出力依存を要す。

正当に新payloadをcopyした別Bufferは新originとして扱う必要があり、pointer/address一致を正常条件にしない。逆に値が同じという理由で旧originを新へ再labelしてはならない。originの定義/伝播・制御依存/許容定数・暗号native処理・ELF解析・JIT/自己変更・全thread/syscall境界・欠落時拒否を実sourceで完全に検証する必要がある。独立checkerがDのlabelや要求をtruthに使うなら循環で不適格。

同じDを観測するengineが通常権限の認可済み起動内で動き、実worldのK/O kernel原票と結べることが必要。engineがDの計算をstub/置換する、未対応経路を無視する、Dの不具合をTCBへ移す場合は採用不可。初期memory originから全実行を覆う必要があり、後からentryだけ観測を始めても旧Buffer由来を判定したとはしない。

[Valgrind core公式](https://valgrind.org/docs/manual/manual-core.html)はsynthetic CPU/プログラムinstrumentationという一般的な実行境界を説明し、[tool API公式](https://valgrind.org/docs/manual/manual-writing-tools.html)は個別toolによるinstrumentationを説明する。これはQ2の追加観測を検討できる資料であって、Memcheckや既存toolが本B_use oracleを実装している証拠ではない。適格tool/version/sourceは選定・取得しておらず、設置/導入/起動もしない。原実行との意味/因果性対応、全coverage、実world依存、通常権限、1160秒/出力上限の成立は全てUNKNOWN。

Q3にもsourceからmachine/runtimeまでの**因果由来を保持する**対応が必要。値を保つ最適化が同値の旧値を再利用してよいモデルなら、source-level証明をmachineのB_useへ転用できない。証明対象から入力差替え/旧Buffer読取/追跡bugを除外してDを無条件にtrustedとするのも不可。登録済の全経路証明chainはない。

**採用可否の結論**: 完成方式として採用YESは0。Q0/Q1/Q4は排除、Q2は追加証拠が必要な仮説、Q3は未立証。B_use一般実現性はUNKNOWN、現構成での実装開始はNO/NOT_READY。追加の証拠経路を示せなければ、この結論で停止し文書増設を反復しない。

## 2. BP-U2: TCBが検査対象を飲み込まないための判定

|主体と保持する責務|TCB/独立観測に許す範囲|独立反例・未取得証拠/決定|
|---|---|---|
|S 所有/lifetime/許可|認可/生成/handle台帳と合法回収route|Sのcaller文字列/PIDだけを所有根拠にすると循環。source/実行物/権限証拠なし→未立証|
|K 唯一ptracer/正kernel object pin|kernel原結果の取得・停止/交付・raw lane|KがDの世代/M/T更新を代作しOがそれを期待値にすると追跡bugが検査外になる。不採用|
|O 独立取得/比較|K共有TCBの限界を表示しD更新を使わず期待を構成|OがD parser/label/summaryを再利用すればF反例を見逃す。source/IPC/書込分離/monitorの独立検証はUNKNOWN|
|D 追跡/lease/derivation/proof|元のDを不具合検査対象に残す|D自体をtrustedへ改名し内部oldBufferを不問にする解決は不適格|
|I 注入/A 監査|intentとkernel到達ack、生成と独立再取得を区別|I returnだけで到達、生成者summaryだけで独立監査なら不適格|

TCB台帳に必要な実source/commit/build/hash/依存・書込lane/IPC/FD経路・Dからの改変路・kernel/runtime/monitorの信頼根拠は、現行文書に要求があるが実体は未取得。別process/同UID/署名/hashだけで改変不能又は機能正当性とはしない。Q2でTCBが拡大するならmonitorの正しさと全観測chainを新たに独立検証し、検査対象Dの不具合を仮定で消していないことが必要。**分類=未立証UNKNOWN、実装開始NO。**

## 3. BP-U1〜U6の決定表

「成立条件を確認済み」は条件の意味を整理したという意味で使わず、実体の成立証拠がある場合に限る。現状は六項目の全体成立を確認済みにできるものはない。

|gate/分類|根拠source・観測主体/信頼境界|未取得・現時点の決定|
|---|---|---|
|U1: Q0/Q1/Q4不適格、Q2条件付き仮説、Q3未立証|E1/E2と上記同値反例を静的審査担当が検討、E3は仕組みの意味だけ|actual-entry/operand-origin/証明chainなし。一般実現性UNKNOWN、採用YESなし、開始NO|
|U2: 未立証UNKNOWN|oracle-contractと上記S/K/O/D/I/A境界、source/実行物の登録状況|TCB役割名以外の実source/build/config/改変経路証拠なし。実装開始NO|
|U3: 安全上BLOCKED|既存stage-bp-environmentの保存済み台帳のみ、kernel原票は未取得|認可済みhost/範囲、kernel/arch/ABI、両UID/通常権限、pidfd/出生所有、sole tracer/events/全停止、proc/maps/map_files、SCM_RIGHTS/kcmp、不変backing/verity、source/依存の一式なし。新hostへ接続せず開始NO|
|U4: 安全上BLOCKED/NOT_READY|既存cleanup/environmentとptrace/wait一次仕様。終了を観測する主体は将来S/K/O|死亡時kernel動作、auto-resume防止/復帰policy、孤児化/S wait-adoption-reap/実status、D/K継続、全FD/IPC/task/残存/保存と有限性なし。開始NO|
|U5: 未立証UNKNOWN/NOT_READY|固定stage-bp-inputsのU/P descriptorと既存23slotを再利用|source/実物/hash/ID/object/M/T/ack/B_use/時間根拠未生成。1160秒算術だけでは不足、開始NO|
|U6: 安全上BLOCKED|E4/E5の既存保存記録。独立監査主体は生成者と別のA|workspace保全とArchive/Vaultの実保存/独立再取得は別。恒久保存の実物証拠なし、完了NO|

U3の各機構はinstalled=UNKNOWN、callable=UNKNOWN、authorized=UNKNOWN、measured=NOT_TESTEDという既存の認可済みcandidate Linux向け台帳状態を維持。APIの存在、過去hosted EPERM、Windowsのtool版を実環境PASSへ転用しない。今回新環境の照会/接続/構築/実process操作はない。必要通常権限がない方式は不適格、新cap/root・保護緩和は解決策にしない。

U4は停止要求、実target終了、D/K終了、FD close、IPC/資源解放、残存、原票保存を別判定する。pidfd可読化からwait権限/実exit statusを推論せず、watchdog returnを有限cleanupへ転用しない。EXITKILL/subreaperは未承認候補で有効化0。安全終了経路が不明なまま実装開始YESにしない。[wait仕様](https://man7.org/linux/man-pages/man2/waitpid.2.html)、[ptrace仕様](https://man7.org/linux/man-pages/man2/ptrace.2.html)の意味を当hostで実測したという主張はない。

## 4. U5: 23slotへの決定適用

source/binary/fixture/SHA/build ID/必要verity/object/M/T/ackとB_use証拠の現在値は、既存[case別入力台帳](stage-bp-inputs.md)のU=UNKNOWN/NOT_GENERATEDを不変更で採用する。架空hashは作らず、必要原票P/phase配分も同台帳を参照する。新しい入力台帳や試行を増やさず、各rowへ実装前判断だけを加える。

|既存slot/case|開始を妨げる追加証拠/境界|時間/入力の判定|
|---|---|---|
|L01/01|正常full BとB_use、全M/T、正常PASS/0のactual-entry|NOT_READY|
|L02/02|exec1/R/V/再停止/新proof/正常受理と因果chain|NOT_READY|
|L03/03|中間Bを含む2exec/g0→g1→g2、旧Buffer識別chain|NOT_READY|
|L04/04|path差替え後元exeの実object/因果新proof|NOT_READY|
|L05/05|2owned lifetime/旧handle拒否、合法終了回収。PID再利用未観測はNTのまま|NOT_READY|
|L06/07|元libraryの実mapping/object、正常受理|NOT_READY|
|L07/08|unlink後元不変object PASS/0、権限不足は事前gate|NOT_READY|
|L08/09|rename後元不変object PASS/0、期待の事後変更不可|NOT_READY|
|L09/10|removed/added tupleとR/V/新proof/因果正常受理|NOT_READY|
|L10/11|追加mapping非空、完全coverage/新proof|NOT_READY|
|L11/12|新TID membership/未停止中B0件、全停止後正常受理|NOT_READY|
|L12/13|stop欠落の安全注入/独立ack/終了許可|NOT_READY|
|L13/14|resume/step旧proof拒否、安全な制御喪失policy|NOT_READY|
|L14/15|owned実終了status/S wait/残存/保存|NOT_READY|
|L15/16|通常permission拒否の事前固定operation/原errno|NOT_READY|
|L16/17|exe取得失敗surfaceの到達/原応答/cleanup|NOT_READY|
|L17/18|必要mapping取得失敗surface/coverage/raw|NOT_READY|
|L18/21|偽caller/旧epoch拒否、真oracleを偽値から作らない|NOT_READY|
|L19/22|01同一正常入力/fresh task/epoch、PASS/0|NOT_READY|
|M01/M0|固定model trace/独立期待/正常PASS/0|NOT_READY（実kernel/B_use証拠へ昇格不可）|
|M02/06|model lifetime不一致の固定入力/拒否|NOT_READY|
|M03/19|不完全read/破損/欠測の固定有限trace|NOT_READY|
|M04/20|close/未確認/遅延traceと保存/期限|NOT_READY|

各1回・追加0、L19×60=1140秒、M4×5=20秒、合計1160秒は不変更。準備/初期proof/R/注入/独立観測/V/再停止/新proof/正常受理/保存/実終了/cleanupを各slot内に含める。Q2の原trace/証明書又はQ3検証を必要phaseへ加えても期限・既存byte上限を増やせない。全trace量/coverage/処理時間・終了回収の上限根拠がなく、現予算成立はUNKNOWN/NOT_READY。lossy要約やtrace欠落を完全原票としない。実行可能性を調べるための試行も今回は0。

## 5. U6: 恒久保全の選択

Archiveは正式成果物、Vaultは承認証拠の指定先として役割を固定。過去Archive拒否を維持し、現在の権限成功を推測しない。Vault実保存/retention/独立取得はUNKNOWN。Library/Spaceは承認/範囲/原実物再取得の証拠がなく未採用。通常保存先から無断で振り替えない。

旧Stage B-P ZIPのworkspace独立照合はE5の範囲で保持。B-Qの新ZIPを作る場合は別原物として、別担当が全byte/SHA/CRC/exact manifest/Git sourceを実物から再計算するまでPENDING。workspace保存が完了しても恒久保全BLOCKEDは解除しない。原ZIP/旧原票の移動/削除/更新は0、投稿受領は後生成の別追補とする。

## 6. 三つの独立判定と次の最小工程

|問い|現在の判定|理由|
|---|---|---|
|A 設計審査の完了可否|YES（独立審査で反例/分類/根拠が確認できた範囲の限定完了）|全体成立を偽らず、排除Q0/Q1/Q4と保留Q2/Q3、U1〜U6の不足証拠を確定できる|
|B backend実装開始|NO / NOT_READY、承認なし|B_use候補の実体/完全性・TCB・認可環境・安全終了・入力/時間・恒久保存が未成立。一般実現性UNKNOWNと区別|
|C 実測開始|NO / NOT_READY、承認なし|同上に加え実行物/実入力と実操作の明示承認がない|

次の最小工程は**Q2又はQ3の一候補について、登録可能な既存の実source/版/観測又は証明chain/独立仕様があるかを資料として提示し、元のDと同値旧Bufferを区別できるかを審査すること**。既存実体がなければその事実で開始NOを維持する。新しいengine/tool開発、環境準備、対象生成、実験で証拠を作る許可は別途必要で、この依頼から推定しない。候補のsourceもなく一般条件を繰返し書くだけの次工程は提案しない。

文書提出はPR36文書branchのみ、変更path/親/権限範囲/workflow原文とイベントを確認し、skip ciを併用。安全に抑止できない場合push BLOCKED。実提出後は最新GitHub実file/manifestとCOMMENTのID/commit/state/本文を読戻し、run/check0をCI PASSにしない。旧文書/レビュー/失敗/未検証と原case/正常期待は不変、現640ゲートを緩和しない。

最終状態: 総合PARTIAL、native BLOCKED、ABA HOLD、保証B UNKNOWN、WebKit根本原因UNKNOWN、製品受入FAIL、追加コードpush HOLD、PR35/36 Draft・マージNO。今回の新規文書指摘の有無は独立原票で分類し、技術未成立を文書の未解決なしで閉鎖しない。
