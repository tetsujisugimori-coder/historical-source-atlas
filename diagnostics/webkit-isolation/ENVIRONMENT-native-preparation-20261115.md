# PR35 native接続環境確認・診断準備（ブラウザ実行なし）

作成: 2026-11-15 JST。総合PARTIAL、native診断BLOCKED、製品受入FAIL、根本原因UNKNOWN、Draft・マージNO・公開NOを維持する。

## 対象・帰属

- PR35 / origin: https://github.com/tetsujisugimori-coder/historical-source-atlas 、branch `data/eikyouki-batch13`。
- 今回の開始local/remote HEAD: `c29cfcc2c130c65cb4cc93eac859aac2dc025139`、tree `193227045ec328d556ef5d45b05e56952eb8625e`。開始時変更なし。指定cwdが空だったため、その配下の `pr35-native-preparation` に新規checkout。既存checkoutの破棄・force更新なし。
- 既存実験HEAD: `c54a6c24d81cbd09345e15f82dbbeb39307fe621`、tree `ba5ad55df3447cd9f3fa4e78a11d1f87094b642d`。c29cfccとの差分は既存レビュー文書1件のみ。既存実験の帰属はc54a6c2から変更しない。
- AGENTS.md、最新PR本文、review5910350484、最終追補6886920261、PLAN-native.mdを読了。正式PR/push各Chromium8PASS・WebKit8FAIL、原4ZIP保全・独立照合完了は既存確定事項。再取得・再監査・再試行していない。
- 今回は環境調査と文書準備だけ。非ブラウザnative preflight **0件**、実ブラウザ **0件**。旧native4枠全NOT_RUNを維持。stack・renderer終了signal/codeは未取得。小子cleanup SIGKILL / GDB exit0はrenderer情報ではない。

## 自動実行の事前確認

`.github/workflows/acceptance.yml` はpush/PRで正式ブラウザ、PRでlegacy診断を実行する。`webkit-isolation.yml` は診断配下のPR変更で旧native4枠runnerを実行し得る。したがって通常の無印commitのpushは禁止する。
既存レビュー文書追加と同様、今回の文書だけのcommitメッセージに **`[skip ci]`** を付けて通常pushする。workflow/guardの変更、dispatch/rerunはしない。push前にメッセージ・差分・remote HEADを再確認し、push後は新HEADに対するrun/jobの有無を読み取り確認する。競合やskip不成立なら成功とせず停止・報告する。最終HEAD/tree・投稿先・保全の最終結果はPR追補に記録する（自己参照のため本文に最終commit SHAを埋め込まない）。

## 調査範囲と候補

今回の原票はcheckout外の案件専用 `../pr35-preparation-evidence-20261115/`。API応答/stdout/stderrは新規ファイルへ保存し、後作成説明はinventory.jsonと本書に区別する。

|候補/範囲|今回の観測|判断・不足|
|---|---|---|
|現在のshell|Windows 11 / NT10.0.26300、ローカルWindows workspace。Python3.14.7、Node/git/gh/sshあり、GDBなし。readelfはMSYSのWindows実行物。既存cacheにwebkit-2215/2248/2336があり、2215内はWindows DLL|Linux `/proc`・sibling ptraceを検証できない。同revision名でもWindows実行をLinuxの代替にしない。実行しない|
|WSL|`wsl --list --quiet` exit1、WSL未導入の案内。初回tool出力と保存原票の双方を区別|利用可能なdistributionを確認できない。installしない|
|ローカル既存container/VM CLI|docker/podman/multipassなし。SSH configなし、利用を指示された接続先なし|ホスト全体のVM不在までは証明しない。任意ホスト走査・推測SSH接続・新規構築なし|
|接続済みCloud Linux|今回公開されたtool一覧にcloud_environment status/Linux shellなし|接続先ID・実行権限・容量・GDB・プロセス関係を確認不能。新環境を作成しない|
|repository self-hosted Actions runner|API `actions/runners`: total_count0|このrepoに登録済み候補なし。組織全体や他repoまで不存在とはしない|
|旧GitHub hosted runner|run43654812679/attempt1 job metadata: ubuntu-24.04 / GitHub Actions 1000020178|過去の一時環境。既存sibling attach拒否。現在接続可能な候補ではない。再dispatch・再実行なし|

