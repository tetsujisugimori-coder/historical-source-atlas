版1 / 2026-11-17 JST / 審査基準 b2adb697efc2ea25c9430533c3f02383bece080a、tree ae77dcfeeddc80d2e7bf6149a32063e372392f0c、親1273d288fc30bce9e176f1a7e917d354ae650e13。今回の提出HEAD/treeと受領後原票はPR #36の追補に記録する。各実fileの内容SHAはmanifest.sha256。

# 審査証拠の再検証と保存先承認照合

**総合PARTIAL。workspaceでの原物識別・実保存・独立再取得は限定PASS、恒久保全BLOCKED。** 最新GitHubのPR #36は開始時b2adb697、Draft/未merge、base main3e56d13d77048d056e79c6971e6e7d24ad92b4ff。main tree bf87c376f7cf86e45cf309feebe1eb15e5684b0f。PR #35は97ce39e8cb9ea38967354aea11cac2282097d7cf/tree b7370577c706aa70f9eebd80e96ef8ee4f73d93e、Draft/未merge。未push2596/640、隔離8eaは変更しない。

この文書は保全工程の結果であり、方式を新たに成立させない。Stage B-Q設計審査限定完了/総合PARTIAL、backend実装開始NO、実測開始NO、完成方式の採用YES=0を維持する。LLVM DataFlowSanitizer 20.1.8標準構成が完成B_use判定器として不適格、追加境界/検査器構成UNKNOWNという依頼時の前提も維持する。ただし当該DFSan審査原票・閉鎖原票・原ZIPの原物は今回未取得で、独立に監査できたとの主張はしない。

## 正本・対象集合と版の対応

新規案件workspace `pr36-evidence-revalidation-20261117T2011JST/` に排他的に保存した。旧原票・ZIPは移動/更新/削除しない。

|集合|実際に取得した対象/作成主体/経路|今回の限界|
|---|---|---|
|GitHub正本|PR #36基準の全22file（21文書+manifest）、GitHub commit/tree/blob rawを独立担当が取得。Git SHA1、実file全byte、SHA-256/CRC32を再計算|文書/コードの静的原物一致でありB実証でない。各blob/size/SHA/CRCはpublic inventoryへ記載|
|Stage B-Q一式|既存 `pr36-stage-bq-evidence-20261117T0524JST/` の全523fileを列挙し新規コピー。作成者は当時の主/独立担当、当時のraw/source帰属を保持|以前のpost-ZIP index356fileだけを完全一覧として再利用しない。旧sourceコピーをb2のsourceへ帰属し直さない|
|既存原ZIP|当時作成の `preservation/stage-bq-decisions-only.zip` を実read。原ZIP全体484639 bytes、SHA `083cfeaf3752c50a510e7529a510c9eb492644d34f733ae3c3542e604071a9af`、119entry/内部manifest118file|原ZIPを作り直していない。後生成GitHub受領票は元ZIP外にあることを保持|
|歴史的閉鎖の参照|P2-R1/P3-R2の450c→134c Git raw、3file差分、初回review5912312048/独立再review5912417314。今回の新verifier P2-E1/P3-E2の同一反例原票も保存|旧reviewの「未解決なし」を新保全やB受入に転用しない。R1/R2は文書契約の限定閉鎖|
|今回の新規証拠|固定対照、source、stdout/stderr/exit/時刻/入力SHA、承認調査票、GitHub応答、独立監査票。`inventory-v2.json` は889実file、closure4件、未取得2項目|ファイル一覧は凍結時点の正確な集合。凍結後の独立監査/投稿受領票は別の追補であり元束内に存在したとはしない|
|未取得|DFSan20.1.8審査原票、閉鎖原票、原ZIPの所在/版/対象commit/hashはUNKNOWN|現行PR #36本文/レビュー/コメントと取得可能なworkspaceでは特定できず、依頼者に所在照会。並行CLIを正本として採用しない|

`inventory-v2.json` のSHAは `98ff2361c903f2c218a4867d6cf8830ac124e0c643529f5e558b076a22b5a833`。各rowにpath/size/SHA/CRC、producer、retrieval、verified_at、case envelopeのheadとcontext_head、実sourceを確認できる場合のsource_headを分離した。source_head=nullは帰属UNKNOWNで、caseの版をsourceの版に読み替えない。Git原文はblob IDも照合。ZIP内部entry一覧とCRC、閉鎖のbefore/after/review参照も保持する。後日原物未取得のまま台帳の記述だけで独立照合PASSにはできない。

