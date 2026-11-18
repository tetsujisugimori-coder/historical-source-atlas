# Stage B-S：DFSan欠損の限定受容・Q2候補1方式の静的ソース審査

作成：2026-11-19 JST。対象：historical-source-atlas Draft PR #36、branch `docs/pr35-binding-feasibility-20261115`。開始HEAD `f47f1a1a3d2889c076961f0b879cd66e19f8090d`、tree `f24952f428b7f24a336f45398e0ec806ec6d78bb`、parent `0e74fde6b99300122a33561b838458d45ccb1169`。中央保全規約 `git-preservation-gate/docs/v0.2.0/policy.md`（正式採用commit `4695c3ce2d61e66df0dd36a4312373459e1557d4`）。本書は文書・公開source読取による**限定審査**であり、実装、Linux実試験、DFSan原証拠の回収、正式CI、保証Bの実証ではない。

**総合判定：文書整理の継続は限定YES／歴史的欠損の事実認定・補完NO／Q2完成方式の採用NO／Q2一般実現性UNKNOWN／backend実装NO／本実測NO／PR #36 Draft・マージNO。** この段階の「欠損受容」は、欠損を無視して証明を完成扱いすることではなく、範囲を限定して将来の設計・資料検討を妨げないという所有者指示への適用である。

## 1. 第1工程：欠損受容の対象と境界

### 1-1. 確認できたもの／引き継げないもの

|対象|確認・既存証拠|現在の制約|
|---|---|---|
|Windows Stage B-R2固定集合|902コピー単位・20,995,024 bytesのArchive実保存・別セッション直接再取得・全byte/size/SHA-256検査が限定PASS。元ログ10範囲、ZIP15本・1,390 entryも独立監査PASS|元データの**現在の同一性**を示す。DFSanの歴史的作成来歴を証明しない|
|同工程の監査証拠|保存receipt SHA-256 `7dc7953eda6bd401f5a35551f1201ed19982d3295b2a2ced9b7f0300ebb58c5e`、独立監査原票（849,401 bytes）SHA-256 `9ca3c5e05fc9ec356e9d1a3b73cd432f822c19a856661e21bad3da3881c2e2e6`。保存先から再取得・照合の所有者報告あり。P2-02 CLOSED|同一所有者アカウント内の別セッション。INDEPENDENCE=LIMITED_SHARED_OWNER、1年保持の実効性は未確認|
|DFSan現存版|従前Library保存2件の限定PASS、現存の審査本文・独立レビュー・既存原ZIPの内容識別は報告済|過去版や初期作成の同一性を証明しない|
|DFSan改稿前byte|UNKNOWN|未回収。現存版・再生成版で代用しない|
|閉鎖専用原票|UNKNOWN|未回収。既存レビュー内の閉鎖記述を専用原票と同一視しない|
|当時の作成主体・正確な時刻・登録履歴|UNKNOWN|現在のGitHub所有者、現在の登録番号、現存版の時刻から推定しない|
|分離stderr、当時の実効Windows権限・正確なPython版|UNKNOWN|新しい検査や現在の環境値で過去実行を補完しない|

