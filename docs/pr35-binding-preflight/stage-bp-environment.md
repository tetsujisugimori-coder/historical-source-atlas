Stage B-P / 版1.3 / 2026-11-16 JST / 基準HEAD4297ce68a6ac60ac2e60365c37c649d548dabe8f・tree190adc2c41f394e073664a26e75548d868a7a5f9。内容SHAはmanifest.sha256。設計/静的審査のみ、現640ゲート・実装/実測承認は不変更。

# Linux・安全終了の成立可能性台帳

今回の資料範囲は4297ceの環境/方法/cleanup文書、レビュー5919580472、既存の拒否/保全原票、Linux一次仕様。認可済みLinuxへの接続/起動/探索・対象生成・実proc照会は行わない。O-Kは第一候補、O-G/GDBはHOLD、C2 numeric PID attachは所有bridge競合窓未解決でHOLD。

次のUはUNKNOWN、NTはNOT_TESTED。installed/callable/authorized/measuredは別欄であり、「仕様に存在」をinstalledへ転用しない。今回のcandidate Linuxについて全機構の実体/版/許可が未取得である。

|要件|installed|callable|authorized|measured|必要な証拠・実装前判定|
|---|---|---|---|---|---|
|host利用範囲|U|U|U|NT|主体/host/期間/生成・trace・cleanup範囲なし。環境BLOCKED|
|kernel/arch/ABI|U|U|U|NT|正確build/config/namespaceとtarget/K/O/D ABI・tool/sourceの対応。NOT_READY|
|UID/eUID/通常権限|U|U|U|NT|両非root値と既存LSM/Yama/seccomp/proc policy。新権限なしで必要操作許可が必要|
|pidfd/出生所有|U|U|U|NT|生成時task handle、S台帳、reap前参照保持の対応。PIDだけ不可|
|sole tracer|U|U|U|NT|出生からK一つ、所有→制御bridge、第二ptracerなし。NOT_READY|
|TRACEEXEC/CLONE/EXIT|U|U|U|NT|実kernelのevent/非leaderexec/thread寿命、fork/vfork経路もcoverage閉包内か。CLONEだけで全出生を断定しない|
|全thread stop/event|U|U|U|NT|各thread stop ack、未処理出生/終了0、排他barrier、中間exec捕捉/欠落検出|
|proc/maps/map_files|U|U|U|NT|必要kernel objectを取得できる既存通常権限。権限不足なら当該方式不適格、caps付与禁止|
|SCM_RIGHTS/KCMP_FILE|U|U|U|NT|実ancillary/peer/lifetime/nonce、同OFD比較、seccomp/syscall/正規アクセス|
|trusted reader分離|U|U|U|NT|K/O lane・source・書込/制御分離、actual-entry handoff証拠。B_use保証UNKNOWN|
|不変backing/fs-verity|U|U|U|NT|実行/map中の同objectの既存verity/全writer排除、full SHA/build IDとは別digest|
|同D/K instance|U|U|U|NT|R→V→新proofのlifetime/state lineage、restart不可|
|K死亡kernel動作|U|U|U|NT|auto-detach/resume/killの正確なmodeと承認済み所有対象限定policy|
|S wait/adoption/reap|U|U|U|NT|K死亡後にSが合法に終了status回収できる親/adoption経路、終了と残存の原票|
|FD/IPC/task/保存cleanup|U|U|U|NT|参照・inflight FD・所有task・writer別の完了/残存、slot内有限性|

既存Windowsのtool版は過去文書の観測履歴でありLinux適格性でない。Archive拒否は過去証拠で、host権限を類推しない。未認可hostへの接続や新WSL/cloud/runnerの構築で欄を埋めない。

## 終了・制御喪失の独立反例

|反例|必要な独立証拠/判定|未成立の理由|
|---|---|---|
|K死亡後auto-detach/resume|kernel版/ptrace mode別挙動と、出生所有対象だけの承認済みfail-stop/復帰policy|lease失効だけは物理的停止でない。未固定ならNOT_READY|
|Kの子targetが孤児化|Sの合法parent/adoption routeと新parent/owned lifetime追跡|SがKの親でもtargetのwait親とは限らない|
|pidfdは生存終端を示すがexit status取得不能|合法wait権限とkernel termination原票、ECHILD等の実結果|pidfd保有/pollをwait権限としない。未確認なら終了UNKNOWN/cleanup BLOCKED|
|TERM/KILL要求だけ成功|S/Kが対象の実終了、controller終了、close、資源、残存、保存を別原票で確認|要求ackを全完了へ転用不可。実終了未確認ならBLOCKED|
|kernel I/O/終了/closeが期限内に終わらない|固定した故障model/期限/責任、未完了の正直な分類|watchdog returnは有限cleanupの証明でない。hard有限性の根拠なし→予算UNKNOWN/NOT_READY|

PTRACE_O_EXITKILLや既存認可subreaper/adoptionは候補であって今回有効化しない。EXITKILLによるkillが仮に許可されても実終了/reap/残存/保存完了は別。復帰・cleanup権限不明の対象を生成しない。任意PID・全process・未所有taskの操作は禁止。

## 参照仕様と結論

[ptrace](https://man7.org/linux/man-pages/man2/ptrace.2.html)、[wait](https://man7.org/linux/man-pages/man2/waitpid.2.html)、[pidfd_open](https://man7.org/linux/man-pages/man2/pidfd_open.2.html)はイベント/終了/寿命APIの根拠で、当hostの利用認可や完全性証拠ではない。[map_files](https://man7.org/linux/man-pages/man5/proc_pid_map_files.5.html)の権限条件と、[kcmp](https://man7.org/linux/man-pages/man2/kcmp.2.html)/[SCM_RIGHTS](https://man7.org/linux/man-pages/man7/unix.7.html)の意味は別審査する。[fs-verity](https://docs.kernel.org/filesystems/fsverity.html)は内容の不変性候補であり実行世代/実mapping帰属やD実使用を証明しない。

資料上のAPI存在/必要条件整理は可能。正規の通常権限で上記一式が同時成立する実環境、終了/cleanupの有限性、B_use保証は未確認。環境BLOCKED、実装前NOT_READY。実測や追加権限で穴を埋めた結果として報告しない。
