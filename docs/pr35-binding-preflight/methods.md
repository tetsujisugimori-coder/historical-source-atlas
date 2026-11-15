版: 1.0 / 作成日: 2026-11-15 JST / 審査基準: 640ce033963837ad0b96ba70830ad7bb4c0f8c2c (tree ee292d4f42fef239ff8ab6dca6d51d08299b51e3)。内容SHA-256は manifest.sha256 を参照。これは設計審査であり実装・実測承認ではない。

# 有限候補の比較と段階別条件

## 一次仕様と設計仮定

以下リンクは2026-11-15に参照した一次仕様。Linux man-pagesはkernel/userspace interfaceの記述であり、今回Windowsや未確保Linuxでの実測ではない。

- [ptrace](https://man7.org/linux/man-pages/man2/ptrace.2.html): 制御はthreadごと。exec/clone/exitイベントと権限検査を要する。全thread停止とイベント欠落0は将来backend側の証明義務。
- [GDB all-stop](https://sourceware.org/gdb/current/onlinedocs/gdb.html/All_002dStop-Mode.html): 停止中の全threadという意味を提供する。resume/stepは状態を変える。全inferiorのcoverage、通知完了、コマンド排他を一件のMIから推定しない。
- [clone/CLONE_PIDFD](https://man7.org/linux/man-pages/man2/clone.2.html): 生成時task参照の候補。利用kernel/backend/flagsの対応と所有責任は未検証。
- [pidfd_open](https://man7.org/linux/man-pages/man2/pidfd_open.2.html): Linux5.3以降。task参照でありexec lockでない。PIDFD_THREADは6.9以降。Node版だけでsyscall/backend利用可能とはしない。
- [proc exe](https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html): linkのopenは実行物へ到達。権限・main thread終了等で取得不能なら拒否。
- [map_files](https://man7.org/linux/man-pages/man5/proc_pid_map_files.5.html): kernel mapping由来の参照。Linux3.3以降、旧kernelのCONFIG条件あり。ptrace READ_FSCREDSに加えreadlinkには初期user namespaceのcapability条件がある。Linux5.9以降CAP_SYS_ADMINまたはCAP_CHECKPOINT_RESTORE、それ以前CAP_SYS_ADMIN。通常権限で自明に使えるとはしない。付与・緩和は禁止。
- [file seals](https://man7.org/linux/man-pages/man2/F_GET_SEALS.2const.html): kernelによる操作制約が存在するが、一般のELF/.soに自動適用されない。既存sealを読めることと新しいsealed実験物作成承認を区別する。F_SEAL_FUTURE_WRITEだけを既存writer排除としない。
- [ELF header](https://gabi.xinuos.com/elf/02-eheader.html)、[program header/notes](https://gabi.xinuos.com/elf/07-pheader.html)、[GNU build ID](https://sourceware.org/binutils/docs/ld/Options.html): ELF形式とGNU noteの根拠。build IDは改変後の全byte checksumを保証しない。640の限定ELF parserの既存検証範囲を拡張認定しない。

## 部品と組合せ

|有限候補|保証できる性質/競合|権限・OS/GDB・復帰責任|審査結論|
|---|---|---|---|
|P: pidfd単独|task寿命の参照。exec/remap/bytesは保証しない|通常許可範囲内のLinux syscall。Node binding未確認|B方式として不採用|
|F: exe/実mapping FD + private copy単独|object pinとA。exec後の旧FD、外部writer、mapping切替を防がない|procアクセス、mapping権限。FDのcloseは取得主体|B方式として不採用|
|S: 一件停止/PID/startTicks/stat一致/caller証明|いずれも連続全停止・byte version・実体帰属を証明しない|待機や確認回数追加でも解決しない|不採用|
|C1: 所有する対象を誕生時からtrace + 全thread停止lease + kernel task/object参照 + 不変backing|所有→制御取得の数値PID再利用窓を避ける設計候補。停止中のexec/remap排除とB0–5を組合せる。外部writer/未知mappingは別ゲート|既存の正規Linux/GDB・trace権限・必要objectアクセスが必要。全thread/event対応をversion別検証。未導入backend、normal非rootで条件成立する環境が未確保|条件付き採用候補。現時点B UNKNOWN、実行不可。旧sibling実験との環境差あり、再現同等とはしない|
|C2: 既存siblingへpidfd前後確認後に数値PID attach + 同停止検証|pidfdがあっても別APIのnumeric attachまでの所有対応に穴がある。事後一致は誤attachを取り消せない|未所有attach禁止。正規attach許可も未確認|所有から制御への原子的/非再利用bridgeの証明がないためHOLD。現在の代替採用不可|

C1も一般のsystem libraryが不変と証明されるとは限らず、map_files権限が認められなければ不成立。一般WebKit環境でC1の全前提を満たせるかはUNKNOWN。別方式を無断導入して穴を埋めない。root/capability付与やsandbox無効化を前提にしない。

## 循環の点検

640はB未証明ならGDB開始前に拒否する。一方B候補はGDB全停止を要する。そのままでは循環する。設計上は次の異なるauthorityへ分けるが、**現ゲートの変更や実測開始を承認しない**。

1. P0: 環境/権限/保存/対象入力を審査し、別工程として実装・制御取得の許可を得る。
2. P1: authorized supervisorが所有対象を誕生時から一意に登録。task参照は将来対応backendでclone(CLONE_PIDFD)等の生成時取得、又は自分の子についてpidfd_open完了前にreapしない（SIGCHLDを無視せずSA_NOCLDWAITなし、別threadもwait/reapしない）というkernel仕様条件を満たす方式を固定する。後者の条件不明なら拒否し、数値PIDの事後取得へ置換しない。ここではA/Bの正常認定をしない。
3. P2: 所有根拠だけに基づく制御取得。対象が未所有なら取得禁止。診断stack/signalはまだ禁止。
4. P3: controllerが全停止を保証しkernel参照・不変bytes/mappingのB0–5を検証。normal full identityはここで初めて検討可能。
5. P4: live lease内で別承認された診断のみ。失効後は拒否。

これは論理上の工程分離でありP2実装・制御取得の承認ではない。現640はP0でBLOCKEDのまま。新backend/ゲート契約変更は別審査・独立レビュー・承認が必要。

取得主体は自分が所有するFD/controller/対象だけを管理し、解放ack・残存状態を原票に残す。予定resume前にleaseを破棄する。切断/停止失敗時に安全な自動resumeを仮定しない。復帰/終了操作は対象所有と別途固定した許可済みcleanup契約が必要。不明状態ではBLOCKEDと人への引継ぎ、任意PID kill・全体kill禁止。今回は解放/復帰操作も実施しない。
