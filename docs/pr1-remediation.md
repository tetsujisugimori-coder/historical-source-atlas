# PR #1 P2根本修正・検証台帳

対象旧HEAD: `ec347901dc4b688927bb3002121ff58e6b7dbd40` / tree `86469d077c427555337763829df2ebbb6ba4929a`。
2026-11-06にGitHubからPR本文・独立レビュー5793714253・コメントを取得。open / Draft / 未マージ、main `410fea4f6d3ccd5e1c1a62c8f2ad49ae97782f70`。ローカル変更・AGENTS.md・リポジトリ内SKILL.mdは無し。旧PR本文の未実施表記は歴史状態であり今回の実行と区別する。

## 修正契約

|P2|原因|修正|確認入口|
|---|---|---|---|
|1|ISO文字列減算がNaN|ISO文字列の大小比較、同日は掲載順→ID。不明換算日は最後。掲載順は独立比較器|`test_sort.cjs`、実画面|
|2|入力の所属・出典を固定値へ黙示置換|固定資料のwork/edition/chapter_id/chapter/source_urlを入力境界で照合。不対応値は記事ID・項目付きValueError|`test_reject_input_mutations_without_replacing_good_db`|
|3|SQLite型名/無条件int()に依存|厳密Python型、暦別実在日、精度・前後・既知月朔との一致。NULL/不明と不正を分離|`test_calendars_precision_unknown_and_research`|
|4|DB比較が3列のみ|JOINで36項目×全記事、型/NULL/ID集合/件数比較。`verify`はmode=ro、再生成しない|全DB/HTML/JSON項目の個別改変|
|5|rowid表のTEXT PRIMARY KEYがNULL許容|入力のID集合/文字集合検査。STRICT ANY+typeof(text)+NOT NULL+一意性+文字集合+NUL禁止|4表への直接INSERT負対照|

IDはASCII英数字で始まり、その後ASCII英数字・`_`・`-`。既存IDは維持。SQLiteのTEXT affinityによる数値→文字列変換を避けるため、主キーはSTRICT ANYにtypeofチェックを併用する（SQLite 3.37以降）。関連付けは別表のまま。同内容・同日でも別ID/掲載順なら独立記事として保存する。

`build_database`は入力検証後、保存先と同じディレクトリの一意な一時ファイルに全構造を作り、整合確認・commit・close後に置換する。途中例外・置換失敗で旧DBを保持しfinallyで一時ファイルを消す。電源断後のディレクトリfsyncや任意OS/ネットワークファイルシステムの耐久性保証は今回の対象外。

## 暦と史料の境界

日付の値は15件とも変更しない。西暦文字列はGregorianとJulianそれぞれの閏年規則でJDNへ変換して検証。Gregorian標準dateをJulian実在日判定には用いない。研究推定はGregorian、両端と根拠を同時指定し形式・実在・前後を検査する。

宣明暦の実在日・閏月・換算範囲の照合は、旧独立レビューの国立天文台6照会から転記された永享8〜10年の月朔と翌年元日の範囲に限定。今回サイトを新規照会した証拠ではない。この範囲外はunresolvedかつ換算値NULLで保持し、確認済みにはしない。支持範囲内の不在閏月・小月30日などはunresolvedでも拒否する。これは汎用旧暦換算器ではない。

`unknown`はera/era_year/western_year/月/日/閏月/換算日NULL、status=unresolvedと未解決理由を要求。既知だが換算未解決の値も保存可能。dayのstart=endは原文が示した日付点の換算精度であり、事件の継続期間や終息日を表さない。EK-0003の「より」の始期注記は保持。

意図した史料注記差分は4項目のみ。EK-0010のdate_interpretation/editorial_noteに年が前文脈由来と明記。EK-0015のlocation_in_textをNULLとし、従来の京都（発給側）をeditorial_noteの編集地理補足へ分離。本文に新たな場所語形を創作しない。全文はNULL、仮登録、provisionalを維持。底本頁・コマ・新規revision IDを推測で補わない。旧レビューの暦日照合と本文校訂・史実認定・引用文書真正性は別判断。

## 再現手順

Python標準ライブラリのみ。新規作業コピーで生成を明示実行し、その後読取検査する。

```sh
python prototype/eikyouki/build.py
python prototype/eikyouki/run_checks.py evidence/checks
# 既存DBの破損調査ではbuildを先に実行しない:
python prototype/eikyouki/test_dates.py
node prototype/eikyouki/test_sort.cjs
# 任意の隔離した依存ディレクトリにplaywright@1.56.1を導入しブラウザを準備
node prototype/eikyouki/browser_acceptance.cjs evidence/browser
python prototype/eikyouki/evidence_manifest.py evidence
```

`run_checks`はbuild/sync_htmlを呼ばず既存出力を検査。JSON編集時のHTML同期は`sync_html.py`という別の明示操作。`<`をJSONエスケープし`</script>`境界突破を防ぐ。検査が破損を修復してからPASSする構造にしない。

ブラウザはChromium/WebKit×390/1280、高さ1000。ローカルHTTPのみ、Pages公開無し。日付順/掲載順、検索、年/章絞込、0件、詳細のEnter/Space、focus、出典href、仮登録、JSONダウンロード全項目、横はみ出し、console/pageerrorを確認。Windows WebKitは既定のリンクTab移動でBODYへ抜けたため、両出典リンクへ明示tabIndex=0を付ける最小のキーボード改善を加え、通常Tab検査を維持する。Alt+Tabでは解消せず、独立担当が隔離DOMで原因を切り分けた。実機Safari/支援技術/外部出典サイトのリンク先配信状態はNOT_TESTED。

## 証拠の扱い

`evidence/*draft*`は作業中ツリーの試行履歴で最終HEADの成功証拠に転用しない。初回WebKit通常Tab失敗、Windows sandbox一時ディレクトリPermissionError、改変試験がSTRICT型制約に先に拒否された試験器修正などを履歴として残す。最終固定HEADの実行・独立実行・CIは後述の最終受入記録およびPRコメントへ追記する。

独立担当は元HEADで5P2を再現。修正中レビューではNULL閏月のint変換、IDのNUL切断、検査runnerの先行buildなどの反例を指摘し、同反例を修正後再実行する。主担当テストと独立実行を件数として混ぜない。

限定ソフトウェア受入と学術検証完了を分ける。Draft維持、マージ/Pages公開無し。


CI初回（84cf587、run 42208828532）は単体/CLIまで成功したが、ubuntu-latestが26.04へ進んでおり固定Playwright1.56.1の対象外でinstallがexit1。ブラウザ段階はSKIPPEDで成功に含めない。ubuntu-24.04へ固定して再実行する。PRイベントではGitHub run自体のhead_shaがmerge commitとなり得るため、checkout実HEADとmanifest/sourceを照合し、artifact名にもPR head SHAを使用する。
