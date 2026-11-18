# Stabilize Sweep 순차 구현

[명세](../../01_plan/environments/2026-11-18_stabilize_sweep_spec.md) · [Ticket 분할](../../01_plan/environments/2026-11-18_stabilize_sweep_ticket_review.md)

## 권한과 기준

사용자가 `$implement`로 Ticket 기능의 순차 구현을 요청했다. 이전 설계 단계의 구현 금지는 이번 요청으로 해제됐다. 기준 환경은 `Inspire-Sweep-Simple-Finger-ForceDirection-v0`, root 기준 commit은 `2b855bcd46b80a4d5088cc723fae6bf8b1d88c43`다. 기존 환경·자산·사용자 작업과 학습 로그를 보존한다.

후속 사용자는 기존 weight를 참고한 초기값 선택을 허용했다. 정규화 setup/완료·이동·회전·압착 weight는 각각1.0, Sweep은30.0으로 선택한다. 거리 왕복 항의 상한은 같은 거리L에 대해 `(30−38.91)L`이며 음수다. 전체 정책의 행동 개선이나 학습 성공을 뜻하지 않는다. Ticket10에서 실제 행동과 구분해 평가한다.

## Ticket01 — 독립 실행 골격

기존 환경 Cfg/runtime 상속 없이 Env/Scene/Manager/PPO 구성과 runtime을 추가하고 `Inspire-Stabilize-Sweep-v0`로 등록했다. Isaac Lab 기반 클래스와 기존 계산·제어 helper만 재사용한다. 기존 역할별 파일 구조를 유지한다. 이 시점은 후속 Ticket의 표면점·Gate·새 보상이 연결되기 전 골격이다.

검증: CPU 등록 테스트 및 mypy 선택7파일 통과. RTX3090에서 등록 환경2개 생성, reset, zero action4step 통과(`/tmp/stabilize_smoke.log`). 당시 관측은 임시66D+64D이며 최종67D 검증으로 세지 않는다.

## Ticket02 — 초기 자세와 충돌 검사

타겟/목표를 한 번 추출하고 같은 명령에서 XY/yaw 후보 최대4개를 계산한다. USD joint frame FK로 초기 손 형상의 방향별 지지점을 얻어 명목 표면 간격5cm를 적용한다. 관절 제한·IK 수렴과 로봇 충돌 형상의 보수적 OBB 겹침을 검사하며, 선택 상태만 쓰고 다른 환경 physics를 진행하지 않는다. 실패 시 환경 ID·후보 자세·IK 오차·충돌 여부를 남기고 중단한다.

기존 `assets/robot.py`는 손 내부 충돌 메쉬의 겹침 때문에 articulation self-collision을 끄고 있다. 실제 진단에서 손바닥–엄지 쌍의 겹침을 확인했다. 사용자가 **기존 손 내부 겹침만 제외하고 검사**하도록 승인했다. 손0rad의 기존 겹침 쌍만 제외하며 팔–팔·팔–손 검사는 유지한다. 기존 자산이나 물리 설정을 수정하지 않는다.

초기2환경 검증에서는 한 환경의 IK가 수렴하고 다른 환경은4후보 모두 수렴하지 않았다. 별도 진단에서 실패 후보 자세의144개 초기 관절값을240회 반복으로 계산해도 수렴하지 않았다. 이 진단은 환경 reset의 추가 재시도가 아니며 production은4후보 상한을 유지한다. 도달 가능성·장면 분포는 후속 통합 검증에서 추가 확인해야 한다. 합의한 목표 분포나 로봇 위치·높이를 임의 변경하지 않았다.

CPU 표면 간격·방향과 OBB 분리 검증 포함3개 통과. 최종 실제 reset·step 및 나머지 Ticket은 진행 중이다.

## Ticket03–08 — 기능 연결

- 03: `surface_point`의 실제 메쉬 광선/연결요소 알고리즘을 활성 패키지 내부 helper로 옮겼다. 비교용 OBB·뷰어와 다른 미추적 패키지에 대한 runtime 의존은 추가하지 않았다. +X 정면1mm, 2cm/20%, 타겟 최대 조각1개, 비타겟 조각별 valid+XYZ 슬롯, episode-fixed 월드 점을 현재 EEF로 변환한다. Actor/Critic67D+64D, latent83D, action12D를 연결했다.
- 04: native target-hand contact view에서 법선 점과 마찰 anchor를 각각 축약한다. 실제 PhysX COM을 사용하고 법선 norm합S를 따로 보존한다. 공유 counts/starts는 법선 축약 후 마찰 API를 호출한다. 무효 범위·비유한 값·가득 찬 packed buffer를 Gate 유효 접촉으로 쓰지 않는다. 압착 비용은 물리 sample별 계산 후 평균한다.
- 05: 기존 RED 공간과 초기 로봇 충돌 OBB의 보수적 XY envelope+1cm를 금지영역으로 사용한다. 기존 크기 우선 후보 순서와 원형 여유·셀 jitter를 유지하고, 막힌 후보만 생략한다. snapshot 미검출/16슬롯 초과는 장애물0개로 한 번 재관측한다. 타겟 단독 미검출은 오류다. 요청/실제 수·생략·fallback 이유·IK횟수·시간을 기록한다.
- 06: 모든 Gate 조건을100Hz에서 평가해30연속 sample을 latch한다. 현재 action의 reward phase는 step 시작에 고정하고 다음 관측은 latch를 표시한다. setup/완료·초기 이동/회전·압착과 Gate 전제 timeout 성공을 연결했다. native7D goal command에서 XYZ만 추출하는 통합 오류를 실제 step 검사에서 발견해 수정했다.
- 07: 이전 policy step 거리 차분, 최근3회 중2회/+1/−2/0–20 contact history, count/20, 실제 평균 힘 방향 및1N 수평 힘 조건을 사용한다. 전환 step에서 거리 이력을 갱신해 Stabilize 이동을 소급하지 않는다. 최종 거리 항은30×양의 변화×h×a 및−38.91×거리 증가이며 Manager dt를 상쇄한다.
- 08: 기존 공통 비용의 callable·params·weight와5개 커리큘럼을 대조했다. 새 환경에만 F/T 변화 비용의 누적 양의 보상5% 상한을 없앴다. raw cap과 기존 환경은 유지한다. deadzone/팔속도 일정은 비활성이며30도·1rad/s를 유지한다.

## Ticket09 — 통합 검증과 발견한 한계

GPU 검사 진입점은 `src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py`다. `--headless`로 실행하며 결과는 기본 `/tmp/stabilize_sweep_validation.json`에 쓴다. 실제 등록 환경을 사용하고 학습 로그를 만들지 않는다.

첫 보수적 OBB 자기충돌 판정에서 유효 자세를 거절하는 사례가 있어 실제 USD collision convex hull의 교집합 검사를 추가했다. OBB는 후보 선별 및 장애물 금지영역에 유지하며, 자기충돌 최종 판정은 convex hull로 좁힌다. 손 표면 간격 계산도 실제 collision hull 정점으로 한다. 기존 손 내부0rad 겹침만 예외로 유지한다.

