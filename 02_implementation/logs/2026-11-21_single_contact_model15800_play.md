# Single Contact model_15800 실제 Play 평가

## 요청·변경 범위

사용자가 `logs/TEMP/wr8/inspire_sweep_single_contact_v0/2026-11-20_20-56-01/model_15800.pt`로 직접 Play하여 성공률·실패 원인과 성공 사례의 목표별 손바닥/손등 사용 비율·힘 방향 정렬을 분석하도록 요청했다. 기준 메인 커밋은 `4102344`, 문서 커밋은 `85ec22b`다. 기존 IsaacLab 미추적 설치 출력 파일은 보존한다.

환경은 `Inspire-Sweep-Single-Contact-v0`이며 EnvCfg `SweepSingleContactEnvCfg`, runtime `SweepSingleContactEnv`, PPO `SweepSingleContactPPORunnerCfg`다. 기존 분석 실행기의 누적 contact_count 필수 접근을 해당 필드가 있는 부모와 contact_recognized boolean만 있는 자식에 각각 대응하도록 바꿨다. 선택 옵션 `--surface-diagnostics`에서 보상 callable의 실제 `_surface_loads` 반환값을 그대로 저장하고, reset 전 종료 원인·물체 바닥/기울기·팔 속도·선반 상태를 추가 측정한다. 보상 callable은 기존과 동일하게 한 번 호출하며 반환값과 물리 상태를 바꾸지 않는다.

집계 실행기 `scripts/summarize_single_contact_analysis.py`를 추가했다. 그 외 환경 패키지·등록·Scene·Action·Observation·보상·종료·reset·PPO 구성은 수정하지 않는다. 체크포인트와 학습 로그도 수정하지 않는다. 산출물은 `outputs/contact_analysis/model15800/`에 새로 생성한다. 이번 요청에 commit·push는 포함하지 않는다.

## 측정 계약

- RTX4070 12GB, Windows, conda `env_isaaclab`, headless deterministic inference. 기존 관측 noise는 유지한다. 학습하지 않는다.
- seed42·43 각각64환경×2500정책스텝을 실행하며 각 환경의 첫5개 완료 episode만 고정하여 총640회를 평가한다. 고정 시간 안에서 짧은 실패 episode가 더 많이 포함되는 편향을 줄이기 위한 cohort다. episode 미완료 또는 누락이면 집계를 중단한다.
- 기존 성공 callable을 사용한다. 10초 시점의 타겟 bounds 중심과 목표 XY 거리가 엄격히3cm 미만이며 다른 실패가 없어야 한다. 일시적 목표 진입과 성공을 구분한다.
- 구역은 episode의 고정 `sweep_dir`을 현재 선반 frame으로 변환한 기존 `sweep_region`과 동일하다. 로봇 기준12시=-X,3시=+Y,6시=+X,9시=-Y. 구역1(12시±30°)·2(오른쪽120°)는 손등, 구역3(6시±30°)·4(왼쪽120°)는 손바닥이 의도한 면이다. 그림 좌표는 기존 top-down 기준인 오른쪽=-Y·위=+X로, 구역의 로봇 시계 방향과 반대다.
- 미는 구간은 현재 타겟 접촉·유효 샘플·normal load0.01N 이상·타겟 COM XY속도0.005m/s 이상·목표 거리3cm 초과인 정책스텝으로 정의한다. 목표 안에서 정지 유지한 구간을 제외한다. 전진한 스텝만 선택하지 않으며 잘못 미는 구간도 포함한다.
- 손바닥/손등은 EEF 자세의 간접 판정이 아니라 보상이 실제 사용하는 양면 표면 분류 하중이다. 분류 하중 합0.01N 이상인 이동 접촉에서 의도한 면의 법선 하중 비중과 하중 우세 frame 비율을 계산한다. 미분류·모서리 접촉은 별도로 coverage를 기록한다. 한 episode 안에서 하중을 합산해 비율을 구한 후 episode 간 동일 가중 평균을 사용한다.
- 힘은 손에서 타겟에 작용하는 normal+friction의 정책스텝 내2개 물리샘플 평균이다. 현재 타겟→목표 방향에 대한 XY cos·XY 각도·30°/60° 이내 비율·반대 방향 비율, 3D 합력 norm을 분모로 쓰는 보상식의 정렬도 함께 기록한다. episode의 원래 목표 방향과의 cos도 보조 지표로 저장한다.
- 표면 하중은 기존 보상과 동일한 정책 경계의 마지막 물리상태 샘플이다. 힘 방향의2-substep 평균과 표면 하중의 샘플링 차이를 유지하고 명시한다.
- EEF +Z의 XY 투영과 EEF→타겟 XY 방향의 내적 부호로 손바닥이 타겟을 향하는 자세인지도 별도로 계산한다. 손등 의도 구역은 음수, 손바닥 의도 구역은 양수를 의도한 자세로 센다. 이는 전체 손 자세 지표이며 개별 손가락의 실제 접촉면 분류를 대신하지 않는다.
- 전체 성공률의 Wilson95% 구간은 episode 표본의 기술적 구간이며 동일 환경·두 rollout seed의 상관이나 학습 seed 불확실성을 완전히 포괄하지 않는다.

