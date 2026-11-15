# PR #35 native診断停止・証拠保全レビュー
対象PR: https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/35
reviewed_sha: c54a6c24d81cbd09345e15f82dbbeb39307fe621
記録前observed_head: c54a6c24d81cbd09345e15f82dbbeb39307fe621
作成日時: 2026年11月15日 20:01 JST

## 判定
今回の停止判断とnative原証拠保全は受入可。今回確認した範囲に新規P1/P2なし。総合PARTIAL、native診断BLOCKED、根本原因UNKNOWN、製品受入FAIL、Draft維持・マージNOを支持する。COMMENTであり、製品のApproveではない。

## 直接確認した範囲
このチャットの先行レビューで、native原artifact14138296489を保存先から実再取得し、276,812 bytes、SHA-256 deb245c0ce28d2d4af5f6c67219d4bc84b1efc327013c8d5e25d188d738e2a56、42エントリCRC正常、内部manifest41件のサイズ・hash全一致を確認した。収録source25件は提出Git treeのblobと一致し、manifest対象の欠落・余分なし。
MI原票の小子への接続は ptrace: Operation not permitted. で失敗。接続・再開とも未成立、固定4枠はNOT_RUN。ソースのpreflight失敗時returnがブラウザworker生成より前にあることも確認した。小子SIGKILLはcleanup、GDB exit0もrenderer正常終了の証拠ではない。native stackとrenderer終了signalは未取得。workflow成功は収集・保存工程の成功としてのみ扱う。

## 正式CIと後続報告
先行レビューで正式PR run43654812726のfailure完了、browser acceptance工程の失敗、artifact生成をAPI/原ログで確認した。その時点のPR/legacy原ZIP未照合を未解決のまま最新状態に転記しない。
投稿前に同一HEADを再確認し、最終追補6886920261と独立監査5908284731を読んだ。そこでは正式PR/push各Chromium8PASS・WebKit8FAIL、正式PRと旧legacy原ZIPの保存後実再取得・別担当のbyte/SHA/CRC/manifest照合完了が記録され、PR本文にも反映済み。この報告更新の残件は解消済みと扱う。
https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/35#issuecomment-6886920261
https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/35#pullrequestreview-5908284731
正式PR/push/legacyの原ZIP全体を本投稿担当が改めて直接再監査したわけではない。後続2ZIPの完全性は既存独立監査記録の照合範囲。CI内にないsource実体を提出Gitから後作成した補足と、実行時捕捉を区別する。旧legacyの自動試行をnative4枠に加算しない。保存先のアクセス範囲・保持期限は未確認。

## 次工程
正規にsibling attachできる診断環境の選定、同じプロセス関係での有限な非ブラウザpreflight、次回の固定計画を先に扱う。Windows通常実行や異なるWebKitビルドを既存Linux診断の代用にしない。権限設定を緩和したり旧4枠を再実行したりせず、環境・計測方法の変更は別計画と事前独立レビューで区別する。製品修正、正式条件変更、公開、マージの根拠は今回得られていない。

## 記録追加の扱い
本ファイルだけを[skip ci]付きで追加する。reviewed_shaの実験結果を文書追加後HEADで実施した結果と扱わない。新しい診断実行の許可を意味しない。