2환경·seed0–7 감사에서 보완 전 모든 배치가 실패했고, 보완 후 seed0·2는 성공, 나머지는 적어도 한 환경의4후보 IK 미수렴으로 실패했다. 이는 수치 IK 미수렴의 관측이며 모든 자세의 수학적 불가능성을 증명한 결과가 아니다. 목표를 다시 추출하거나 실패를 숨기지 않는다. 성공 reset에서 실제 장애물 수와 요청 수가 일치했고, 별도 CPU 경계 검사에서는 큰 후보 생략 후 작은 후보 유지와 최대2회 fallback을 검증했다.

실제2환경 reset·step, 부분 reset의 다른 환경 상태/physics counter 보존, 초기 월드 표면점 고정, Actor/Critic forward·gradient·TorchScript export를 확인했다. 실물 시각 모델이나 대규모2048환경 throughput 검증은 아니다. 실제 Gate의 물리적 달성은 미검증이며, Manager 단계 경계는 알려진 안정화 입력을 replay해 별도로 검사한다.

PhysX readback에서 원통 높이 약0.104831m/0.094898m에 대해 centroid는 root 위0.052415m/0.047449m, COM은0.020966m/0.018980m로 구분됐다. 실제 손바닥–원통 접촉을 만든 제어된 검사에서 법선 하중24.674N/17.728N, 합력과 COM 모멘트를 native packed 데이터·force matrix와 대조했다. 이는 Gate의0.5N 하중을 달성했다는 검증이 아니다.

## Ticket10 — 사용자 결정에 따른 미완료

reset 감사 결과를 사용자에게 제시했고, **기존 조건 유지, 행동 평가 미완료 기록**을 선택했다. 기존 목표 분포·로봇 위치·초기 높이·손 방향과4후보 상한을 유지한다. 따라서 학습 행동 평가를 실행·완료했다고 보고하지 않는다. Gate 직전 정체, 통과 후 정지, 왕복, 조기 실패의 학습 결과는 미검증이다. 초기 weight 선택과 거리 왕복 항의 대수적 상한만 확인한 상태다. `logs/rsl_rl`을 수정하지 않았다.

## 최종 검증과 측정

- 새 기능 CPU 테스트: 검토 보완 후37개 통과. Actor/Critic forward·gradient·TorchScript export, 실제 mesh ray·노출·최대 타겟 조각, Gate 조건별 위반, 초기 자세 비용, 압착 sample 평균, Sweep 높이/힘/접촉·dt 경계를 포함한다. ONNX는 adapter 입력 계약을 확인했으며 실제 ONNX 변환 실행은 하지 않았다.
- 전체 활성 패키지 회귀: 검토 보완 전1270 passed,10 skipped,2 failed(105.26초). 두 실패 `test_final_versions.py::test_shelf_termination_is_union` 및 `test_termination_debug.py::test_tasks_use_their_registered_runtime_family`는 시작 커밋 `2b855bc`를 별도 임시 디렉터리에 풀어 동일하게 재현했다. 기존 실패를 수정 범위에 포함하지 않았다. 보완 후 전체 suite를 반복하지 않고 변경 기능37개와 GPU 통합 검사를 재실행했다.
- mypy: 신규 production22파일 통과(`--follow-imports=skip --ignore-missing-imports`). 무타입 함수 본문 전체를 엄격 검사했다는 의미는 아니다.
- GPU RTX3090:2환경 seed42, 실제 reset·step·부분 reset 격리·centroid/COM·접촉 계측 통과. 제어된 sample replay에서 Gate 달성 step의 보상 단계, 같은 step timeout 성공, 선택 환경만 phase 초기화를 확인했다. replay는 물리적으로 Gate를 달성했다는 증거가 아니다.
- [GPU 원시 진단](../../03_assets/validation/2026-11-18_stabilize_sweep.json): seed0 전체 reset2157.49ms(초기 cache 포함), seed2 전체87.53ms. 성공 배치의 요청/실제 장애물 평균은 각각3.5/3.5와0.5/0.5다. 실패6배치도 진단에 보존했다.
- 마지막1환경 부분 reset 내부54.54ms, 관측2.035ms. 관측 중 mesh 입력 upload0.311ms·ray0.635ms·mask/hit readback0.171ms·CPU 연결요소0.468ms. 전송 구분을 위한 GPU 동기화 및 계측 비용이 포함되며 장면 계획의 모든 CPU/GPU 전송을 합산한 profiler 결과는 아니다. fallback 시 각 세부 시간을 합산해 Reset 로그에 보존한다.
- 실제 초기4step 평균338.65ms는 lazy/JIT 비용을 포함하므로 정상상태 throughput으로 해석하지 않는다.2048환경 처리량과 학습 iteration 시간은 미검증이다.

## Standards

최초 검토에서 문서화된 규칙 위반은 발견되지 않았다. 역할별 디렉터리, 독립 EnvCfg·runtime·Manager 구성, 기존 환경 불변성을 지켰다. 비차단 Data Clumps 의견1건: 초기 자세의6개 위치 기반 반환값을 여러 함수가 slice/index로 해석했다. `InitialPose` NamedTuple로 바꾸고 모든 호출부를 필드 이름으로 접근하도록 보완했다. 재검토에서 반환값 대응·호출부 누락 없음, 의견 해결을 확인했다.

## Spec

최초 검토에서 확정된 기능 오류나 범위 확대는 없었고, 검증 부분 충족2건이 나왔다. 관측 전송 비용의 분리 기록 부족은 upload/readback/ray/components 측정과 fallback 합산으로 보완했다. 노출·타겟 조각·Gate 거부·비용·Sweep 경계 누락은 테스트37개로 보완했다. 재검토에서 중대한 누락이나 수정 오류 없음으로 확인했다. 학습 iteration 및 행동 평가는 사용자 승인으로 유보된 미검증 범위로 남긴다.

검토 결과: Standards1건 해결(최대 심각도 비차단 유지보수), Spec2건 보완(최대 심각도 검증 부분 충족); 승인된 학습 평가 유보는 남아 있다.

## 최종 대조와 인계

기존 실행 코드 변경은 새 Gym 등록뿐이며 기존 환경의 함수·자산·설정은 수정하지 않았다. 사용자 미추적 연구 패키지와 문서 작업은 보존했다. 문서 인덱스는 이번 환경 항목만 선택적으로 commit하며 다른 작업을 포함하지 않는다. root 구현 commit `c39c904`, 검토 보완 commit `d70802e`다. 변경 문서7개의 수식·링크(내부359개·외부1개) 검사를 통과했다. 코드 staged diff 검사도 통과했다. 기존 인계 문서의 과거 trailing whitespace는 변경하지 않았다.


## 후속 요청에 따른 상세 환경 설명 작성

사용자가 현재 환경을 상세하게 설명하는 문서 하나를 요청했다. 기존 [환경 안내](../environments/STABILIZE_SWEEP.md)를 짧은 요약에서 현재 구현의 독립 설명서로 확장했다. 중복 기준 문서를 만들지 않고 기존 인계·활성 환경 링크의 표시를 갱신했다. 코드 기준은 `d70802e`, 문서 연결 포함 root 기준은 `3a94b60`이다.

