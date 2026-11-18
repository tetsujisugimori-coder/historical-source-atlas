# Stage B-S：DFSan欠損の限定受容・Q2候補1方式の静的ソース審査

## 最新判定追補：Stage B-S2 独立再審査の確定（2026-11-19 JST）

**文書限定独立再審査 PASS。BS-P2-01（固定版の記述）と BS-P3-01（DFSan第6欠損の独立行）は文書指摘として CLOSED。** 根拠は [独立レビュー #5966316287](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#pullrequestreview-5966316287)（審査対象HEAD `67739c34deb7e5379438e6b3b34587c19ccc95fa`、COMMENTED）。これは**文書についての閉鎖**であり、TaintgrindとValgrind 3.27.1の固定ペア互換性、ビルド／実行、保証B、DFSan歴史的欠損の技術的解消を意味しない。

|最新の対象|判定|維持する境界|
|---|---|---|
|BS-P2-01|**CLOSED（文書）**|固定tag `v3.27.1` と固定README／DockerfileのValgrind **3.25.1** 記述を区別。Valgrind **3.27.1** の公式配布物の実在と固定ペア互換性を混同せず、互換性 **UNKNOWN**、ビルド・実行 **NOT_TESTED**|
|BS-P3-01|**CLOSED（文書）**|改稿前byte、閉鎖専用原票、実作成主体、正確な原作成時刻、初期登録履歴、当時の原ファイル識別・版対応の**歴史的6欠損はすべて UNKNOWN**|
|BS-P2-02|**OPEN（技術）**|K/Oから独立する偽造不能なorigin・epoch証明と独立checker未成立。taint状態・Dのclient request・値一致を`B_use=PASS`へ転用禁止|
|BS-P2-03|**OPEN（技術）**|実FD/OFD→読取→SHA／ELF／proof各operandの完全追跡、未対応syscall・scatter-gather・native／JITの欠測検知・fail-closed未成立|

**新しい一次根拠の有無：** この判定同期では、BS-P2-02／03を解除できる新しい固定source/build、独立trace原票、Good／旧Buffer Bad反例の検証結果は提示・取得されていない。既存の第2章に必要証拠と採用禁止条件があるため、同じ静的な一般論の重複審査を行わず**OPEN維持**とする。具体的な新証拠と別途承認が得られるまで実装・実測・技術的CLOSEDへ進めない。

**中央規約 [v0.2.0](https://github.com/tetsujisugimori-coder/git-preservation-gate/blob/4695c3ce2d61e66df0dd36a4312373459e1557d4/docs/v0.2.0/policy.md) の適用：** 今回の公開GitHub文書追補は**Level 1**（Git履歴と案件別レビューで管理、追加Archive保存は非適用）。既存Stage B-R2の重要原票902単位は**Level 2の限定保存・再取得PASSを維持**し、再コピー・上書きしない。Level 1の追加Archive CUSTODY／VERIFICATION／INDEPENDENCEは **NOT_TESTED・非適用**であり、既存Level 2保全の判定を変更しない。人的独立性は `LIMITED_SHARED_OWNER` のまま。

**PR #36全体：PARTIAL、保証B UNKNOWN、Q2一般実現性 UNKNOWN、現行Taintgrind単体の完成方式採用 NO、backend実装 NO、本実測 NO、正式CI NOT_TESTED、Open・Draft維持、マージ NO。** 本追補自体の別担当による独立再審査は未実施であり、先行B-S2の審査PASSを新HEAD全体の独立承認へ自動拡張しない。

**履歴の扱い：** 以下の初期判定表や「独立再審査PENDING」は補訂前の状態を示す履歴として保持し、現行判断には本追補と上記固定レビューを優先する。

---

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
|当時の実作成主体|UNKNOWN|GitHubの投稿者・OWNER属性・既存の役割名から当時の作成主体を断定しない|
|当時の正確な原作成時刻|UNKNOWN|現存版の保存日時・報告時刻を原作成時刻へ転用しない|
|当時の初期登録履歴|UNKNOWN|現在のLibrary・GitHub登録記録だけから初回登録IDや登録経緯を復元しない|
|当時の原ファイル識別・版対応|UNKNOWN|現存ファイル名・ZIP内entry・既知SHAから、当時の原ファイル識別子と改稿前／閉鎖時等の歴史版の一対一対応を認定しない。独立した原票や版対応表は未回収|
|分離stderr、当時の実効Windows権限・正確なPython版|UNKNOWN|新しい検査や現在の環境値で過去実行を補完しない|

根拠：[Stage B-R2独立監査 #5961724602](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#pullrequestreview-5961724602)、[Stage B-R2限定閉鎖 #5964826899](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#pullrequestreview-5964826899)、PR #36現行本文。

補訂（2026-11-19 JST）：BS-P3-01対応で欠損A〜Fを独立6行へ整理した。現存のファイル名・hashが分かっても、当時の原ファイル識別や歴史版対応が立証されたとはしない。

### 1-2. 限定受容の許可範囲

- **継続YES：** 現存版と欠損項目を区別した索引・台帳の整理、公開一次資料の読取、既存保証B契約の静的反例・必要条件のレビュー、Q2候補の公開source/版/API/観測境界の読み取り審査、今後の文書設計と独立文書レビュー。これらは過去証拠の完全性を主張しない。
- **継続NO：** 欠損原物の架空作成、現存版を過去版と断定、過去の完全な作成・閉鎖証明、保証B PASS、B_use実証、Q2の完成方式採用、backendコード実装、実測、Linux権限変更・ptrace/対象起動、CI強制起動、PR #35の製品受入、Draft解除、マージ。
- **再探索の発動条件：** 既知原ファイル名・保存参照ID・具体的な保存領域・既知SHA・当時担当からの新しい回答など**新規で限定可能な手掛かり**がある場合のみ、許可済み範囲を読取調査。手掛かりがなければ探索の範囲を広げずUNKNOWNを維持する。
- **保全：** B-R2の902原物・receipt・監査原票の再保存は不要。既存の保持契約と原物不変更を維持。今回新たに作成する普通のGitHub設計文書はLevel 1として管理し、別途Archiveの一律保存は求めない。Level 2の新規原物が発生する場合だけ個別に分類・承認条件を判定する。

この限定受容は、ユーザーの2026-11-19依頼で指定された「UNKNOWNを保持した設計・資料審査の継続」に限る。歴史的欠損の解消承認や品質保証の代替と拡大解釈しない。後日に新しい具体証拠が出た場合は追記再判定する。

## 2. 第2工程：Q2の固定候補（一方式のみ）

**静的審査用の固定候補：Taintgrind tag `v3.27.1`（commit `2f7f792f0e99838508970d0f18181aeff8b9ad76`）＋Valgrind 3.27.1。** 両者の**配布・ソースの実在は確認済み**だが、**この固定ペアの互換性はUNKNOWN、ビルド・実行はNOT_TESTED**。固定READMEに記載のLinux x86／amd64／ARM32対応はValgrind **3.25.1** の行に属し、3.27.1との組合せの動作証拠として利用しない。Q2に必要な実operand/provenance観測に近い資料候補として扱うが、**完成済みB_use oracleとして採用しない**。

|証拠ID|実在する資料・固定版|読取で確認できる事項|読取では証明できない事項|
|---|---|---|---|
|Q2-S1|Taintgrind GitHub [tag v3.27.1](https://github.com/wmkhoo/taintgrind/tree/2f7f792f0e99838508970d0f18181aeff8b9ad76)、commit `2f7f792f0e99838508970d0f18181aeff8b9ad76`、[そのcommitのREADME](https://github.com/wmkhoo/taintgrind/blob/2f7f792f0e99838508970d0f18181aeff8b9ad76/README.md)|tag/ソースの実在。固定README冒頭で明記されるのは**2025-05-27付のValgrind 3.25.1** とx86_linux／amd64_linux／arm_linuxへの対応であり、3.27.1対応の記載ではない|固定候補とValgrind 3.27.1の互換性、対象D/OS/ABIでのビルド成功、実命令・JIT・暗号ライブラリ全経路のcoverage|
|Q2-S2|[tnt_translate.c](https://github.com/wmkhoo/taintgrind/blob/v3.27.1/tnt_translate.c)、[tnt_main.c](https://github.com/wmkhoo/taintgrind/blob/v3.27.1/tnt_main.c)、[tnt_syswrap.c](https://github.com/wmkhoo/taintgrind/blob/v3.27.1/tnt_syswrap.c)|VEX IR上の汚染値伝播、shadow状態、syscall wrapperの実ソースを識別|今回epoch/task/sourceを区別する非改変・非迂回のorigin-ID証明、独立checker、全経路完全性|
|Q2-S3|Valgrind公式の[tool作成仕様](https://valgrind.org/docs/manual/manual-writing-tools.html)、[v3.27.1配布元](https://sourceware.org/pub/valgrind/valgrind-3.27.1.tar.bz2)|tool `instrument()` とVEX IRの観測機構。バージョンが存在すること|Taintgrindが元Dと意味的に同一の実行を保証すること、ソースから実物への対応、時間成立|
|Q2-S4|[固定Taintgrind READMEのNotes](https://github.com/wmkhoo/taintgrind/blob/2f7f792f0e99838508970d0f18181aeff8b9ad76/README.md)|explicit data flowのみ追跡。制御フロー依存、tainted pointerの間接参照の依存は追跡しないと明記|全D命令の追跡可能性、制御依存・間接参照・native/JIT経路欠測時の適正拒否|
|Q2-S5|[固定Dockerfile](https://github.com/wmkhoo/taintgrind/blob/2f7f792f0e99838508970d0f18181aeff8b9ad76/Dockerfile)、[build_taintgrind.sh](https://github.com/wmkhoo/taintgrind/blob/2f7f792f0e99838508970d0f18181aeff8b9ad76/build_taintgrind.sh)|DockerfileはValgrind **3.25.1** をダウンロードし、Taintgrindをtag/commit未指定でclone。ビルドはValgrindソース・Autotools・Capstone取得とパッチ適用に依存|固定tagとValgrind 3.27.1を再現可能に組み立てられること、依存版の一致、認可Linuxでの成功|

**BS-P2-01の訂正：** Taintgrindのtag名が`v3.27.1`であることと、固定README/DockerfileがそのValgrind版との互換性を明記・再現することは別。固定README・Dockerfileは3.25.1を示す。Valgrind 3.27.1の**公式配布物の実在と公表SHA-512との一致は別担当の独立静的レビューで報告済み**（署名検証NOT_TESTED）だが、固定Taintgrind tagとの**ペア互換性UNKNOWN、ビルド/動作NOT_TESTED**。3.28.0等ほかの版の互換性も推定しない。実環境への取得・導入・実行は今回行わない。[Stage B-S独立レビュー #5965496603](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#pullrequestreview-5965496603)。

### 2-1. 既知の不適格点：同値の旧Buffer反例

- Good：新しいhandoffのXを受け、DがSHA/ELF/proofに使う。
- Bad：Dは新しいhandoffのXを一度読んでも捨て、別由来の旧Buffer X（同じbyte列）をSHA/ELF/proofに使い、現在のreceipt等と組み合わせる。
- **現行Taintgrind単体の不足：** `TAINTED/UNTAINTED` 等の伝播状態と「その値が今回のFD/epochから来たこと」の厳密な識別は別命題。旧Bufferも以前の追跡対象としてtaintedなら、両方のoutputはtaintedになり得る。単純な汚染到達だけではGoodとBadを必ず識別できない。control-flow/汚染ポインタ由来はREADMEが対象外とする。
- **判定：** *現行Taintgrind単体を完成済みB_use判定器とみなす方式は不適格（採用NO）*。これはQ2全般が数学的に不可能という結論ではなく、今回固定した実在版での完成性の不足である。

### 2-1a. BS-P2-02（独立origin／epoch真正性）OPEN

**原因：** 現行Taintgrindのshadow/taint伝播は、当期のK pin→trusted read→handoffという**真正な入力由来**と自動的に同義ではない。[固定tnt_main.cのclient request](https://github.com/wmkhoo/taintgrind/blob/2f7f792f0e99838508970d0f18181aeff8b9ad76/tnt_main.c#L3777-L3794)には`TAINT`／`TAINT_NAMED`／`UNTAINT`によるshadow操作入口があり、D側の要求や命名を独立したepoch証明と認定すると循環する。Goodで正常copyしたXと、Badで当期Xを読んで捨て既にtaintedな旧Xを利用する場合を、taint有無と値一致だけでは必ずしも分離できない。

**欠損証拠：** K/OがDの自己申告から独立に採取・保持するtask/case/epoch/FD/OFDの識別、当期handoffに対する偽造不能なorigin付与・失効、実read-from/store/copyからSHA・ELF・proofの各sinkへの連続的依存、およびDから変更できない収録経路・独立checkerの固定source/build/実物とGood/Bad反例の判定原票。

**採用禁止条件：** `tainted=true`、名付きtaint、Dが発したclient request、Dの自己申告receipt・ログ、SHA一致だけで`B_use=PASS`としない。K/Oの由来認証と独立検証が未成立の間、**BS-P2-02=OPEN、現行候補のB_use受入NO**を維持する。文書補訂は技術閉鎖ではない。

### 2-2. Q2を再検討できるための具体的解除条件

1. **origin取得：** Kのkernel pin→trusted read→Dへ交付した新payloadを、旧Xと区別する非偽造のepoch/task/case/source識別へ対応づける実sourceと権限。Dの自己申告を真実にしない。
2. **全命令経路：** Dとそのruntime/native cryptography・ELF処理・proof・動的生成コード/JITについて、実行されるread/store/copy/branch/pointer/syscall/helperと出力依存が欠落なく追える証拠。非対応ならfail-closed。合法copyは受理し、値一致のみで旧originを洗い替えしない。
3. **独立性：** instrumentationと独立trace checkerの正確なsource/build/実物SHA、変更不能な証拠取得lane、K sole ptracerと競合しない実行境界。traceをDの書込可領域から真実として採らない。
4. **実行環境：** 正式に認可されたLinux/非root権限/必要ABI、起動・有限停止・tracer死亡時の扱い・cleanup・保存経路。root化、sandbox解除、ptrace制限緩和を前提にしない。
5. **反例と時間：** 同値旧Bufferを含む偽陽性をFAILにし、正当な別Buffer copyと正常受理をPASSにする独立反例。固定23slot（L19/M4）と総上限1160秒の変更なしで成立する時間/出力量/後片付けの証拠。
6. **実データ/採用：** 対象Dの実source/build・instance lineage・task/epoch/leaseに結び付く実入力・独立検証を得た後、**別の実装／実測開始承認**を取る。

### 2-2a. BS-P2-03（追跡経路欠測・fail-closed不足）OPEN

**原因：** [固定tnt_main.cのsyscall dispatch](https://github.com/wmkhoo/taintgrind/blob/2f7f792f0e99838508970d0f18181aeff8b9ad76/tnt_main.c#L3596-L3719)ではpre-syscall handlerは空で、post-syscallの許可確認呼出しの結果をここで拒否として適用せず、未列挙syscallのdefault拒否も見えない。[固定tnt_syswrap.cのrecvmsg](https://github.com/wmkhoo/taintgrind/blob/2f7f792f0e99838508970d0f18181aeff8b9ad76/tnt_syswrap.c#L654-L665)にはscatter-gather／`readv`未対応の注記があり、`msg_control`にtaintを付す処理は交付されたOFDとDが実消費したoperandの由来を証明しない。IR命令側のpanicとsyscall全経路のfail-closedは別の主張である。

**欠損証拠：** `SCM_RIGHTS`で交付された実FD／OFDから実readした各byte範囲・consumer operandまでの証拠、`readv`／scatter-gather／`recvmsg`を含む全利用経路の追跡coverage、未対応命令・syscall・helper・native/JIT経路の欠測検知と拒否、通常の正当copyを許容した反例と旧Bufferの拒否原票。これらの独立source/実測は未取得。

**採用禁止条件：** unsupported syscallや追跡欠測を無視して全経路観測済みと認定しない。`recvmsg`のtaintや一部IR命令の追跡成功を全FD→sinkのorigin証明に転用しない。**BS-P2-03=OPEN、完全coverage・fail-closedの受入NO**を維持する。文書補訂は技術閉鎖ではない。

今回確認できたのは**実在ソース・版・機構の一部・既知の適用限界**だけ。Q2の完全成立構成、非迂回性、独立checker、対象Dの実instrumentation、23枠予算、終了安全性、適格Linuxの存在はすべて**UNKNOWN/NOT_READY**。候補採用YESは0、backend実装NO、本実測NO。

## 3. 判定と変更禁止境界

|項目|Stage B-S現判定|
|---|---|
|第1工程：欠損付き資料整理・公開source読取の継続|**限定YES**。不足は個別UNKNOWNのまま|
|改稿前byte/閉鎖専用原票/作成・登録来歴の存在・完全性|**UNKNOWN**。欠損受容でPASSにしない|
|第2工程：Taintgrind v3.27.1の実source/版調査|**実在資料の限定静的再審査PASS**。Valgrind 3.27.1ペア互換性UNKNOWN、全経路の実証NOT_TESTED|
|BS-P2-01（固定tagの対応版記述）|**文書補訂済／独立再審査PENDING**。固定ペア互換性UNKNOWN、ビルド・実行NOT_TESTED。旧レビュー指摘OPENの閉鎖は別担当が判定|
|BS-P3-01（6番目のDFSan欠損）|**文書補訂済／独立再審査PENDING**。当時の原ファイル識別・版対応UNKNOWNは不変更|
|BS-P2-02（origin・epochの真正性）|**OPEN／技術未成立**。taintとDのclient requestを独立証拠として採用禁止|
|BS-P2-03（全経路欠測時拒否）|**OPEN／技術未成立**。syscall・scatter-gather等の欠測を隠して完全coverageと認定禁止|
|現行Taintgrind単体を完成済みB_use oracleとして採用|**NO（不適格）**|
|拡張を含むQ2一般実現可能性|**UNKNOWN**|
|Linux環境・終了・時間・全依存経路|**BLOCKED／NOT_READY**|
|Stage B-R2 Windows Level 2証拠保全|**既存の限定PASSを維持**。新規コピー0|
|PR #36正式CI・技術受入|**NOT_TESTED／PARTIAL**|
|backend実装／本実測／PR #36マージ|**NO／NO／NO**（Draft維持）|

**停止規則：** 今回調べた固定1方式については、追加する実source/具体的な新根拠が提示されなければ同じ一般論の調査・設計文書の増設を繰り返さない。次に実証へ進むには、上記の具体的解除証拠と所有者による別承認が必要。PR #35のWebKit問題は別件として保持する。

## 4. 検証範囲の透明性

公開資料とGitHubの既存記録を静的に読んだ結果である。[別担当の独立静的レビュー #5965496603](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#pullrequestreview-5965496603)により、Taintgrind固定5ソースの取得・Git blob照合、Valgrind 3.27.1公式tarballのSHA-512照合と内包仕様の確認、BS-P2-01〜03・BS-P3-01の指摘が報告された。これは**静的資料審査**であり、固定ペアの互換性・ビルド・実行、全経路の技術的保証の証拠ではない。本補訂はその指摘を対象文書に反映したもので、独立した**補訂後の再審査はPENDING**。

Taintgrind/Valgrindの全ソースの完全解析、署名検証、固定ペアのビルド・実行、Linux能力試験、性能試験、保証Bのraw実測、正式CI、歴史的作成担当への追加照会は本工程で**未実施**。所有者が認めたのは「欠損UNKNOWNを保持した限定資料審査」であり、実験・技術採用・マージの新承認ではない。旧文書・独立レビューの本文と固定HEADはGit履歴上に保持し、改稿前の誤認を削除してなかったことにしない。
