# Sweep 세 체크포인트의 영역별 Timeline 평가

## 요청·의도

사용자가 지정한 2026-11-23 TEMP 폴더의 최신 학습 run·체크포인트 세 개에 대해 병렬 환경에서 데이터를 수집하고, 영역1~4별 0~10초 평균 보상, 양의 밀기 보상 지급 구간의 힘 방향 일치도, Contact와 F/T 신호의 Timeline을 작성했다. 기준은 이전 답변에서 확정한 세 파일이며, 평가 도중 더 높은 iteration 파일로 자동 교체하지 않았다.

| 환경 | run | checkpoint |
| --- | --- | --- |
| Inspire-Sweep-v0 | 2026-11-22_17-07-15 | model_20900.pt |
| Inspire-Sweep-Single-Contact-v0 | 2026-11-22_17-14-33 | model_15550.pt |
| Inspire-Sweep-Single-Contact-v1 | 2026-11-22_17-15-01 | model_10950.pt |

## 변경 전후와 영향

이전에는 공통 보상 Timeline probe와 접촉 정책 분석기가 있었지만, 이 세 체크포인트를 대상으로 실제 정책 촉각·F/T와 원시 물리 신호를 함께 기록하는 영역별 보고서는 없었다.

- [수집 스크립트](../../../../src/inspire_sweep_baseline/scripts/collect_sweep_region_timelines.py)를 추가했다. 등록된 Gym 환경과 기존 runner·정책을 사용한다. 원래 RewardManager.compute 호출 후, 자동 reset 전에 `_step_reward × dt`와 total을 복사한다. 원래 contact.capture를 정확히 한 번 호출한 뒤 물리 substep별 법선 하중과 법선 합력을 복사한다. 기존 `_surface_loads`의 반환값도 원래 계산 후 복사한다.
- 물리 접촉력은 타겟에 작용한 손의 법선+마찰 합력이며, 두 물리 substep을 평균했다. 촉각은 기존 observation term의 noise 적용 전 범주와 실제 반환된 policy observation을 따로 보존했다. 물리 F/T는 기존 보상 term과 같은 보상된 EEF 측정 sample을 읽고, 정책 F/T는 실제 noise·clip·scale 적용 후 값을 읽었다. 별도 noise 재추출이나 observation-manager 재계산은 하지 않는다.
- [보고서 재계산 스크립트](../../../../src/inspire_sweep_baseline/scripts/report_sweep_region_timelines.py)를 추가했다. 새 환경이나 학습 코드는 추가하지 않았다. 총 24개 과학 그래프와 요약 CSV 5개, 검증 JSON을 [자산 폴더](../../03_assets/sweep_region_timelines_2026-11-23)에 저장했다.
- 환경·보상·종료·관측·제어·등록·PPO 소스는 수정하지 않았다. 학습 로그와 체크포인트는 읽기만 했다. 평가 시 환경 수·seed·log_dir와 PhysX aggregate-pair capacity(2²⁵→2²¹)만 설정했다. capacity 축소는 12GB GPU 메모리 사용량을 위한 것이다.
- 기존 IsaacLab submodule의 사용자 untracked 파일 `2.7.0+cu128`은 보존했다. 루트 기준 HEAD는 `b705a505fe11ec9e85db66c4f29b47314d1178ae`, 문서 저장소 시작 HEAD는 `dda40165854ee7a78dbc01fe69f26a2d3223df66`이다. 커밋·submodule 포인터 변경은 하지 않았다.

## 수집 범위와 평균의 정의

RTX4070, env_isaaclab Python, headless에서 각 체크포인트를 시드42·43, 각256환경·500정책step으로 실행했다. 체크포인트 내부의 환경들은 병렬, 체크포인트·시드는 GPU 메모리를 고려해 순차 실행했다. 소규모 v1 8환경·8step smoke도 선행했다.

6회 본 실행의 초기 episode는 총1,536개다. 초기 episode만 분석하며 reset 이후 다른 episode는 제외했다. 영역별 표본 수는 정책마다 동일하게 87·171·80·174개다. 보상은 조기 종료 후0을 넣어 초기 cohort를 고정하고, 센서는 종료 후 값을 결측으로 처리하여 생존 episode만 평균했다. terminal 물리·보상 sample은 포함하고, 자동 reset된 terminal 정책 관측은 제외했다.