실제 Env/Scene/Action/Observation/Reward/Termination/Curriculum/PPO Cfg, runtime, reset·surface·contact·state helper 및 직접 사용하는 공용 함수를 대조했다. Scene·물성의 생성 시점과 reset 난수,4후보 IK와 자기충돌 예외, RED+로봇 금지영역, 관측2회 fallback, 표면점·centroid·COM 구분,67D+64D 입력 순서, 손 제어 clamp와 raw action 이력,100Hz Gate와50Hz 보상 경계, 보상 수식·dt·전체 공통 비용, 종료·집계·학습 일정과 실행 방법을 기술했다.

현재 구현상의 구체적인 차이도 명시했다. 노출20%는 면적이 아닌 투영 가로 폭이며 초기 시각에 로봇 가림은 포함하지 않는다. 목표 Z는 초기 link root 높이이고 거리 평가는 XY다. 자기충돌 reset 검사는 PhysX self-collision 활성화와 다르다. 공통 선반 비용의1.06m와 종료의1.05m, 거리 성공의 엄격한3cm 경계, raw F/T 변화 cap1과 제거된 누적5% 상한을 구분했다. 과거 검증 결과와 승인된 Ticket10 행동 평가 미완료 상태를 보존했다.

설명서의 수식 검사와 코드 경로를 포함한 링크 검사(내부5개·외부13개) 및 해당 파일 `git diff --check`를 통과했다. 최종 인계·활성 안내·로그를 포함한4개 문서도 수식·링크·diff 검사를 수행했다. 실행 코드·설정·자산·학습 로그는 변경하지 않았고, 문서 작업에서 CPU/GPU 테스트나 학습을 새로 실행하지 않았다. 문서의 실제 UI 렌더링은 미확인이다.


## 후속 수정: 목표 재추출 없는 초기 자세로 reset IK 오류 해결

### 요청·재현·원인

사용자가 학습 시작의 `RslRlVecEnvWrapper.__init__ → env.reset()` 오류 수정을 요청했고, 설계 대안 질문에 **“재추출 없이 초기 자세 조건 변경”**을 선택했다. 이 결정은 앞의 초기 조건 유지 결정을 대체한다. 기존 `Inspire-Stabilize-Sweep-v0`에 직접 적용하며 새 환경 ID를 만들지 않는다. 기준 root는 `3a94b60`, 실행 코드 기준은 `d70802e`이고 앞 절의 문서 작성 변경과 다른 사용자 작업이 있는 작업트리를 보존했다.

4환경·seed42에서 사용자 trace와 같은 env1·같은4개 희망 위치·위치 오차 약0.18–0.20m를 재현했다. 실제 USD에서 얻은 FK chain·IK 입력을 CPU로 옮겨 기본 seed 문제, 위치+방향 도달성, frame/Jacobian 오류를 구분했다. 512개 초기 관절값·480회 반복으로도 기존 자세는 수렴하지 않았으며 별도 SciPy 풀이에서도 위치+방향 잔차가 남았다. 위치만의 해는 수렴했고 수치 Jacobian과 구현 Jacobian도 일치했다. 고정 손 방향 때문에 손목이 로봇에서 멀어지는 것이 핵심 원인이었다. 이는 모든 가능한 풀이에 대한 수학적 불가능성 증명으로 기록하지 않는다.

손목을 베이스 쪽으로 회전한 뒤 남은 경계 배치에서는 팔뚝–선반 충돌 또는 IK 미수렴을 확인했다. 실제 충돌 형상·고정 타겟/목표를 저장한 반복 검사에서 손목 방향과 높이 후보를 조합해 해소했다. 베이스 이동, 목표 재추출, 충돌 검사 완화, IK 허용오차 확대는 적용하지 않았다.

### 변경 전후와 영향

- 이전: 기본 roll/pitch·기본 FK 높이+1cm 고정, XY±1cm/yaw±10도4후보. 일부 정상 추출 목표에서 학습 시작 전 실패.
- 이후: 손바닥 법선은 목표 방향으로 유지하고, 법선 주위 회전으로 EEF→손목 부착 축을 수평 베이스 방향에 정렬한다. 부착 축은 실제 EEF offset의 역변환으로 계산하며 로봇 위치나 frame 수치를 하드코딩하지 않는다.
- 기본 높이 `h0`에 대해 `(높이, 손목 고도각)`은 `(h0,0°)`, `(h0+4cm,−10°)`, `(h0+4cm,−20°)`, `(h0+6cm,−10°)`의 최대4후보다. 성공 행은 고정하고 실패 행만 다음 후보로 이동한다. 추가 자세 난수는 없으며 기존 XY/yaw jitter는 유지한다.
- 후보마다 실제 손 정점으로 명목 표면 간격5cm를 계산하고 기존 Warp IK·관절 범위·충돌 검사를 통과해야 채택한다. 모두 실패하면 자세·오차·충돌·높이·고도각을 담아 중단한다.
- 타겟·목표 분포, 목표6–12cm·제외각30도, 베이스 위치, 손 관절0rad, 최대4후보, 손 내부 기존 겹침만 제외하는 정책, 장애물·시각 fallback은 유지한다. 초기 팔/손 방향과 일부 행의 높이가 달라져 로봇 공간 기반 장애물 배치와 초기 로봇 관측은 달라질 수 있다.
- 변경 production 파일은 전용 `mdp/common/stabilize_sweep_reset.py`와 `mdp/event_functions/stabilize_sweep.py`뿐이다. 공유 IK solver와 기존 Finger 계열·보상·관측 차원·Gate·종료·PPO 설정은 변경하지 않았다.

### 회귀 검사와 실행

영구 검사 `check_stabilize_sweep.py`에 학습 래퍼의 첫 reset, 병렬 환경 수 선택, 타겟·목표 추출 횟수 및 실제 배치/명령 대조, IK 허용오차 검사를 추가했다. 수정 전에 기본4환경 seed42로 사용자 오류를 다시 검출했다. 예전 검사는 감사 중 IK 실패를 기록만 하고 PASS를 출력했지만, 이제 하나라도 실패하면 실패 처리한다.

```bash
WARP_CACHE_PATH=/tmp/stabilize_warp_cache PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q
/home/min/.local/bin/mypy --follow-imports=skip --ignore-missing-imports src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_reset.py src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/stabilize_sweep.py
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 4 --audit-resets 32 --output /tmp/stabilize_reset_fix_4.json
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 64 --audit-resets 32 --output /tmp/stabilize_reset_fix_64.json
```

CPU38개와 수정 production2파일 mypy가 통과했다. CPU 새 회귀는 허용 목표 방향10개에서 손바닥 법선·손목 방향·표면 간격·입력 높이 보존을 검사한다. 전체 패키지 회귀는 이번 전용2파일 수정에서 반복하지 않았으며 앞의 기존 실패2개 판정은 유지한다.

4환경 통합 검사는 seed42 학습 래퍼 첫 reset, seed0–31의128배치 행, 타겟·목표 추출1회 및 커밋 결과 일치, 실제 step·접촉 계측, 부분 reset 격리, 제어된 Gate replay·timeout 경계를 모두 통과했다. 이 감사의 최대 IK 위치 오차는0.4701mm, 회전 오차는0.002710rad로 기존 허용오차0.5mm·0.003rad 안이다.