## 検証器・反例・閉鎖範囲

既存package/owner-readback/verify-scopeはZIP/byte/sourceのad hoc検査で、承認scopeや閉鎖リンクの受入interfaceを持たない。重複置換せず、読取専用の [verify-review-evidence.py](verify-review-evidence.py) と [固定対照](test-review-evidence.py) だけを追加した。backend/B_use/製品/原テスト/期待値/workflowは変更しない。

実物台帳検査は **content=PASS / custody_consistency=BLOCKED / exit1**。889file、closure4を検査。exit1を証拠破損と混同せず、stdoutの軸別判定を読む。正常合成policyの受理は、本件の恒久承認が存在する証拠ではない。

|系列|固定入力と実結果|
|---|---|
|先行固定11対照|正常1と、欠落・SHA・size・CRC・ZIPentry欠落・必須field欠落・別HEAD・closure対応欠落・未承認先・読戻し未実施の10負対照。正常exit0、負対照exit1。主担当11/11、別担当も別領域で同じ11/11。重複加算しない|
|P2-E1（独立追加）|内部HEADが別版のZIPを正しい外側hashで登録すると旧verifierが誤受理。修正前source/同一ledger/policyを先に保存。内部HEAD比較（宣言treeも比較）を追加し、同一入力で `ZIP internal HEAD mismatch`/exit1を独立確認。限定閉鎖|
|P3-E2（独立追加）|storage_actor空欄でも旧verifierが誤受理。保存主体非空・再取得主体との相違を必須化。同一入力でexit1を独立確認。限定閉鎖|

初回ad hoc処理には同じ受入interfaceがないため、存在しない旧runnerのRED成功を創作しない。今回実際に再現したREDは追加2件であり、修正後の入力SHA不変を別担当が確認した。修正後に元11対照も受理/拒否を維持。

**信頼境界:** verifierは外部からhash固定された台帳/policyの整合を検査する。承認書の真正性、scopeの意味、別actorの実在、保存先からの取得経路は、人手による原票確認が必要。`APPROVED`という文字列、actor名、path記載だけを実承認/独立性の根拠にしない。policy未指定の本件はcustody BLOCKED。ZIP内部にHEADを持たない形式はHEAD対応を証明しない。必要なGit source照合/真正性審査を、この検証器単独のPASSへ置換しない。

再検証例（新しい専用領域でZIPを取得し、その実物と外側SHAを先に照合する）:

```text
python -B verify-review-evidence.py <bundle内frozen> <inventory-v2.json> --head b2adb697efc2ea25c9430533c3f02383bece080a --ledger-sha256 98ff2361c903f2c218a4867d6cf8830ac124e0c643529f5e558b076a22b5a833
python -B test-review-evidence.py <まだ存在しない案件専用の対照出力先>
```

前者は承認policy未指定なのでcustody BLOCKED/exit1が正しい。policyを渡す場合は承認原物とscope/actor/取得経路を別担当が審査し、`--policy` と独立固定した `--policy-sha256` を指定する。仮policyを作って実保全PASSを得る用途は禁止。verifierは原物を書かず、ネットワークアクセス/ZIP展開/対象生成をしない。対照用scriptは新規directoryのみ生成し、既存領域は拒否する。

## 保存先承認と実操作

|保存先|既存指定/今回確認|実保存・再取得/判定|
|---|---|---|
|Dev-Artifact-Archive|過去の一般成果物用指定は文書で読取。過去のerrno13/WinError5原票を実read。既存PR35 reportも読取可。しかし今回scope/承認者/日時が分かる承認原物は未特定|今回書込NOT_TESTED（承認原物未確定、workspace外は現在write対象外）。過去BLOCKEDを維持。新たなACL変更/迂回/無断書込0。恒久保存BLOCKED|
|Hachibei-Evidence-Vault|承認証拠の役割指定のみ。root一覧は読取できたが別案件だけで、本件への適用承認として流用しない|書込/再取得NOT_TESTED。一般ZIPのArchive代替承認なし/UNKNOWN、恒久保存BLOCKED|
|ChatGPT Library|本人限定container・承認原票・retention未取得。接続探索はMCP初期化失敗、UI inventoryもNode runtime起動失敗|保存/再取得NOT_TESTED、利用経路BLOCKED。Library成功をArchive成功と称さない|
|ChatGPT Space|代替保存方針・適用scope・container・原byte往復経路未確認。同じ接続制約|保存/再取得NOT_TESTED、UNKNOWN/BLOCKED。文書Page生成を原ZIP保存の代わりにしない|
|案件workspace|今回の依頼とworkspace write権限の範囲。新規案件領域に実物を排他的copy|実保存PASS、別担当の新規pathへの再取得/全byte照合PASS。**一時保全であって恒久保全PASSではない**|