0.2초 구간 평균으로 그래프를 작성했다. 보상 단위는 weight·dt가 적용된 정책 step당 기여값이다. 범주형 촉각 숫자를 직접 평균하지 않고 면별 활성 채널 수와 채널별 활성 확률을 사용했다. F/T N·Nm은 분리했고, 힘·모멘트 노름은 표본별로 계산한 후 평균했다.

양의 Sweep 지급 step에서 현재 타겟→목표 XY와 접촉력 XY 사이 각도를 계산했다. v1은 θ<30°에서만 양수가 되는 보상식이므로, 이 조건의 선택 편향을 보고서 본문에 설명하고 전체 타겟 접촉(수평 합력≥1N)의 분포도 함께 보존했다.

## 결과와 최종 대조

완성된 결과는 [영역별 실측 보고서](../experiments/2026-11-23_sweep_region_timelines.md)가 기준이다.

- 전체 성공률: Sweep v0 355/512=69.3%, Single Contact v0 392/512=76.6%, v1 247/512=48.2%.
- 영역3 성공률: 2.5%·13.8%·32.5%. 영역4: 80.5%·81.6%·3.4%.
- v1 영역4는 양의 Sweep 누적 보상 평균0.188, 전체 유효 타겟 접촉 평균 방향 오차85.54°였다.
- 모든 정책·시드의 초기 robot joint·물체 state·목표·방향·bounds·활성 물체 hash가 일치했다. 동일한 초기 물리 장면 비교다.
- 학습 당시 `params/env.yaml`과 현재 평가 설정의 Action·Reward·Observation·Command·Termination·Event·Curriculum, episode 길이·decimation·목표 반경·F/T 제한값을 안전한 YAML BaseLoader로 읽어 대조했고 모두 같았다.
- RewardManager total과 보상항 합의 최대 절대 차이는2.3842e-7이었다. v1의 Sweep·Reaching은 내부 저장 구성요소로 별도 재계산해 실제 지급값과 대조했다.
- 초기 episode의 sensor_fresh와 접촉 샘플 valid는6회 모두100%였다. 모든 초기 episode가500step 안에 정확히1회 종료했고, episode0 재진입·reset 혼입이 없었다. 촉각 범주·정규화 F/T 범위·v1 양의 보상 각도 조건도 검사했다.
- checkpoint SHA-256을 수집 전후 대조했다. 보상·정책 배열 유한성, 원시 데이터 길이, 표본 수·모든 초기사건 종료를 검사했다. 실행별 trace와 script hash는 [validation.json](../../03_assets/sweep_region_timelines_2026-11-23/validation.json)에 기록했다.
- 실행 로그의 `NativeCommandError` 표시는 Gymnasium이 v0 대신 v1을 권하는 DeprecationWarning을 PowerShell이 감싼 것이다. 요청한 정확한 v0를 그대로 사용했고, 해당 두 실행은 exit0·metadata complete로 완료했다. 접촉 buffer overflow나 수집 실패는 관찰되지 않았다.
- 그래프 시각 검수에서는 영역3·4의 보상·접촉·F/T와 영역3 방향 CDF, 영역2 개별 Reward heatmap을 확인했다. 촉각 신호가 희소하므로 처음의0~17축을 실제 평균 활성 범위에 맞춰 확대하고, heatmap 색 범위는 영역 내 세 정책이 같은 범위를 사용하도록 조정했다. 나머지 그림도 같은 생성 경로를 사용하며 파일·링크 검사를 적용했다.

## 재현

본 수집은 다음 명령을 각 task·checkpoint·seed 조합에 적용했다. `--output-dir`은 기존 폴더를 덮어쓰지 않으므로 재실행 시 새 폴더를 지정한다.

