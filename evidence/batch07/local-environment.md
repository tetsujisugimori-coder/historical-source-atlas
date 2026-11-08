# ローカル試験環境の履歴

npm初回試行は既定cache /home/agent/.npm への書込みがEROFSで失敗。インストール先は /tmp/atlas07-pw、cacheを許可済み/tmp/atlas07-npm-cacheに指定した再試行は成功。Playwright1.56.1（CIと同版）。OS設定変更は行わない。
途中単体:35 methods、5413 method/subtest records、2 CLI commands PASS。dirty tree実行なので最終HEAD CIとは別証拠。
ブラウザ実行結果はlocal-browser/results.jsonと起動失敗原文に記録。実機Safari・物理入力はNOT_TESTED。

初回ブラウザ:新章・新年度のselect optionが不足しChromium2幅とも新章選択でtimeout、失敗画像・JSONをlocal-browserに保存。年1439と対象章optionを追加し同じ試験を再実行。
修正後:Chromium390/1280は成功。WebKitは必要共有ライブラリ不足で起動失敗、ローカルはNOT_TESTED（全体runner exit1）。失敗・未実施をPASSへ変更しない。CIは従来のinstall --with-depsを実行する。
Git CLI pushは認証入力端末なし（could not read Username / No such device or address）で失敗。AGENTS.mdの正規GitHub連携APIを使用し、同一treeを照合する。認証設定変更・秘密取得はしない。

独立目視P2:対象年KPIの1436–1438を1436–1439に訂正。独立担当が最小2行patch（表示＋KPIassert）を提案し、主担当が適用。独立RED/GREENは同じ155-check runner、旧2幅FAIL/新2幅155checks PASS、WebKit未実施で全体exit1。原画像は提出ZIP、hashと詳細はkpi-red-green.json。
原画像blobの自動承認審査が期限切れとなったため、追加画像のGitHub保存を停止。全原画像/JSONを上記ZIPとしてSpaceへ保存し、GitHubにmanifestとログを残す。既存第6便以前の証拠は一切削除しない。正式CIはGitHub Actions原ZIPを別途保存する。
