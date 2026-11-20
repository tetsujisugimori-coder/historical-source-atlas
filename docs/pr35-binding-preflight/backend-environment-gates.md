版1.2 / 2026-11-16 JST / 文書基準HEAD 134c5133d0d04892ec0f0ff0e9d2ee50fedb2f98、tree aea16bc285391a21c68934f02c143cb18de30b86。現640ゲート不変更。内容SHAはmanifest.sha256。設計案と必要条件であり、実装・生成・実測の許可/証拠ではない。

# Linux/backendの適格性ゲート

## 現在の範囲

この文書はhost探索・新環境構築・稼働確認の依頼ではない。[environment](environment.md)のWindows読取り/過去Linux記録を履歴として維持。今回Linux hostの起動/接続/対象生成/実proc照会なし。認可済みLinux、K/O/backend、以下の機能の実取得はUNKNOWN、実環境成立性BLOCKED。C2 numeric PID attachは所有bridge競合窓が解決するまでHOLD。

各gateの台帳field: requirement / candidate構成 / 観測主体 / 取得source・raw参照 / version / installed / callable / authorized / measured / 判定 / UNKNOWN理由 / 解除に必要な証拠。存在・呼出・利用許可・実測済みを別boolean又はUNKNOWNで保存。全fieldをインストール済みという一語で代替しない。

|gate|通常権限で必要な条件・証拠|現在/不成立時|
|---|---|---|
|E0 host/保存/期間|利用認可主体・host ID・利用期間・task生成/trace/読取り/cleanup範囲、Archive/Vaultの保存役割別許可|認可host未提示。UNKNOWN/BLOCKED|
|E1 OS/kernel/arch|Linux kernel正確version/build/config、architecture、proc namespace/boot、対象ELF/backend互換|Windowsを同等としない。版未取得UNKNOWN|
|E2 UID/eUID/既存制約|両UIDの非root有効整数、ptrace/LSM/Yama/seccomp/capability/proc mount/hidepidを読取り記録。通常実行で必要operationが許可済み|未取得/拒否ならBLOCKED。sudo/root化、caps追加、ptrace_scope緩和、sandbox無効化は禁止|
|E3 誕生時所有|Sによる生成とkernel task handleの対応。CLONE_PIDFD等、又は自分の子でpidfd取得前reapを防ぐkernel条件。所有registryの改ざん防止|Nodeだけでsyscall bridgeが存在すると仮定しない。backend source/ABI未作成UNKNOWN|
|E4 sole tracer/bridge|O-KではKが出生時から唯一のtrace owner、数値PID再取得窓なし。TRACEEXEC/CLONE/EXITの有効化、thread/exec例外を扱う原票|実装未作成。GDB第二attachは不可。O-Gは別adapter審査までHOLD|
|E5 stop/event完全性|全thread wait stop、閉じたbirth/exit処理、unknownevent失効、O/D snapshot中排他、Kへのcommand channel1つ|一件停止/反復stat/caller証明では不可。feature動作の実証は未実施|
|E6 exec/membership|各kernel exec commitで新世代、nonleader execの旧/新TID処理、clone membership/終了の全管理。中間Bをpinする停止点|2 execを取り逃がす構成は03不能。取得不能はUNKNOWN/NOT_READY|
|E7 実mapping参照|O/Dがmapsに加えmap_files由来実objectを保持しF/Mを照合できる既存権限、必須coverage閉包|map_filesのreadlink等にはkernel版ごとの初期namespace capability条件があり、通常権限で自明に使えない。必要権限がない場合この方式はNOT_ELIGIBLE/BLOCKED。付与や未検証代替で救済しない|
|E7b FD交付/比較|K一回open→SCM_RIGHTS複製→Oで実返却FDのKCMP_FILE一致、trusted read receiptとD copyの由来。syscall/seccomp/通常権限/端点所有/TCB分離の根拠|kcmp/transfer実取得とread境界の監査はUNKNOWN。別openのinode一致やD tokenへfallback禁止、取得不能はNOT_READY/BLOCKED|
|E8 不変backing|対象が実行/mapする同一objectの全writer排除。既存fs-verity fileなら通常readでverity flag/digestとFD bytesを区別して保存、EIO/欠測は拒否|新規enable/新mount禁止。普通のread-only FDやhash反復は不可。08/09のunlink/renameを同時に許すdirectory条件も必要|
|E9 version/TCB|K/O/DとNode/ABI/GDB（使用構成のみ）の正確version・source・実file SHA。TCB独立審査とDの論理/書込分離|O-KにGDB version N/Aを置いてGDB診断が成立したとしない。O-G具体化未完了。既存GDBインストールだけで全停止適格にしない|
|E10 lifetime/lease|Kによる独立単調seq、D世代とO世代の写像、resume前失効、現在M/Tに結び付く新epoch|K/Tの停止管理とDのlease検査を同じ自己申告に統合しない|
|E11 completion|通常終了/制御喪失/保存失敗時の所有資源ごとの停止・終了・close・残存・保存statusと責任、各slot内の期限|tracer異常終了時のkernel auto-detach/resumeを禁止できる承認済みpolicyも必要（次段落）。終了/復帰手段又は権限が不明なら開始不可。常時拒否やcleanupだけ成功でcase PASSにしない|

