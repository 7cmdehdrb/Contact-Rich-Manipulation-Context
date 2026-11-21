# LinearReach model_1800 성공 사례의 접촉 벡터 분석

## 요청·변경 범위

사용자가 `logs/TEMP/wr7/inspire_sweep_only_v2_test_action_penalty_linear_reach/2026-11-20_16-18-48/model_1800.pt`의 성공 사례에서 미는 중의 접촉 벡터를 시각화하도록 요청했다. 11시 방향 목표에서 예상한 손바닥 밀기 대신 손등을 대고 붙여 움직이는 듯한 현상의 원인을 확인하고, 후속 방향 보상 수정의 근거를 만든다.

기준 메인 커밋은 `2c3480c`, 문서 커밋은 `a142510`이다. 시작 작업트리에는 IsaacLab의 기존 미추적 설치 출력 파일만 있었다. 이번 변경은 `scripts/analyze_sweep_contact_policy.py`, `scripts/plot_sweep_contact_analysis.py`와 이 로그 추가다. 환경·관측·액션·보상·종료·PPO·자산·체크포인트·학습 로그는 수정하지 않았다. push는 이번 분석 요청 범위에 포함하지 않았다.

## 환경·측정 계약

- Task: `Inspire-Sweep-Only-v2-Test-ActionPenalty-LinearReach`. 기존 v2-Test-ActionPenalty 직접 파생, Reach만 선형인 구성을 그대로 사용했다.
- 체크포인트 SHA-256: `54f222ca81e1e85ac96043a884c9ba8e570317b399902cd9217ee8d270e3cbc6`.
- RTX4070, Windows11, `env_isaaclab` Python, headless, 결정론적 inference action. 기존 환경 관측 잡음은 유지했다. 훈련 실행이 아니다.
- 성공은 기존 termination의 10초 timeout·현재 타겟 bounds 중심–목표 XY 거리 3cm 미만·실패 없음 판정을 사용했다. 자동 reset 전의 실제 terminal frame을 저장한다. 녹화처럼 reset 후 위치를 성공 frame으로 오인하지 않는다.
- physics 100Hz의 2개 substep을 정책 50Hz마다 평균했다. 손에서 타겟에 가해진 힘을 normal과 friction으로 분해했다. 기존 ContactSamples의 합력과 같은 시점의 PhysX contact data를 읽으며 contact normal force matrix와도 비교했다.
- 접촉 위치는 normal load로 가중한 접촉점 중심이다. 여러 접촉점을 하나로 줄인 위치이므로 실제 단일 접촉점이나 개별 점의 힘 벡터로 해석하지 않는다.
- 이동 접촉 구간은 타겟–손 접촉 유효, normal load 0.01N 이상, 타겟 COM XY 속도 0.005m/s 이상, 목표 거리 0.03m 초과로 정의했다. 목표 안에 머무는 나머지 시간을 평균에 섞지 않는다.
- 먼저 각 성공 에피소드의 이동 접촉 평균을 구한 다음 에피소드 간 동일 가중 평균을 냈다. 긴 접촉 한 사례가 전체를 지배하지 않게 했다.
- 좌표는 초기 선반 frame이다. 그림의 오른쪽은 선반 −Y, 위쪽은 +X로 `record_three_views.py`의 inside_top_down과 같다. 시계각은 위=0°, 오른쪽=90°, 11시=−30°다. 사용자가 시점을 별도로 지정하지 않아 이 기준으로 진행했다.
- 초록 방향은 EEF +Z를 회전한 손바닥 바깥 방향이다. 손바닥/손등 구분의 자세 지표이며 손가락 개별 mesh 면의 정확한 접촉 분류는 아니다. 회색 연결선은 실제 손 링크 원점의 연결이며 손 외곽 메시가 아니다.

## 실험과 결과

### 원래 초기 분포

seed42·43 각각 32환경×2500step을 실행했다. 각각 완료160회/성공71회, 완료162회/성공66회다. 미완료 episode는 통계에서 제외했다. 총322회 중137회 성공(이번 평가에서42.55%)이다. 이는 학습 로그의 집계 성공률을 대체하지 않는다.

