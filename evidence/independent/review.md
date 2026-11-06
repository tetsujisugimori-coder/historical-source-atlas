# Historical Source Atlas PR #1 独立再レビュー

担当: `/root/independent_review`（実装担当とは別の子エージェント）。製品コードを編集せず、独自スクリプトと隔離コピーで検査した。

## 固定対象と判定

- 旧HEAD: `ec347901dc4b688927bb3002121ff58e6b7dbd40` / tree `86469d077c427555337763829df2ebbb6ba4929a`。
- 修正コード最終候補: `aaea5c26e22cf3c8060dac17c260bee9717454a9` / tree `13d7ab9fa8d9b90749c4cc8babb5068f2a7b6b11`。
- 各対象は `git archive` の独立コピーから実行した。候補の前段 `84cf587` の結果と、最終候補の新規実行を区別した。
- **上記修正コード候補の独立ソフトウェア受入: PASS。未解決P1/P2なし。今回の修正範囲の限定マージ推奨: YES。**
- この文書作成時点では、証拠追加後の最終提出HEAD・最終CI/ZIPは未確定。Hの最終対応は後続の独立確認とPR記録で確定する。Draft解除・マージ・公開は許可しない。

## P2の独立閉鎖判断

|項目|旧HEADの実行RED|修正候補の独立GREEN|判定|
|---|---|---|---|
|P2-1 年代順|逆順入力でも実比較器が掲載順へ戻り、0015が最後。実ブラウザ4条件でも再現|逆順の実比較器と実画面4条件で0012→0015→0013。掲載順は1〜15を保持|閉鎖|
|P2-2 所属・出典|work/edition/chapter名/source URLの4変異すべてbuild/test exit0|同じ4変異を記事ID・項目付きでbuild exit1。chapter_idも実装境界で照合|閉鎖|
|P2-3 型・日付・精度|不正Julian、逆順、float月、負era、文字年、float/string閏月、unknown矛盾等を受理|独立19不正入力をbuild exit1。正当unknownのNULL、研究日付、暦別閏年、支持範囲の閏月・小月境界を別検査|閉鎖|
|P2-4 全項目|DB6列を直接破損しても既存test exit0|DB36列・payload36列の個別改変を検出。実際のJSON/HTMLファイル読取経路でも36×2=72変異を検出。既存DBを再生成せず検査|閉鎖|
|P2-5 恒久ID|NULL2件・空文字・空白を直接INSERT可能|全4PKについてNULL/空/空白/非文字/BLOB/NUL/重複の40直接反例を拒否。同内容別IDの記事16件を保持|閉鎖|

旧版および修正候補の原出力は `red-results.json` と `candidateaaea-probe-results.json`。正常baselineのbuild/testは0、19入力変異は非0、6列DB破損はbuild0後のtest非0であり、ケース数を正常テスト数と混同しない。

## 独自の追加指摘と修正確認

1. 検証中のID制約がUnicode空白、整数のTEXT affinity変換を許した。文字集合を入力/DBで統一し、STRICT ANY＋typeofで拒否する修正を確認。
2. その後もSQLite GLOB/lengthのNUL打切りにより `A\0#` / `A\0B` が直接INSERTできた。`instr(id,char(0))=0` の追加で実行RED→GREEN。`id-nul-red.json` / `id-nul-green.json`。最終候補でも全4PKの独自直接反例を再実行。
3. unknownの `int(None)`、未解決表示の確定扱い、閏月表示不足をコードレビューで指摘。正当unknownを実DBへ保存してNULL保持、UI分岐・閏表示修正を確認。これらの修正前はコード読取であり、実行REDと称しない。
4. 集約runnerの検査前buildを指摘。修正後、意図的に破損させた既存DBへ集約runnerを起動しexit1、前後SHA同一を独立確認。`candidateaaea-runner-results.json`。修正前の実行REDは取得していない。
5. Windows WebKitの通常TabがsummaryからBODYへ出た。Alt+Tabも同じ。一時DOMに明示tabIndex=0を付けると正しい出典リンクへ移った。製品側で明示し、条件を通常Tabのまま維持して4条件GREEN。`focus-platform-results.json`。この結果を実機Safari仕様と同一視しない。
6. カードのoverflowによる既定focus outlineの上左右の欠損はP3として報告。内側outline追加後、WebKit390画像を目視し四辺の輪郭を確認した。
7. 別レビューの指摘を受けた換算根拠URL検証を独立追試。7cコードではjavascript/data/相対等を受理する実行REDを保存した。中間8a修正でも空userinfoとDELを受理したため、P3契約不一致として実行REDを報告。最終aaeaではURL16ケースがすべて期待通りとなった（14不正拒否、2正当HTTPS受理）。unknownのNULL出典は別deep positiveで保持。`url-code-red-results.json` / `url-draft-results.json` / `candidateaaea-url-results.json`。任意のHTTPSリンク先の信頼性・内容検証を実装したという意味ではない。