## 재현 명령

Workspace 루트에서 `env_isaaclab` Python으로 실행한다. 기존에 없는 출력 경로를 사용한다.

```powershell
python src/inspire_sweep_baseline/scripts/analyze_sweep_contact_policy.py --headless --task Inspire-Sweep-Single-Contact-v0 --checkpoint logs/TEMP/wr8/inspire_sweep_single_contact_v0/2026-11-20_20-56-01/model_15800.pt --num_envs 64 --steps 2500 --seed 42 --surface-diagnostics --output-dir outputs/contact_analysis/model15800/seed42
python src/inspire_sweep_baseline/scripts/analyze_sweep_contact_policy.py --headless --task Inspire-Sweep-Single-Contact-v0 --checkpoint logs/TEMP/wr8/inspire_sweep_single_contact_v0/2026-11-20_20-56-01/model_15800.pt --num_envs 64 --steps 2500 --seed 43 --surface-diagnostics --output-dir outputs/contact_analysis/model15800/seed43
python src/inspire_sweep_baseline/scripts/summarize_single_contact_analysis.py outputs/contact_analysis/model15800/seed42 outputs/contact_analysis/model15800/seed43 --output-dir outputs/contact_analysis/model15800/new_results
```

## 검증·결과

체크포인트 SHA-256은 `23b1c9eaf954c6ee89a160e6929fecd0bbac5b4f64cf8f8574bb0dc2ae81439a`, runner iteration은15800이다. 저장된 학습 설정의10초·decimation2·목표 반경3cm·높이12cm·F/T 한계150N/8Nm·접촉면 보상1.5/0.7·Sweep weight50·runner class와 wrapper clip 없음이 현재 구성과 일치함을 확인했다. 평가 시 물리 pair buffer 용량만 기존 분석기대로2**21로 줄였다. 이는 소규모 평가의 메모리 할당 설정이며 물성·제어·보상은 바꾸지 않았다.

### 성공률과 실패

seed42는223/320(69.69%), seed43은209/320(65.31%) 성공이다. 총 **432/640=67.50%**, episode Wilson95% 구간63.78–71.01%다. 고정 cohort 밖의 뒤 episode와 마지막 미완료 episode는 포함하지 않았다. 전체 실행에서는 seed42 완료330/성공228, seed43 완료340/성공216이었다.

| 구역·의도 | 성공/시도 | 성공률 | 팔 속도 종료 | 목표 진입 후 이탈 | 3–5cm 밖 정지 | 더 먼 거리에서 진행 부족 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1·12시·손등 | 76/95 | 80.00% | 3 | 16 | 0 | 0 |
| 2·3시·손등 | 155/220 | 70.45% | 35 | 10 | 17 | 3 |
| 3·6시·손바닥 | 7/108 | 6.48% | 29 | 1 | 40 | 31 |
| 4·9시·손바닥 | 194/217 | 89.40% | 13 | 3 | 7 | 0 |
| 전체 | 432/640 | 67.50% | 80 | 30 | 64 | 34 |

물체 낙하/전도·선반 실패는0회다. 실패208회 중80회(38.46%)는 팔 관절속도 절댓값1rad/s 초과로 종료했다. 종료 시 최대 팔 속도의 중앙값은1.123rad/s, 종료 시각 중앙값1.49초다. 이 중21회는 타겟 접촉 전에 종료했다. 따라서 모든 실패를 물체를 잘못 민 결과로 묶으면 안 된다.

시간 초과 실패128회 중64회는 한 번도3cm 안으로 들어가지 못하고 최종3–5cm 밖에서 끝났다(최종 거리 중앙값4.078cm).34회는 더 먼 거리에서 진행이 부족했다(최종 거리 중앙값6.228cm).30회는3cm 안으로 들어갔다가 벗어났다(최소 거리 중앙값0.974cm, 최종3.484cm). 세 범주의 모든128회에서 마지막1초의 순 목표 거리 변화 절댓값은1mm 미만이었다. 마지막1초 타겟 XY속도의 범주별 중앙값은약0.0016m/s로, 종료 직전에 빠르게 지나가는 실패보다는 목표 밖에서 움직임이 거의 멈춘 경우다. 다만 이 수치가 특정 관절 제어·보상 항의 인과 원인을 분리하지는 않는다.

