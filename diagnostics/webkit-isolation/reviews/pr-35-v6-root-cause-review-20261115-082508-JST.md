# 診断v6 根本原因レビュー
対象PR: https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/35
reviewed_sha: 187810113b4e02de5cd465fb53f6f43cc3d04576
reviewed_tree: 72ea76f78359172fbb9eead1b4b6cfba51495b88
記録前HEAD: 187810113b4e02de5cd465fb53f6f43cc3d04576
作成日時: 2026年11月15日 08:25 JST

## 判定
診断v6の限定PASSは妥当。今回確認した範囲で新規のP1/P2指摘なし。総合PARTIAL・根本原因UNKNOWN・製品受入FAIL・マージNOを支持する。PRはopen/Draft/未マージ。正式COMMENTとして記録し、Approveやマージ承認とは扱わない。
判断基準は、比較実験の成立と原因の特定を分けることである。

## 直接確認した範囲
対象HEAD、v5提出HEADからの6ファイル差分、診断計画・コード・検査コード・workflow、CI情報、既存独立レビューを確認した。診断原ZIPと後作成補足ZIPをLibraryから実再取得し、SHA-256・全CRC・内部manifestを独自照合した。診断原ZIPは74 CRC/manifest73、補足ZIPは68 CRC/manifest67で一致。取得済みGit原文4ファイルと原ZIP内sourceのGit blob hashも一致した。
診断原ZIP: 382891 bytes、SHA256 cb45c7cd553c0ddbbd9f2d35d129b9e884ea825d03db75172ccc498184c4a46a。
後作成補足ZIP: 561426 bytes、SHA256 6b69026f88dfeba5d8a12cca547bb0caaa5528079d18799dc515857b3e41dec8。
正式PR/pushと旧legacyの原ZIP全体は本レビューでは再監査せず、既存監査記録とCI情報を照合した。新規のブラウザ実行・38単体検査の再実行・Windows読戻しは行っていない。

## 評価
- 比較は成立。57バイトのみの削除と全byte完全復元、固定8入力一致、全8枠の先行20操作完了を原票から確認した。WebKit全6件で目的reload開始後に同署名assertionが記録され、reload未完了・post-state未取得。Chromium全2件はreloadとpost-state取得まで完了した。
- 支持されるのは「指定呼出しは、この固定経路での同署名再現に必須ではない」まで。別のscrollIntoView呼出しは残っている。スクロール全般の無関係、各クラッシュの根因同一性、WebKit本体・driver・Playwrightの責任層は立証されていない。
- 診断収集成功と製品受入成功を区別している。正式PR/push各Chromium8 PASS/WebKit8 FAILを保持し、Pages upload/deployはSKIPPED。製品修正・公開なし。
- 後作成source補足を実行時捕捉と読み替えていない。Libraryアクセス範囲・保持期限はUNKNOWN、Windows未移管という限界を保持する。

## 次工程
独立したnative stack診断を推奨する。原記録ではGDB未導入である。まずデバッガの利用・接続可否と、同じWebKit buildに対応するデバッグ情報の入手可否を確認する。
試行数と停止条件を実行前に固定し、(1)落ちたプロセスの識別、(2)停止時のsignalと実際の終了情報の区別、(3)呼出し履歴と実行物の対応確認を目標とする。デバッガの動作タイミングへの影響は別に記録する。取得不能なら不足理由を残し、raw stackや同署名だけで原因を確定しない。
v6の一因子比較とは別工程とし、製品コード・正式条件・期待値・timeout・既存guard・Pages・旧証拠を保護する。

## 参照
最終報告: https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/35#issuecomment-6885351512
実装時独立レビュー: https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/35#pullrequestreview-5907550024

## 記録commitの扱い
本書だけを診断用の許可領域へ追加する。完了済みv6固定8試行の意図しない再実行を避けるため、この文書commitは[skip ci]付きとする。workflow・guard・正式受入条件は変更しない。submission_headはreviewed_shaと異なる文書追加版で、新HEADのCI未実行をPASSに読み替えない。Draft解除・マージ・auto-merge・ブランチ削除・main更新は行わない。

2026年11月15日 08:25 JST