## 独立実行と保全

- `candidateaaea-deep-results.json`: 正当unknown、同内容別ID、全36DB列改変、全36payload列改変、実JSON/HTML72変異、全4PK40直接反例、暦の規則差、6生成障害を検査。
- `candidateaaea-calendar-results.json`: 永享8閏5月29日受理/30日拒否、通常月への換算流用拒否、存在しない閏6月拒否、unresolvedでも支持範囲の不実在日拒否。Gregorianの5日を標準datetimeのordinalで別計算し、固定JDNも照合。
- opened/初回記事/最終記事/validated/committed/before_replaceの6障害で旧DBの前後SHA一致、一時ファイル0。正常な内容変更時は置換され、全項目一致を確認。
- 元15記事のID・日付・本文候補・要約・換算値は保持。差分はEK-0010の解釈と注記、EK-0015の本文場所NULL化と編集注記の4項目だけ。EK-0003の「より」は始期との注記を保持。

## 独立実ブラウザ

`candidateaaea-browser/results.json` / `judgment.json`: Chromium141.0.7390.37とPlaywright WebKit26.0、390/1280×1000の4条件を新規実行。独立判定器exit0、**4/4条件、17checks×4=68判定成功**。12PNGと4ダウンロードJSONを保存。前段7cとHTML hashが同じであっても、aaea独立コピーで新規実行した。

表示された年代順・掲載順、検索、年/章絞込、Enter詳細、Tabで正しい出典リンク・Shift+Tab復帰、Space詳細、JSON実ダウンロード、0件表示、focus/visibility、横スクロール、console/pageerrorを検査。出典はhrefを照合し、外部サイトへの実遷移・配信内容は検査していない。ダウンロードはEK-0015の全レコードを比較した。旧版4条件では同じ年代順期待値を判定器がexit1で拒否している。

Python3.14.7 / SQLite3.50.4 / Node24.20.0 / Playwright-core1.56.1 / Windows11 build26300。sandbox内localhostは初回接続を拒否したため、承認された非sandboxローカル検証で実行。Pagesや外部ホストは作成しなかった。

## 残存範囲

- 学術的受入はPARTIALのまま。底本画像校合、記事境界・網羅性、史実認定、原文全文、厳密な版・頁/行・revision/権利確認は未完了。
- NAO月朔は旧独立レビューの検証履歴を読取り、コードの支持範囲・計算を今回独立検査した。NAOへの新規照会は実施していない。provisionalをverifiedへ変更していない。
- 任意年代の旧暦換算、実機Safari、VoiceOver、物理入力、強制終了/電源断/同時生成耐久性、外部リンク先の配信はNOT_TESTED。
- ソフトウェア受入と学術検証完了を分離する。未取得の版/頁等を創作していないことを確認した。

## A〜H

A〜Gは上記固定修正候補の範囲でPASS。Hは独立実行と候補HEAD/hashの対応を確認済みだが、最終提出HEAD/CI原成果物の確認は後続記録待ち。最終HEADの証拠確認を省略して全提出PASSにはしない。