GitHub connectorは起動時ハンドシェイクエラー。gh CLIの読取は成功した。初回cloneはSchannel SEC_E_NO_CREDENTIALS、次はOpenSSL issuer検証エラー。既存Windows Rootストアの公開証明書を案件領域へexportし、command単位のCA指定でclone成功。TLS検証は有効のまま、global config変更なし。これはGit転送の解消であり、Linux ptrace許可の解消ではない。CIM情報取得はアクセス拒否、OS/free spaceは別APIで確認。証拠保存前空き約406.5GB。

## 実行物の確認状態

新Linux候補なしのため、OS/kernel/image/GDB version、UID/capability、ptrace許可、対象PID/PPID/startTicks/実行物、Playwright配置・版・WebKit実物hash/build IDは全て **今回NOT_OBTAINED**。既存原票の「4実行物一致」と混同しない。
次の候補ではPlaywright1.56.1 / WebKit2215を要求し、native-stack.cjs EXPECTED_WEBKITの以下4SHAを実物で照合する。build IDは `readelf -n` の実出力を取得し既存原票と照合、matching debug symbolsは別途確認する。

|実行物|既存固定SHA-256（今回の新測定ではない）|
|---|---|
|launcher|a85baad3d8c07173ac387a59b41500c382b21ed692afe0964d29aac247ccc63b|
|MiniBrowser|e0d1da0ec4ccb9dd0e6ed9242ee00e16d9341c086f7bdf85499d25d135bd7dc9|
|WPEWebProcess|b46f88603e43eca28083389188944f7f47fd26311c8697a14f910e4f8bfa0d66|
|libWPEWebKit|daa10258a2161710c7c1d6a3e3f7abe0a100a6f269c00f5843dcd0f7df46ec29|

## 次の非ブラウザpreflightの固定仕様（未実施・開始ゲート未充足）

候補が特定された時点で環境ID/場所/実行者・一般ユーザー権限・出力絶対パスを記入し、計画/コードを独立確認・commitしてから開始する。候補の差替えも別記録とする。**この文書だけでは未特定環境での実行を開始しない。**

- 対象: core limit0のLinux一般ユーザーNode親が、READYを出す小Node子とGDBを別々にspawnする。GDBは子のsibling、実rendererと同じ共通祖先下の非親debugger関係。renderer側に中間launcherがある差も記録する。GDBを子の親にする方式、PR_SET_PTRACER付与、sudo/root、ptrace_scope/seccomp/capability緩和は使用しない。
- 回数: 選定した候補1環境につき1回、予備・成功まで反復・replacementなし。今回の候補0につき実施0。
- 時間: 全体60秒（起動・収集・終了確認を含む）、小子READY5秒、GDB45秒、終了通知待ち3秒、TERM後2秒で自身の小子/GDBだけKILL、残存確認最大2秒。時刻/単調時間を併記。上限超過やcleanup不明はBLOCKED。
- 出力: GDB stdout+stderr合計2MiB、小子stdout/stderr各64KiB、イベント/結果各1MiB。上限到達で打切り、truncatedと捨てたbyte数を記録しBLOCKED。環境読取コマンド各5秒/128KiB。保存不能もBLOCKED。
- 保存先: 選定Linuxの案件専用絶対root配下、例 `<approved-case-root>/pr35-native-preflight-<env-id>-<UTC>/` の非既存ディレクトリ。TMPDIR/TMP/TEMPもこの配下。事前2GiB・1024inodeを確認。共有/tmp、既存outDir再利用、上書き・削除禁止。Windows移管先は `C:/Users/tetsu/Dev-Artifact-Archive/historical-source-atlas/PR35/native-preparation-<UTC>/` の新規先。
- 接続前: `/etc/os-release`、kernel、image、GDB/Node/readelf version・SHA/build ID、読み取れるptrace_scope/Uid/TracerPid/NoNewPrivs/Seccomp/CapEff、親/GDB/対象のPID・PPID・startTicks・exe実物を記録。生環境変数・秘密・任意system logを採取しない。PID/PPID/startTicks/実行物はattach直前・停止後に一致確認、不一致でattachしない/中断する。
- 各機構を別判定: token対応attach成功応答 **かつ** stopped通知 → 同一性再確認 → continue応答 **かつ** running通知 → 親が同一対象に意図したSIGABRT → SIGABRT stopped通知 → `thread apply all bt 24` raw stack → `handle SIGABRT stop print pass`でcontinue応答/running → GDB exited-signalled(SIGABRT) **かつ** 親の小子実exit(signal SIGABRT)。group exit/PID消失/GDB exit0だけでは実終了signalを認定しない。
- 拒否・PID不一致・欠測・timeout・出力上限・途中終了・残存・保存失敗のいずれでもBLOCKED。以後のbrowser起動は0。preflight PASSは小子の機構確認だけで、実renderer診断・再現性・根因の成功ではない。