| 성공137회 이동 접촉의 에피소드 동일 가중 평균 | 값 |
| --- | ---: |
| 손바닥 바깥 방향이 타겟 반대쪽인 frame 비율 | 99.83% |
| 손바닥 방향과 EEF→타겟 XY 방향의 평균 cos | −0.499 |
| EEF가 목표 방향 기준 타겟 뒤쪽인 frame 비율 | 97.61% |
| 타겟에 작용한 합력의 목표 방향 성분 | 1.501N |
| 그중 수직항력 성분 | 1.413N |
| 그중 마찰력 성분 | 0.088N |
| 전방 양의 힘 기여 중 마찰 비중의 에피소드 평균 | 7.90% |
| 목표 방향·합력 방향 cos(분모는 3D 합력 norm) | 0.878 |
| 이동 접촉 시간 | 0.497초 |

normal load의 접촉 body별 에피소드 평균 비중은 중지 두 번째 링크32.92%, 손 몸체32.63%, 약지 두 번째 링크22.04%, 중지 첫 번째 링크6.93%, 약지 첫 번째 링크4.47%다. 몸체 링크는 손바닥과 손등을 모두 포함하므로 이 값만으로 면을 확정하지 않는다. 손바닥 센서 body의 비중은0이다.

에피소드 bootstrap 2000회로 계산한 평균의 참고95% 구간은 손바닥 반대 방향 비율99.50–100%, 수직항력 목표 성분1.352–1.473N, 마찰 목표 성분0.072–0.104N이다. 두 seed만 사용했으므로 학습 seed 간 불확실성까지 포괄하지 않는다.

### 11시 방향 조건부 추가 표본

원래 분포322회에서 초기 목표 각도 −45° 이상/−15° 미만인 성공은1건뿐이었다. 이 한 건을 11시 방향 평균이라고 일반화하지 않았다.

seed44·128환경에서 정상 reset을 rejection sampling하여 최초 목표 방향만 −30°±15°로 제한했다. 70회 부분 reset round 후 최초 장면128개가 조건을 만족했다. reward나 초기 자세 계산식은 바꾸지 않았다. 500step 실행 후 각 환경 최초 episode만 사용했다. 이후 자동 reset된 비조건부 episode는 이 통계에서 제외했다. 완료128회 중5회 성공이며 원래 분포 성공률과 합산하지 않았다.

성공5회 모두 이동 접촉 동안 손바닥이 타겟 반대쪽을 향했다. 목표 방향 합력1.157N=normal0.927N+friction0.230N, 전방 양의 힘 중 마찰 기여 평균23.14%다. 마찰 기여가 원래 분포 성공 평균보다 커도 normal이 주성분이다. 표본5개라 방향별 성능 결론은 탐색적이다.

대표 그림은 성공5개 중 손바닥–타겟 평균 cos가 중앙값에 가장 가까운 사례를 선택했다. seed44/env36/episode0, 초기 목표−39.79°(약10시40분), 마지막 거리2.733cm다. 힘 목표 성분은normal0.878N/friction0.072N이고, 평균 접촉 하중은 중지 두 번째 링크62.7%, 약지 두 번째 링크31.6%, 약지 첫 번째 링크3.9%, 중지 첫 번째 링크1.9%다. 소수점 반올림으로 합이100%와 약간 다를 수 있다.

조건부 성공에서는 EEF가 타겟 뒤쪽인 비율이32.1%에 그쳤지만 힘은 타겟을 누르는 방향이었다. EEF와 실제 손가락 접촉 위치가 다르므로 EEF 위치만으로 밀기/끌기를 판정하면 오분류할 수 있다.

## 코드와 연결한 해석

현재 Sweep 정방향 보상은 다음 구조다. `h`는 기존 높이 조건·접촉 history·count/20이며, 합력 XY norm이1N 미만이거나 접촉이 무효이면 방향 계수는0이다. RewardManager dt 적용까지 포함한 step 기여다.

```math
R_+ = 50\max(d_{t-1}-d_t,0)\,h_t\,
\max\left(0,\frac{\mathbf{F}_{xy}\cdot\hat{\mathbf{d}}}{\|\mathbf{F}\|_3}\right),
\qquad \mathbf{F}=\mathbf{F}_N+\mathbf{F}_T.
```