根拠：[Stage B-R2独立監査 #5961724602](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#pullrequestreview-5961724602)、[Stage B-R2限定閉鎖 #5964826899](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#pullrequestreview-5964826899)、PR #36現行本文。

### 1-2. 限定受容の許可範囲

- **継続YES：** 現存版と欠損項目を区別した索引・台帳の整理、公開一次資料の読取、既存保証B契約の静的反例・必要条件のレビュー、Q2候補の公開source/版/API/観測境界の読み取り審査、今後の文書設計と独立文書レビュー。これらは過去証拠の完全性を主張しない。
- **継続NO：** 欠損原物の架空作成、現存版を過去版と断定、過去の完全な作成・閉鎖証明、保証B PASS、B_use実証、Q2の完成方式採用、backendコード実装、実測、Linux権限変更・ptrace/対象起動、CI強制起動、PR #35の製品受入、Draft解除、マージ。
- **再探索の発動条件：** 既知原ファイル名・保存参照ID・具体的な保存領域・既知SHA・当時担当からの新しい回答など**新規で限定可能な手掛かり**がある場合のみ、許可済み範囲を読取調査。手掛かりがなければ探索の範囲を広げずUNKNOWNを維持する。
- **保全：** B-R2の902原物・receipt・監査原票の再保存は不要。既存の保持契約と原物不変更を維持。今回新たに作成する普通のGitHub設計文書はLevel 1として管理し、別途Archiveの一律保存は求めない。Level 2の新規原物が発生する場合だけ個別に分類・承認条件を判定する。

この限定受容は、ユーザーの2026-11-19依頼で指定された「UNKNOWNを保持した設計・資料審査の継続」に限る。歴史的欠損の解消承認や品質保証の代替と拡大解釈しない。後日に新しい具体証拠が出た場合は追記再判定する。

## 2. 第2工程：Q2の固定候補（一方式のみ）

**候補：Taintgrind v3.27.1 + Valgrind 3.27.1、x86/amd64/arm Linuxの動的命令・データ追跡。** Q2に必要な「同じDの実operand/provenanceを検査対象外に移さず監視する」構成に近い実在の資料候補として選定。**完成済みB_use oracleとしての採用ではない。**

|証拠ID|実在する資料・固定版|読取で確認できる事項|読取では証明できない事項|
|---|---|---|---|
|Q2-S1|Taintgrind GitHub tag [v3.27.1](https://github.com/wmkhoo/taintgrind/tree/v3.27.1)、commit `2f7f792f0e99838508970d0f18181aeff8b9ad76`、[README](https://github.com/wmkhoo/taintgrind/blob/v3.27.1/README.md)|2026-06-15にValgrind 3.27.1/x86_linux/amd64_linux/arm_linux対応を記載。ソース・使い方・明記された制限を確認|この対象D/OS/ABIでのbuild成功、実命令・JIT・暗号ライブラリ全範囲のcoverage|
|Q2-S2|[tnt_translate.c](https://github.com/wmkhoo/taintgrind/blob/v3.27.1/tnt_translate.c)、[tnt_main.c](https://github.com/wmkhoo/taintgrind/blob/v3.27.1/tnt_main.c)、[tnt_syswrap.c](https://github.com/wmkhoo/taintgrind/blob/v3.27.1/tnt_syswrap.c)|VEX IR上の汚染値伝播、shadow状態、syscall wrapperの実ソースを識別|今回epoch/task/sourceを区別する非改変・非迂回のorigin-ID証明、独立checker、全経路完全性|
|Q2-S3|Valgrind公式の[tool作成仕様](https://valgrind.org/docs/manual/manual-writing-tools.html)、[v3.27.1配布元](https://sourceware.org/pub/valgrind/valgrind-3.27.1.tar.bz2)|tool `instrument()` とVEX IRの観測機構。バージョンが存在すること|Taintgrindが元Dと意味的に同一の実行を保証すること、ソースから実物への対応、時間成立|
|Q2-S4|[Taintgrind READMEのNotes](https://github.com/wmkhoo/taintgrind/blob/v3.27.1/README.md)|explicit data flowのみ追跡。制御フローの依存、および汚染ポインタを間接参照した場合の依存は追跡しないと明記|全D命令の追跡可能性、制御依存・間接参照・native/JIT経路欠測時の適正拒否|

Valgrind全体の2026-10-23最新安定版は3.28.0だが、**Taintgrindの当該tagが対応を明記する3.27.1**に固定し、3.28.0との互換性は推定しない。対象Linux環境への取得・導入・実行はしていない。

### 2-1. 既知の不適格点：同値の旧Buffer反例

- Good：新しいhandoffのXを受け、DがSHA/ELF/proofに使う。
- Bad：Dは新しいhandoffのXを一度読んでも捨て、別由来の旧Buffer X（同じbyte列）をSHA/ELF/proofに使い、現在のreceipt等と組み合わせる。
- **現行Taintgrind単体の不足：** `TAINTED/UNTAINTED` 等の伝播状態と「その値が今回のFD/epochから来たこと」の厳密な識別は別命題。旧Bufferも以前の追跡対象としてtaintedなら、両方のoutputはtaintedになり得る。単純な汚染到達だけではGoodとBadを必ず識別できない。control-flow/汚染ポインタ由来はREADMEが対象外とする。
- **判定：** *現行Taintgrind単体を完成済みB_use判定器とみなす方式は不適格（採用NO）*。これはQ2全般が数学的に不可能という結論ではなく、今回固定した実在版での完成性の不足である。

### 2-2. Q2を再検討できるための具体的解除条件

1. **origin取得：** Kのkernel pin→trusted read→Dへ交付した新payloadを、旧Xと区別する非偽造のepoch/task/case/source識別へ対応づける実sourceと権限。Dの自己申告を真実にしない。
2. **全命令経路：** Dとそのruntime/native cryptography・ELF処理・proof・動的生成コード/JITについて、実行されるread/store/copy/branch/pointer/syscall/helperと出力依存が欠落なく追える証拠。非対応ならfail-closed。合法copyは受理し、値一致のみで旧originを洗い替えしない。
3. **独立性：** instrumentationと独立trace checkerの正確なsource/build/実物SHA、変更不能な証拠取得lane、K sole ptracerと競合しない実行境界。traceをDの書込可領域から真実として採らない。
4. **実行環境：** 正式に認可されたLinux/非root権限/必要ABI、起動・有限停止・tracer死亡時の扱い・cleanup・保存経路。root化、sandbox解除、ptrace制限緩和を前提にしない。
5. **反例と時間：** 同値旧Bufferを含む偽陽性をFAILにし、正当な別Buffer copyと正常受理をPASSにする独立反例。固定23slot（L19/M4）と総上限1160秒の変更なしで成立する時間/出力量/後片付けの証拠。
6. **実データ/採用：** 対象Dの実source/build・instance lineage・task/epoch/leaseに結び付く実入力・独立検証を得た後、**別の実装／実測開始承認**を取る。

今回確認できたのは**実在ソース・版・機構の一部・既知の適用限界**だけ。Q2の完全成立構成、非迂回性、独立checker、対象Dの実instrumentation、23枠予算、終了安全性、適格Linuxの存在はすべて**UNKNOWN/NOT_READY**。候補採用YESは0、backend実装NO、本実測NO。

## 3. 判定と変更禁止境界

|項目|Stage B-S現判定|
|---|---|
|第1工程：欠損付き資料整理・公開source読取の継続|**限定YES**。不足は個別UNKNOWNのまま|
|改稿前byte/閉鎖専用原票/作成・登録来歴の存在・完全性|**UNKNOWN**。欠損受容でPASSにしない|
|第2工程：Taintgrind v3.27.1の実source/版調査|**資料確認PASS（部分）**。source全経路の独立レビューは未実施|
|現行Taintgrind単体を完成済みB_use oracleとして採用|**NO（不適格）**|
|拡張を含むQ2一般実現可能性|**UNKNOWN**|
|Linux環境・終了・時間・全依存経路|**BLOCKED／NOT_READY**|
|Stage B-R2 Windows Level 2証拠保全|**既存の限定PASSを維持**。新規コピー0|
|PR #36正式CI・技術受入|**NOT_TESTED／PARTIAL**|
|backend実装／本実測／PR #36マージ|**NO／NO／NO**（Draft維持）|

**停止規則：** 今回調べた固定1方式については、追加する実source/具体的な新根拠が提示されなければ同じ一般論の調査・設計文書の増設を繰り返さない。次に実証へ進むには、上記の具体的解除証拠と所有者による別承認が必要。PR #35のWebKit問題は別件として保持する。

## 4. 検証範囲の透明性

公開資料とGitHubの既存記録を静的に読んだ結果である。Taintgrind/Valgrindの全ソースの完全解析、tarballのハッシュ再計算、署名検証、ローカル取得・ビルド・実行、Linux能力試験、性能試験、実物rawの新規採取、正式CI、作成担当からの照会は**未実施**。独立した別担当によるStage B-S文書レビューも未実施。ユーザーが承認したのは「欠損UNKNOWNを保持した限定資料審査の推進」であり、実験・技術採用・マージ等の新承認はしていない。
