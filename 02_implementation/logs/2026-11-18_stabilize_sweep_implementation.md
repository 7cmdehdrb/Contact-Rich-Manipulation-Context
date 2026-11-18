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