이 식은 타겟이 목표에 가까워지고 손 전체 합력이 목표 쪽이면 지급한다. 손바닥/손등, 어떤 손가락 링크인지, 허용 접촉면, 손바닥 방향은 검사하지 않는다. normal도 타겟 쪽으로 작용하는 것으로 측정되었다. 따라서 힘 벡터 부호가 반대로 적용되어 끌기가 밀기로 인정된다는 근거는 얻지 못했다.

Test reset은 `sample_initial_eef`로 위치를 바꾸고 IK에 `default_quat`를 그대로 전달한다. `_robot()`은 wrist_3=−π/2이고 기본 손바닥은 선반−Y다. 저장된 첫 frame들의 손바닥 평균은 약(−0.0006,−1.0000,+0.0004)로, top-down 화면에서는 약3시 방향이다. 11시로 가려면 반드시 손바닥을 회전해야 한다는 조건은 없다. 이 초기 자세와 접촉면 무관한 보상이 손의 반대 면/손가락을 쓰는 해법을 허용한다는 해석이 측정과 일치한다. 이 원인의 인과 효과를 분리한 재학습 실험은 하지 않았다.

현재 근거는 강한 마찰 부착/접착으로 끈다는 설명보다 손바닥 반대 방향 자세의 손 몸체·손가락으로 누른다는 설명에 가깝다. 정확히 손등 mesh인지 손가락 측면인지는 링크별 국소 접촉 normal과 mesh 면 분류가 추가로 필요하다.

## 수식 수정 방향: 아직 적용하지 않음

원하는 조건이 손바닥 밀기라면 목표 방향 힘의 부호를 뒤집는 대신 허용 접촉면/손바닥 정렬을 추가하는 편이 분석과 맞다. 예를 들어 기존 방향 계수에 다음 계수를 곱하는 후보가 있다.

```math
g_{\mathrm{palm}}=\max\left(0,\hat{\mathbf{n}}_{\mathrm{palm},xy}
\cdot\frac{\mathbf{c}_{xy}-\mathbf{p}_{\mathrm{EEF},xy}}
{\|\mathbf{c}_{xy}-\mathbf{p}_{\mathrm{EEF},xy}\|}\right).
```

이는 단순 자세 후보이며 손바닥 패치 접촉을 보장하지 않는다. 정확한 손바닥 밀기가 목적이면 허용 palm collision patch의 접촉 조건을 함께 설계해야 한다. EEF 뒤쪽 조건만 추가하는 방법은 긴 손가락의 실제 접촉 위치를 고려하지 않아 유효 동작도 막을 수 있다. 마찰력을 전부 배제하면 이번의 normal 중심 동작이 그대로 보상될 수 있으므로 이 현상을 겨냥한 충분한 수정이 아니다.

초기 회전을 유지하면서 palm 계수만 강제하면 특정 방향에서 회전 부담과 성공률 저하가 생길 수 있다. 초기 자세와 허용 접촉면을 먼저 합의하고 별도 파생 환경에서 비교하는 것이 후속 작업이다. 이번에는 보상을 수정하지 않았다.

## 산출물·재현

- [원래 분포 성공 평균 그림](../../../../outputs/contact_analysis/model1800_results/success_contact_summary.png)
- [원래 분포 접촉 body 비중](../../../../outputs/contact_analysis/model1800_results/contact_body_summary.png)
- [11시 조건부 대표 벡터 그림](../../../../outputs/contact_analysis/model1800_11oclock_results/representative_contact_vectors.png)
- [11시 조건부 대표 애니메이션](../../../../outputs/contact_analysis/model1800_11oclock_results/representative_contact_vectors.gif)
- [원래 분포 전체 수치](../../../../outputs/contact_analysis/model1800_results/summary.json)
- [11시 조건부 전체 수치](../../../../outputs/contact_analysis/model1800_11oclock_results/summary.json)

원시 데이터와 metadata는 `outputs/contact_analysis/model1800_seed42_run3`, `model1800_seed43`, `model1800_sector11_seed44`의 `trace.npz`, `metadata.json`에 있다. metadata에는 checkpoint hash·정의·실행 시간·filter body 순서가 있다. PowerShell workspace 루트에서 활성 conda 환경으로 실행한다.

