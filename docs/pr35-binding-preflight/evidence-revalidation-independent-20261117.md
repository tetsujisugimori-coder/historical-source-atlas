版1 / 2026-11-17 JST / 独立担当 /root/custody_independent / 審査基準 b2adb697efc2ea25c9430533c3f02383bece080a、tree ae77dcfeeddc80d2e7bf6149a32063e372392f0c。今回の新Git commit/remote受領監査は後生成の別票とする。内容SHAはmanifest.sha256。

# 審査証拠再検証・保全工程の独立レビュー

## 範囲と結論

主担当の提出結論、過去のレビュー表示を受入根拠として採用せず、GitHubの実commit/tree/blob、local Git、審査文書、固定反例、既存原ZIP、新保全束と実fileから判断した。総合PARTIAL、workspace内の識別・保存・独立再取得・byte照合は限定PASS。恒久先への承認原票/実保存/再取得は成立しておらず、恒久保全BLOCKED。DFSan20.1.8原票/原ZIPは未取得UNKNOWN。

独立担当は別agent/別Python process/新規pathを使用した。同一Windows host/accountであり、別security principalや別機器の隔離を証明した監査ではない。保存元はworkspaceで、Archive/Vault/Library/Spaceから原物を再取得したとは認定しない。

新規P2-E1/P3-E2は同じ固定入力で誤受理を再現した後、最小修正後の拒否を独立確認し、この限定範囲で閉鎖可能。確認範囲で未解決の新規P1/P2/P3はなし。これは既存の保証B/実装/回帰/環境/恒久保全残件の閉鎖ではない。

## 実際に再取得・再計算した物

1. GitHub PR35/36、commit/tree、PR36の全22 Git blobを自担当のgh REST経路で取得。Git blob SHA1を実bytesから再計算し、workspace実fileと全byte一致。PR36 b2adb697/tree ae77dcfe/親1273、PR35 97ce39e8、両Draft/未mergeを確認。文書manifest21件は全SHA/exact集合一致。
2. BQ原ZIPを自担当が新規pathへcopyし再open。484639 bytes、SHA256 `083cfeaf3752c50a510e7529a510c9eb492644d34f733ae3c3542e604071a9af`。全byte/size/SHA/CRC32一致、119entry全CRC、内部manifest118file exact集合と全size/SHA/CRC、final Git22fileとの一致を確認。原物は変更していない。
3. inventory-v2.json（SHA256 `98ff2361c903f2c218a4867d6cf8830ac124e0c643529f5e558b076a22b5a833`）とfrozen全889fileを検証器とは別の独立scriptで再計算。全size/SHA/CRC、Git blob、frozen exact集合、ZIP12個のentry構成とCRC、closure4件の参照先存在を確認。context_headとsource_headを分け、未確認sourceはnullとしている。旧BQ後生成index356件だけをcase全体523fileの完全一覧へ転用していない。
4. 新束を保存済みworkspaceから自担当の新規directoryへ実copyし再open。11142693 bytes、SHA256 `2ae61582787d08f2976f80c37e283194beea77e9d111e1e33b9559707a859c66`、CRC32 `da2626b8`。全byte/size/SHA/CRC一致、894entry全CRC、内部manifest893file exact集合と全size/SHA/CRC、frozen889file全byte、基準Git22file、証拠検証source2fileを確認。内包BQ原ZIPは元原物と全byte一致。これは今回の新束であり、再生成した旧原ZIPでも恒久保管先でもない。

監査原票は案件領域のindependent/github-raw-source-audit.json、existing-original-audit.json、inventory-v2-independent-audit.json、new-zip-independent-audit.json。後二票のSHA256はそれぞれ `93d55241a76550d79cd21a2fcf1cb8b2d773446b74f7368c35ea7765ebe2ca5b`、`6fd98f5e039dca97e7d2362e197d1ae0c3ed847876f9fa9b0c151c9472f9d2e8`。新束生成後の監査原票は元ZIP内に含まれたとは扱わない。

