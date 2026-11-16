版: 1.0 / 作成日: 2026-11-15 JST / 審査基準: 640ce033963837ad0b96ba70830ad7bb4c0f8c2c (tree ee292d4f42fef239ff8ab6dca6d51d08299b51e3)。内容SHA-256は manifest.sha256 を参照。これは設計審査であり実装・実測承認ではない。

# 環境適格性台帳

2026-11-15 14:46 UTCの読取り確認。版確認用CLI・Git/GitHub・文書/ZIP処理は実行したが、検証対象taskは生成していない。インストール済み、呼出可能、利用許可、B実測確認は別欄とする。

|候補|インストール/現状観測|利用可能/認可根拠|B環境判定と不足|
|---|---|---|---|
|現在Windows workspace|Windows NT10.0.26300.0 AMD64、Node24.20.0、PowerShell5.1.26100.9818、Python3.14.7。GDBコマンドなし。Linux kernel/browser/GDB版 UNKNOWN|本依頼とworkspaceの書込範囲により文書・既存証拠読取りは認可済み。Linux ptrace/proc/mapping機能なし|文書環境適格、B実測環境BLOCKED。Windows通常実行をLinux診断と同一視しない|
|WSL|wsl.exeがパス上に存在。今回distribution起動/生成なし。kernel/distro/実行可否 UNKNOWN|exeの存在はLinux利用権限やdistributionの存在証明でない。既存承認接続先なし|UNKNOWN/BLOCKED。インストール/起動許可へ読み替えない|
|SSH/remote Linux|ssh.exe存在、既存ユーザーssh configなし。認可済みendpoint提示/取得なし|一般sshが使えるだけでは接続先利用許可にならない。接続試行なし|UNKNOWN/BLOCKED。OS/kernel/arch/UID/GDB/Node/browser/権限/容量/保存先すべて不足|
|repo self-hosted runner|GitHub API total_count=0|認可済み常設runnerは今回取得範囲では見つからない|BLOCKED。新設/dispatch禁止|
|過去hosted Linux run43654812679 attempt1|既存記録の非browser sibling attach EPERM。現在環境・権限は未取得|過去runの証拠であり現在利用できる承認済みendpointでない|BLOCKED。旧native4全NOT_RUN、stack/renderer終了情報未取得を維持。再runなし|

調査範囲は現在workspace/コマンド発見、GitHub refs/workflows/runner一覧、既存報告/原source。未提示のhost/cloudアカウントへ探索・接続せず、認可済みLinuxなしを全世界の不存在とは言わない。

## 保存・容量・権限

今回の専用worktree: `C:\Users\tetsu\Dev-Workspace\historical-source-atras\pr35-binding-docs-20261115`。
専用一時保全: sibling `pr35-binding-design-evidence-20261115T1438Z`。共有/tmp不使用。

Python標準APIでCドライブ total999043362816 / used610443014144 / free388600348672 bytesを取得。PowerShell Get-PSDriveはFree=nullを返したためその値を容量確認に使わない。Windows inodeはNOT_APPLICABLE。workspaceへの新規文書保存は実際に成功。Archive `C:\Users\tetsu\Dev-Artifact-Archive` は存在を確認したが、存在≠書込可≠恒久保全完了。前回PermissionError13は過去証拠、今回専用Archive directory作成も14:50:50 UTCにPermissionError errno13 / WinError5で拒否された（archive-probe.json）。今回の恒久保全もBLOCKED。権限変更なし。workspaceは許可済み一時保存先であり恒久代替先の承認はない。

## 次工程環境の必須欄（現状UNKNOWN）

認可主体/対象host/利用期間/通常非root UIDとeUID、Linux kernel/arch/GDB/Node/backend版とhash、browser/実行物/library hash/build ID（browserは次々工程まで不要）、対象生成所有契約・誕生時追跡、ptrace/LSM/seccomp/procアクセスの既存許可、pidfd/thread-event/mapping参照機能、byte不変性の根拠、全thread停止の意味とexclusive controller、保存容量/上限/恒久保存権限/独立読戻し先。read-only設定確認だけで実測適格とはしない。backend未実装につきcontrol/B実測欄はNOT_TESTED。必要capabilityが現権限でなければ緩和せず当該方式不成立とする。

## 2026-11-16 具体化工程の追補

上記2026-11-15の値は履歴であり今回新しいLinux実測値ではない。[backend-environment-gates](backend-environment-gates.md)へinstalled/callable/authorized/measuredを分ける適格性schemaを具体化した。新hostの探索/起動/導入/接続なし、K/O/backendと通常権限の実取得はUNKNOWN/BLOCKED。Vaultの役割指定と実書込/恒久保全は[evidence-cleanup-contract](evidence-cleanup-contract.md)で分ける。