```powershell
python src/inspire_sweep_baseline/scripts/analyze_sweep_contact_policy.py --headless --checkpoint logs/TEMP/wr7/inspire_sweep_only_v2_test_action_penalty_linear_reach/2026-11-20_16-18-48/model_1800.pt --num_envs 32 --steps 2500 --seed 42 --output-dir outputs/contact_analysis/new_seed42
python src/inspire_sweep_baseline/scripts/analyze_sweep_contact_policy.py --headless --checkpoint logs/TEMP/wr7/inspire_sweep_only_v2_test_action_penalty_linear_reach/2026-11-20_16-18-48/model_1800.pt --num_envs 128 --steps 500 --seed 44 --initial-direction-center -30 --output-dir outputs/contact_analysis/new_sector11
python src/inspire_sweep_baseline/scripts/plot_sweep_contact_analysis.py outputs/contact_analysis/model1800_seed42_run3 outputs/contact_analysis/model1800_seed43 --output-dir outputs/contact_analysis/model1800_results
python src/inspire_sweep_baseline/scripts/plot_sweep_contact_analysis.py outputs/contact_analysis/model1800_sector11_seed44 --output-dir outputs/contact_analysis/model1800_11oclock_results
```

출력 폴더는 기존에 없는 새 경로를 지정한다. seed43은 첫 수집 명령의 seed와 출력 경로를 바꾸면 된다.

## 검증·미검증

완료된 물리 수집3회에서 normal 접촉점 수는 filter당 최대4개였다. normal 합계와 PhysX force matrix의 최대 차이는1.53e−5N 이하, 저장 합력−normal−friction의 최대 차이는1.91e−5N 이하였다. 저장 좌표에서 독립 재구성한 정방향 거리 보상과 실제 값의 최대 차이는2.85e−5m 미만이며 bitwise 일치로 기록하지 않는다. 모든 저장 float가 유한하고, 완료 episode만 선택하며, 조건부 수집은 최초 episode만 사용하는 것을 확인했다.

PNG를 렌더해 눈으로 확인했고 GIF가 각각750×750·100frame으로 열리는 것을 확인했다. 스크립트2개의 AST 구문 검사와 문서 수식·링크·공백 검사를 통과했다. 환경 패키지 본체의 차이는0이며 학습 로그는 건드리지 않았다.

최초 수집 준비는 runner class 예상 차이, 두 번째는 inference tensor 갱신 위치로 실패했다. 실패 metadata와 log를 남기고 runner 대응과 inference scope를 수정한 뒤 run3를 seed42 최종 데이터로 사용했다. 실패 run은 통계에 포함하지 않았다.

미검증 범위는 재학습, 손 mesh 면 단위 접촉 분류, 관측 잡음 비활성화 비교, 카메라가 있는 단일 환경과의 궤적 일치, 다른 체크포인트·실물로의 일반화다.

## 2026-11-21 저장소 동기화·커밋

사용자가 현재 변경의 pull·merge·commit·push를 요청했다. 메인 저장소는 `2c3480c`에서 `f3059f3`으로, 문서 저장소는 `a142510`에서 `8dfcb81`로 각각 원격 main의 3개 커밋을 fast-forward 병합했다. 충돌은 없었으며 기존 분석 스크립트 2개와 이 문서를 보존했다. 이번 동기화에서는 분석 코드나 환경 동작을 수정하지 않았다.

문서 저장소를 먼저 커밋·push하고 메인 저장소에서 그 문서 커밋을 참조한다. IsaacLab의 기존 미추적 설치 출력 파일 `2.7.0+cu128`은 보존하며 커밋 대상에서 제외한다. 다른 서브모듈과 `logs/rsl_rl`도 변경하지 않는다.

스크립트 2개의 AST 구문 검사를 통과했다. 문서 수식·링크·공백 검사를 수행하고 결과를 아래에 기록한다. 이번 작업에서는 물리 시뮬레이션·학습·그림 생성을 재실행하지 않으므로 위의 기존 실험 결과를 새 검증으로 간주하지 않는다.

검증 결과: 변경 문서 수식 검사 1개 통과, 전체 문서 링크 검사 642개 문서에서 오류 0개, 변경 문서의 외부 workspace 링크 6개 검사에서 오류 0개, `git diff --check` 통과. 원격에서 가져온 환경 코드에는 추가 수정을 하지 않았다.
