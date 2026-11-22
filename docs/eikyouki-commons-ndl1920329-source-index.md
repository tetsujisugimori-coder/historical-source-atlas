# 『永享記』底本候補 Commons 複製の参照・保全索引（Issue #50）
作成日：2026-11-22 JST。これは**画像の原本保存ではなく参照情報のGit管理**である。過去のIssueコメントだけに依存せず、対象ページと記事IDの対応を保存する。画像取得・実読・差異認定を一切偽装しない。

## 複製元と出典識別
- NDL資料ID：`1920329`
- NDL書誌：[NDLサーチ](https://ndlsearch.ndl.go.jp/books/R100000039-I1920329)、[NDL画像閲覧](https://dl.ndl.go.jp/pid/1920329)
- 対象刊本：近藤瓶城編『史籍集覧』第12冊（Wikisourceで言及される底本候補）
- Commons側のファイル名：`NDL1920329_史籍集覧_第12冊_part4.pdf`
- Commons：[ファイル詳細](https://commons.wikimedia.org/wiki/File:NDL1920329_%E5%8F%B2%E7%B1%8D%E9%9B%86%E8%A6%A7_%E7%AC%AC12%E5%86%8A_part4.pdf)
- 固定比較先：Wikisource『永享記』oldid=218476、リポジトリ `evidence/batch08/source/wikisource-fixed.html`、既存のSHA-256 `cd120c44ccd7fbd69fbad81d1d5578c91574bdd2e70f21e5c086e915fe2abae0`
- 関連記録：[Issue #50](https://github.com/tetsujisugimori-coder/historical-source-atlas/issues/50)、[Commons経路の発見報告](https://github.com/tetsujisugimori-coder/historical-source-atlas/issues/50#issuecomment-7073577903)

## 限定対象のページ索引
以下のページ番号は**Commons part4 PDF内のページ指定**であり、NDLのコマ番号や本文の印刷頁番号とは未照合。

| 記事ID | 対象 | Commonsページ参照 |
|---|---|---|
| EK-0159 | 「永享記終（イ）」および『東乱記』校合注 | [83](https://commons.wikimedia.org/w/index.php?title=File%3ANDL1920329_%E5%8F%B2%E7%B1%8D%E9%9B%86%E8%A6%A7_%E7%AC%AC12%E5%86%8A_part4.pdf&page=83)、[84](https://commons.wikimedia.org/w/index.php?title=File%3ANDL1920329_%E5%8F%B2%E7%B1%8D%E9%9B%86%E8%A6%A7_%E7%AC%AC12%E5%86%8A_part4.pdf&page=84) |
| EK-0189 | 固定翻刻の頁標識 `【 NDLJP:386】` と前後本文 | [85](https://commons.wikimedia.org/w/index.php?title=File%3ANDL1920329_%E5%8F%B2%E7%B1%8D%E9%9B%86%E8%A6%A7_%E7%AC%AC12%E5%86%8A_part4.pdf&page=85)、[86](https://commons.wikimedia.org/w/index.php?title=File%3ANDL1920329_%E5%8F%B2%E7%B1%8D%E9%9B%86%E8%A6%A7_%E7%AC%AC12%E5%86%8A_part4.pdf&page=86) |
| EK-0192 | 「武勇の名をそ残しける、」の後と明治期校訂後記 | [86](https://commons.wikimedia.org/w/index.php?title=File%3ANDL1920329_%E5%8F%B2%E7%B1%8D%E9%9B%86%E8%A6%A7_%E7%AC%AC12%E5%86%8A_part4.pdf&page=86) |

## 保管・検証状況
| 対象 | 状態 | 根拠・制限 |
|---|---|---|
| NDL書誌とID、Wikisource固定翻刻との照合候補 | 記録済み | リンク・ファイル名・既存翻刻SHAを索引化 |
| 4ページの閲覧候補URL | 記録済み | リンク先のページ本文の実表示・画像読取は未完了 |
| Commons PDF原ファイルのbyte保存 | **NOT_SAVED** | この環境で外部画像取得に失敗。157MB級のPDF全体を無条件で取り込まない |
| 83〜86ページの切出し画像のbyte保存 | **NOT_SAVED** | ファイル未取得。画像SHA-256、サイズ、再取得照合はいずれも UNKNOWN |
| 画像の原字と固定翻刻の逐字一致 | **NOT_TESTED** | 画像を実読していない。旧字正規化と本文異同を未分類 |
| 頁番号・NDLコマ番号・印刷頁の一致 | **UNKNOWN** | Commons PDFページ番号との対応は未確認 |
| 異本校合・史実認定 | **NOT_TESTED** | 本索引の対象外 |

次工程：実画像が取得できる環境で83〜86ページを実際に保存し、取得した原byteとSHA-256・ファイルサイズを記録。保存先から再取得して一致した場合のみ「原物保管済み」と更新する。画像で判読できた3箇所に限り文字対照し、訂正が必要なら別Issue・Draft PRで検討する。

**変更禁止：** 既存192記事・恒久ID・原文・JSON・SQLite・HTML、診断用PR #35/#36および史実評価方針PR #23はこの索引作成では変更しない。