64환경 통합 검사도 seed42 학습 래퍼 reset과 seed0–31의2,048개 reset 행을 모두 통과했다. 같은 무재추출·실제 step·접촉·부분 reset·Gate 경계 검사가 통과했으며 최대 IK 위치 오차0.4979mm, 회전 오차0.00299955rad였다. 감사 batch 전체 reset 시간 중앙값은4환경143.78ms,64환경1,489.44ms이며 평균 후보 횟수는 각각1.046875·1.033203이다. 이 값은 관측·진단을 포함한 reset 호출 시간이며 학습 iteration throughput은 아니다. [수정 전 재현 및 최종 GPU 원시 진단](../../03_assets/validation/2026-11-18_stabilize_sweep_reset_fix.json)에 결과를 보존했다.

최종 대조: 전용 자세 계산과 후보 선택 외 production 변경 없음, 타겟·목표 재추출 없음, 공유 IK/관절 한계/충돌 검사 보존, 기존 환경과 사용자 작업 보존을 확인했다. 개발 명세 FR-03·T03·제외 범위, Ticket02와 현재 상태, 상세 환경 설명, 활성 안내·인계를 최신 사용자 결정으로 갱신했다. 과거 실패 수치는 수정 전 이력으로 남겼다. 임시 진단 스크립트와 입력은 `/tmp/stabilize_sweep_reset_debug`로 모으고 영구 회귀만 패키지에 남긴다. 학습 로그는 건드리지 않았다.

미검증:2,048개 환경의 동시 실행·장기 반복 reset의 모든 가능한 조합·PPO 학습 iteration 및 실제 안정화/Sweep 행동 성능. Gate replay 검사는 물리적인 안정화 달성 증거가 아니며 Ticket10 행동 평가 미완료는 유지한다.

변경 문서6개의 수식 검사와 링크 검사(내부315개·외부14개), root 및 대상 문서의 `git diff --check`를 통과했다. 영구 실행 코드에 임시 probe 출력이 남지 않았음을 확인했다. 문서 실제 UI 렌더링은 미확인이다.


## 후속 수정: 오른손 손바닥 방향 축 정정

사용자가 오른손 손바닥이 로봇이 선반을 바라볼 때 왼쪽을 향해야 하는데 오른쪽을 향한다고 지적했다. 방향 기준을 확인한 뒤 추가 확인에서 **“좌우 목표 유지, 손바닥 축만 수정”**을 선택했다. 타겟·목표 분포나 초기 자세 후보 정책을 바꾸지 않고 기존 Stabilize 환경의 축 판정을 직접 수정한다.

실제 오른손 USD의 손바닥 센서 바깥 +Z축을 joint-frame FK와 현재 EEF frame으로 변환한 결과 약 `[-0.00000415, 0.00000751, 1.00000060]`이었다. 즉 손바닥은 EEF +Z이며 기존 코드의 −Z는 손등이었다. 기본 관절 자세에서 실제 손바닥은 선반 −Y(로봇 기준 왼쪽)를 향하지만, reset helper가 반대 축을 목표로 정렬해 왼쪽 목표에서 손등을 향하게 했다.

`stabilize_sweep_reset.hand_pose`의 명목 정렬과 법선 주위 회전에 쓰는 축을 −Z→+Z로 정정했다. 실제 손 정점의 표면 지지점도 수정된 자세로 계산하므로 명목5cm 간격은 유지한다. 좌우 목표, 목표 재추출 금지,4후보 높이·손목 기울기, XY/yaw jitter, 실제 충돌 검사, 기존 손 내부 겹침 예외, Warp IK 허용오차는 유지한다. 공유 solver·Scene·runtime·보상·관측·종료·PPO 및 다른 환경은 수정하지 않았다.

이전 CPU 테스트도 잘못된 −Z 가정을 사용했으므로 실제 자산의 +Z를 기준으로 수정해 기존 코드에서2개 실패를 먼저 확인했다. 축 수정 후38개 테스트가 통과했고 수정 production1파일의 mypy도 통과했다. GPU 영구 검사에는 helper 축을 재사용하지 않고 실제 `inspire_palm_force_sensor` body quaternion으로 구한 바깥 법선과 목표 방향의 cosine을 검사하도록 추가했다. 기존 yaw±10도와 IK 오차를 고려해 모든 reset 행에서 cosine>0.98을 요구한다. 앞의 IK 수정 검사 통과만으로는 실제 손바닥 면의 정렬까지 검증하지 못했던 부분을 보완한다.


최종 GPU 결과:4환경 및64환경 각각 seed42 학습 래퍼 첫 reset과 seed0–31 반복 reset(128개·2,048개 행)이 모두 통과했다. 실제 손바닥–목표 cosine 최솟값은 0.98463112(각도 약10.058도)로 기존 yaw±10도와 IK 회전 허용오차0.003rad를 반영한 범위 안이었다. 목표 재추출 없음, 기존 IK 허용오차, 실제 step·접촉 계측·부분 reset·제어된 Gate/timeout 경계도 통과했다. [실제 손바닥 축 및 GPU 원시 진단](../../03_assets/validation/2026-11-18_stabilize_sweep_palm_axis_fix.json)을 보존했다. 실행 명령은 앞 절과 같으며 출력 파일을 `/tmp/stabilize_palm_fix_4.json`, `/tmp/stabilize_palm_fix_64.json`으로 지정했다.

최종 대조에서 이번 요청의 production 차이는 전용 `hand_pose`의 법선 축2곳과 설명뿐이며 후보 선택 event 파일은 직전 수정 완료본과 동일하다. 기존 사용자 작업과 학습 로그를 보존했다. 명세·상세 설명·인계·활성 안내를 정정했다. 새 방향에서 장기 학습·2,048환경 동시 실행·GUI 육안 확인은 하지 않았으며 실제 물리 자산의 방향을 수치로 검증했다.

변경 문서5개의 수식·링크(내부314개·외부14개) 검사와 root/대상 문서 diff 검사가 통과했다. 문서 UI 렌더링은 미확인이다.


## 후속 수정: 손바닥은 항상 왼쪽, 상판 기준 낮은 초기 자세

### 요청·원인·변경

사용자는 오른쪽으로 밀 때 손등을 쓰므로 손바닥은 여전히 로봇이 선반을 볼 때 왼쪽이어야 한다고 정정했고, 높은 Z 때문에 물체가 손 아래에 들어가는 문제를 지적했다. 이전의 “손바닥 축만 수정”을 모든 목표에 손바닥을 정렬하는 의미로 해석했던 부분을 이번 명시적 정정에 맞춰 변경한다. 좌우 목표 분포 및 타겟·목표 재추출 금지는 유지한다.

실제 자산 입력을 보존한64행 seed3 재생에서 이전 helper는38행에서 손바닥이 선반 +Y를 향했고26행에서 손 충돌 형상의 최하단이 타겟 상단보다 높았다. 이전 첫 후보 EEF는 상판 위 약16.15cm이고 실패 후보에서는22.15cm까지 올라갔다. 타겟은 높이9–11cm이므로 단순한 EEF 높이 유지로는 접촉 높이를 보장할 수 없었다.