```powershell
python src/inspire_sweep_baseline/scripts/collect_sweep_region_timelines.py --task Inspire-Sweep-v0 --checkpoint logs/TEMP/2026-11-23/inspire_sweep_v0/2026-11-22_17-07-15/model_20900.pt --num_envs 256 --steps 500 --seed 42 --headless --output-dir outputs/sweep_region_timelines_20261123/sweep_v0_seed42

python src/inspire_sweep_baseline/scripts/report_sweep_region_timelines.py --input outputs/sweep_region_timelines_20261123 --assets example/Contact-Rich-Manipulation-Context/03_assets/sweep_region_timelines_2026-11-23 --report example/Contact-Rich-Manipulation-Context/02_implementation/experiments/2026-11-23_sweep_region_timelines.md
```

[원시 결과](../../../../outputs/sweep_region_timelines_20261123)에는 실행별 trace.npz·initial_scene.npz·environment.yaml·agent.yaml·metadata.json과 콘솔 로그를 보존했다.

## 검증 범위와 한계

Python 구문 검사와 실제 Isaac Sim 수집·배열 수치 대조를 수행했다. 원시 데이터는 평가 출력이며 학습을 수행하거나 새 정책을 만들지 않았다.

- 추가한 Python2개 `py_compile` 통과, 루트·문서 저장소 `git diff --check` 통과.
- 변경 Markdown2개 수식 검사 통과. 두 문서의 외부 workspace 링크까지 포함한 검사에서 internal34·external9·오류0.
- 문서 저장소 전체 링크 검사: Markdown656개·internal5607·external1276·오류0. CSV10개·XLSX5개의 데이터셋 링크도 검사했다.
- PNG24개 디코딩 검사 통과. CSV 행 수는 summary12·alignment12·sensors12·reward_terms184·timeline600이다.
- 같은 비종료 물리 sample과 실제 정책 촉각 입력을34bit로 복원하여 비교했을 때, 영역·정책별 관측 bit flip 비율은0.9946~1.0161%였다. 구성된1% noise와 일치하는 범위이며, 원시 신호와 정책 입력을 별도로 기록한 근거도 CSV에 보존했다.

실물 센서·실물 성능, 학습 seed를 바꾼 재학습 분산, 센서 ablation, 관측 noise 제거 비교, 학습 개선의 인과 효과는 미검증이다. v1과 v0의 보상 정의가 다르므로 return을 같은 성능 척도로 해석하지 않는다. 센서 평균은 생존 episode 조건부이므로 시간에 따른 cohort 변화가 포함된다.

## 후속: 최신 Single Contact v1 보상 비중

사용자가 최신 `inspire_sweep_single_contact_v1` 체크포인트의 항별 비중을 요청했다. logs 아래 해당 experiment 디렉토리들을 다시 확인했고, 최신 run은 `2026-11-22_17-15-01`, 그 안의 최대 iteration은 여전히 `model_10950.pt`였다. checkpoint hash가 기존 두 시드 metadata와 같음을 재확인하여 새 시뮬레이션 없이 기존512개 초기 episode의 실제 weight·dt 적용 보상 배열을 재집계했다. 환경·수집 데이터·기존 보고서·학습 로그는 변경하지 않았다.

비중의 분모는 순보상 합이 아니라 **모든 term·step의 기여값 절댓값 합**이다. 한 term 내부에서 양수·음수가 상쇄되기 전에 절댓값을 취했다. 양수 보상 pool과 음수 비용 pool 내부의 비중도 별도 계산했다. episode0·terminal 포함 규칙과 영역별 표본 구성은 본 평가와 같다.

- episode당 평균 양수 합2.95848470, 음수 합−1.57635069, 순합1.38213401, 항별 절댓값 합4.53483539.
- 전체 절댓값 비중: Sweep37.1651%, Reaching31.6373%, 손 관절 속도18.4744%.
- 양수 보상 안에서 Sweep54.8137%·Reaching45.1863%. 음수 비용 안에서 손 관절 속도53.1469%·팔 속도 실패11.1512%·선반 충돌8.1353%.
- 절댓값 비중 합100%와 각 term의 순합=양수합+음수합을 대조했다. 기존 영역별 보상 CSV에 영역 표본 수를 가중한 값과 새 전역 순합도 대조했다.
- [16개 term의 비중 CSV](../../../../outputs/sweep_region_timelines_20261123/reward_shares_model10950/reward_shares.csv)와 [정의·분모·체크포인트 hash JSON](../../../../outputs/sweep_region_timelines_20261123/reward_shares_model10950/reward_shares.json)을 보존했다. 이 비중은 해당512개 평가 episode의 실현 기여량이며 학습 gradient 비중이나 재학습 seed 평균은 아니다.

