Stage B-Q / 版1.4 / 2026-11-17 JST / 基準HEAD1273d288fc30bce9e176f1a7e917d354ae650e13・tree1592f45dd641e59dc6f264d67019a6e39b22849f。別担当の新規独立静的原票をLF掲載。workspace raw実bytesは別保存、旧原票不変更。内容SHAはmanifest.sha256。

# Stage B-Q 判定recordの独立静的最終審査

担当 /root/stage_bq_independent。修正担当とは別agent/別プロセス。主担当の自己評価や旧reviewの受入を判定根拠にせず、AGENTS、基準1273d288fc30bce9e176f1a7e917d354ae650e13/tree1592f45dd641e59dc6f264d67019a6e39b22849f、関連基礎契約、Stage B-P、review5922091789原応答、新stage-bq-decision.md全文とREADME追記を実物から読取り審査した。

提案実bytesはindependent-final-proposed-source/、SHA台帳はindependent-final-proposed-source-ledger.jsonへ新規保存。基準20fileのGit実blobとbaseline copyは全byte一致。現在proposalの旧20fileはREADME全文prefix追記以外全byte不変、.github/prototype/AGENTSの差分0。原case/正常期待/失敗/未検証/1160秒/現640 gateを変えていない。最終manifestはまだ基準版なので、現proposalのmanifest合格とは認定しない。追加review掲載/最終commit/ZIP/GitHub/COMMENTは後続照合が必要。

backend/アプリ/原テスト/診断の実行、対象生成/制御、ptrace/GDB/browser/実proc/メモリ/実測、Linux接続/探索/構築、権限/設定/CI操作、repo編集/commit/push/投稿はこの担当から0。新規静的原票とGit/hash読取りのみ。

## 総合判断

**設計審査は、根拠と排除/保留理由を確定する範囲で限定完了可能。総合PARTIAL。backend実装開始NO/NOT_READY、実測開始NO/NOT_READY、どちらも未承認。一般的実現可能性UNKNOWN。** 文書の限定完了と方式実体の成立を分けており、未解決事項をPASSへ変えていない。

新規の未解決文書P1/P2/P3は確認範囲でなし。これはBP-U1–6や既存B/正常回帰/恒久保全の課題閉鎖ではない。完成方式としての採用YESは0、O-K第一候補/O-G・C2 HOLD/両PR Draft・mergeNOを維持する判断は妥当。

## BP-U1: 同値旧Bufferと候補排除

Q0はFD/OFD/read receipt/digest/proof値という観測集合がGood D/Bad Dで同じなら、その集合だけに依存する判定関数が識別できないという限定論理で不適格にしている。hash衝突を必要とせず、一般の全方式不可能とは結論していない。

Q1はentry/Buffer IDだけでは内部SHA/ELFが旧global/aliasを読む、新Xをreadして捨て旧Xで計算する反例を排除できないため、限定構成として不適格。入口をtrustedと命名するだけで成立しない。

Q2は同じ元Dのactual operand/read-write provenanceをSHA/ELF/proof sinkまで非迂回に観測する追加経路の仮説である。実出力依存を要求し、新payload readの存在や単純な過大近似taintタグだけは不足と明記。正当なcopyは新originとして扱いpointer一致を要求せず、旧originのrelabelを禁止する。全native/JIT/thread/syscall/crypto/ELF/初期メモリ・独立checker・実worldとの対応・通常権限・trace量/1160秒の実source証拠は未取得であり、仮説から採用可能へ昇格していない。

独立反例: Bad Dがnew Xをentryで読み捨て、old Xで出力を計算しても『newを読んだ』traceは存在する。recordはそのactual出力依存を必要とするため、この弱いmonitorをQ2完成方式として成功にできない。逆に元Dの命令を計算serviceの正しい値で置換するとQ4であり、同じDを検査する境界を失う。unsupported pathの無視/TCBへのbug移転も不採用としている。

