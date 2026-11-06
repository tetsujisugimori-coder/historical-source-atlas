# PR #1 修正受入報告

## 判定の範囲

コード最終候補 `aaea5c26e22cf3c8060dac17c260bee9717454a9`（tree `13d7ab9fa8d9b90749c4cc8babb5068f2a7b6b11`）。旧HEADは`ec347901dc4b688927bb3002121ff58e6b7dbd40`。候補のソフトウェア修正受入はPASS、5件のP2は閉鎖、限定マージ推奨YES。学術的検証はPARTIALのまま。Draft・未マージ・未公開を維持する。

この報告を含む証拠追加commit後には、製品コードを変更せず、**最終提出HEADそのもの**で主担当検査・独立再実行・CIを実施する。最終HEAD/tree/run/attempt/artifact ZIPの対応は、自己参照commitを避け、PR #1の最終受入コメントと最終CI原成果物に記録する。この候補の成功を、後続HEADを実行した証拠として扱わない。

## 受入A〜H

|条件|候補判定|根拠・範囲|
|---|---|---|
|A 5件の原因・修正・旧RED/新GREEN|PASS|[修正台帳](pr1-remediation.md)、[元レビュー](../evidence/historical/original-review.md)、独立red-results.jsonとcandidate原票。ソートはreverse入力と実画面でも確認|
|B 15記事保持・全項目整合|PASS|JSON/HTML/DB JOIN全36項目×15=540値を型/NULL込み照合。ID/日付/要約/原文手掛かり/全文NULLを保持。後述の注記4項目のみ意図的差分|
|C 不正拒否・正当unknown・同内容別記事|PASS|型/暦/精度/所属/URLの負対照、unknown/unresolved+NULL、研究日付、同内容別IDの16記事生成|
|D 直接INSERTのID制約|PASS|works/editions/chapters/articlesの4PK。NULL/空白/非文字/BLOB/NUL/重複を拒否。独立40反例|
|E 全項目の個別改変を検出|PASS|DB36項目、実HTML36項目、実JSON36項目を個別改変。欠落/余分/重複IDも拒否。破損した既存DBを再生成せず検査|
|F 再生成失敗時の保全|PASS|opened/first article/last article/validated/committed/before_replaceの6障害で既存DB SHA256同一・tmp0。OS置換失敗の合成例外も検査。正常変更は置換され全項目一致|
|G 実ブラウザ|PASS|主担当4条件92操作判定、独立4条件68判定。旧版の4条件は年代順検出FAIL/exit1、新版は同条件PASS/exit0。以下の対象範囲に限る|
|H 独立とHEAD/証拠対応|候補PASS・最終照合待ち|候補は独立archive/hash照合済み。最終提出HEADはPR最終コメント・最終CIのmanifestと原ZIPで判定を確定する|

## P2の閉鎖

P2-1は文字列減算を除去し、日付順は検証済みISO開始日、同日は掲載順→ID、不明は末尾とした。掲載順は別比較器を使い、元・逆順・回転した入力すべてで0012→0015→0013を確認する。

P2-2は固定作品・底本・章段・出典の完全照合を生成前に実施する。レビューのwork_id/edition_id/chapter/source_urlの4変異にchapter_id変異も加え、記事ID・項目名のある拒否を確認。別史料の記事を既存所属へ黙って取り込まない。

P2-3はint厳密型（boolも拒否）、閏月bool/NULL、年月日精度と換算範囲、Gregorian/Julian別実在日、期間前後、研究推定値と根拠を検査する。支持範囲の旧暦月朔と小月末・閏月を確認し、範囲外は未解決のまま保持する。

P2-4は正規化所属JOINと全フィールド照合、型/NULL/ID集合/件数の検査へ変更。read-only検査は壊れたDBを上書きしない。HTML同期も生成と別の明示操作にし、script境界エスケープを検査する。

P2-5は入力境界とSQL制約でIDの非NULL・非空・一意・文字集合・型を一致させる。NULでSQLite GLOBが打ち切られる独立反例も修正前RED/修正後GREEN。既存恒久IDを再採番せず、同本文・同日付の記事も別IDなら保存する。

## 試験と証拠分類

- **今回の主担当実行**: `evidence/checks-code-final/results.json`は9 unittestメソッド、211 method/subtest記録、2 CLIコマンド。これを211件の独立テストメソッドとは数えない。ブラウザ候補は`evidence/browser-candidate/`の4条件・92判定・8PNG・4実ダウンロード。
- **独立実行**: `evidence/independent/`の旧RED、NUL RED/GREEN、Windows WebKit focus切分け、候補別probe/deep/calendar/browser/manifest、独立review.md。主担当のPASSを前提としない別著の反例と実ブラウザ。候補7cのブラウザは4条件・68判定・12PNG・4ダウンロード。aaeaから全反例・4ブラウザ条件を改めて独立実行済み（candidateaaea-*）。URL16例は14拒否・2正当受理。
- **過去の参考記録**: `evidence/historical/original-review.md`は旧独立レビューの写し。国立天文台の6照会・39月朔はこの検証履歴の読取であり、今回の新規サイト照会ではない。
- **作業中履歴**: `*draft*`、`checks-candidate*`は作業中の版と明記。初回WebKit通常Tabの2条件FAILを残し、tabIndex明示後に通常Tabの条件を維持してGREEN。sandboxの一時ディレクトリPermissionErrorは環境エラーとして区別。DB全項目改変の初回2例はSTRICT型制約が先に拒否したため、保存できる型の改変へ検査器を修正した。
- **CI照合**: 初回run42208828532はUbuntu26.04と固定Playwright1.56.1の不一致でFAIL（ブラウザSKIPPED）。ubuntu24.04へ固定し、候補10747/7cではCI全段階成功。10747のartifact ZIPは43files、manifest42filesの全hash一致を主担当が読取検査済み。最終HEADの結果として流用しない。
- **NOT_TESTED**: 実機Safari、VoiceOver、物理キーボード、外部リンク先の現配信、任意年代の旧暦変換、電源断/OSクラッシュ/同時生成の耐久性、底本画像の校合、全文校訂・史実認定・権利の最終確認。

## 実ブラウザの対象

Windows11 build26300、Python3.14.7、SQLite3.50.4、Node24.20.0、Playwright-core1.56.1、Chromium141.0.7390.37 / Playwright WebKit26.0。390/1280×1000の4条件。localhost専用、外部公開無し。

日付順・掲載順の実描画、検索、年/章絞込み、詳細Enter/Space、正しい出典リンクへのTabとShift+Tab、検索0件、focus-visible輪郭、仮登録表示、href/rel、ダウンロードされたEK-0015の全レコード、横はみ出し、console/pageerrorを検査。WebKit既定リンクTab移動を切り分けてtabIndex=0を明示し、輪郭はカード内側に描いた。出典サイトへ実遷移して内容を再照合したとは報告しない。

## 史料注記と残存P3

EK-0010のdate_interpretation/editorial_noteへ「年は前文脈から補完」を追加。EK-0015のlocation_in_textをNULLとし、従来の京都（発給側）はeditorial_noteの編集地理補足へ分離。本文中の場所語形を創作して補わない。EK-0003の「より」は始期という注記を維持し、換算start=endを事件終息日とはしない。

残るP3/研究課題は版固定・底本頁/行・記事境界・抜粋網羅性・権利の精査。全文は未転記、15件は仮登録、換算はprovisional。これらの学術的完成をソフトウェア修正受入のPASSと取り違えない。今回の限定受入を一般公開や汎用史料システム完成の承認としない。