## コード準備の制約と反例

今回のrepository変更は本調査文書と独立レビュー記録だけ。製品・採録データ・正式16条件/期待値/timeout・guard・Pages・native実行コードは変更しない。環境がないため実機に即したコード修正は見送る。
既存native-gdb.cjsのstartCaptureはGDB45秒/2MiB、outDir非既存、identity、MI通知を扱う。ただし上の次回仕様（全体60秒、小子出力上限、環境採取、原票の非上書き保存等）を全て満たす完成runnerとは認定しない。
接続拒否では `await capture.ready` がthrowし、preflight.jsonのresult.captureが未設定のままになり得る。別のgdb/native-result.jsonは保存されるが、概要への収録と原票参照を次回修正で確認する必要がある。既存結果のBLOCKED判断を覆すものではない。

|同一反例の修正前後比較|今回|
|---|---|
|成功 / 接続拒否 / PID不一致 / 通知欠落 / timeout / 出力上限 / 途中終了|全7分類NOT_RUN（コード変更なし・Linux候補なし）|

既存61非ブラウザ検査の過去PASSを今回の新しい比較結果にしない。次回runnerを修正するなら同じ7入力をbefore/afterの別ディレクトリへ保存し、fake MIの成功を実接続成功に昇格させない。WindowsでLinux依存テストを走らせて意味の異なる失敗を作らない。

## 実ブラウザの別計画と再開条件

正規の接続許可を確認できなかったので、実行可能な次回ブラウザ計画は **未作成/開始不可**。旧PLAN-native.mdは履歴として保持し、旧4枠の実行命令として再利用しない。
再開には、既存利用を認められたLinux接続先/一般ユーザー、案件専用保存・転送先、同版実物4SHA/build ID、非ブラウザ1回を許す実行範囲、上の不足を修正・反例確認したrunner、事前独立レビューが必要。権限緩和でなく、その環境の正規のsibling attach許可を確認する。
そのpreflightが成功した後にのみ、環境差（OS/image/kernel/GDB/許可/launcher祖先関係）・固定v6-B入力101900bytes/SHA d2989329db626bf06f26f3db5bedd951d9cd2edbfeb1da1867c481311508c1d1・実行物・介入時点・新しい有限試行順/数・期限・分類・停止条件を別文書で固定する。API30秒や製品保護を緩和しない。接続成功から同じ再現性を推論しない。本依頼ではブラウザを実行しない。

## 保全・独立確認

原票と後作成説明を分け、manifest、ZIP CRC、保存前後SHA/byte一致を担当自身の再検算として記録する。保存後別ファイルとして再取得して照合する。別担当の計画/コードレビューと原票監査の範囲を別記録に明示し、担当自身の再検算を独立監査とは呼ばない。
最終Windows保全結果、独立レビュー結果、最終HEAD/treeはPR追補に記載。保存・転送拒否ならBLOCKED/PENDINGと明記し、workspaceコピーでWindows恒久保全完了としない。既存Library原4ZIPの完了状態は変更しない。

今回、空き容量を確認して指定Archive配下の新規案件先 `historical-source-atlas/PR35/native-preparation-20261115T111100Z` を作成しようとしたが、PermissionError13（アクセス拒否）。`archive-destination-probe.json` に実結果を保存した。**指定Archiveへの保存・保存後再取得はBLOCKED/未実施**。権限変更や別プロセスによる回避はしない。workspace内ZIP/別readbackの自己照合が成功しても、この阻害は解消しない。

2026-11-15 20:11 JST