## 仕様根拠と未検証の境界

[ptrace](https://man7.org/linux/man-pages/man2/ptrace.2.html)、[wait](https://man7.org/linux/man-pages/man2/waitpid.2.html)、[pidfd_open](https://man7.org/linux/man-pages/man2/pidfd_open.2.html)、[clone](https://man7.org/linux/man-pages/man2/clone.2.html)はkernel APIとthread/exec/lifetimeの根拠。syscallの存在はK/Oの完全性やアプリ所有認可の証拠でない。

[proc task](https://man7.org/linux/man-pages/man5/proc_pid_task.5.html)、[maps](https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html)、[map_files](https://man7.org/linux/man-pages/man5/proc_pid_map_files.5.html)を必要なraw元として区別。通常のmaps pathname再openではなく実参照を要求する。readlink/openの正確な権限判定は実kernel/LSMで独立確認が必要、現時点未確認。

[fs-verity公式](https://docs.kernel.org/filesystems/fsverity.html)は内容をreadonlyにしつつimmutable bitとは異なるnamespace操作の性質と、verity digest/full-file digestの違いを説明する。08/09の設計候補として整合するが、当hostのsupport/既存有効file/実unlink許可/全dependency適合は未取得。F_SEAL_FUTURE_WRITEだけや事後copyのsealは対象への対応を保証しない。[seals](https://man7.org/linux/man-pages/man2/F_GET_SEALS.2const.html)は別backing条件、勝手にfallbackしない。

[GDB all-stop](https://sourceware.org/gdb/current/onlinedocs/gdb.html/All_002dStop-Mode.html)、[catchpoints](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Set-Catchpoints.html)はO-G候補の一般機能の根拠に留まる。必要catch/event/exportが全て存在する正確なversion組合せと停止barrierは未検証。文書に機能名を挙げたことを構成承認にしない。

各sourceは2026-11-16に読取り参照。上記は設計要求/仕様からの推論でありLinux/GDB実測結果ではない。全gateの正常成立+独立審査+別の実装/実測許可が必要で、一つでもUNKNOWNならfull B/診断開始BLOCKED。

## K/D異常終了の実行前ゲート（独立指摘D2/P3への補訂）

K死亡時にkernelがtargetをdetach/resumeし得る点は、単なる「自動resume禁止」という運用文では防げない。正確なkernel/ptrace modeの死亡時動作、Sが所有する全対象/threadの終了/復帰policy、失効・残存・reap、期限内cleanupを先に固定する。候補PTRACE_O_EXITKILLはtracer死亡時にtraceeをSIGKILLするkernel機能であり、全対象の出生所有・例外・通常終了時の解除/detach順序と終了許可を別審査した場合だけ候補となる。今回設定/実行/承認はしない。未所有taskへの作用可能性、policy未承認、実動作不明、期限内の終了確認不能なら開始不可/NOT_READY。O-GもGDB死亡時の同じ問題を未解決のまま代替採用できない。

R/V間にD/Kが終了・再起動した事実をconsumer returnへ折り畳まない。case manifestにD/K instance source/lifetime/開始stateを固定し、state lineageの連続性を原票で要求。TCB/GDBを含むこれらのfail-stop機能は未検証、backend実装開始の承認ではない。

E11にはSの法的なkernel wait親/adoption経路（例:既に認可済みのsubreaper構成）も必要。K死亡後の所有target終了statusの回収主体/順序を固定し、pidfdだけでwait権限を仮定しない。未確認はNOT_READY/終了UNKNOWN。今回subreaper等を設定しない。
