# 北条五代記：第1便（巻第一5記事）

- `hojo_godaiki_records.json`：5つの節見出しに対応するHG-0001〜0005。要約と出典リンクを仮登録。**原文全文は未収録**。
- `person_links.json`：暫定人物ID、史料固有表記、旧『永享記』EK記事への参照（人物評価・史実認定なし）。
- `index.html`：5記事の簡易表示。既存『永享記』画面は変更しない。
- `build.py`：『永享記』192記事を読み取り専用で取り込み、計197記事・人物参照を**独立した別SQLite**へ生成。記事単位の出典URL197件を `article_source_urls`、人物言及8件の根拠URLを `person_mentions.evidence_url` に保存する。『永享記』専用DBには書き込まない。
- `test_batch01.py`：192件×全項目の同値性・新ID・リンク正当性・検証状態・反例を確認。

```sh
python prototype/hojo-godaiki/test_batch01.py
python prototype/hojo-godaiki/build.py
```

出典：https://ja.wikisource.org/w/index.php?oldid=217784&title=北条五代記/巻第一 （博文館1899年刊行本に基づく公開翻刻）。固定版oldid=217784を参照済み。節への閲覧リンクは現行Wikisourceの見出しアンカーを利用し、固定版は出典として別に保持する。HG2件はNDL画像の該当字面のみ照合済み（全篇未照合）。原HTML全量・SHA・出典画像照合・再利用条件の最終確定は別途実施。節内の日時を記事全体へ転写しない。学術的な正しさとCIの成功は別の判定です。