가장 큰 취약점은 구역3이다.108회 중101회 실패하며 전체 실패의48.56%를 차지한다. 성공 사례의 평균 힘 각도34.36°에 비해, 이동 접촉이 있는 실패91회의 평균은65.64°다. 실제 궤적도 목표 직선에서 옆으로 벗어난 뒤 진행이 멈추는 사례를 포함한다. 이 방향에서의 힘 전달·목표까지의 추가 진행이 부족하다는 관찰이며, 초기 자세나 보상의 원인 효과를 분리하는 재학습은 하지 않았다.

### 성공 사례의 손 방향·실제 접촉면

모든 비율은 각 episode 안에서 먼저 계산한 후 episode 간 동일 가중 평균이다. 아래의 분류율은 전체 이동 접촉 중 손바닥/손등 하중을 분류할 수 있는 frame 비율이다. 하중 비중의 표본수는 해당 frame이 하나 이상 존재하는 성공 episode 수다.

| 구역·의도 | 성공 episode | 의도한 전체 손 자세 비율 | 의도면의 분류 하중 비중 | 하중 집계 episode | 이동 접촉 분류율 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1·손등 | 76 | 51.68% | 4.02% | 35 | 27.58% |
| 2·손등 | 155 | 98.11% | 96.59% | 123 | 34.77% |
| 3·손바닥 | 7 | 100% | 100% | 3 | 21.40% |
| 4·손바닥 | 194 | 100% | 100% | 190 | 71.01% |

구역1은 의도한 손등 사용이 충분히 학습됐다고 볼 수 없다. 분류 가능한 접촉에서는 손바닥 하중이95.98%였고,35회 중 손등 하중 우세 episode는1회뿐이다. 전체 이동 접촉 frame 기준 평균은 손등 우세0.60%·손바닥 우세26.97%·미분류72.42%다. 미분류까지 전부 손바닥이었다고 주장하지 않는다.

구역2는 분류 가능한 접촉과 손 전체 자세 모두 손등 선호에 맞지만, 이동 접촉의65.23%는 표면 미분류다. 구역4는 손바닥 선호와 일치한다. 구역3은 손바닥 자세를 취해도 성공 자체가 드물고, 실제 표면 하중을 확인할 수 있는 성공은3회뿐이라100%를 강한 일반화로 해석하면 안 된다.

전체 성공432회의 이동 접촉 frame 기준 episode 평균은 의도면 우세44.67%·반대면 우세4.90%·미분류50.44%다. 성공81회에서는3cm 밖 이동 접촉 중 표면을 한 번도 분류하지 못했다. 따라서 분류 가능한351회의 의도면 하중 비중89.23%만 단독으로 제시해 전체 의도면 사용률이라고 부르면 잘못된 해석이다.

### 성공 사례의 힘 방향

| 구역 | 평균 XY cos | 평균 XY 각도 | 목표 방향30° 이내 | 60° 이내 | 반대 방향 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.9210 | 16.39° | 86.51% | 97.27% | 1.15% |
| 2 | 0.9436 | 14.95° | 90.91% | 99.08% | 0.42% |
| 3 | 0.7905 | 34.36° | 49.13% | 90.55% | 1.13% |
| 4 | 0.9499 | 14.23° | 89.65% | 99.58% | 0.08% |
| 전체 | 0.9400 | 15.20° | 88.89% | 98.85% | 0.41% |

전체3D 합력 norm을 분모로 쓰는 정렬도는0.9052다. 수평 방향 정렬이 좋은 경우에도 수직 성분 때문에 보상식 계수가XY cos보다 작을 수 있다. 성공한 구역1은 손등 선호와 다른 면을 써도 힘은 목표 쪽을 향했다. 따라서 접촉력 방향 일치와 의도한 손 접촉면 사용은 별도로 평가해야 한다.

### 실제 검증과 산출물

각 실행의 모든 저장 float가 유한하며, 열별 step 수·고정 cohort의 완료 여부·episode 경계·구역 고정을 검사했다. 원래 sweep_dir과 최초 타겟→목표 방향의 cos는최소0.9999998이었다. PhysX normal matrix 대조 최대 오차는seed42에서6.10e-5N, seed43에서1.22e-4N이었다. 저장 합력−normal−friction의 최대 오차는각각1.41e-4N·1.35e-4N이었다.3cm 밖 양의 거리보상 재구성 오차는각각3.26e-6m·2.42e-6m로 검사 기준을 통과했다.

