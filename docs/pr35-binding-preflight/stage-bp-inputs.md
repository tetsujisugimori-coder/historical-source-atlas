Stage B-P / 版1.3 / 2026-11-16 JST / 基準HEAD4297ce68a6ac60ac2e60365c37c649d548dabe8f・tree190adc2c41f394e073664a26e75548d868a7a5f9。内容SHAはmanifest.sha256。設計/静的審査のみ、現640ゲート・実装/実測承認は不変更。

# 実入力と1160秒の固定可能性

## 台帳の意味

実入力は未生成。以下の各caseは同じ必須descriptorを持つ設計台帳で、実fileを作成した台帳ではない。source commitは将来target/K/O/D/I sourceのcommitを指し、文書基準4297ceや既存native640をその実装sourceとして代入しない。既存のA-only toy fixtureが存在しても、このStage B-Pで適格source/entry/TCBを固定した実入力とはみなさない。

各rowの共通descriptor **U** は source_commit=UNKNOWN、binary/fixture=NOT_GENERATED、file_size/SHA256/build_ID=UNKNOWN、verity_digest=UNKNOWN（適用不要の根拠も未固定ならnullをN/Aへ変えない）、object_pin/M/T=UNKNOWN、kernel ack/raw=NOT_GENERATED、budget_basis=UNKNOWN、read_handoff/derivation_binding=UNKNOWN、cleanup_time_bound=UNKNOWN。すべてのcaseに明示適用し、null同士を一致としない。予算成立判定は全row NOT_READY、試行実績は全row NOT_RUN。

予定独立ackのE/M/T/Fは既存oracle-contract、B_use因果境界の不足は[TCB審査](stage-bp-tcb.md)を参照。必須原票セット **P** は原入力/固定manifest、source Git/実file、K raw、O独立ack、I intent/return、D R/V/proof、phase別正常受理、stdout/stderr、byte上限/破棄、timeout/終了/close/残存/保存と独立照合。Mはkernel実物を持たず固定model traceと独立期待台帳をPの該当laneへ置き、Lへ流用しない。

## case別固定可能性（各1回、追加試行0）

|系列/slot/case|source/binary/hash/ID/verity/object/M/Tの現値|必要ackと前後状態/固定期待|必須原票・phase/終了時間根拠|
|---|---|---|---|
|L01 /01|U|O F/M/T・正常full identity PASS/0|P・L配分・根拠UNKNOWN|
|L02 /02|U|E commit A→B、R旧拒否、V、新再停止proof PASS/0|P・R/V/新proof別、L配分・UNKNOWN|
|L03 /03|U|E 2commit A→B→A、中間B/最終g2、R/V、新proof PASS/0|P・g0再利用不可、L配分・UNKNOWN|
|L04 /04|U|F/M/path差替え、元exe objectの正常PASS/0|P・L配分・UNKNOWN|
|L05 /05|U|旧/新owned寿命参照、旧handle拒否、実PID再利用未観測ならNOT_TESTED|P・同slotの2寿命、L配分・UNKNOWN、反復禁止|
|L06 /07|U|F/M/path差替え、元library正常PASS/0|P・L配分・UNKNOWN|
|L07 /08|U|unlink後元object/version正常PASS/0|P・L配分・UNKNOWN、事後BLOCKED期待へ変更禁止|
|L08 /09|U|rename後元object/version正常PASS/0|P・L配分・UNKNOWN、取得拒否は16/17/18|
|L09 /10|U|M退役/新mapping差、R/V、新M proof正常PASS/0|P・removed/added tuple両方、L配分・UNKNOWN|
|L10 /11|U|M追加非空・既存保持、R/V、新proof正常PASS/0|P・L配分・UNKNOWN|
|L11 /12|U|T new member、未停止中B0件、全停止後新proof PASS/0|P・不完全/適格phase別、L配分・UNKNOWN|
|L12 /13|U|全stop未達→STOP_INCOMPLETE/BLOCKED、B0件|P・live安全承認未成立、L配分・UNKNOWN|
|L13 /14|U|resume/step境界の旧proof→BLOCKED/1|P・live安全承認未成立、L配分・UNKNOWN|
|L14 /15|U|owned実終了→EXITED/BLOCKED、D/K exitと区別|P・L配分・UNKNOWN|
|L15 /16|U|事前指定の既存permission拒否→BLOCKED/1|P・必要operation到達、L配分・UNKNOWN|
|L16 /17|U|exe acquisition故障到達→BLOCKED/1|P・fault surface未固定、L配分・UNKNOWN|
|L17 /18|U|mapping acquisition故障到達→BLOCKED/1|P・coverage原票、L配分・UNKNOWN|
|L18 /21|U|偽caller/旧epoch入口→拒否BLOCKED/1|P・L配分・UNKNOWN、偽値をack源にしない|
|L19 /22|U|01同一固定normal bytes、fresh task/epoch、PASS/0|P・L配分・UNKNOWN|
|M01 /M0|U|固定toy trace/独立期待、model正常PASS/0|Pのmodel lane・M配分・UNKNOWN|
|M02 /06|U|固定lifetime/startTicks不一致→BLOCKED/1|Pのmodel lane・M配分・UNKNOWN|
|M03 /19|U|固定不完全read/破損/ID欠測の有限trace→拒否|Pのmodel lane・M配分・UNKNOWN|
|M04 /20|U|close失敗/未確認/遅延の有限trace→完了BLOCKED/1|Pのmodel lane・M配分・UNKNOWN|

Uのbuild IDやverityが不要となるmodel入力も、実入力schemaで理由を固定した後にのみN/Aにできる。今は全rowの該当実物を未生成として扱う。文書契約の内容SHAと将来fixture hashは別である。

## 予算の成立可能性

元順序はL `01,02,03,04,05,07,08,09,10,11,12,13,14,15,16,17,18,21,22`、M `M0,06,19,20` のまま。19×60=1140秒、4×5=20秒、全1160秒、各case1回・追加0。case ID・正常/故障期待を変更しない。

Lの既存配分8秒準備/生成+10秒初期proof+14秒R/注入/ack+18秒V/再停止/新proof+10秒保存/cleanup=60秒。Mは0.5+1.5+1.5+1.5=5秒を保持。保存/終了/close/資源解放の全時間をslot起点から含め、後段へ期限を延ばさない。追加のB_use観測/receipt/TCB照合もこの内側、収まる根拠がなければNOT_READY。

R一致、V一致、全停止再確認、新proof帰属、適格正常受理、期限/cleanup/保存を別fieldとし、全部の必要条件が確認済みでなければcase PASSにしない。R consumer return1とD/K OS exit、normal return0とfull B実証を区別。権限/観測不能はUNKNOWN/BLOCKED、未到達はNOT_REACHEDで故障検出PASSでない。適格正常状態のD常時拒否はFAIL、現在の入力未生成/開始前NOT_READYは試験FAILではない。

各phaseに実体/上限/保存byte量/終了回収の根拠がなく、TCB因果観測と有限cleanupも未成立なので、現在の予算評価はUNKNOWN、全slot NOT_READY。算術合計が合うことを実行可能性の実証にしない。試行数・期限・正常期待の変更で成立した扱いにしない。