- 방향: `goal direction Y>0`인 오른쪽 목표에서는 실제 손바닥 법선(+Z)을 목표 반대 방향으로 정렬한다. 왼쪽 목표는 같은 방향으로 정렬한다. 따라서 손바닥은 항상 선반 −Y 반구를 향하며 오른쪽은 손등(−Z)으로 민다. 대각선 목표의 정렬 및 기존 yaw±10도 jitter는 유지한다.
- 높이: 회전된 실제 손 충돌 정점의 최하단을 구해 타겟 밑면(상판) 위5mm에 맞춘다. EEF Z를 기본 FK 높이에서 복사하지 않는다. 현재 수평 손목 후보의 EEF Z는 선반 로컬 약1.102714m, 즉 상판 위 약5.27cm다.
- 후보: 기존 높이+4–6cm/음의 손목 고도각을 폐기하고 손목 고도각 `0°,+2°,0°,+2°`를 사용한다. 각 후보는 동일한5mm 하단 여유를 유지하며 실패 행만 기존 XY/yaw 난수를 새로 추출한다. 낮춘 수평 자세에서 남는 경계 IK 실패를 작은 양의 고도각으로 보완한다. 모든 후보는 기존 IK 허용오차·관절 한계·충돌 검사를 통과해야 한다.
- 표면 간격: 목표 방향의 실제 손 정점 지지점을 그대로 사용하므로 손바닥/손등 각각 명목5cm 간격을 계산한다. 최대4후보·손0rad·목표6–12cm·30도 제외각·로봇 위치·기존 손 내부 겹침만 제외하는 정책을 유지한다.

### 회귀 및 검증 절차

CPU 회귀2개를 먼저 새 방향·높이 조건으로 바꿔 기존 production에서 실패를 확인했다. 수정 후 해당 회귀가 통과했으며, 다른 타겟 크기·높은 기본 EEF·양쪽 목표·0°/+2° 손목·yaw±10도 끝값에서도 손 하단5mm가 유지되는 회귀를 추가했다. 전용 CPU 테스트39개 및 production2파일 mypy가 통과했다. 첫 pytest 실행의 ROS 자동 plugin 오류와 Warp cache 쓰기 제한은 각각 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `WARP_CACHE_PATH=/tmp/stabilize_warp_cache`로 환경을 맞춰 해결했으며 production 원인은 아니었다.

영구 GPU 검사에서는 실제 손바닥 센서 body quaternion으로 왼쪽 방향을 검증하고, 오른쪽 목표에서 손등 법선과 목표를 대조한다. 실제 reset EEF pose에 충돌 정점을 변환하여 하단 여유5mm(허용차1mm) 및 타겟 높이 구간과의 겹침도 검사한다. 기존 학습 래퍼 첫 reset·무재추출·IK·부분 reset·실제 step·접촉·제어된 Gate/timeout 검사는 유지한다.

최종 GPU 결과:4환경·64환경 각각 seed42 학습 래퍼 reset과 seed0–31의128개·2,048개 reset 행이 모두 통과했다. 손바닥이 항상 왼쪽을 향했고 목표 접촉면 cosine 최솟값은 0.98491549였다. 실제 손 하단 상판 여유는 4.54–5.04mm다. 무재추출·기존 IK 허용오차·충돌 검사·실제 step·접촉 계측·부분 reset 격리·제어된 Gate/timeout 경계도 통과했다. [수정 전 재생 수치 및 최종 GPU 원시 진단](../../03_assets/validation/2026-11-18_stabilize_sweep_left_low_fix.json)을 기록했다.

```bash
WARP_CACHE_PATH=/tmp/stabilize_warp_cache PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q
/home/min/.local/bin/mypy --follow-imports=skip --ignore-missing-imports src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_reset.py src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/stabilize_sweep.py
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 4 --audit-resets 32 --output /tmp/stabilize_left_low_4.json
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 64 --audit-resets 32 --output /tmp/stabilize_left_low_64.json
```

최종 대조: 이번 요청 직전 백업과 비교하여 production은 전용 `hand_pose`의 좌우 정렬·정점 기반 높이와 전용 reset event의4후보·높이 인수 전달만 수정했다. 공유 IK solver·충돌 판정·Scene·runtime·보상·관측·종료·PPO 및 기존 다른 환경은 변경하지 않았다. 손이 낮아지면서 초기 로봇 점유 공간에 따른 장애물 배치와 초기 로봇 관측은 달라질 수 있다. 개발 명세 FR-03/T03·Ticket02·상세 설명·인계·활성 안내를 최신 사용자 정정과 대조했다. 이전 검증 결과는 이력으로 보존했다. 사용자 작업과 학습 로그를 보존했다.

미검증: GUI 육안 확인, 장기 학습·2,048환경 동시 실행, 초기 자세 이후 정책이 선택하는 모든 궤적에서 손 아래 통과 방지, 실제 안정화/Sweep 학습 행동 성능. 이번 변경은 초기 자세에 적용되며 동작 중 Z를 강제 제한하지 않는다. Ticket10 행동 평가 미완료는 유지한다.

변경 문서6개의 수식 및 링크 검사(내부319개·외부14개), root/대상 문서 diff 검사가 통과했다. 문서 UI 렌더링은 미확인이다. 임시 재생·격자/seed 실험과 실행 로그·수정 전 백업은 `/tmp/stabilize_sweep_reset_debug/left_low_fix`에 모았으며 production에 임시 진단 코드는 남기지 않았다.


## 후속 수정: IK/충돌 실패 행의 제한적 배치 재추출

### 요청·설계 판단

사용자는4후보가 모두 실패하면 학습이 중단되는 방식이 불안정하다고 지적하고, Termination을 유발하는 등의 방법으로 다른 환경 배치를 만들 수 있는지 요청했다. 이전의 무재추출 조건은 이 최신 실패 복구 요청으로 변경한다. 이 실패는 정책 행동 이전의 reset 도중 발생하므로 Termination을 만들어 잘못된 초기 자세를 한 step 실행하는 대신, reset 내부에서 실패한 배치를 거부하고 새 배치를 준비한다. 초기화 실패를 episode 실패·timeout·보상·성공률에 섞지 않는다.

구현 기본 상한은 추가 재추출8회다. 최초 포함9배치×배치별4자세, 환경당 최대36개 IK 후보로 유한하게 제한한다. 사용자가8회라는 수치를 지정한 것은 아니며, 무한 reset을 방지하기 위한 구현 기본값이다. `reset_scene`의 `max_layout_resamples` 인자로 조정할 수 있다. 이 상한까지 지속 실패하면 설정/자산/도달 가능성 문제를 진단할 수 있도록 명시적 오류를 유지한다. 모든 종류의 오류에서 학습을 계속하는 처리는 아니다.

### 변경 전후·영향