[Valgrind core公式](https://valgrind.org/docs/manual/manual-core.html)と[tool API公式](https://valgrind.org/docs/manual/manual-writing-tools.html)を独立読取りし、synthetic CPU/instrumentationと個別tool実装の一般機構の根拠に留める書き方を確認した。特定toolがB_useを観測できる証拠、installed/authorized/measured、正常再現性や時間成立の証拠ではない。今回導入/実行なし。

Q3は全D経路の因果/dataflow証明、実artifact/runtimeへのprovenance保持refinementが未立証UNKNOWN。source hash/functional correctnessだけでcompiler/JITの同値旧値再利用を除外できないため、sourceの証明をmachine実使用へ自動継承しない。Dの不具合を証明前提で除外しDを無条件trusted化する解決も禁止している。

Q4の外部trusted計算/KへのD追跡移転/B_value弱化は、元Dの保証B要件を維持しないので不適格。Q0/Q1/Q4を排除し、Q2仮説/Q3未立証を保留する決定は、現証拠から言える範囲に限定されている。

## BP-U2: TCBとD scope

S所有、K唯一ptracer/実kernel object取得、O独立比較、D追跡/lease/derivation/proof、I注入/A監査を再評価し、実source/build/hash/依存/IPC/lane/改変経路の証拠がないためUNKNOWNとしている。KにD更新を代作させ、それをDの正しさとして採用する反例、OがD parser/labelを期待源にする反例、Dを名前だけtrustedへ移す反例を不適格にしている。Q2がTCBを拡大しても、Dの本来の不具合を検査対象から消してはならないという条件を保持する。

## BP-U3/U4/U5/U6

U3は既存のinstalled/callable/authorized=UNKNOWN、measured=NOT_TESTED台帳を維持。API/過去hosted/Windowsの存在を実Linux適格性へ変えず、認可host/ABI/通常権限/sole tracer/event/全停止/実object/FD交付/不変backing/source依存の一式が不足して安全上BLOCKED。

U4はK死亡kernel挙動、auto-resume、孤児化、Sの合法wait/adoption/reap、実status、D/K同instance、FD/IPC/task/残存/保存/有限時間を別に必要とする。pidfd/要求ack/watchdog returnをcleanup完了としない。EXITKILL/subreaperは未承認候補で実施0、安全上BLOCKED/NOT_READYが妥当。

U5は既存23slot入力台帳を参照して各slotへ開始NO理由だけを加え、source/fixture/hash/ID/object/M/T/ackは未生成UNKNOWNのまま。L19/M4各1回・原順・正常PASS/0・L60秒/M5秒・1160秒・追加0を保持。Q2のtrace又はQ3確認を入れても上限を変えず、時間/量/終了回収根拠なしならNOT_READY。常時拒否を正常対照成功にしない。

U6はArchive過去拒否/Vault実保存UNKNOWN/Library・Space未承認を保持。旧469215byte ZIPの監査原票は参照証拠に留め、今回の新ZIP/恒久保全へ転用しない。workspace実物読戻しと恒久保全を分け、独立実物未取得はPENDINGとする。新ZIPはこの原票時点で未取得・未監査。

## 独立判定と次の最小工程

- 設計審査の完了可否: YES、上記限定範囲。
- backend実装開始: NO、NOT_READY/未承認。方式一般の可能性UNKNOWNを、現在開始してよいUNKNOWNと混同しない。
- 実測開始: NO、同じ未成立条件と実行承認なし。

次はQ2又はQ3の一候補について、登録可能な既存実source/version/独立仕様/観測又は証明chainを資料として提示できるかの審査だけ。実体がなければ現NOを維持し、同じ一般条件の文書反復や未承認開発/試行でPASSを作らない。この最小工程はユーザーの『文書を増やすことが目的ではない』という範囲とも整合する。

native BLOCKED/ABA HOLD/B UNKNOWN/WebKit根本原因UNKNOWN/製品FAIL/追加コードpush HOLD/両PR Draft・mergeNO。最終Git/manifest/新ZIP/投稿読戻しの監査は後続別原票へ。

2026年11月17日 05:36 JST