## 후속: 손 관절별 실제 속도 확인

사용자가 손 관절 속도 비용이 큰 이유와 관절별 속도 수준을 물었다. 기존 trace에는 손 관절 속도 자체가 없어, 수집기에 기본값 false의 `--joint-diagnostics` 옵션만 추가했다. 켜면 Reward의 asset_cfg가 실제로 참조하는12개 joint의 joint_vel·joint_pos를 원래 보상 계산 직후, reset 전에 복사한다. 정책 입력·보상 함수·weight·물리 파라미터는 변경하지 않았다. 옵션을 끈 기존 수집 동작은 보존한다.

첫 실행은 선반 자산 서버 접속이 지연됐고, 사용자가 재연결한 후 같은 프로세스가 초기화·수집을 완료했다. 서버·캐시·자산을 수정하거나 대체하지 않았다. `joints_v1_seed42`·`joints_v1_seed43`에 각256환경·500step을 수집했다. 원래512개 초기 장면의6개 hash 항목이 모두 일치했고, **기존 실행과 재실행의 모든 step·term 보상 배열 최대 차이는 두 시드 모두0**이었다.

- 표본: 초기 episode512개, 유효 env-step242,583개, 평균 episode 길이9.475898초. 각 통계는 보상 계산 시점인50Hz 마지막 물리 substep의 실제 rad/s를 사용한다. 부호 평균이 아닌 절댓값 평균·RMS·절댓값 P95를 구분했다.
- 식: 손 실제12관절 속도 제곱합을100으로 cap한 뒤 weight−0.03·dt0.02를 적용한다. 제어 입력은6개지만 mimic 관절도 별도 합산한다. 평균 연산이 아니다.
- 관절별 RMS 범위0.30579~0.57431rad/s, 전체 관절·시간 통합 RMS0.49557rad/s. 중지·약지의 구동·mimic 관절들이 각각 비용의약10~11%를 차지했다.
- 속도 제곱합 평균2.947063, step당 비용 평균−0.00176824, episode당 누적 비용−0.83778222. cap 활성은0%였다. 실제 qdot로 구성요소를 재계산한 값과 RewardManager 지급값의 최대 차이는1.98e-9였다.
- 처음3초 누적 비용 평균−0.451343, 3초 이후−0.386439. 따라서 짧은 양의 Sweep 지급 구간에만 비용이 생기는 것이 아니다.
- 속도 제한 설정은1rad/s다. 수치 오차 수준의1초과를 별도 사건으로 과장하지 않도록 초과 비율은1.001rad/s 기준으로 저장했다. sampled 최대값은일부 관절에서 제한 설정을 초과했으나 이 작업에서 원인 진단이나 파라미터 수정은 하지 않았다.
- [관절별 CSV](../../../../outputs/sweep_region_timelines_20261123/hand_joint_velocity_model10950/per_joint.csv), [영역별 관절 속도](../../../../outputs/sweep_region_timelines_20261123/hand_joint_velocity_model10950/per_joint_per_region.csv), [요약·재계산 검증 JSON](../../../../outputs/sweep_region_timelines_20261123/hand_joint_velocity_model10950/summary.json), [재계산 스크립트](../../../../outputs/sweep_region_timelines_20261123/summarize_hand_joints.py)를 보존했다.
- 수집기·재계산 스크립트 py_compile과 실제 두 시드 물리 수집을 통과했다. 관절별 비용 비중 합100%, 체크포인트 hash·속도 유한성·원시 보상 재계산을 확인했다. 학습·실물 검증·100Hz 전체 substep의 관절 속도 peak 검증은 수행하지 않았다.