- 이전: 한 배치에서4개 자세가 실패한 환경이 하나라도 있으면 즉시 예외로 학습 중단.
- 이후: `choose_initial_pose`가 성공 mask·진단과 pose 계획을 반환하고 `plan_initial_layout`이 실패한 행만 타겟·목표를 다시 추출한다. 성공한 행의 물체 위치·목표·관절·충돌 형상·자세를 보존한다. 재추출에서도 동일한 XY 범위·목표6–12cm·30도 제외각을 사용한다.
- 모든 행이 유효해진 뒤 장애물 배치→시각 snapshot→simulator 반영을 한 번 수행한다. 재시도 도중 physics step, 실패 자세의 simulator write, Manager 종료/보상 갱신은 없다. 최초 학습 래퍼 reset과 episode 후 자동 reset 모두 같은 경로를 사용한다.
- geometry의 half-extents는 batch expanded view일 수 있으므로 행 병합 전에 pose boxes를 복제한다. 성공 행을 덮어쓰거나 공유 expanded storage에 쓰는 일을 피한다.
- IK/충돌 결과의 거부만 복구한다. solver 예외·자산 오류·시각 snapshot 실패 등 일반 오류는 포괄적으로 잡아 숨기지 않는다.
- 최종 장면 분포는 기존 제안 분포에서 IK·충돌 검사를 통과한 배치에 조건부가 된다. 형상·scale·물성은 바꾸지 않는다. 성공한 행의 목표·초기 자세는 그대로지만 장애물 난수는 추가 재추출의 RNG 소비에 따라 달라질 수 있다. 동일 seed·동일 실패 결과에서 재현 가능하다.
- `Reset/ik_attempts`는 재추출한 배치를 포함한 총 후보 수 평균으로 확장한다. `Reset/layout_resamples`와 `Reset/ik_recovery_fraction`을 추가하여 재추출 횟수와 복구된 환경 비율을 기록한다.

### 회귀와 실제 검증

CPU planner 회귀를 먼저 추가해 기존 코드에서 미구현 실패를 확인했다. 비연속 env ID `[2,0]` 중 실패 행만 재추출하고, 성공 행 pose/boxes와 target·goal을 보존하며, IK 시도를 합산하는 동작을 검사한다. 같은 seed의 재현성과 최초 포함3배치로 낮춘 예산의 정확한 상한, 일반 solver 예외 전파도 확인한다. simulator가 없는 계획 단계에서 검사하므로 실패 pose를 물리 상태에 반영할 수 없다.

영구 GPU 검사에 `--inject-reset-failures`를 추가했다. 실제 IK와 충돌 계산은 수행하되 특정 행의 성공 flag만4회 연속 거부하여 초기 배치 실패를 만든다. 첫 학습 래퍼 reset에서 IK 실패, 부분 reset에서 충돌 실패, timeout 후 자동 reset에서 IK 실패를 각각 주입한다. 복구 이후 정상 관측/보상·episode 길이, 성공한 행의 배치·목표, 비대상 행의 상태/시간, 기존 timeout 결과·Gate 상태·통계를 대조한다. 일반 seed 감사와 의도적 실패 주입의 결과는 별도 키로 기록한다.

최종 결과:CPU41개와 변경 production1파일 mypy가 통과했다. GPU4환경·64환경 모두 세 가지 실패 주입을 복구했다. 정상 seed0–31의128개·2,048개 행도 전부 통과했으며 정상 감사에서는 추가 재추출0회였다. 주입된 배치는 새 타겟·목표로 복구되고 정상 초기 관측 및 학습 step이 이어졌다. 실제 손바닥 왼쪽·상판 하단 여유·IK 허용오차·물리 접촉·부분 reset·Gate/timeout 검증도 유지했다. [최종 GPU 원시 결과](../../03_assets/validation/2026-11-18_stabilize_sweep_reset_recovery.json)를 보존했다.

```bash
WARP_CACHE_PATH=/tmp/stabilize_warp_cache PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q
/home/min/.local/bin/mypy --follow-imports=skip --ignore-missing-imports src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/stabilize_sweep.py
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 4 --audit-resets 32 --inject-reset-failures --output /tmp/stabilize_reset_recovery_4.json
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --num-envs 64 --audit-resets 32 --inject-reset-failures --output /tmp/stabilize_reset_recovery_64.json
```

최종 대조:production 변경은 Stabilize 전용 reset event의 결과 반환·실패 행 재계획·진단 지표뿐이다. 직전 손바닥/높이 helper, 공유 IK solver·허용오차·충돌 판정, 자산·관측·보상·종료·커리큘럼·runtime·PPO 설정은 유지한다. 기존 환경과 사용자 변경·학습 로그를 보존했다. 명세 FR-03/T03·Ticket02·상세 설명·인계·활성 안내의 이전 무재추출 조건을 최신 요청에 맞춰 갱신하고 과거 검증은 이력으로 남겼다.

미검증:실제 기하 조건이 연속9배치 실패하는 모든 경우, 장기 PPO 학습·iteration throughput·2,048환경 동시 실행. 실제 IK/충돌의 거부를 인위적으로 주입한 검증이며 자연 발생 실패율을 추정하지 않는다. 재추출 상한까지 실패하는 경계는 CPU에서 확인했다. GUI 및 문서 UI 렌더링은 미확인이다. Ticket10 행동 평가 미완료는 유지한다.

변경 문서6개의 수식·링크 검사(내부321개·외부14개)와 root/대상 문서 diff 검사가 통과했다. 검증 로그는 `/tmp/stabilize_sweep_reset_debug/reset_recovery`에 모았고 production에 실패 주입을 추가하지 않았다. 실패 주입은 명시적 GPU 검증 옵션에서만 실행된다.


## 파생 환경 추가: Stabilize 보상과 Gate 없는 Sweep Only

사용자는 Stabilize 리워드와 Gate를 제거한 추가 환경을 요청했다. 기존 환경 직접 수정이 아니라 현재 `Inspire-Stabilize-Sweep-v0`의 자식 `Inspire-Sweep-Only-v0`를 추가한다. 같은 계열의 역할별 기존 파일에 클래스를 추가하며 폴더나 기존 함수를 이동하지 않았다.

### 부모와의 차이 및 보존

- `SweepOnlyEnvCfg(StabilizeSweepEnvCfg)`와 `SweepOnlyRewardsCfg(StabilizeSweepRewardsCfg)`는 `stage`, `initial_movement`, `initial_rotation`만 None으로 비활성화한다. Stabilize 단계가 없으므로 단계 전용 초기 자세 비용도 제거한다. Gate 이후의 상수 stage 완료 보상도 없다.
- `SweepOnlyEnv(StabilizeSweepEnv)`는 부모 구성·Manager·물리 계측을 초기화한 뒤 전용 `SweepOnlyState(StabilizeState)`를 연결한다. state reset부터 achieved/reward_phase를 True로 유지하고 sample에서 Gate·안정화 점수·초기 자세 비용을 계산하지 않는다. begin/finish와 접촉 이력·거리 감소/멀어짐 수식은 부모를 상속한다. 부모 runtime의 step/reset 본문은 변경하지 않았다.
- Gate를 제거했지만 Sweep의 최근3회 중2회 접촉 인정, count/20, 힘 정렬·크기·높이 조건은 유지한다. 압착 비용은 안정화 전용이 아니므로 유지한다. 부모 contact reducer가 계속 실제 힘·모멘트·load를 계측한다.
- policy67D의 마지막 phase 값은 항상1로 유지한다. 차원을 줄이거나 관측을 추가하지 않는다. obstacles64D·액션12D·OSC·손 제어·시각 snapshot·초기 자세·IK 실패 재추출·10초 종료·성공 판정·나머지 보상·커리큘럼은 동일하다.
- `SweepOnlyPPORunnerCfg(StabilizeSweepPPORunnerCfg)`는 experiment_name만 `inspire_sweep_only_v0`로 바꿔 학습 로그를 구분한다. 모델·optimizer·PPO hyperparameter·rollout 길이·export 계약은 그대로다.

### 검증 및 최종 대조

