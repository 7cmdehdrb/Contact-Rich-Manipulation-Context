# 2026-11-10 Finger model3550 OSC action 실측

사용자가 빠른 움직임의 원인이 지나치게 큰 OSC action인지 확인하도록 요청했다. 지정 체크포인트를 실제 GPU PhysX에서 재생하여 정책 출력, 처리된 명령, OSC 목표 pose, EEF 속도, 관절 토크와 포화를 수집했다. **큰 상대 목표가 실제로 출력되고 적용된다.** 학습 환경이나 제어 설정을 수정하는 작업은 수행하지 않았다.

## 재현과 보존 범위

- 대상: `Inspire-Sweep-Simple-Finger-v0`, `logs/TEMP/inspire_sweep_simple_finger_v0/2026-11-10_14-30-35/model_3550.pt`, iteration3550.
- SHA256: `b64d17711f4c3d797e69e1529e46fe4dea79bdcc1ae0b12e5d6ba9e8e2b59642`. 실행 전후 동일함을 assert했다.
- Seed42, 16환경, 3,000 policy step, 환경당60초 시뮬레이션, 정책 샘플48,000개, 물리 샘플96,000개, 완료96에피소드. 마지막 부분 에피소드도 step 통계에 포함한다.
- 기존 `scripts/play.py`를 메모리에서 실행한다. export를 생략하고 `log_dir`만 outputs로 돌렸다. runtime action term의 원래 `process_actions`/`apply_actions` 호출 뒤 값을 복사했다. 제어 입력이나 연산은 변경하지 않았다. Headless 실행이며 영상 관찰은 하지 않았다.
- 정책 결정적 출력을 사용한다. 학습의 Gaussian 무작위 샘플링 결과가 아니다. play 기본과 같이 관측 노이즈는 환경 설정을 유지했다.
- 학습 당시 저장된 `params/env.yaml`과 실측 `env.yaml`의 actions/observations/rewards/terminations/curriculum/decimation이 모두 같고 physics dt도0.01로 같음을 비교했다.
- `logs/rsl_rl`, 체크포인트, 기존 사용자 변경과 서브모듈 커밋은 변경하지 않았다. 새 조사 도구와 산출물은 outputs 안에만 추가했고 이 개발 로그를 작성했다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/action_diagnostics/finger_3550/run_probe.py --task Inspire-Sweep-Simple-Finger-v0 --checkpoint logs/TEMP/inspire_sweep_simple_finger_v0/2026-11-10_14-30-35/model_3550.pt --num_envs 16 --seed 42 --max_steps 3000 --headless --kit_args=--/app/vulkan=false
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/action_diagnostics/finger_3550/analyze.py
```

## 정책 raw action 범위

첫6채널이 팔, 뒤6채널은 손가락 절대 관절 목표다. 아래는 팔만 집계했다. 축은 매 policy step에 고정되는 현재 EEF 좌표축이다.

| 축 | 최소 | 최대 | 절댓값 P95 | 절댓값1 초과 |
| --- | ---: | ---: | ---: | ---: |
| X | -194.283 | 14.089 | 0.845 | 4.49% |
| Y | -4.608 | 158.012 | 1.077 | 6.20% |
| Z | -9.990 | 197.500 | 0.957 | 4.62% |
| Roll | -14.761 | 509.848 | 5.000 | 98.75% |
| Pitch | -311.688 | 9.319 | 1.300 | 10.69% |
| Yaw | -3.094 | 367.848 | 2.168 | 21.61% |

±1は現在コードで定義された有効範囲ではなく、比較用目安。NaN/Infは全12 actionで0個。有限値でも過大な目標は発生している。

## 実際のOSC命令と速度

位置はraw×0.03m、回転はraw×0.15radのRPYをQuaternion経由でaxis-angleへ変換する。50Hz、physics100Hz。現在EEFを基準とする相対pose目標であり、速度命令でも1stepで必ず達成される変位でもない。

| 指標 | 中央値 | P95 | P99 | 最大 |
| --- | ---: | ---: | ---: | ---: |
| 相対位置目標ノルム | 1.506cm | 4.913cm | 27.971cm | 956.807cm |
| 相対回転目標角度 | 33.81度 | 46.97度 | 68.32度 | 162.06度 |
| 実際EEF並進速力 | 0.00942m/s | 0.21596m/s | 1.03542m/s | 3.35253m/s |

相対位置目標が3cmを超えたのは13.81%。並進いずれかのraw軸が±1を超えたのは9.31%。位置スケールとの全数一致、OSC desired poseと同step現在poseの距離が処理後並進ノルムと一致することを確認した。大きなrawが途中で抑えられているわけではない。

最大の例は全体policy step8、env15、episode step8で、raw=`[-194.2829,158.0116,197.5004,509.8475,-311.6881,367.8477]`。並進目標はEEFから`[-5.8285,4.7403,5.9250]m`、ノルム9.5681m。回転は変換後axis-angle=`[-1.1433,-1.7683,0.7211]rad`。同policy stepの2物理サンプルの実際速力は1.0203/1.1536m/s。RPY raw×scaleの巨大な角度を、そのまま実際の回転回数と解釈してはいけない。

初回エピソードだけの異常ではない。各環境の初回エピソードを除いた40,486サンプルでも、相対位置目標の最大7.5973m、P99 27.673cm、P95 4.917cmだった。

## 高速区間

| エピソード内時刻 | 相対位置目標中央値 | 実際速力中央値 | 実際速力P95 |
| --- | ---: | ---: | ---: |
| 0–0.1秒 | 32.73cm | 0.899m/s | 1.510m/s |
| 0.1–0.2秒 | 23.13cm | 1.080m/s | 1.477m/s |
| 0.2–0.5秒 | 9.57cm | 0.397m/s | 0.943m/s |
| 0.5–1秒 | 3.13cm | 0.090m/s | 0.233m/s |
| 1–2秒 | 2.64cm | 0.025m/s | 0.181m/s |
| 2–5秒 | 1.43cm | 0.010m/s | 0.041m/s |
| 5–10秒 | 1.42cm | 0.007m/s | 0.016m/s |

0.5秒未満全体では位置目標中央値14.49cm、実際速力中央値0.588m/s。0.5秒以降では位置目標中央値1.479cm、実際速力中央値0.00904m/s。速力0.5m/s超のサンプルの99.963%が最初0.5秒にある。リセット前後の位置差分を速度に換算しておらず、OSCが計算するlink-origin+offsetのEEF速度を使う。

いずれかの関節トルクが飽和した物理サンプルは0.07292%。常時のトルク飽和ではない。各関節絶対トルク最大は150/150/150/28/28/3.213Nm、絶対関節速度最大3.407rad/s。

## コード確認と解釈

`mdp/actions/sweep_simple.py`はposition_scale0.03、orientation_scale0.15、固定剛性100/50、減衰比1、effort_limit_scale1を設定する。`WrenchRefactorOSCAction`は現在EEFをtask frameとして固定し、`UR10OperationalSpaceControllerAction`とIsaac Labの親実装でscaleとRPY変換を行う。actionのclamp/tanhはない。runnerのclip_actionsもnull。観測`previous_action_command`のtanhはLast Action観測だけを圧縮し、実行actionには作用しない。Gaussianの決定的出力もMLP出力をそのまま返す。

action-rate罰則は前stepからの変化量で、action絶対値の上限を保証しない。手の6関節はURDF限界へclampするが、腕のOSC相対poseは同様には制限しない。

**ユーザーの疑いである過大actionを実測で確認した。** 特に開始直後は外れ値を除いても数十cmの相対目標を連続更新しており、速い動作との時間的一致がある。ただし固定剛性や接触、入力状態、学習原因の寄与率は介入比較していない。今回の結果だけで過大actionが唯一の原因とは断定しない。次に変更する場合は位置・回転それぞれの目標上限とスケールを明示し、再生時だけclipする対応は学習時との契約変更として扱う。

## 成果物・検証・未検証

- [実行ハーネス](../../../../outputs/action_diagnostics/finger_3550/run_probe.py)、[集計処理](../../../../outputs/action_diagnostics/finger_3550/analyze.py)、[実行metadata](../../../../outputs/action_diagnostics/finger_3550/metadata.json)。
- [生トレース](../../../../outputs/action_diagnostics/finger_3550/trace.npz)、[集計JSON](../../../../outputs/action_diagnostics/finger_3550/summary.json)、[軸別CSV](../../../../outputs/action_diagnostics/finger_3550/axis_ranges.csv)、[時間別CSV](../../../../outputs/action_diagnostics/finger_3550/episode_time_profile.csv)。
- 実際playハーネス終了コード0、3,000step完了。両調査スクリプトpy_compile成功。チェックポイントhash一致。スケールおよびdesired pose距離の全数照合成功。学習保存設定の上記6セクションとdtが一致。
- 未検証: 別seed・他チェックポイント、視覚的な再生観察、学習ノイズの無い環境、修正後挙動、実機。安全な許容速度やaction値の仕様は今回定義していない。
