# 北条五代記 巻第一・巻第二

- `hojo_godaiki_records.json` に巻第一5節（HG-0001〜0005）と巻第二7節（HG-0006〜0012）の見出し・要約・閲覧リンクを収録。巻第一の固定版情報は既存の `metadata`、巻第二は `metadata.additional_volumes` に保存。本文欄はNULL。
- `person_links.json` に巻第一と『永享記』の暫定人物対応、史料ごとの表記、根拠URLを保存。底本画像を照合した範囲は巻第一の指定表記2箇所。
- `index.html` で各巻の節と固定版参照を閲覧可能。
- `build.py` で両作品204記事の独立SQLiteを生成。記事単位の閲覧URLは `article_source_urls.source_url`、北条五代記12記事の固定版URLは `article_fixed_sources.fixed_source_url` に保存。いずれも `article_id` で参照する。`editions.base_url` は刊本版の既存の参照値で、北条五代記各記事の固定版は `article_fixed_sources` から取得する。人物言及8件の根拠URLは `person_mentions.evidence_url` に保存。
- `test_batch01.py` で両巻のJSON・HTML・SQLiteと出典対応を検査。節リンク専用CIではChromiumで全12節を実際に開く。

```sh
python prototype/hojo-godaiki/test_batch01.py
python prototype/hojo-godaiki/build.py
node --test prototype/hojo-godaiki/verify_source_navigation.test.cjs
```

採録の基準は[巻第一の固定版217784](https://ja.wikisource.org/w/index.php?oldid=217784&title=北条五代記/巻第一)と[巻第二の固定版214082](https://ja.wikisource.org/w/index.php?oldid=214082&title=北条五代記/巻第二)。記事の閲覧リンクはWikisource現行ページの該当節を開く。両巻とも全文、暦換算、異本、史実認定の照合状態は各採録台帳に記録する。