새 task 등록과 Gate 우회 회귀를 먼저 추가해 기존 코드에서 미등록/미구현 실패를 확인했다. 자식 상태는 Gate 조건을 의도적으로 위반한 입력에서도 Sweep을 유지하고, 기존 접촉 history/정규화 수식으로 두 번째 인정 접촉에서 밀기 보상을 계산한다. 멀어짐 비용과 부분 reset 이력 격리도 확인하며 부모는 같은 입력에서 여전히 Gate 이전 상태를 유지한다. 전체 전용 CPU43개 및 변경5파일 mypy가 통과했다.

GPU 영구 검사에 `--task Inspire-Sweep-Only-v0` 선택을 추가했다. 실제 EnvCfg 전체 to_dict를 부모와 대조해 보상3개만 다름을 확인했고 PPO 전체 대조에서 experiment_name만 다름을 확인했다. 실제 활성 RewardManager에서3개 안정화 term이 없고 squeeze가 있음을 확인했다. 등록 task의4환경에서 seed0–7 reset, 첫 물리 step부터 phase1, 부분 reset/timeout 자동 reset에서도 phase1, Gate 카운터0 유지, 실제 접촉 계측 및 IK/충돌 실패 주입 복구를 통과했다. [원시 결과와 부모 정의 해시](../../03_assets/validation/2026-11-18_sweep_only.json)를 보존했다.

```bash
WARP_CACHE_PATH=/tmp/stabilize_warp_cache PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q
/home/min/.local/bin/mypy --follow-imports=skip --ignore-missing-imports src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/common/stabilize_sweep_state.py src/inspire_sweep_baseline/inspire_sweep_baseline/runtime/stabilize_sweep.py src/inspire_sweep_baseline/inspire_sweep_baseline/envs/stabilize_sweep_envs.py src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/rewards/stabilize_sweep.py src/inspire_sweep_baseline/inspire_sweep_baseline/agent/stabilize_sweep_ppo_cfg.py
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --task Inspire-Sweep-Only-v0 --num-envs 4 --audit-resets 8 --inject-reset-failures --output /tmp/sweep_only_4.json
```

부모 정의 대조: 변경5모듈의 기존 class/function 모두 작업 전 AST 해시와 일치했다. 부모 task 등록을 유지하고 새 task만 추가했다. Scene·Actions·Observations·Commands·Events·Terminations·Curriculum과 PPO의 차이는 실제 전체 설정 대조로 확인했다. 기존 사용자 변경과 학습 로그를 보존했다.

미검증:장기 PPO 학습·부모 대비 학습 성능·대규모 throughput·GUI 육안 확인. 실제 GPU 등록/reset/step 통과는 학습된 조작 성능의 증거가 아니다. 기존 Stabilize 명세/티켓은 부모 계약으로 유지하고 자식 차이는 상세 환경 문서의 별도 절에 기록한다.

수식 검사5개 문서 및 root/대상 문서 diff 검사가 통과했다. 링크 검사에서는 새 링크 오류가 없으나 기존 README의 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 참조1개가 누락 경로로 검출됐다. HEAD의 README에도 같은 참조가 있음을 확인했으며 이번 요청과 무관하여 변경하지 않았다. 문서 저장소의 변경4개 문서만 검사하면 링크 오류가 없다. 임시 GPU 로그와 부모 정의 기준 파일은 `/tmp/stabilize_sweep_reset_debug/sweep_only`에 모았다.


## 파생 환경 추가: Finger 초기화 Test2종

### 요청 및 범위

사용자가 학습 iteration 약90초를 보고하고, 직접 최적화보다 우선 각 환경에 `-Test`를 붙여 기존 Finger와 같은 초기화를 사용하도록 요청했다. 초기 관측 범위를 확인한 결과 **초기 배치·IK만 교체하고 대표 표면점 관측 유지**를 선택했다. 따라서 이번 작업은90초 원인 전체 분석이나 PPO/physics 최적화가 아닌 초기화 비교 환경 추가다.

`Inspire-Stabilize-Sweep-v0-Test`와 `Inspire-Sweep-Only-v0-Test`는 각각 기존 EnvCfg를 직접 상속하고 같은 부모 runtime을 재사용한다. Finger-v0/v1/v2와 ForceDirection의 공통 `SweepSimpleEventsCfg`가 사용하는 `fast_reset_scene`을 그대로 호출한다. Hard 계열의 변경 분포는 사용하지 않는다. Test EventCfg는 Finger reset term을 복사하여 파라미터를 보존하고 callback만 표면 관측 어댑터로 교체한다.

### 차이·보존·제약

- Finger 원형 장애물 배치·RED ZONE·단일 Warp IK를 재사용한다. EEF는 선반 앞 X0.28–0.30m, 타겟의 반대 Y쪽0.10–0.18m, 기본 FK 높이+1cm±2cm이며 방향은 기본 quaternion이다. 원본 Stabilize의 목표 정렬·표면5cm·손 하단5mm 초기 자세와 다르다.
- 전용 robot collision hull 구성·self-collision LP 검사·4자세 후보/8회 재추출은 호출하지 않는다. 단일 IK 실패나 원형 배치 불가 예외는 Finger 원본 처리 그대로다. 기존 원본2환경의 회복 로직은 그대로 유지한다.
- 어댑터는 Finger가 커밋한 물체 pose를 선반 frame으로 복원해 기존 snapshot 함수를 호출한다. 대표 표면점·mask 노출 조건·분리 component 및 target-only fallback을 보존한다. fallback으로 제거할 장애물만 선택 환경의 물리 state·중력 mask와 배치 cache에 반영한다. physics step은 없다.
- Finger가 만든 중심점 관측 buffer는 정책에 연결하지 않는다. 기존 표면점 world cache만 갱신한다. 정책 관측67D/obstacles64D, 동작12D, Gate 유무·보상·종료·센서·커리큘럼은 부모와 같다. 물성·자산 분포도 그대로다.
- PPO는 각각 experiment_name에 `_test`만 붙인다. 기존 체크포인트나 학습 로그를 변경하지 않는다. 부모 클래스 정의와 Finger 공유 코드의 원본 해시를 기록해 변경하지 않았음을 대조한다.
- reset 비용 진단에 `Reset/finger_placement_ms`를 추가한다. 표면점 생성은 유지되므로 그 비용까지 제거됐다고 주장하지 않는다. Test에서 수집하지 않는 IK 복구 횟수는0, 단일 IK 시도는1로 기록한다.

### 검증

CPU 회귀에서 두 task가 각각 부모 runtime을 재사용함을 확인하고, 어댑터의 실제 표면점 cache 반영 및 target-only fallback의 선택 행 state/중력 갱신과 다른 환경 불변을 검사한다. 전용45개 테스트가 통과했다.

첫 GPU 실행에서 EventManager가 `**finger_params`를 필수 파라미터로 오인하여 구성 검증을 거부했다. 공개 event 함수의 인자를 Finger와 같은 명시적 signature로 바꿔 수정했다. 임의의 Manager 우회 없이 실제 reset event 경로에서 검증한다.

