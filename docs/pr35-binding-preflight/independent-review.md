版: 1.0 / 作成日: 2026-11-15 JST / 基準HEAD: 640ce033963837ad0b96ba70830ad7bb4c0f8c2c / 内容SHA-256: manifest.sha256参照。

独立原票のbyteコピーはworkspace証拠内に別保存。このファイルは同原票へ版情報を付した文書。

# 独立レビュー最終: 保証Bの方式・環境成立性

担当: /root/binding_design_independent。主担当とは別agent/別プロセス。対象は6文書の修正後実bytes（hash台帳 independent-final-doc-observations.json）、raw一次review/環境原票、local640のsource帰属。backend実装・対象生成・GDB/browser/signal・テスト実行なし。独立原票をworkspaceへ新規保存したのみ。

## 文書審査判定

設計記録と不足条件の整理について限定的に受入可能。実装可能性は条件付き、認可済みLinux環境はBLOCKED、B実証UNKNOWN、実測承認なし。B0–5の全体保証や正常full identity受理を成立済みとは認定しない。文書の提出は未pushコードを含まないmain基準の文書差分に限る。正本取り込みNO・追加コードpush HOLD・Draft維持・製品FAIL・根本原因UNKNOWN・mergeNO。

## 初回指摘への対応

- P2-D1 閉鎖: 22 case IDをL19 slotとM4 slot(M0+06/19/20)へ分離。L1140秒/M20秒、合計1160秒。各系列正常対照失敗時の停止、manifest/予算/raw/台帳の分離、系列間転用禁止を実物で確認。13/14のlive安全審査未成立時はNOT_READYでありmodelで代替しない。
- P3-D2 閉鎖: B3は対象が実際に実行/mapする同一不変backingに限定。後作成immutable copyでは対応証明にならないと明示した。
- P3-D3 閉鎖: 04/07/08/09は元不変実体の正しいidentity PASS/0に期待を固定。環境不足は実行前NOT_READY、取得/権限拒否は別16/17/18入力で評価。実行後の都合のよい期待選択をしない。
- P3-D4 閉鎖: 生成時clone(CLONE_PIDFD)等、又は自分の子についてpidfd_open完了までreapしないkernel仕様条件を明示。不明なら拒否、数値PID事後取得へ置換しない。

## P1/P2/P3

新規文書P1なし、P2-D1は修正済み、未解決の文書P2/P3なし（確認範囲）。実装の継続P2は閉鎖しない: B/backendとLinux権限・mapping実体/byte不変性の成立未確認、固定7正常とStageA13FAIL等回帰未回復、指定Archive恒久保存BLOCKED。今回mkdir原票はerrno13/WinError5で文書と一致。workspaceを恒久保全へ昇格していない。

## 支持する保証と残る仮定

同一copyのSHA/build ID=Aと、task/exec世代/mapping/byte version=Bを分離。pidfd/FD/一件停止/caller booleanを十分条件にせず、全thread/event coverage、controller排他leaseと失効を要求する。外部writerやprivate memory/JIT/COWを未証明のまま含めない。GDB前Bゲートの循環をP0–P4の別authorityとして設計上整理したが、現640ゲートは不変更。C1は誕生時所有→制御、停止/実体参照/不変backingのすべてを条件とする候補。C2のnumeric PID attach窓はHOLD。正常受理の期待をBLOCKEDへ緩めず、早期gate拒否を故障検出としない。実入力binary/hash未生成のため計画NOT_READYとする判断は妥当。

Windowsのread-only inventory、WSL exe存在、SSH configなし、repo runner0、過去hosted EPERMの区別は原票と整合。認可Linuxの不存在を全世界へ一般化せず、現在調査範囲で未確保と記録する。Linux/GDB/ELF一次仕様と将来backendの証明義務の区別も妥当。

## 未実施と後続監査

この原票時点では最終commit/tree、追加されるreview/index/manifest、GitHub PR/受領・run/job、今回ZIP全体の独立照合は未実施。後続の別原票で確認する。旧ZIPや過去試験を今回再実行/再監査したとは認定しない。

2026-11-15T23:53:25.777621+09:00
