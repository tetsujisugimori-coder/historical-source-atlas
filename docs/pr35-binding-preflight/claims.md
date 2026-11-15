版: 1.0 / 作成日: 2026-11-15 JST / 審査基準: 640ce033963837ad0b96ba70830ad7bb4c0f8c2c (tree ee292d4f42fef239ff8ab6dca6d51d08299b51e3)。内容SHA-256は manifest.sha256 を参照。これは設計審査であり実装・実測承認ではない。

# AとBの主張・観測・拒否契約

Aは一回取得したprivate bytesからSHAとELF GNU build IDを導出する性質。FD保持もAも、対象task・exec世代・実mappingへの帰属を証明しない。build IDはファイル全体のchecksumではない。

Bは以下の積。いずれかUNKNOWNならfull identity受理・診断開始はBLOCKED。`sameIdentity` のschema/値一致やcallerの `stopped/proven` は証明主体でない。以下は新backendに要求する設計契約であり、640の現ゲートは解除しない。

|主張|必要観測・観測主体|根拠/競合窓|失敗時の拒否・証明できない事項|
|---|---|---|---|
|B0 task同一性/PID再利用排除|所有を登録したsupervisorが生成時からkernel task参照、namespace/boot識別、PID/TID/PPID/startTicksと終了イベントを保持。controllerは同じtaskへの制御取得を裏付ける|pidfdはtask寿命の補強。数値PID取得→別途attach間の再利用窓は残る。生成から追跡する候補のみ条件付き|TASK_UNBOUND/EXITED。pidfd単独でexec世代やattach対象を証明しない|
|B1 executable対応|controllerの検証済み全thread停止lease内に、kernelの対象exe参照を一回openしFD保持。取得元task/epoch/FD objectと固定copyを結ぶ|proc exeは対象実行物をopenするが、停止・exec排除が別途必要。realpath先を再openしない|EXEC_BINDING_UNKNOWN。FD取得前後のstat一致だけでは不足|
|B2 各libraryと実mapping|同lease内に全必要mappingのrange/offset/protection/dev/inode等を列挙し、各kernel mapping-backed object参照をopen、FDとcopyを結ぶ。全mappingのcoverage台帳を作る|maps pathnameはラベル。map_files等の正規アクセス必要。thread停止外の外部操作/共有mappingも別途評価|MAPPING_UNBOUND/COVERAGE_INCOMPLETE。同path・同build IDは実体証明でない|
|B3 copyとfileのbyte version|取得主体が対象の実行/map先そのものである同一不変backingのkernel保証・適用範囲を記録してからread。後作成のimmutable copy/snapshot単独では対象との対応にならない。seal/既存の検証済みimmutable snapshot等、全writerを排除する根拠を要す|FDはobjectを保持しても内容不変でない。対象停止は外部writerを止めない。stat反復は対処にならない|BYTE_VERSION_UNKNOWN。一般のread-only open/permissions/checksum一致をimmutabilityとしない|
|B4 exec/thread/dlopen/dlclose/remap排除区間|exclusive controllerが全thread・生成/exec/exitイベントを追跡し、全停止完了から取得/利用完了までresume禁止。未追跡thread、非leader exec、複数inferiorを扱う|一件のMI停止通知では不足。GDB仕様・kernelイベントとbackend状態機械の整合を後工程で検証|STOP_INCOMPLETE/EVENT_GAP/EXEC_EPOCH_CHANGED。対象外の共有メモリwriter等は保証しない|
|B5 利用期間と失効|controller発行epoch/lease ID、単調時刻、sequence、全thread集合、FD一覧、取得source/終了状態、失効イベントを原票に保持。consumerは生存leaseを直接照合|有効開始はB0–4完了、終了は最初の失効。過去の証明と現在の利用権を分ける|LEASE_REVOKED/CONTROLLER_LOST。caller発行boolean・保存JSON再利用は禁止|

Bのscopeは「停止epoch中の対象に対応するfile objectと不変byte version」。relocation、private COW、JIT、anonymous mapping、実メモリ内容の同一性は別主張。必要library範囲を定義できない、file-backedでない必要領域がある、別taskからmappingが変えられる等ならfull coverageはUNKNOWN。ファイル識別だけで実メモリを認定しない。

resume/step/inferior call、exec、thread membership変化、dlopen/dlclose/remap/unmap、exit、切断、unknownイベント、FD/close失敗、外部書込み可能性の発覚は直ちにlease失効。通知遅延を安全とみなさないためconsumerはcontroller排他区間内でのみ利用する。再開後のsignal/stackへ過去leaseを自動流用しない。新epochの再審査が必要で、今回は承認しない。close確認不能なら完了票はBLOCKEDのまま。