영구 GPU 검사에 두 Test task 선택을 추가했다. 실제 EnvCfg 전체 대조에서 object_spawn event만 변경됨과 PPO 로그 이름만 변경됨을 확인한다. 동일 자산·seed123의 Finger 원본 함수와 Test reset을 대조해 관절·타겟·목표 및 관측 fallback 뒤 남는 물체 pose 일치를 확인한다. 전용 `_stabilize_robot_geometry`가 생성되지 않음과 표면점이 centroid로 바뀌지 않았음도 검사한다. 부모별 실제 step·Gate 유무·부분/자동 reset·timeout·실제 contact probe 검증을 재사용한다.

최종 GPU 결과:Stabilize Test4환경·Sweep Only Test64환경에서 각각 seed0–7 감사32개·512개 행이 모두 성공했다. 학습 래퍼 첫 reset, Finger 원본 함수와 동일 seed 결과 대조, 실제 reset/step·부분 격리·자동 reset·부모별 Gate 동작·접촉 계측이 통과했다. 변경4파일 mypy도 통과했다. [원시 검증 및 부모/Finger 기준 해시](../../03_assets/validation/2026-11-18_stabilize_sweep_finger_tests.json)를 보존했다.

reset 호출 중앙값은4환경143.79ms·64환경1,993.98ms, Finger 배치·IK 호출만은18.53ms·19.81ms였다. 환경당 표면점 생성 중앙값은9.96ms·10.67ms다. 실제 학습 iteration90초를 재현/분해하거나 동일 조건 A/B throughput을 측정하지 않았으므로90초 문제가 해결됐다는 결론을 내리지 않는다. 공유 센서/보상/관측/정책 처리도 최적화하지 않았다. 이번 Test는 초기화 비교를 위한 환경이다.

```bash
WARP_CACHE_PATH=/tmp/stabilize_warp_cache PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/inspire_sweep_baseline/tests/test_stabilize_sweep.py -q
/home/min/.local/bin/mypy --follow-imports=skip --ignore-missing-imports src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/event_functions/stabilize_sweep.py src/inspire_sweep_baseline/inspire_sweep_baseline/mdp/events/stabilize_sweep.py src/inspire_sweep_baseline/inspire_sweep_baseline/envs/stabilize_sweep_envs.py src/inspire_sweep_baseline/inspire_sweep_baseline/agent/stabilize_sweep_ppo_cfg.py
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --task Inspire-Stabilize-Sweep-v0-Test --num-envs 4 --audit-resets 8 --output /tmp/stabilize_finger_test_4.json
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --task Inspire-Sweep-Only-v0-Test --num-envs 64 --audit-resets 8 --output /tmp/sweep_only_finger_test_64.json
```

최종 대조:기존5모듈의 class/function 정의 AST와 Finger 공유3파일 전체 해시가 작업 전과 동일하다. 부모 reset/runtime·보상·Gate/phase state·관측·action·termination·curriculum·PPO 연산은 수정하지 않았다. 신규 event adapter·Cfg/PPO 자식·task 등록과 검증만 추가했다. Test EnvCfg 전체의 차이는 event1개이고 PPO 전체의 차이는 experiment_name1개임을 실제 로딩 결과로 확인했다. 기존 학습 로그 및 사용자 작업을 보존했다.

미검증:2,048환경 실제 학습 iteration·장기 PPO·완전한 시간 병목 분석·모든 seed에서의 Finger 단일 IK 성공. 표면 관측은 사용자 선택에 따라 유지하므로 per-env ray/mask 비용이 여전히 있다. GUI 및 문서 UI 렌더링은 확인하지 않았다.

수식 검사5개 문서와 root/변경 문서 diff 검사가 통과했다. 문서 저장소의 변경4개 문서 링크 검사도 통과했다. README의 기존 누락 링크는 이전 절의 기록대로 별도 이슈이며 새 링크는 정상 상세 절을 가리킨다. 임시 실행 로그와 기준 해시는 `/tmp/stabilize_sweep_reset_debug/finger_tests`에 모았다.


## 두 Test에 Finger Reach 추가

사용자 요청: “Reach 보상을 추가하는걸 깜빡했네. -Test 에는 추가해줘.” 적용 대상은 `Inspire-Stabilize-Sweep-v0-Test`와 `Inspire-Sweep-Only-v0-Test`다. 앞 절의 초기화 교체 당시에는 부모와 동일하게 Reach가 없었으며, 이번 변경은 두 Test에만 이를 추가한다.

`mdp/rewards/stabilize_sweep.py`에 각 부모 보상 설정을 상속하는 Test 보상 설정을 두고 `SweepSimpleFingerRewardsCfg().reaching.copy()`로 독립된 term을 재사용한다. 두 Test EnvCfg에만 연결했다. 공유 Finger 함수·설정 및 원본 두 보상 클래스는 변경하지 않았다.

수식은 Finger-v0/v1의 `InverseDistanceReach`, weight30, near_radius0.10m, distance_scale0.10m, ee_frame이다. 현재 EEF–타겟 BBOX 중심의 3차원 거리에 대한 역거리 proximity를 초기 EEF–타겟 root의 유효 거리와10초 episode 길이로 정규화한다. RewardManager의 dt 적분을 그대로 적용한다. 접촉·높이·Gate 조건 없이 지급하며, Stabilize Test의 Gate 이후에도 유지한다. 초기 거리 정규화는 선택 행 reset에서만 갱신한다. 관측용 대표 표면점을 보상 계산용 실제 중심점으로 교체하는 작업은 하지 않는다.

최종 대조:실제 등록 EnvCfg 전체를 각 부모와 비교하여 object_spawn event 및 reaching term만 다름을 검사했다. Reach term의 함수·weight·params는 Finger와 일치하며 원본의 reaching은 계속 None이다. 나머지 보상·Gate 유무·표면점 관측·초기화·IK·action·termination·curriculum·PPO는 기존 계약을 보존한다. 학습 로그와 사용자 변경은 보존했다.

검증:CPU45개 통과, 수정 보상/EnvCfg2파일 mypy 통과. 두 Test 각각 GPU4환경·seed0–1의 reset 감사, 학습 래퍼 초기 reset, 동일 seed Finger 배치 대조, 실제 step·부분/자동 reset·Gate 차이·접촉 계측을 통과했다. 새 검사에서는 실제 RewardManager의 reaching 출력과 weight30 적용값을 현재 거리 수식과 대조하고, reset 대상 행의 초기 거리 갱신과 다른 행의 불변을 검사했다. [원시 결과](../../03_assets/validation/2026-11-18_stabilize_sweep_test_reach.json)에 보존했다.

```bash
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --task Inspire-Stabilize-Sweep-v0-Test --num-envs 4 --audit-resets 2 --output /tmp/stabilize_test_reach.json
OPENBLAS_NUM_THREADS=1 /home/min/miniconda3/envs/env_isaaclab/bin/python src/inspire_sweep_baseline/scripts/check_stabilize_sweep.py --headless --task Inspire-Sweep-Only-v0-Test --num-envs 4 --audit-resets 2 --output /tmp/sweep_only_test_reach.json
```

미검증:Reach 추가 후 장기 PPO 학습·학습 행동 개선·iteration time 개선·GUI 및 문서 UI 렌더링. 기존 CPU 검사는 회귀 검증이며 새 Reach 연결과 수치 검증은 위 GPU 통합 검사에 포함했다.

문서 수식 검사5개 파일, 문서 링크 검사4개 파일, root/변경 문서 diff 검사가 통과했다. README의 기존 누락 링크는 앞 절에 기록한 별도 이슈다.
