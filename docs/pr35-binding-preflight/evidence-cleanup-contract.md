版1.2 / 2026-11-16 JST / 文書基準HEAD 134c5133d0d04892ec0f0ff0e9d2ee50fedb2f98、tree aea16bc285391a21c68934f02c143cb18de30b86。現640ゲート不変更。内容SHAはmanifest.sha256。設計案と必要条件であり、実装・生成・実測の許可/証拠ではない。

# 証拠・保存・復帰/cleanupの責任契約

## 保存対象と型付き原票

K/O/D/I/S/Aごとの独立laneを持ち、原byte列にproducer、run/case/phase、source HEAD/tree/Git blob/実file SHA、UTC+単調時計/seq、channel、取得byte数とSHA、原票参照を付ける。kernel wait/ptrace/proc原結果、O独立ack、D event/proof、I intent/return、原入力/source/期待manifest、stdout/stderr、exit/timeout/close/残存を別票にする。説明/集約は派生票で、原応答を整形置換しない。

artifact stateはPLANNED / NOT_GENERATED / GENERATED_PARTIAL / GENERATED_COMPLETE / UNAVAILABLE。予定path/hashは未生成ならnull、reason付き。保存の完了、独立検証の完了、意味上の成功は別status。各streamのobserved/retained/discarded bytes、cap/truncated、原byteのoffset/順序を保持。出力上限/書込例外でも保存済み原票は残し、completion=BLOCKED。cleanup SIGKILLとrenderer signal、debugger exit0と対象exitを別fieldとする。

今回のK/O/D原票、対象binary/fixture、ack/proof実物はNOT_GENERATED。生成済みは設計文書・取得したGitHub API/参照・独立静的レビュー・静的hash照合だけ。過去実行票やZIPを新版実証へ継承しない。

## 責任表（将来契約、今回は操作0）

|項目|責任主体/根拠|独立に記録するstatus|
|---|---|---|
|所有登録/停止要求|S/K、出生台帳と保持task handle。対象task/threadだけ|NOT_REQUESTED / REQUESTED / ACKED / FAILED / UNKNOWN|
|対象の実終了|S/Kのkernel wait termination、task参照終端をOが原票照合|ALIVE / EXITED(code又はsignal/core情報) / UNKNOWN。要求ackを終了へ転用しない|
|controller/K終了|Sが所有する各childの別termination票|D_EXIT/K_EXITを対象のexitと混ぜない|
|FD close|FDを取得したO/K/Dそれぞれ、handle台帳とclose syscall結果|NOT_ATTEMPTED / PENDING / CONFIRMED / FAILED。遅延結果を別eventで追記|
|資源解放|SがcaseごとのFD/IPC/owned process registryを照合|残数と不明資源を列挙。closeだけで全解放としない|
|残存task|SとOがowned lifetime参照から確認|NONE_CONFIRMED / OWNED_REMAINING / UNKNOWN、PID番号再検索だけ不可|
|保存完了|writerとA、原票exclusive create/flush/manifest実物読戻し|PARTIAL / COMPLETE / FAILED / UNKNOWN。process終了と別|
|lease復帰/再開|Kのcommand排他。再開前にD旧lease破棄とOの対応seqを記録|旧proof再利用0。切断時の無条件自動resumeは禁止|

case終了は上記各statusの積。要求成功だけ、D終了だけ、FD閉だけで正常終了としない。将来の計画済み通常終了はlease失効→許可済みresume/normal exit→対象終了確認→controller終了→全FD/資源/残存/保存確認。制御喪失時は旧lease即失効、以後診断なし。操作権限・復帰手段が不明なら勝手にresume/killせずBLOCKEDと責任者へ引継ぎ、残存UNKNOWNを残す。

将来のTERM→2秒→必要時KILLは、別承認されたS所有childだけ・slot期限内という条件付き案。今回その許可を与えない。未所有/任意PID、全プロセスkillは禁止。所有確認不能なら対象操作を止める。残存/close/保存が不明なら実行完了をPASSにしない。有限cleanupを示せないhost/backendは実行前NOT_READY。

## 保管先の役割と現在値

|保管先|指定/確認範囲|今回判定|
|---|---|---|
|案件workspace|本依頼が文書保存を許可。専用pr36-oracle-spec-evidence-20261116T1940JSTへ新規保存|一時保全。恒久保全へ昇格しない|
|C:\Users\tetsu\Dev-Artifact-Archive|正式成果物の通常保存先。過去の専用mkdirはerrno13/WinError5で拒否という原票を維持|過去BLOCKEDを継続、今回再試行/ACL変更/迂回なし。現在書込可能とはしない|
|C:\Users\tetsu\Hachibei-Evidence-Vault|本依頼で指定された承認証拠保管先。保存すべき承認原票の役割は指定済み|存在/アクセス/書込/retention/独立再取得はUNKNOWN・未実施。Archiveの正式成果物を無断でこちらへ振り替えない|

Vaultの名称指定は書込成功・恒久保全完了の証拠ではない。承認原票の保存範囲と通常成果物の代替許可は別。いずれも新規案件directory/exclusive create、既存証拠の移動/削除/名称変更/上書き禁止。恒久保存不能のままならBLOCKED。保存先の権限変更や別経路回避はしない。

## ZIP/読戻しの受入条件

原入力/source/raw/全attempt/未到達理由/cleanupをexact manifest（path/size/SHA）へ固定し、ZIP内名重複/余剰/欠落0、各entry CRCとbyte実物を記録。manifest自身は自己hashを除外し外側SHAで包む。sourceはGit blob rawと実fileを全byte照合し、改行差も区別。新ZIPは新pathへ一度作成、旧ZIPを更新しない。

保存した実物ZIPを別保存先へ新規取得し、全byte・size・SHA・全entry CRC・manifest exact set・全source帰属を別プロセスと独立担当が再計算する。提出受領は生成時刻が後なので別immutable追補へ保存。未取得ZIPを独立監査PASSにしない。今回もし文書ZIPを作る場合もdesign-onlyのscopeを付け、実測rawを含むと表示しない。workspace読戻し成功でもArchive/Vaultへの恒久保存と区別する。

## Tracer喪失時のkernel作用とphase継続

Kの死亡/切断はproof失効だけで物理的停止を保証しない。auto-detach/resumeを含むkernel動作を事前固定し、出生所有が保証された対象だけに適用する承認済みの死亡時終了/復帰policyがなければ開始不可。PTRACE_O_EXITKILL等は未承認の設計候補に留める。K死亡→target死亡と仮定せずS/Oの独立termination原票と残存確認が必要。policy発動で対象を終了した場合もrendererの自然終了signalや故障原因へ転用しない。

Rのreturn1、新proofのreturn0は同じ生存D/Kに対するphase別consumer結果であり、Dをexit1させて再起動してよい意味ではない。D/Kの途中終了、FD転送/比較失敗、state lineage欠落を別原票へ残してFAIL/BLOCKED、同slotの再試行や別instance正常受理で上書きしない。

Sのwait権限も別条件である。O-KではKがtargetの親なので、K死亡後にSが当然waitできるとはしない。参照候補は、既に認可され検証済みのS subreaper/adoption経路等により、所有targetがSへ継承されkernel終了statusを回収できる構成。parent/adoption/reap順と全owned対象の帰属を事前固定する。pidfd保有/pollによる寿命終端だけをwaitid exit情報取得権へ昇格しない。ECHILD/終了status欠落は終了情報UNKNOWN・cleanup BLOCKED、開始前にこの経路が未成立ならNOT_READY。新たなsubreaper設定は本工程では実施/承認しない。