## 反例・修正・同一入力の再検算

既存ad hoc verifierは今回の承認/閉鎖/読戻しinterfaceを持たないため、証拠専用verifier追加は重複置換ではない。新verifierは読み取り専用で、backend/B_use/対象process操作をしない。合成対照scriptだけが呼出先の新規専用directoryへ記録を生成する。

- 固定11対照を自担当の新規領域で実行。正常exit0、負対照10件exit1、11/11。これは単一系列の独立再確認であり主担当の件数へ重複加算しない。
- P2-E1: ZIP内部manifestのHEADを別版へ変更し、外側size/hash/CRCを正しく固定した入力を旧verifierが誤受理。修正前source/入力/実結果を先に保存。内部HEADと宣言HEADの比較、宣言treeがある場合の比較という最小修正後、同じ入力SHAで `ZIP internal HEAD mismatch`、FAIL/BLOCKED/exit1を確認。
- P3-E2: storage_actor空欄の固定policyを旧verifierが誤受理。保存主体の非空と再取得主体との相違を必須化した後、同じ入力SHAで `independent actor missing`、FAIL/BLOCKED/exit1を確認。
- 修正後に元の11対照を別新規領域で再確認し11/11。無変更の再試行成功で閉鎖したものではない。

修正前source SHA256 `bef369cb9163966eeefcf90f9c110218327f37a1a4e21a7882e3354c8446bf68`、修正後 `fbb2662e516eff5883c6636af6c766875e2ae48a0a2309bbbbb2157bee81bba4`。固定追加入力と原票はindependent/additional-counterexamples/に保持。inputのbyte列を都合よく変更していない。

## 承認・閉鎖・保全の限界

approval-investigation.jsonは既存の役割指定、今回の適用承認原票、技術access、実保存を分け、恒久先の今回承認UNKNOWN/保存0/恒久保全BLOCKEDを維持している。この区分は妥当。ただし自担当は各恒久先の承認原票や保存済み実物を取得できておらず、承認の真正性/適用性やその保存先からの独立取得をPASSとしていない。過去Archive errno13/WinError5原票は実readしたが、現在の権限試行や承認原票の代替ではない。別案件のVault承認は流用していない。

verifierの合成APPROVED policy受理はschema/byte整合の対照であり、本件の承認が存在する証拠ではない。承認原物、scopeの意味、actorの実在、保存先からの取得経路は外部審査が必要。policy未指定の実案件はcontent PASS/custody BLOCKED/exit1のまま。内部HEAD欠測ZIPの帰属やGit sourceとの関係を検証器単独で証明したとはしない。

R1/R2の旧指摘→450c/134c source差分→5912417314レビュー、E1/E2の誤受理→最小修正→同一反例拒否を追跡可能にした範囲は受入可能。文言限定閉鎖をTCB/B_use/実Linux安全性へ昇格していない。DFSan審査/閉鎖/ZIP原物の所在が未確認なので、全成果物の網羅性はPARTIALである。

## 不実施と次の条件

backend/製品/原テスト/期待値/workflow変更、対象生成/制御、GDB/ptrace/browser/native診断、signal、実proc/メモリ照会、Linux環境構築、権限変更/導入、CI dispatch/rerun、main/PR35/隔離資産変更、merge/Draft解除はこの担当から0。証拠専用合成試験と通常ファイル/Git/GitHub読取りだけを実行した。正式CIはこのレビューの検証手段ではなく未実施。

次はDFSan原物の正本所在、今回に適用する承認原票、通常権限の原byte保存・独立取得経路を提示して不足分だけ再開する。現時点の技術方式採用YES0、backend実装開始NO、実測開始NO、native BLOCKED、ABA HOLD、保証B UNKNOWN、WebKit根本原因UNKNOWN、製品受入FAIL、両PR Draft/マージNO、追加コードpush HOLDを維持する。

2026年11月17日 20:28 JST
