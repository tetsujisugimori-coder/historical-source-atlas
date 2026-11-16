版: 1.0 / 作成日: 2026-11-15 JST / 審査基準: 640ce033963837ad0b96ba70830ad7bb4c0f8c2c (tree ee292d4f42fef239ff8ab6dca6d51d08299b51e3)。内容SHA-256は manifest.sha256 を参照。これは設計審査であり実装・実測承認ではない。

# 原証拠契約・非上書き保存・提出

## 状態と帰属

各artifactは version、case/phase、producer、source HEAD/tree/path/blobと実file SHA、UTC/単調時刻（計測未実施ならnull）、byte数、SHA、状態、失敗理由、親原票IDを持つ。`PLANNED`（予定名だけ）、`NOT_GENERATED`（未実行等）、`GENERATED_PARTIAL`、`GENERATED_COMPLETE`、`UNAVAILABLE` を区別する。取得・保存・独立検証の各状態は別フィールドとし、予定pathの存在だけで生成済みとしない。

今あるもの: 文書、取得したAPI JSON/stdout/stderr/exit、local640 reference sourceの読取りコピー、環境inventory、文書差分/manifest。今回B backend/対象/原capture/実測resultはNOT_GENERATED、参照path/hash/sizeはnull、reason=DESIGN_ONLY_NOT_AUTHORIZED。過去原票と今回生成物はproducer/epochで分ける。過去80,097,385bytesのABA ZIPおよび87,248,504bytesのCLI ZIPは改変せず、新規ZIPへ原物を混入しない。今回それらのZIP全体を独立再照合したとは報告しない。

source attributionはGit blobのraw bytesとworkspace readの差を改行含め明示し、Git HEADだけから実行source一致を推測しない。今回はコード実行ではなく読取りsource比較。report review、code read、実行、原票読戻し、ZIP監査をそれぞれ別scopeにする。

## 保存手順と受入条件

1. 新規専用directoryとexclusive create。既存同名なら拒否し、旧原票は改名/移動/削除しない。実行eventは追記/段階別immutable原票、summaryは原票参照。部分書込はPARTIAL、原stdout/stderrを失わない。書込失敗はBLOCKED、正常票へ昇格しない。
2. 全fileのbyte数/SHA manifestを固定。manifest自身は自己hashに含めず、外側ZIP SHAで包む。文書 `manifest.sha256` も同じく自身を除く全文書のexact setを表す。最終commitのdoc Git blob/source一致を別票へ保存。
3. ZIPは新規pathに一度作成。内部name重複/欠落/余剰を拒否。CRCとmanifest各file bytes/SHAを別プロセスで確認する。
4. 保存済みZIPを別保存先へ実物copyして新規取得し、size、全byte、SHA、各entry CRC、manifest完全集合、source Git帰属を照合。独立担当は主担当の結論を採用せずcopy実物から再計算する。不可読/転送失敗はBLOCKED。
5. workspace一時保全成功と指定Archive恒久保全成功は別欄。Archiveへは今回専用新directoryのみ。PermissionError13なら緩和/別経路回避なし、恒久保全BLOCKED。workspaceを恒久保存と表示しない。代替の恒久先は保存権限・retention・アクセス/独立取得・承認主体の明示承認後のみ。

今回実施結果・ZIP SHA/CRC/件数・読戻しscopeは提出受領/保全票に記録する。文書に未生成ZIPの架空SHAを埋めない。GitHub受領記録は原ZIP生成後に生じるため別のimmutable追補とし、必要なら別ZIP+manifestで包む。原ZIPを後から更新しない。

## 投稿制御と残る境界

文書専用branchはmain3e56を親にし、提出差分をdocs/pr35-binding-preflightだけに限定。全commit `[skip ci]`、workflow二件原文を保存してトリガ確認、CI抑止が不確実ならpushしない。独立review後のみ通常push、新Draft PR。main/PR35/隔離code branchにpushしない。PR35へ文書PRリンクと未解決事項をコメントする。投稿後HEAD/tree/Draft/merge状態・run/jobを読取り照合し、CI未実施をPASSとしない。

独立照合や恒久保全が未完了なら全体PARTIAL/BLOCKEDのまま。設計整理完了は実装実測許可でもB実証でもない。次工程は環境・権限・実入力・backend別審査・保存条件が成立してから別途判断する。

## 2026-11-16 具体化工程の追補

[原票lane・保管先・cleanup責任](evidence-cleanup-contract.md)を追加。Archiveの過去拒否を保持、Hachibei-Evidence-Vaultは承認証拠の指定先であって成果物Archiveの自動代替ではない。今回workspace文書保存は恒久保全と別。独立oracle実測rawは未生成、旧ZIPの監査は新版へ転用しない。今回文書変更は既存PR36に集約し、新PR作成や正本変更は行わない（上記初回提出手順は履歴）。