- [최종 수치와 검사 결과](../../../../outputs/contact_analysis/model15800/results_final/summary.json)
- [640개 episode별 표](../../../../outputs/contact_analysis/model15800/results_final/episodes.csv)
- [성공률·접촉면·힘 각도·실패 분류 그림](../../../../outputs/contact_analysis/model15800/results_final/evaluation_summary.png)
- [대표 성공·실패 궤적](../../../../outputs/contact_analysis/model15800/results_final/representative_trajectories.png)
- [대표 사례 선택 목록](../../../../outputs/contact_analysis/model15800/results_final/representatives.json)

별도 seed44·1환경·20초의3시점 실제 렌더 Play도 완료했다.960×540·50fps·각1000frame이며 `outputs/contact_analysis/model15800/play_video_seed44`에 저장했다. 이 렌더 실행은640회 통계에 합산하지 않으며, 다른 환경 수·카메라 유무의 실행을 기존 trace와 동일 episode라고 간주하지 않는다. 렌더 recorder는 reset 이후 장면을 촬영하므로 성공 판정은 영상 끝 위치가 아닌 위의 reset 전 trace를 사용한다. high_angle·inside_top_down의250·750frame을 직접 열어 실제 로봇·타겟·목표가 촬영된 것을 확인했다.

- [실제 Play 상부 시점 영상](../../../../outputs/contact_analysis/model15800/play_video_seed44/inside_top_down.mp4)
- [실제 Play 사선 시점 영상](../../../../outputs/contact_analysis/model15800/play_video_seed44/high_angle.mp4)

```powershell
python src/inspire_sweep_baseline/scripts/record_three_views.py --headless --task Inspire-Sweep-Single-Contact-v0 --checkpoint logs/TEMP/wr8/inspire_sweep_single_contact_v0/2026-11-20_20-56-01/model_15800.pt --seconds 20 --width 960 --height 540 --seed 44 --output-dir outputs/contact_analysis/model15800/new_play_video
```

재학습·보상 수정·실물 검증은 하지 않았다. 특히 미분류 접촉의 정확한 mesh 면, 학습 seed 간 변동, 목표 방향을 균등하게 강제했을 때의 성공률은 이번 결과가 입증하지 않는다.

최종 검증: 분석 스크립트2개 AST 통과, 변경 Markdown2개 수식 검사 통과, 전체643개 문서 링크 오류0개, 변경 문서의 외부 workspace 링크7개 오류0개, 메인·문서 `git diff --check` 통과. 환경 패키지 본체의 변경 파일은0개이며 IsaacLab의 기존 미추적 파일도 그대로다. 최종 집계 그림을 렌더해 직접 확인했다.3개 영상 모두1000frame임을 디코딩 검사했고 영상 실행의 reset은2회였다.

표면 분류 기준의 보조 점검으로 성공 episode의 이동 접촉10454frame을 합쳐 세었다. 분류 하중이 정확히0(1e-12 이하)인 frame은5002개, 양수이지만 평가 분류 임계0.01N 미만인 frame은26개였다. 따라서 평가의 미분류에는 작은 양수 하중도 소수 포함되며 모두 보상 중립1.0이라고 간주하면 안 된다. 이 frame 합산 수치는 위의 episode 동일 가중 coverage와 집계 방식이 다르다.

## 해석 경계

현행 접촉면 보상은 선호 면1.5·반대 면0.7·미분류1.0의 양의 계수이며 잘못된 면이나 미분류 접촉을 금지하지 않는다. 따라서 성공률이 높아도 의도한 면을 썼다고 간주할 수 없다. 미분류에는 기존 양면 표면 판정이 붙지 않는 모서리·측면 등이 포함될 수 있으나, 모든 미분류를 특정 면으로 단정하지 않는다. 하중 비율의 분모는 분류 가능한 접촉만이며 전체 이동 접촉 coverage를 반드시 함께 제시한다.

첫 집계의 보상 재구성 검증에서 목표까지0.55mm인 frame의 최대 오차가0.000204m로 나타났다. 세계 좌표를 각각 float32 선반 좌표로 뺀 후 다시 목표 차이를 구하는 계산은 거의0인 거리에서 각도 오차에 민감하다. 이 좌표 차감의 수치 오차가 유력한 설명이지만 세계 좌표 원본을 별도로 저장하지 않아 전체 원인을 확정하지 않았다. 분석 대상인 목표 밖3cm 구간의 최대 오차는0.00000326m였다. 검증은 전체 최대 오차와3cm 밖 최대 오차를 각각 기록하며, 주 분석 구간의 오차1e-5m 이하와 힘 분해 오차1e-3N 이하를 검사한다. seed43의 전체 최대 오차는0.000237m였다. 최초 집계 실패 폴더와 console log는 보존했고 물리 Play를 실패로 취급하거나 통계에서 제외하지 않았다.