保存先の名前だけを承認としない。承認原票の提供と通常権限での原byte保存/再取得経路が再開条件。今取得できた範囲では承認済み恒久経路を確認できず、書込しない判断は「成功応答がない」だけでなくscope/権限未成立に基づく。生成者が同じworkspaceを再計算しただけの結果と、別担当の実再取得を区別する。

## ZIPと独立監査

今回作成した**新しい保全束** `preservation/review-evidence-custody-new.zip` は11142693 bytes、SHA `2ae61582787d08f2976f80c37e283194beea77e9d111e1e33b9559707a859c66`、CRC32 `da2626b8`、894entry/内部manifest893file。旧BQ原ZIPを変更せず内包する。ZIP_STOREDで格納し、旧原ZIPの再生成や不要な再圧縮はしない。

保存元は案件workspace。保存先から実際に別pathへ取得した別担当 `/root/custody_independent` が、全byte/size/SHA/CRC/内部manifest exact集合/原BQ ZIP/基準Git source/889file台帳を確認した。別agent・別Python process・新規pathであるが、同一Windows host/account内であり、別security principalによる隔離ではない。詳細な実施・未実施と原票SHAは今回の独立レビューとPR追補を参照。生成時receiptのPENDINGは履歴として更新せず、後の監査票で状態を追補する。GitHub投稿受領は生成後なので元ZIP内に含まれない。

原束は非公開の可能性を含む原応答を保持するためpublic repoへuploadしない。GitHubにはpublic source metadataと結果/限界のみを提出する。取得可能な恒久URLはまだなく、別担当が将来同原物を恒久先から取得できる状態は未達。

今回のGit文書directoryのmanifest対象は、従来の.mdだけでなく今回追加した証拠専用.py/公開.jsonを含む全実file（manifest自身を除く）へ拡張する。基準b2の21文書manifestと現在版の集合を区別し、過去のmanifest原物は変更しない。新ZIP内の基準Git22fileはb2そのもので、今回提出報告/後生成監査票は別commit/追補で識別する。

## 軸別の限定判定と残件

|判定軸|結果|
|---|---|
|審査文書の識別/再取得|取得済みGit22file/BQ範囲PASS、DFSanを含む全対象はPARTIAL|
|閉鎖原票対応|取得したR1/R2/E1/E2の4件PASS（静的/検証器限定）。DFSan原票UNKNOWN|
|原ZIP完全性|既存BQ原物PASS。DFSan原ZIPUNKNOWN。新束は新束としてのみ監査|
|manifest完全性|取得済みexact集合PASS、未取得の網羅性はUNKNOWN|
|再検証手順|固定11+追加2の範囲PASS、承認真正性/独立取得の意味審査は手動必須|
|既存保存先承認|歴史的な役割指定のみ確認PARTIAL、今回恒久scopeの承認原票UNKNOWN|
|実保存/実物再取得/独立照合|workspace範囲PASS。恒久先からはNOT_TESTED/BLOCKED|
|恒久保全の限定受入|BLOCKED|

正式acceptance workflowはブラウザ導入/実行を含むため起動しない。workflow原文・変更path・eventを確認し、文書/証拠検証のみのcommitに[skip ci]を付ける。skip文字列だけに頼らず、workflow変更0・新HEADのrun/check-runを読取り確認する。正式CI未実施をCI PASSとはしない。手動dispatch/rerunなし。

禁止工程は未実施: backend/B_use実装、対象process生成/制御、ptrace/GDB、ブラウザ/native診断、signal、Linux接続/構築、権限変更、依存導入、正式診断/受入試験、main/PR35/隔離branch変更、merge/Draft解除/Pages公開。証拠専用の合成対照processと通常Git/読取CLIだけを実行した。

次工程は、DFSan資料の正本URL/版/原ZIPと閉鎖根拠の取得、今回に適用する承認原票、通常権限で原byte保存・再取得可能な保管先の確認。その後に同じ台帳/検証器と独立監査を用いて不足分だけ再開する。native BLOCKED、ABA HOLD、保証B UNKNOWN、WebKit根本原因UNKNOWN、製品受入FAIL、追加コードpush HOLD、PR35/36 Draft・マージNO。今回の証拠検証script提出はbackendコードpush承認ではない。
