# 현재 개발 인계

2026-11-23: **Single Contact Zone3 v0 추가**. `Inspire-Sweep-Single-Contact-Zone3-v0`는 Single Contact v0 직접 자식이다. 목표 방향만 Zone3(선반 +X/6시 ±30°)로 제한하고 Sweep 진행50→100·후퇴−10→−20을 적용했다. 초기 타겟 원판·거리6–12cm·배치/IK·접촉·중심 Reach·관측·제어·종료·PPO는 부모 보존, 로그 `inspire_sweep_single_contact_zone3_v0`. CPU66개·전체 설정 대조·기존 정의/등록 AST 보존 검사 통과. 사용자 요청으로 GPU·Isaac Sim·학습 미실행, 실제 reset/장기 성능 미검증. [환경 계약](../02_implementation/environments/SWEEP_V0.md#single-contact-zone3-v0) · [개발·검증](../02_implementation/logs/2026-11-23_single_contact_zone3_v0.md).

2026-11-22: **Sweep v0·Single Contact v0/v1 공통 action 안정화**. `SweepEnvCfg`에서만 손6D를 [0,1] 비율(0펼침·1굽힘)로 매핑, 손 속도 weight −0.01→−0.03, Arm/Hand action-rate raw cap100, action-limit weight −3.0·raw cap10을 적용했다. 계통 밖 기본 동작·PPO는 보존한다. 기존 rad 출력 checkpoint와 손 의미가 달라 새 학습 기준이다. [계약](../02_implementation/environments/SWEEP_V0.md#행동과-제어) · [변경·검증](../02_implementation/logs/2026-11-22_sweep_action_stability.md).

2026-11-21 후속 **Single Contact v1 구현·등록 완료**. 아래 명세 작성 당시의 미구현 상태를 갱신한다. `Inspire-Sweep-Single-Contact-v1`는 v0 직접 자식이며 Reach5cm/4.9·구역3 +15° 고정점·수평 signed 방향30°/p4·팔 종료−3을 구현했다. 기존 물리 step 루프·부모 함수19개 정의·기존 등록 보존, 전체 Cfg 대조에서 요청한 보상3개 외 차이 없음. CPU196개·RTX4070 GPU4환경11step·부분/자동reset·16환경 PPO1회 업데이트 통과. trace/초기 world pose/모델은 `outputs/sweep_single_contact_v1`, 기존 `logs/rsl_rl` 불변. 성공률·장기 학습 개선은 미검증. [구현 계약](../02_implementation/environments/SWEEP_V0.md#single-contact-v1) · [개발·검증·실행](../02_implementation/logs/2026-11-21_single_contact_v1_implementation.md).

2026-11-21 **Single Contact v1 개발 명세만 작성, 미구현**. v0 직접 상속 예정. 최신 정정으로 Reaching은 이동 접근점까지**5cm** 초과 거리의 대칭 변화·weight**4.9**(기존 성공82개 재계산 약29.84:70.16), 일반 구역1/2/4 접근점은 외접 원 반대편이다. **예외는 구역3(당기기) 전체이며,12시에서 시계방향+15도 단일점을 사용한다. 구역1 예외가 아니다. 접근 방향/반경은 물체 회전에 영향받지 않고 중심 이동만 따라간다.** 면 계수1.5/0.7/중립1 유지, signed 방향30도/p4, Joint 종료 일회-3.0. 거리별 결합·감속·주먹 강제는 제외. [최종 명세](environments/2026-11-21_SINGLE_CONTACT_V1_SPEC.md) · [산정·검증 한계](../02_implementation/logs/2026-11-21_single_contact_v1_spec.md). 환경 등록·소스 수정·학습은 하지 않았다.

2026-11-21 사용자 보상 수정안 정정(미구현): Reaching은 실시간 손–물체 거리의10cm 초과분 감소/증가를 대칭 보상/비용으로 평가하며 최소기록 방식은 폐기한다. Joint 속도 종료 일회−3.0, 손끝/주먹 강제 없음. 거리별 방향·정밀도 결합은 보류. 좌우120도 구역의 오른쪽 손등/왼쪽 손바닥 설정을 코드·13방향 probe로 확인했고 음수 방향 함수 후보 그래프/CSV를 저장했다. [제안·그래프·검증 범위](../02_implementation/logs/2026-11-21_reward_revision_proposal.md).

2026-11-21 후속: **교수님 지시 기반 보상 timeline**. Single Contact 동일128개 초기 scene/관측 bank로0·1000·4000·8000·12000·15800의768episode를 현재 보상으로 재평가했다. 성공률0/29.69/50.00/44.53/50.78/64.06%.15,800 평균 Reach7.012·Sweep3.251·전체9.543, 목표 밖 정지 중 양의 순보상 지속을 확인했다. 원값·가중 rate·dt 적용값·문턱 입력·초기 상태·해시·소스312개 snapshot과약231MiB trace를 `outputs/reward_timeline/model15800_family`에 보관했다. 최종 `reviewed_analysis`. 환경·보상·가중치·학습 로그 불변. [분석·교수님 지시 대조](../02_implementation/experiments/2026-11-21_single_contact_reward_timeline.md) · [계측 변경·검증 한계](../02_implementation/logs/2026-11-21_reward_timeline_instrumentation.md).

2026-11-21: **Single Contact `model_15800` 실제 Play 평가**. wr8/2026-11-20_20-56-01 체크포인트, seed42·43 각64환경의 첫5episode 총640회에서432회 성공(67.50%). 구역별 성공률1/2/3/4=80.00/70.45/6.48/89.40%. 실패는 팔 속도80회·목표 밖 timeout128회, 낙하/전도·선반 실패0회. 구역1은 손등 의도와 달리 분류된 접촉의 손바닥 하중95.98%; 다만 이동 접촉72.42% 미분류. 구역3은 성공7회뿐이며 성공 시 힘 각도34.36°·실패 시65.64°. 환경·보상·학습 로그 불변, 분석기만 확장. 별도20초3시점 영상 포함. [측정 정의·전체 결과·한계](../02_implementation/logs/2026-11-21_single_contact_model15800_play.md).

2026-11-20 최신 사용자 보고: **`.180`: `Inspire-Sweep-v0`, `.250`: `Inspire-Sweep-Single-Contact-v0`(약칭 Contact-v0) 학습 중**. 이전 환경은 Pull/Push 외에서 상당히 성공했지만 손등으로만 밀려는 편향이 관찰되어 방향별 손바닥/손등 선호를 추가했다. 기존 관찰은 사용자 보고이며 새 환경의 편향 개선·최신 성공률은 미확인이다. [Sweep 계통·비교·학습 현황](../02_implementation/environments/SWEEP_FAMILY.md) · [Sweep-v0 상세](../02_implementation/environments/SWEEP_V0.md). 아래의 개발 당시 학습 미실행 및 이전 서버 배치 기록과 구분한다.

2026-11-20 후속: **`Inspire-Sweep-Single-Contact-v0`** 추가. Sweep v0 직접 자식, 최근3 policy step 중2회 인정 여부를 boolean으로 판정, 보상 계수1/0. 후속 정정으로 count20/0 표현도 제거했고 자식 state에는 contact_count 필드가 없다. 부모 누적 방식·높이·현재 힘 조건·모든 설정 보존, PPO는 로그 이름 `inspire_sweep_single_contact_v0`만 변경. CPU110개·GPU4환경8step/부분reset/이력probe 통과, 학습 미실행. [계약](../02_implementation/environments/SWEEP_V0.md#single-contact-파생-환경) · [개발·검증](../02_implementation/logs/2026-11-20_sweep_single_contact.md).

2026-11-20 후속: **독립 `Inspire-Sweep-v0`** 추가. EnvCfg/PPO Cfg는 Isaac Lab 기반 직접 상속, 별도 runtime 진입점·공통 lifecycle 재사용. v2-Test-ActionPenalty-LinearReach 기능 기준, 구역1/2 손등·3/4 손바닥1.5/반대0.7, Deadzone0°·Pull/Push60°·좌우120°, 활성5개 커리큘럼 삭제·50N/-0.04/30N/3Nm/-0.1 고정, 관측만 F/T clip÷한계로 [-1,1]. 물리 reward 보존. CPU116개·RTX3090 GPU4환경8step/부분reset 통과, 학습 미실행. 로그 `inspire_sweep_v0`. [계약](../02_implementation/environments/SWEEP_V0.md) · [개발·검증](../02_implementation/logs/2026-11-20_sweep_v0.md).

2026-11-20 후속: `Inspire-Sweep-Only-v2-Test-ActionPenalty-LinearReach` 추가. v2-Test-ActionPenalty 직접 상속, Reach만 weight0.8·10cm plateau·45cm에서0인 선형식으로 교체했다. 초기 거리·episode 길이 배율 제거, Sweep50/−10/count÷20·Deadzone0°·ActionPenalty·나머지 구성 유지. 로그 `inspire_sweep_only_v2_test_action_penalty_linear_reach`. CPU108개·RTX3090 GPU4환경8step·부분reset/추가step 통과, 학습 미실행. [계약](../02_implementation/environments/SWEEP_ONLY_FAMILY.md#linearreach-파생-환경) · [개발·검증](../02_implementation/logs/2026-11-20_sweep_only_v2_test_action_penalty_linear_reach.md).

2026-11-20: `Inspire-Sweep-Only-v1-ActionPenalty` 추가. v0 직접 상속, 물체 옆 IK·Reach 없음·Deadzone30° 유지, Sweep50/−10/count÷20과 공통 ActionPenalty 적용. 로그 `inspire_sweep_only_v1_action_penalty`. 기존 ID·서버별 학습 현황은 그대로다. [변경·검증](../02_implementation/logs/2026-11-20_sweep_only_v1_ik_action_penalty.md).

2026-11-20 최종 학습 배치: **`.250`은 `Inspire-Sweep-Only-v2-Test-ActionPenalty`, `.180`은 `Inspire-Sweep-Only-v1-Test-ActionPenalty` 학습 중, `.30`은 학습 없음**. 계수·카운트 변경(v1_2)의 효과가 없다고 잠정 가정하고 두 실행 모두 progress50·retreat−10·count/20을 사용한다. 효과 부재의 확정이나 새 성공률 보고는 아니다. [최신 상태](../02_implementation/environments/SWEEP_ONLY_FAMILY.md#현재-학습-현황-2026-11-20-사용자-보고).

2026-11-20 이전 사용자 학습 보고(후속 배치로 갱신): **`.180` v1_2-Test는 중단 없이 성공률20% 미만, `.250` v2-Test는 약10k에서50% 수준을 기록했으나 중단, `.30` v1-Test는 약5k에서20% 수준을 기록했으나 중단**. v1의 추가 상승은 사용자 기대이며 미검증이다. 기존 환경 실행 결과이며 새 ActionPenalty의 결과가 아니다. 기존11월19일 실행 중 기록보다 이 상태가 우선한다. [관찰·원인 가설·검증 경계](../02_implementation/logs/2026-11-20_sweep_only_training_status.md).

2026-11-20: Sweep Only 기존 6종 각각에 `-ActionPenalty` 직접 파생 환경을 추가했다. 원본 ID 보존, wrapper clip 해제 후 팔 ±π/2·손 URDF 한계는 Action term에서 실행 제한한다. 원본 출력의 팔/손 범위 초과 비용 각 −0.03 추가, 기존 Action 변화 L2는 원본 이력으로 계산한다. Last Action 관측은 기존 ±π/2 유지, 모델·IsaacLab·Sweep 보상·Deadzone 불변. [변경·검증](../02_implementation/logs/2026-11-20_sweep_only_action_penalty.md).

2026-11-19 최종 사용자 학습 현황: **`.30`에서 v1-Test, `.180`에서 v1_2-Test, `.250`에서 v2-Test를 모두 학습 중**이다. v2는 처음 실패한 것으로 판단했으나 약 2000 iteration부터 성공률 상승 경향이 보여 컴퓨터를 바꿔 시도 중이다. 이전 Deadzone 제거 실험 보류 방침과 v1_2 학습 예정 상태는 이 보고로 갱신한다. v1의 약 20%는 이전 보고값이며 최신 수치는 미보고다. 원격 로그 재검증이나 실행 없이 사용자 보고로 기록했다. [계열·버전·학습 현황 안내](../02_implementation/environments/SWEEP_ONLY_FAMILY.md).

2026-11-19: `Inspire-Sweep-Only-v2_2-Test`는 v1_2-Test 직접 자식으로 Deadzone만 **0° 고정**이다. 보상 100/−25·원시 접촉 카운트와 나머지 조건 유지, 로그 `inspire_sweep_only_v2_2_test`. GPU·Isaac Sim 없이 표준 라이브러리 기반 코드 검사를 통과했다.

2026-11-19: `Inspire-Sweep-Only-v1_2-Test`는 v1-Test 직접 자식이다. 접촉 카운트 정규화를 끄고 정방향 100·역방향 −25로 설정하여 동일 상태에서 v1 대비 정방향 40배·역방향 2.5배다. Deadzone 30°와 나머지 조건은 유지하며 로그 이름은 `inspire_sweep_only_v1_2_test`다. CPU 코드 검사만 수행했고 GPU·Isaac Sim·학습은 실행하지 않았다.

2026-11-19: `Inspire-Sweep-Only-v2-Test`는 v1-Test 직접 자식으로 목표 방향 Deadzone만 **0° 고정**이다. 보상 50/−10 및 나머지 구성 유지, 로그 `inspire_sweep_only_v2_test`. 학습 중인 GPU 보호 요청에 따라 GPU·Isaac Sim 실행 없이 CPU 정적 검사만 수행했다.

2026-11-19 후속: `--heavy-occlusion`으로 거의 가려진 물체가 있는 정면 사진24장을 `outputs/shelf_front_heavy_24`에 추가했다. 각 장면에2개씩 총48개 물체의 가시 면적이0.55–7.72%(92.28–99.45% 가림)임을 실제 mask로 확인했다. 기존48장은 보존했다. [강한 가림 검증](../02_implementation/logs/2026-11-19_shelf_front_photography.md#후속-거의-보이지-않는-강한-가림24장).

2026-11-19 후속: `photograph_shelf_front.py --occlusion`으로 물체8개의 부분 가림 정면 이미지24장을 `outputs/shelf_front_occluded_24`에 추가했다. 장면마다 실제 mask로2–4쌍의 부분 가림을 확인했으며 기존 무가림24장은 보존했다. [후속 검증](../02_implementation/logs/2026-11-19_shelf_front_photography.md#후속-부분-가림-사진24장-추가).

2026-11-19: 로봇 없는 선반·물체8개 정면 사진24장을 `outputs/shelf_front_24`에 생성했다. 현재 source8종·scale 범위를 재사용하고 촬영용 가림 방지 배치·수평 직교 카메라를 사용한다. 기존 학습 환경은 변경하지 않았다. [촬영 실행기·검증](../02_implementation/logs/2026-11-19_shelf_front_photography.md).

2026-11-19: UR5e–Axia80–오른손 RH56E2의 비학습 촬영 실행기 `scripts/photograph_robot.py`를 추가했다. Sweep Only와 같은 로봇 factory를 재사용하며5개 PNG 구도·수동 뷰포트 촬영·정적 USD를 제공한다. 기존 학습 환경은 유지한다. [실행·검증 기록](../02_implementation/logs/2026-11-19_robot_photography.md).

2026-11-19: `Inspire-Sweep-Only-v1-Test`를 `Inspire-Sweep-Only-v0-Test` 직접 자식으로 추가했다. `sweep_progress=50`, `sweep_retreat=−10`만 변경하며 로그 이름은 `inspire_sweep_only_v1_test`다. 부모의 30/−20과 나머지 환경은 유지한다.

2026-11-19 후속: Sweep Only 일반·Test의 `sweep_retreat` weight를 −38.91에서 **−20**으로 변경했다. 정방향 weight 30과 거리 식은 유지하고 Stabilize 두 환경은 기존 −38.91을 유지한다.

2026-11-19 후속: **Sweep Only 일반·Test에서 Phase 관측과 압착 페널티를 제거**했다. Phase는 내부 상태만 유지하고 Actor·Critic 직접 입력은 66D, obstacle 64D, export 130D다. Stabilize 두 환경은 변경하지 않았다. 기존 67D 모델 체크포인트는 직접 호환되지 않는다. [변경·검증](../02_implementation/logs/2026-11-19_stabilize_family_audit.md#sweep-only-phase-관측압착-페널티-삭제).

2026-11-19 **Stabilize/Sweep Only 네 환경 조건 검토·공통 코드 정리 완료**: 사용자 확인대로 `clip_actions=π/2`를 유지하고 미사용 14cm 필드를 실제 계산에 연결된 `sweep_contact_height_limit=0.12`로 정리했다. 상태 생성·초기 표면점 저장을 공통화했으며 CPU 211개와 네 ID 각각 GPU 4환경 reset·step·부분 reset 검사를 통과했다. Test도 단일 IK를 사용하며 초기 로봇 점유 공간 제외는 미적용이다. mask 대표점과 bbox 중앙점, 팔 전용 속도 종료 등은 [조건별 검토·변경·검증](../02_implementation/logs/2026-11-19_stabilize_family_audit.md)에 구분했다. [일반 Sweep Only 상세 설명](../02_implementation/environments/SWEEP_ONLY.md)을 추가했으며 이번 정리 후 2048환경 학습 성능은 재측정하지 않았다.

2026-11-19 **일반 Sweep Only 물체 옆 초기화 성능 개선 완료**: `Inspire-Sweep-Only-v0`가 RTX3090·2048환경·headless·seed42·32회 전부 collection10초 미만(collection 중앙값8.322초·최대9.579초)을 기록했다. 실제 hull의 GPU 분리 증명+기존 LP fallback, 경계 재검사를 포함한 GPU SAT·FK·채택 FK 재사용, 로봇 점유 검사와 장애물 셀 선택의 GPU 처리를 적용했다. 손의 밀기 반대편 위치·RED·로봇 비겹침·분포·관측·보상·PPO를 유지했다. 일반 Stabilize도 공통 초기화 계산을 사용하며 Stabilize 보상 자체는 이번 범위가 아니다. Test 경로는 보존한다. [병목·변경·실제 배치·측정·한계](../02_implementation/logs/2026-11-19_sweep_only_ik_performance.md).

2026-11-19: 두 Stabilize/Sweep Only `-Test`에 GUI 대표 표면점 빨간 마커를 추가했다. 초기 관측 위치에 고정되며 물리 속성이 없다. 일반 headless에서는 생성하지 않는다. [비활성 물체 간섭 검토와 검증](../02_implementation/logs/2026-11-19_stabilize_surface_markers.md).

2026-11-19 **일반 IK 환경에도 공통 성능 개선 적용**: `Inspire-Stabilize-Sweep-v0`와 `Inspire-Sweep-Only-v0`에 대표점 GPU 배치·고정 COM cache·비활성 XY 주차·중복 native 기록 생략을 연결했다. 일반 배치는 로봇 점유 공간 검사를 유지한32행 처리/fused RED이며,4후보 IK·충돌 메쉬·실패 행8회 추가 재추출·손 방향/높이·보상/PPO는 유지한다. Test 초기화 경로는 보존한다. CPU132개·일반 Stabilize GPU4환경 실패 주입·Sweep Only GPU64환경8seed 통과. 아래 Test의10초 미만 수치는 일반 환경의 측정값이 아니다. [후속 변경·검증](../02_implementation/logs/2026-11-19_stabilize_parent_performance.md).

2026-11-19 **Stabilize/Sweep Only Test 성능 개선 완료**: 두 `-Test`만 대표점 GPU 배치 처리·배치 셀 선택·고정 COM cache·중복 reset 생략을 적용하고 비활성 물체 주차를 작업 영역 밖 XY 격자로 옮겼다. RTX3090에서 각각2048환경·headless·seed42·32회가 모두10초 미만이었다. Stabilize 중앙값8.81/최대9.44초, Sweep Only8.69/9.18초. 관측1mm·활성 배치/RNG·보상/Gate·horizon36·PPO8×4 유지, CPU131개·양쪽 GPU64환경 검증 통과. 최초 시뮬레이터 생성은 시간 지표에서 제외하며 장기 행동 평가는 미완료다. [변경·실행·검증·한계](../02_implementation/logs/2026-11-18_stabilize_sweep_performance.md).

2026-11-18 **Finger 초기화 Test2종 추가**: `Inspire-Stabilize-Sweep-v0-Test`와 `Inspire-Sweep-Only-v0-Test`가 각각 원본을 상속한다. 사용자 선택에 따라 Finger 공통 원형 배치·기본 방향 단일 Warp IK를 재사용하고 대표 표면점 관측은 유지한다. 후속 요청으로 Test에만 Finger Reach(weight30)를 추가했다. 나머지 보상/Gate 및 기존 두 환경은 보존한다. Test는 원본의5mm 초기 높이·충돌 hull/4후보/8회 복구를 사용하지 않는다. [차이·실행·검증 범위](../02_implementation/environments/STABILIZE_SWEEP.md#finger-초기화-test-환경).

2026-11-18 **Sweep Only 파생 환경 추가**: `Inspire-Sweep-Only-v0`는 Stabilize 부모를 상속하고 안정화 점수·초기 이동/회전 비용·Gate를 제거한다. 초기 관측부터 Sweep(phase1), 압착 및 모든 나머지 보상·초기화 복구·관측·제어·종료는 유지한다. 별도 PPO 로그 이름 `inspire_sweep_only_v0`. CPU43개·GPU4환경 검증 통과, 장기 학습 미실행. [차이·실행·검증](../02_implementation/environments/STABILIZE_SWEEP.md#sweep-only-파생-환경).

2026-11-18 **독립 Stabilize → Sweep 구현·검증**: 후속 `$implement` 지시로 `Inspire-Stabilize-Sweep-v0`를 추가했다. 초기 표면점 관측, 제한된 reset, 실제 COM 접촉 계측,30sample Gate, 단계별 보상·timeout과 독립 PPO를 연결했다. 초기 자세 변경 후, 사용자가 **IK 실패 행만 다른 배치로 복구**하도록 요청했다. 후속 방향·높이 정정으로 손바닥은 항상 로봇 기준 왼쪽을 향하고 오른쪽 밀기는 손등을 사용한다. 손 하단은 실제 충돌 정점 기준 상판 위5mm에 맞추며 손목 고도각0°/+2°를 최대4후보로 검사한다. 좌우 목표 분포는 유지하되4후보 실패 행만 타겟·목표를 최대8회 추가 재추출한다. 성공 행을 보존하고 정책 Termination·보상에 초기화 실패를 섞지 않는다. 최초 포함9배치가 모두 실패하면 진단 오류로 중단한다. 검증 범위는 상세 설명·개발 로그를 따른다. Ticket10 행동 평가는 여전히 미완료다. [상세 환경 설명](../02_implementation/environments/STABILIZE_SWEEP.md) · [명세](environments/2026-11-18_stabilize_sweep_spec.md) · [구현·검증·한계](../02_implementation/logs/2026-11-18_stabilize_sweep_implementation.md).

2026-11-18 **실제 가시 메쉬 표면점으로 수정·사용자 확인 완료**: `surface_point` 뷰어 기본을 OBB 근사에서 실제 USD 시각 메쉬의 GPU 광선 질의로 변경했다. 기본 1 mm, 가시 mask 면적 중심 대표점 및 bbox 중앙 비교 옵션. 사선 원근·자유 검토 카메라와 고정 관측 분리, 실제 mask 창 추가. 사용자가 현재 결과를 수용하고 기록을 요청했다. 이전 박스 근사 설명은 과거 방식이며 최종 환경에는 아직 연결하지 않았다. [변경·원리·검증·후속 기준](../02_implementation/logs/2026-11-18_surface_point_mesh.md).

2026-11-18 **정면 대표 표면점 벤치**: 별도 `src/surface_point`에서 유한 높이 정면 노출 영역의 대표 표면점을 기존 관측 OBB·원본 OBB와 비교한다. 이미지 없이 박스 근사 기하를 사용하며 실제 메쉬 표면은 미측정. Simple/fixture GPU 검증 및 CPU 29개 테스트 통과. [변경·수치·실행](../02_implementation/logs/2026-11-18_surface_point_bench.md).

2026-11-18 **OBB 중심 Gaussian 원리 문서**: 현재 조회 방식의 입력·사전 표·후보 재관측·가중치·평균/공분산·예외·확률 해석을 코드 참조 없이 읽는 [독립 설명](../02_implementation/environments/OBB_CENTROID_GAUSSIAN_METHOD.md)에 정리했다. 계산 동작 변경 없음.

2026-11-18 **Gaussian 조회 가속**: 8종 사전 기하 표와 최대 16개 후보 검증을 뷰어 기본값으로 적용했다. RTX 3090 반복 Reset부터 전체 표시까지 중앙값 238 ms(9회), 첫 렌더 Reset 1.43초. 기존 추정기는 비교용으로 유지한다. 미보정 근사 모델이며 최종 환경 미연결. [변경·측정·한계](../02_implementation/logs/2026-11-18_centroid_lookup_acceleration.md).

2026-11-18 **Gaussian 가시성 보완**: 얇은 타원만 표시하던 뷰어에 밀도 색상 mesh·90% 경계와 관측별 확대 XY 밀도 패널을 추가했다. 계산 대기/ON/OFF를 명시하고 실제 공분산은 보존한다. [변경·검증](../02_implementation/logs/2026-11-18_gaussian_density_visibility.md).

2026-11-18 **Gaussian 뷰어 버튼 수정**: 계산 중 New placement·재관측을 막던 처리를 삭제했다. 이전 계산을 후보 평가 단계에서 취소하고 최신 요청만 실행하며 stale 결과를 폐기한다. CPU49개·GPU 실제 버튼 검증. [원인·검증](../02_implementation/logs/2026-11-18_centroid_viewer_buttons.md).

2026-11-18 **관측 OBB + Gaussian GPU 뷰어**: `src/centroid_belief/scripts/show.py`에서 기존 Simple 정지 장면의 관측별 Gaussian 평균·90% 타원을 비충돌 표시한다. 실제 RTX 3090 데스크톱에서 실행했으며 추정은 백그라운드로 진행한다. 기존 baseline/관측 코드는 보존하고 최종 환경 미연결이다. [변경·검증](../02_implementation/logs/2026-11-18_centroid_gaussian_viewer.md).

2026-11-18 **중심 확률 단일 Gaussian 출력**: `src/centroid_belief` 기본 API를 평균 2개·공분산 3개의 5값 출력으로 변경했다. 완전 관측 후보군을 먼저 재관측하여 템플릿 부분 관측 후보군과 함께 평가한다. 초기 비중 0.5와 3 mm 허용 오차는 미보정 모델 설정이다. 이전 KDE 결과는 보존하며 최종 환경 미연결이다. [실험·계약](../02_implementation/experiments/2026-11-18_obb_centroid_gaussian.md) · [변경 기록](../02_implementation/logs/2026-11-18_centroid_gaussian.md).

2026-11-18 **OBB 기반 전체 중심 확률 추정**: 별도 `src/centroid_belief`에서 관측 OBB만 입력받는 CPU 기하 추정기를 구현했다. 8종 OBB 근사 템플릿·중요도 표집·KDE를 사용하며 물리 시뮬레이션·학습·최종 환경 연결은 없다. 실제 YCB 치수와 확률 보정은 미검증이다. [실험 및 한계](../02_implementation/experiments/2026-11-18_obb_centroid_belief.md) · [변경·검증](../02_implementation/logs/2026-11-18_centroid_belief.md).

2026-11-18 **초기 부분 관측 OBB 통합 인계**: 독립 검토 패키지의 관측 계약·무제한 뷰어·가림 후보 선택·좌표 및 reset 연결·미확정 정책 입력을 [별도 인계](../02_implementation/environments/OBSERVED_OBB_INTEGRATION.md)에 정리했다. 최종 환경 미연결, GPU 라이브 검증 미완료. 검토용 배치 조건과 뷰어 무제한 실행을 학습 배치·episode 계약으로 자동 확대하지 않는다.

2026-11-13 **Simple17환경 EEF 높이12cm 통일·ForceDirection cosine**: 활성 보상 eef_height_limit를 모두0.12로 고정. Finger-ForceDirection-v0만 힘 방향 원점수를 signed cosine(정방향+1·직각0·반대−1)으로 변경했다.1cm 방향/접촉 예외·성공3cm·가중치0.33 유지. Semi-Prof 방향식·충돌/후퇴 높이는 유지. [변경·검증](../02_implementation/logs/2026-11-13_simple_height_cosine.md).

2026-11-13 **Finger-ForceDirection-v0 추가**: Finger-v0-Test 직접 자식. 기존 힘 방향 보상0.33 추가(방향 무시1cm·실제 접촉/수평1N 필요), 목표 내 접촉 간주3→1cm. 성공 종료/메트릭3cm·Clip·Last Action·PPO·기존 보상 보존. 장기 학습 개시 보고 없음. [계약·리뷰·검증](../02_implementation/logs/2026-11-13_finger_test_force_direction.md).

2026-11-13 **Simple 학습 현황 정정(사용자 보고)**: 기존 Finger-v1/v2·Semi-Prof-v0는 실패·방안 잠정 폐기. 과도한 손 동작 대응을 우선하며 현재 .180에서 Finger-v0-Test, .250에서 Prof-v2 학습 중. v1 실패 후 Test를 수정한 네이밍 혼선은 기록만 보존한다. 실제 Prof 변경 대상은 Prof-v1 자식 Prof-v2이며 Prof-v0 직접 수정이 아니다. [상태·경위](../02_implementation/environments/SWEEP_SIMPLE_ENVIRONMENTS.md#학습-현황과-후속-방향).

2026-11-13 **Prof-v2 손6축 후속 변경**: 해당 ID에만 Finger와 같은 drive6관절 관측·절대 rad 제어를 적용했다. 액션12D·policy66D+obstacles64D, PPO 모델·action-rate 손6채널·zero-radian reset 연동. Runner Clip±π/2·raw Last Action·팔1rad/s 종료·접촉 높이12cm 유지. Prof-v1/Finger 유지, 구8D Prof-v2 checkpoint 직접 재개 불가. [변경·검증](../02_implementation/logs/2026-11-13_sweep_simple_prof_v2.md#후속-변경-prof-v2-손6차원-관측제어).

2026-11-13 **Simple Prof-v2 추가**: Prof-v1 직접 상속. 팔 속도 종료1.0rad/s 고정·해당 커리큘럼 제거, Runner `clip_actions=π/2`, 접촉 조건부 Goal Distance/방향 비용의 EEF 높이15→12cm. Last Action은 Clip 후 raw 입력·tanh 제거, 보상식/계수 보존. CPU69개·GPU64환경/2iterations 검증, 장기 행동 개선 미검증. [변경·검증](../02_implementation/logs/2026-11-13_sweep_simple_prof_v2.md).

2026-11-13 **Finger-v0-Test Runner Clip**: 해당 ID에만 `clip_actions=π/2`를 적용한다. 12축 공통 Clip은 OSC scale 전이며, Last Action은 manager 입력 그대로(tanh·추가 Clip 없음), action-rate는 Clip 후 current/previous 값의 제곱합·cap 없음. 부모·v1·Wrench 유지. [변경·검증](../02_implementation/logs/2026-11-13_finger_v0_test_runner_clip.md).

2026-11-11 **전체 환경 Action 변화 비용 상한 제거**: 활성 inspire_sweep_baseline 전 계열의 action-rate 출력 cap과 관련 설정 제거. 가중치·입력 처리·다른 비용 상한 유지. 과거 문서의 action-rate cap100 설명보다 이번 계약이 우선한다. [기록](../02_implementation/logs/2026-11-11_action_rate_uncapped.md).

2026-11-11 **Finger-v1 속도 조건 변경**: 팔 속도 종료1.0rad/s 고정·해당 커리큘럼 제거·팔 비용−0.03. v2/Semi-Prof 및 세 Raw 자식에도 상속. 액션·Last Action·PPO 및 다른 일정 유지. [기록](../02_implementation/logs/2026-11-11_finger_v1_fixed_velocity.md).

2026-11-11 **Wrench 실행·관측 Clip 적용**: 참고 예제와 같은 센서 범위 Clip→Scale→모멘트 보정, 손6축 URDF Raw Clip, Last Action은 tanh 없이 Clip된 Raw12D. PPO 원본 샘플·기존 action-rate·고정1rad/s 종료 유지. [계약·검증](../02_implementation/logs/2026-11-11_finger_wrench_action_clipping.md).

2026-11-11 **Wrench 팔 속도 종료 수정**: 기존 Finger-v0-Wrench ID의 임계값을1.0rad/s 고정으로 변경하고 해당 커리큘럼만 비활성화했다. 부모·제어기·보상·다른 일정 보존. [후속 기록](../02_implementation/logs/2026-11-11_finger_v0_wrench_osc.md#후속-변경-팔-속도-종료10rads-고정).

2026-11-11 **Simple 최종 환경 문서 갱신**: Test/Wrench를 포함한15개 ID와 Finger 제어·종료 비교표, 프레임 차이 및 검증 범위를 정리했다. 코드 변경 없음. [기록](../02_implementation/logs/2026-11-11_sweep_simple_final_documentation.md).

2026-11-11 **Finger-v0-Wrench 추가**: Finger-v0 직접 상속, 팔 액션만 AXIA80 센서 원점·축 기준 wrench_abs OSC로 변경. 힘10N/모멘트1N·m scale, 중력 보상·기존 effort 방어 유지, native 모멘트 원점 보정. 손·관측·보상·종료·커리큘럼 보존. CPU67개 통과, GPU 미검증. [계약·검증](../02_implementation/logs/2026-11-11_finger_v0_wrench_osc.md).

2026-11-11 **Finger-v0-Test 추가**: Finger-v0 직접 상속, 팔 절댓값 관절 속도>1.0rad/s 실패 종료를 고정 적용하고 해당 임계값 커리큘럼만 제거했다. 나머지 구성·다른 커리큘럼·부모 환경 보존. CPU65개 통과, GPU/PhysX·학습 미검증. [변경·검증](../02_implementation/logs/2026-11-11_finger_v0_test_velocity_termination.md).

2026-11-11 **현재 계약: 원환경 롤백·Raw ID 분리**. 기존 Finger-v1/v2·Semi-Prof-v0를 실행 Clip·Clip된 Last Action·팔 비용−0.06으로 복원해 기존 ID로 play한다. Clip 제거·tanh Last Action·비용−0.03은 각 부모를 직접 상속한 Finger-Raw-v1/Finger-Raw-v2/Semi-Prof-Raw-v0로 분리했다. 속도 터미네이션 유지, Semi-Prof5% 상한 제거는 원환경에도 유지. [ID·play·대조·검증](../02_implementation/logs/2026-11-11_finger_raw_environment_split.md). 아래 직접 수정 이력은 이 결정으로 대체된다.

2026-11-11 **최종 후속 변경: Finger-v1/v2·Semi-Prof-v0**. 팔 Joint Velocity 비용−0.06→−0.03, 추가 Raw Action Clip 삭제, Last Action은 tanh(raw action)으로 복원했다. 제어·PPO·action-rate는 원본 Raw Action. 일반 Gaussian·초기 분포·속도 종료2→1rad/s(2000–5000/250)·Semi-Prof5% 상한 제거는 유지. 과거 bounded 정책 복원 아님. [변경·검증](../02_implementation/logs/2026-11-11_finger_raw_action_restore.md). 아래 동일 날짜의 사건 기록보다 이 계약이 우선한다.

2026-11-11 **Semi-Prof 중대 이슈 후속 수정**: 양의 `force_direction`이 부모 `wrench_change` 뒤에 배치되어 Wrench 활성화 시 순서 검사로 중단됐다. 사용자 후속 지시로 Semi-Prof의 양의 보상 연동5% 상한과 순서 의존을 제거했다. Wrench 변화량·가중치·일정·Gaussian 정책은 유지한다. 실제 RewardManager/커리큘럼 CPU 회귀와 관련92개 검사 통과, GPU 학습 미검증. [원인·검증 누락·수정](../02_implementation/logs/2026-11-11_semi_prof_reward_order_incident.md).

2026-11-11 **중대 이슈: Finger-v1/v2·Semi-Prof PPO gradient 비유한값**. 공유 tanh→atanh 정책의 포화·역복원 경로에서 동일 오류를 CPU 재현했다. 일반 Gaussian + 실행 직전 clip으로 수정: PPO 원본 샘플 보존, Last Action/action-rate는 clip 후 raw 값, 정규화 없음. 축별 초기 분포와 진단을 적용하고 구 tanh checkpoint 직접 Resume를 거부한다. 원격 실패 dump 미확보·GPU 장기 학습 미검증. [사건·근거·검증](../02_implementation/logs/2026-11-11_gaussian_action_clipping_incident.md). 아래 초기 구현 기록보다 이 수정 계약이 우선한다.

2026-11-11 **물체 스폰 영역 시각화 삭제**: 사용자 요청으로 Simple 베이스와 Relative-IK v0_2_2_4의 표시 구현·설정·전용 분류 함수·train/play 활성화 코드를 모두 제거했다. 실제 RED/WHITE 배치·IK·보상·종료는 유지한다. [범위·검증](../02_implementation/logs/2026-11-11_remove_spawn_region_visualization.md).

2026-11-11 **Simple Semi-Prof-v0**: Finger-v1 직접 파생. 손6축·bounded OSC/Last Action·속도 일정 보존. 현재 Reach30, 접촉2-of-3+현재 EEF15cm 미만 조건부 로그 Distance120(불인정 개선분 소급 없음), 접촉 유지 삭제, 멀어짐−31.128. 방향0.33은 현재 물체→목표 XY(Z=0)와 법선+마찰3D 합력 비교. 수평1N 이상·실제 접촉 필요, XY<1cm이면 방향 점수1이고 재이탈하면 각도 계산 복귀.3cm latch 없음.1cm 내부에서는 수직 힘 감점도 우회. CPU 검증·GPU 미검증 범위는 [개발 로그](../02_implementation/logs/2026-11-11_sweep_simple_semi_prof.md), 전체 계약은 [환경 안내](../02_implementation/environments/SWEEP_SIMPLE_ENVIRONMENTS.md#semi-prof-v0-접촉-조건부-정밀-이동과-힘-방향).

2026-11-11 **Simple 학습 현황(사용자 보고)**: Prof-v1·Finger-v0 학습 종료. Prof-v1은 목표 근처에서 물체를 위에서 누르며 빠르게 왕복하는 현상이 관찰되어 거리 보상 구조 개선 환경을 계획한다. Finger-v0의 정확도·과속 문제에 대응하는 v1/v2는 구현 완료이며 효과는 후속 학습에서 확인한다. Simple-Hard-v0는 결과 확인 중이고 후속 연구는 Finger 중심으로 진행할 예정이다. [관찰·판단·후속 방향](../02_implementation/environments/SWEEP_SIMPLE_ENVIRONMENTS.md#학습-현황과-후속-방향).

2026-11-11 **Simple Finger-v1/v2**: v0→v1→v2 직접 상속. v1은 정책 출력/입력/Last Action raw clip(팔±0.5/±π/2, 손 URDF6축), Last Action tanh 제거, 팔속도 비용−0.06 및 종료2→1rad/s(2000–5000/250). v2는 면적 일치 로그 Distance·중심까지 접근, XY<2cm 연속3초 후 영구 gate, 목표에서 초기 물체 방향5cm·선반 위8cm의 후퇴 Reach(최대 보상 반경2cm), gate 기반 Contact/timeout success. 부모 보존. CPU110개 통과·2개 skip, GPU/PhysX·학습 미검증. [계약·검증](../02_implementation/logs/2026-11-11_sweep_simple_finger_v1_v2.md).

2026-11-10 **Finger model3000 evaluation complete**: 128 envs x20 episodes, seed42; timeout2470 / early90. Timeout <=3cm79.84%, median1.71cm, moving Contact88.12%. Final pastel/Times New Roman plots, 200-point-per-quadrant scatter alpha0.65, Q1-Q4 box0-7cm, theoretical goal region saved under `outputs/sweep_evaluation/finger_3000_seed42/analysis/plots`. Raw reconciliation zero mismatches; CPU30 passed. [Results](../02_implementation/experiments/2026-11-10_finger_model3000_evaluation.md).

2026-11-10 **오차 박스 서식만 갱신**: 사용자 요청으로 현재 `analysis/plots2`의 종합오차그림2개만 재렌더링. Times New Roman 실제times.ttf 적용, Y축0–7cm, all 집계항목 제거(Q1–Q4의 평균마커 유지), 박스 간격0.5→0.22 축소. `--error-only`로 기존box CSV를 사용해 다른42개 그림/CSV 해시불변 확인. [실행 안내](../02_implementation/environments/SWEEP_EVALUATION.md).

2026-11-10 **박스 플롯 큰 오차 제외**: 사용자 요청으로 공통 상위Q3+1.5IQR(6.198785cm) 초과144개를 오차 통계에서 제외,2,299개로 박스/평균/극값 재계산. 주축0–10cm, 잔존최대6.183cm여서 이번엔 break 불필요. 잔존10cm 초과 시 상단+물결 축 생략 지원. 원본85개 파일 불변, 제외목록CSV 보존. [결과](../02_implementation/experiments/2026-11-10_finger_model1200_evaluation.md).

2026-11-10 **오차 통계 박스 플롯**: 사용자 요청으로 기존 error 통계Bar를 box plot으로 대체. 상자25–75%·중앙값선·평균마름모·실제최소–최대 수염, 전체+GT Q1–Q4와 개별이미지 재생성. `error_boxplot.png` 및 기존 `error_statistics.png`에 저장. 입력85개 해시 불변·검사28개 통과. [결과](../02_implementation/experiments/2026-11-10_finger_model1200_evaluation.md).

2026-11-10 **GT 사분면 플롯 정정**: 사용자 확인으로 선반 원점 GT의 X/Y 부호(Q1–Q4)로 모든 플롯을 재분류, 축은 선반X/Y, 중심 확대±5cm로 변경했다. 기존 절대 GT 위치를 초기→목표 sector로 색칠해115/2,560개가 경계를 넘어 보였음. GT값은 수정하지 않음. 오차 중앙값·평균·최소·최대 Bar Plot과 최소 caption 적용, 종합6장+개별30장. 원시/추출85개 파일 불변, 검사27개 통과. [현재 결과](../02_implementation/experiments/2026-11-10_finger_model1200_evaluation.md) · [실행 안내](../02_implementation/environments/SWEEP_EVALUATION.md).

2026-11-10 **평가 플롯 후속**: 사용자 요청으로 재수집/재추출 없이 기존 model1200 결과를 다시 그렸다. 없는11–1/5–7시를 생략하고 전체+유효4방향만 표시한다. `plot_sweep_results.py --individual`로 종합5장+개별25장 저장, raw/추출85개 입력 해시 불변, 평가 검사16개 통과. [재실행 안내](../02_implementation/environments/SWEEP_EVALUATION.md) · [결과](../02_implementation/experiments/2026-11-10_finger_model1200_evaluation.md).

2026-11-10 **Finger model1200 실제 평가**: 사용자 요청으로128환경×각20개 완료 에피소드(2,560개)를 순차 수집→추출→플롯했다. Timeout2,443/조기 종료117, 목표3cm 이내69.05%(전체 에피소드 기준65.90%), 오차 중앙값2.20cm/P90 4.89cm, moving Contact84.42%. 11–1/5–7시는30도 DeadZone으로0샘플. 원시1,224,661행 접촉 판정 독립 대조 불일치0. 전체 범위+±10cm 확대 플롯 제공. [정량 결과·그림·근거](../02_implementation/experiments/2026-11-10_finger_model1200_evaluation.md).

2026-11-10 **병렬 정책 결과 수집**: 환경/학습 계약 변경 없이 `collect_sweep_results.py` → `extract_sweep_results.py` → `plot_sweep_results.py` 추가. Timeout 최종 오차·실제 생성 목표를 전체/6방향으로, 속력>=0.001m/s인 policy step의 실제 Contact 인정 비율을 집계한다. 목표 내부 보상20과 실제 Contact 구분, reset 전 capture, 환경당 완료 quota·빈 방향·부분 에피소드 표시. CPU44개 통과, 제공 Finger model1200으로2환경×500step 실제 수집·추출·플롯 완료. [사용·데이터 계약](../02_implementation/environments/SWEEP_EVALUATION.md) · [개발·검증](../02_implementation/logs/2026-11-10_sweep_evaluation.md).

2026-11-10 **Simple Finger-v0**: `Inspire-Sweep-Simple-Finger-v0`는 Simple-v1 직접 상속. 손 관측은 실제 drive6관절(rad), 액션은 독립 절대 목표6관절(rad), 순서는 엄지 굽힘→검지→중지→약지→소지→엄지 대립. Last Action tanh 유지. policy66+obstacles64, 전체action12; 모델·action-rate·reset 차원 대응. 나머지 부모 계약 보존. CPU86개 통과·2개 skip, GPU/PhysX·학습 미검증. [개발·검증](../02_implementation/logs/2026-11-10_sweep_simple_finger.md).

2026-11-10 **Simple 목표 내부 풀 카운트**: Simple-v0의 접촉 유지 term을 변경했다. 목표 XY 거리<3cm이면 접촉·이력·EEF 높이와 무관하게 count/reward20. 밖에서는 기존 +1/−2·불인정 보상0. Simple-v1/Hard-v0에 상속, Prof와 과거 Relative-IK 환경은 보존. [변경·검증](../02_implementation/logs/2026-11-10_simple_goal_full_contact.md).

2026-11-10 **Simple 계열 종합 설명서**: 베이스 환경의 전체 Manager 구성·관측/액션·보상·종료·커리큘럼·메트릭·PPO와 파생 환경별 변경/실험 의도를 정리했다. 환경 코드는 변경하지 않았다. [설명서](../02_implementation/environments/SWEEP_SIMPLE_ENVIRONMENTS.md) · [문서화 기록](../02_implementation/logs/2026-11-10_sweep_simple_documentation.md).

2026-11-10 **Simple Hard 계열**: `Inspire-Sweep-Simple-Hard-v0`는 Simple-v1, `Inspire-Sweep-Simple-Prof-Hard-v0`는 Simple-Prof-v1 직접 상속. 목표7–15cm·전방향 DeadZone0도 고정, 방향별 최대 가능 거리가15cm 미만이면 그 최대 거리(7cm 미만 포함)를 선택한다. 안전 root 경계 startup 캐시·reset에서 직접 교점 산출, 방향 재추출 없음. 나머지 부모 계약 유지. CPU78개 통과·2개 skip, GPU/학습 미검증. [계약](../02_implementation/environments/SWEEP_SIMPLE_ENVIRONMENTS.md#hard-v0-공통-변경) · [개발·검증](../02_implementation/logs/2026-11-10_sweep_simple_hard.md).

2026-11-10 **Sweep Simple 독립 계열**: `Inspire-Sweep-Simple-v0`는 현재 Relative-IK v0_2_2_4와 동등한 독립 EnvCfg/runtime이다. Simple-Prof-v0는 v0_2_2_5 보상, Simple-v1는 v0_2_2_6 Reach, Prof-v1는 Prof-v0에서 Reach만 변경한다. 기존 환경 보존·Fast reset 유지. CPU71개 통과, GPU/PhysX·렌더·학습 미검증. [환경 계약](../02_implementation/environments/SWEEP_SIMPLE_ENVIRONMENTS.md) · [개발·검증](../02_implementation/logs/2026-11-10_sweep_simple_family.md).

2026-11-09 **Relative-IK-v0_2_2_6**: v0_2_2_4 직접 상속(v0_2_2_5 아님), Reach만 현재 타겟3D BBOX 중심–EEF 거리의 완화된 역수 보상으로 교체.10cm 이내 최대, 지속 근접/추종 유도. weight30 유지·기존 초기 Reach 최대예산을10초로 나누어 규모 보정. Goal Distance100·접촉 카운트 보상 등 부모 계약 유지. CPU56개 통과, GPU/학습 미검증. [계약·검증](../02_implementation/logs/2026-11-09_relative_ik_v0_2_2_6.md).

2026-11-09 **최근 에피소드 집계 적용**: 카운터 최초 도입 환경 v0_2_2_4의 runtime부터 직접 수정했다. 최근 완료 에피소드N개(기본10,000·설정 가능, 조기실패 포함) 안에서 timeout/success count와 rate를 계산한다. v0_2_2_5 및 새 v0_2_2_6도 상속한다. 성공 판정·종료·보상 의미는 보존한다. [변경·검증](../02_implementation/logs/2026-11-09_relative_ik_v0_2_2_6.md).

2026-11-09 **Relative-IK-v0_2_2_5**: v0_2_2_4 직접 상속. 현재 타겟 접촉·EEF15cm 미만 조건으로 policy step 접근 보상120·고정 지시 방향 이탈 비용−6. 기존 후퇴−25.94 유지, 접촉 카운트 보상 삭제. physics 누적 없음, Holding/가속도 복원 없음. 나머지 부모 계약 보존. CPU53개 통과, GPU/학습 미검증. [계약·검증](../02_implementation/logs/2026-11-09_relative_ik_v0_2_2_5.md).

2026-11-09 **Relative-IK-v0_2_2_4**: v0_2_2_3-Fast-Test 직접 상속. play 전용 RED/WHITE·장애물 점유 표시(기본4환경), 물체 가속도 비용/관련 일정2개 제거.10초 timeout에서 XY 거리<3cm이고 동시 실패가 없으면 success 분류; timeout bootstrap 유지. 최초 구현은 세션 누적이었으며 현재 최근N개 집계로 변경됨(위 최신 기록 참조). CPU47개 통과, GPU/play 렌더·학습 미검증. [계약·검증](../02_implementation/logs/2026-11-09_relative_ik_v0_2_2_4.md).

2026-11-09 **Relative-IK-v0_2_2_3-Fast-Test**: v0_2_2_2-Fast-Test 직접 상속. 접촉 카운트 상한20, 최종 불인정마다−2(하한0). 최종 불인정 step 보상0, 재접촉 인정 시 잔여 카운트+1로 지급 재개. 높이15cm 이상도 보상0. Holding 보상 goal_hold 및 커리큘럼 goal_speed_scale 제거. 나머지 부모 계약 보존. CPU43개 통과, GPU/학습 미실행. [계약·검증](../02_implementation/logs/2026-11-09_relative_ik_v0_2_2_3_fast.md).

2026-11-09 **Relative-IK-v0_2_2_2-Fast-Test 구현**: 사용자 후속 지시에 따라 v0_2_2_2-Test를 직접 상속한 새 환경에만 적용했다. 부모 보존. GRAY 삭제·장애물0–6 균등분포·외접원 RED/WHITE·5mm 안전 셀·Warp IK·IK 박스 기본 OFF·기하 캐시/중복 쓰기 제거. CPU 회귀156개 통과, 합성 배치100,000개 실패0, 실제 로봇 USD 기반 IK2048개 대조 통과. **GPU/PhysX·실제 물체 배치·Collection 개선은 미검증**. [환경·실행](../02_implementation/environments/WRENCH_REFACTOR_RELATIVE_IK_FAST_TEST_ENVIRONMENT.md) · [개발·검증](../02_implementation/logs/2026-11-09_relative_ik_fast_test.md).

2026-11-09 **Relative-IK-v0_2_2_2-Test**: v0_2_2_1-Test 직접 상속. 목표 XY 거리 증가량에만 부과하는 `target_inverse_distance` 추가, 참조 weight -12.97의 두 배인 -25.94. Contact 및 나머지 설정 유지. [계약·검증](../02_implementation/logs/2026-11-09_relative_ik_v0_2_2_2_inverse_distance.md).

2026-11-09 **Relative-IK-v0_2_2_1-Test**: v0_2_2-Test 직접 상속. Contact의 2-of-3 인정은 유지하고, 1회 불인정 시 누적 카운트를 즉시 초기화한다(부모는 5회). 높이 15cm 미만·상한 10·weight 0.1 및 나머지 설정 유지. 사용자 관찰인 “후반에 멈춘 뒤 물체가 추가로 밀리는 현상”을 줄이려는 의도로 접촉 유지 요구를 강화했다. [계약·검증](../02_implementation/logs/2026-11-09_relative_ik_v0_2_2_1_contact.md).

2026-11-09 **Relative-IK 실험 의도**: 기본 환경에서 원하는 방향의 밀기를 확인 → 일부 페널티를 제거해 지나친 구속 완화 → 접촉 불유지·방향 오류·목표 지나침을 사용자 관찰 → v0_2_2의 접촉 유지 보상으로 천천히 미는 행동을 유도. EEF 높이 15cm 조건은 위에서 누르기를 억제하려는 의도다. 최종적으로 필수 구속만 남기는 것이 방향이며, **현재 행동을 확인한 뒤 Distance 보상을 변경할 예정**이다. 구체적인 Distance 변경은 미정이고 접촉 보상 효과는 아직 검증할 가설이다. [사용자 사고 흐름 기록](../02_implementation/logs/2026-11-09_relative_ik_v0_2_2_contact.md#사용자가-명시한-실험-의도와-다음-판단-순서).

2026-11-09 **Relative-IK-v0_2_2-Test**: 일반 v0_2_1-Test 직접 상속. Contact만 타겟 전용2-of-3 카운트로 변경(상한10·5회 연속 불인정 초기화·weight0.1), 후속 수정으로 Contact의 EEF 높이를 초기 선반 표면 위15cm 미만으로 제한, 목표 점유 우회 없음. 속도 초과 비용은 계속 없음. [계약·검증](../02_implementation/logs/2026-11-09_relative_ik_v0_2_2_contact.md).

2026-11-09 **Relative-IK-v0_2_1-Reset-Test — 잠정 보류**: 사용자 비교에서 효과가 크지 않아 후속 실험에 적용하지 않는다. 기존 코드·로그는 보존한다. v0_2_1-Test 직접 상속.16개 크기 그룹, 그룹당8개 초기 배치·목표·IK 공유/재사용, 목록 충전 뒤32회마다1개 교체. 질량·관성·마찰은 매 reset 독립 추첨. 보상·관측·제어·종료·커리큘럼 유지. [검증·실행](../02_implementation/logs/2026-11-09_relative_ik_reset_test.md).

2026-11-09 **Relative-IK-v0_2_1-Test**: v0_2-Test 직접 상속, object를 tilt/장애물 변위로 동등 분리, EEF·타겟 속도 비용/일정 제거. 부모·자식 공통 목표 거리·속도 Metrics8개 수집을 복구하고 장애물 개수 Metrics 제거. [계약·성능 검증](../02_implementation/logs/2026-11-09_relative_ik_v0_2_1_metrics.md).

2026-11-09 **Relative-IK-v0_2-Test 독립 환경**: IK-v0_1 Scene·EEF OSC·대칭 관측·실패 종료와 Holding OSC v2 보상을 결합. 반경3cm 고정·성공 종료 삭제·장애물 증가 없음·느린 방향/팔 종료 일정 유지. 후속 요청으로 `arm_speed_excess`/`arm_free_speed` 삭제, 팔 제한은 IK-v0_1 유지, 손은 원본 URDF의10Nm·1rad/s 명시. [환경 계약](../02_implementation/environments/WRENCH_REFACTOR_RELATIVE_IK_V0_2_TEST_ENVIRONMENT.md) · [검증 기록](../02_implementation/logs/2026-11-09_relative_ik_v0_2_test.md).

2026-11-09 **Relative-IK-v0_1**: direct IK-v0 child; only first-entry bonus disabled. Other environment and PPO settings preserved. [Contract and validation](../02_implementation/logs/2026-11-09_relative_ik_v0_1.md).

2026-11-08 **Collection 최적화**: 환경 구성 변경 없이 reset 작은 배치의 IK(≤128)·Refactor OBB search(≤8)를 CPU로 계산한다. CUDA 난수 순서와 검색/수렴 계약은 유지한다. [프로파일·성능·동등성 검증](../02_implementation/logs/2026-11-08_collection_profile.md).

2026-11-08 **Relative-IK-v0/v1 최종**: 공통 초기 물체 관측, 양쪽 비물리 IK 박스. 사전86,722개 후보 검사로 전면 바깥8–10cm·물체 좌우10–18cm·기본 높이−1~+3cm로 확정했다. reset SVD·재추출은 비활성화하며 후보1개/IK1회 호출이다. v1의 접촉 조건부 누적 cosine Distance(weight5), 보상4개·3초 성공 종료 제거 및 일반10초 Timeout은 유지한다. [계약](../02_implementation/environments/WRENCH_REFACTOR_RELATIVE_IK_ENVIRONMENTS.md) · [비교 실험·검증](../02_implementation/logs/2026-11-08_relative_ik_family.md).

2026-11-08 **Relative-v2_7**: direct v2_1 child; goal-conditioned IK initial Arm pose, opposite target side, outside shelf, default orientation preserved. CPU91 and GPU reset/IK checks passed. [Contract and validation](../02_implementation/logs/2026-11-08_relative_v2_7.md).

2026-11-08 **Relative-v2_6**: direct v2_1 child; only goal distribution changes to a fixed 9cm straight-left offset. [Contract and validation](../02_implementation/logs/2026-11-08_relative_v2_6.md).

2026-11-08 **Relative-v2_5**: direct v2_4 child; Contact reward disabled, all other environment settings preserved. [Contract and validation](../02_implementation/logs/2026-11-08_relative_v2_5.md).

2026-11-08 **Relative-v2_4 ??**: v2_1 ?? ??, EEF14cm ?? ??? ??? ?? XY ?? ???(weight100), cosine??? ?? ?? ??. Contact ? ?? ?? ??. [?????](../02_implementation/logs/2026-11-08_relative_v2_4.md).

2026-11-08 **Relative-v2_3 추가**: v2_1 직접 상속, Contact 유지. Reaching을 현재 물체의 목표 반대쪽 XY5cm·높이 중간점으로 변경하고 접근 반경도5cm로 설정. [계약·검증](../02_implementation/logs/2026-11-08_relative_v2_3.md).

2026-11-08 **Relative-v2_2 추가**: v2_1 직접 상속, `rewards.target_contact = None`만 적용. GPU 스모크는 사용자 요청으로 생략. [변경·정적 검증](../02_implementation/logs/2026-11-08_relative_v2_2.md).

2026-11-08 **Relative-v2_1/v3 방향별 Test 8개 추가**: 각 부모 직접 상속, Right/Pull/Left/Push 목표 각도만 제한. [환경 계약 및 8개 순차 녹화 명령](../02_implementation/logs/2026-11-08_relative_direction_tests.md).

2026-11-07 **Relative-v2_1 추가**: v2 직접 상속, 거리 항만 시작→목표와 시작→현재의 XY 누적 변위 cosine으로 교체한다. weight5·scale0.05·높이 gate·거리 증가 페널티−12.97 및 나머지 v2 전체 계약 보존. v0/v2/v3 기존 동작은 변경하지 않는다. [환경 계약](../02_implementation/environments/WRENCH_REFACTOR_RELATIVE_V2_ENVIRONMENT.md#relative-v2_1-시작점-기준-누적-변위-cosine) · [개발·검증](../02_implementation/logs/2026-11-07_relative_v2_1.md).

2026-11-07 **Relative 공통 실시간 이동 보상**: v0의 cosine을 현재→목표와 저장 기준점→현재의 XY 방향 비교로 변경했다. 매step 평가 후1mm 이상 이동한 환경만 기준점을 갱신한다. 별도 매step 거리 증가 페널티 `target_inverse_distance`는 실제 `−12.97×max(d_t−d_(t−1),0)`이며 v2/v3도 동일 상속한다. v3는 최초 진입·Hold·성공 보상과 성공 종료를 제거한다. 실패가 없으면10초 timeout까지 진행한다. CPU85개, 버전별GPU2환경180step, v3 PPO32환경2iteration 통과. [설계·계수·검증·제약](../02_implementation/logs/2026-11-07_relative_motion_rewards.md).

2026-11-07 **Relative-v0 관측·Action Rate 한도 구현**: v0의 공통 설정으로 v2/v3에도 전파한다. 질량·관성 보정과 EEF 변환, noise를 거친 최종 F/T 관측을 힘 각 축±150N·모멘트 각 축±8N·m로 제한한다. raw Arm/기존 clamp Hand action-rate는 그룹별 제곱합 cap100을 적용한다. 공통 센서 보정·보상/진단용 wrench·다른 Refactor 환경은 보존한다. [변경·검증 및 미검증 범위](../02_implementation/logs/2026-11-07_relative_observation_action_limits.md).

2026-11-06 **현재 Relative 계약**: 활성 환경은v0·v2·v3, v1은 코드·등록·runner를 삭제했다. Axia는 v0부터280g 공통이다. v0/v3는 Actor·Critic 모두 초기 타겟, v2는 **Actor 초기 / Critic 현재**다. 모두 EEF 좌표이며 EEF pose만 Base다. v3는 v0 직접 상속으로 접촉 유지 보상을 없애고 현재 접촉 조건부 cosine 거리(weight25)를 사용한다. 물리 속도3.14rad/s·effort150/150/150/28/28/28Nm·종료4→2 커리큘럼은 유지한다. [최종 변경·검증](../02_implementation/logs/2026-11-06_relative_family_280g_v3.md) · [v3 계약](../02_implementation/environments/WRENCH_REFACTOR_RELATIVE_V3_ENVIRONMENT.md).

아래 날짜별 항목은 이전 작업 이력이다. Relative의 질량·v2 관측 역할·v1 활성 여부는 위 현재 계약을 우선한다.

2026-11-06 최종: Relative-v0/v1/v2의 Arm6축 물리 속도3.14rad/s, effort150/150/150/28/28/28Nm. 종료 임계값4.0을10,000까지 유지하고10,250부터250iteration마다0.05 감소하여20,000부터2.0 유지. 진단 print 롤백·속도 종료 활성. **사용자 정정으로 Relative-v1 Axia280g 유지**, v0/v2 질량은 기존값. [변경·검증](../02_implementation/logs/2026-11-06_relative_joint_limits_curriculum.md).

2026-11-06 후속: Relative-v1에만 Axia 질량 0.280 kg 적용. F/T 측정 경계 위쪽 하우징이므로 하위 손 보정식 유지. CPU86개·4환경 PhysX 보정 시험 통과. model_400/seed42/400step 비교에서 wrist3 종료11→13회로 완화 확인 안 됨. v0/v2·공통 질량 상수는 보존.

2026-11-06 후속: Relative-v1에만 arm joint velocity 종료 진단 출력 활성화. 초과 관절명·속도·env ID·3 rad/s 임계값 출력, 종료 판정과 다른 환경은 보존. CPU 79개 통과, Sim·Lab 실행 생략.

2026-11-06: **Inspire-Wrench-Refactor-Relative-v2** 추가. v0 직접 상속, Actor 타겟만 현재 위치로 변경하고 Critic은 초기 위치를 유지한다. 둘 다 EEF 기준이며 장애물도 v0의 EEF snapshot이다. CPU 검사만 실행; 사용자 요청으로 Sim·Lab·학습 검증 생략. [계약](../02_implementation/environments/WRENCH_REFACTOR_RELATIVE_V2_ENVIRONMENT.md) · [검증](../02_implementation/logs/2026-11-06_wrench_refactor_relative_v2.md).

2026-11-06: **Inspire-Wrench-Refactor-Relative-v1** 추가. Relative-v0 직접 상속, 장애물 입력만 EEF→Base 초기 snapshot으로 변경한다. Refactor Actor와 동일 함수이며 다른 환경·encoder·공통 Actor/Critic 입력은 보존한다. [계약](../02_implementation/environments/WRENCH_REFACTOR_RELATIVE_V1_ENVIRONMENT.md) · [검증](../02_implementation/logs/2026-11-06_wrench_refactor_relative_v1.md).

2026-11-06: **Inspire-Wrench-Refactor-Relative-v0** 추가. v3_1 직접 상속, Actor/Critic 공통 EEF 상대 초기 관측·goal XYZ·촉각17D, URDF Hand effort10Nm, 최초 진입+10. 부모 스폰/reset/기타 보상 보존. [계약](../02_implementation/environments/WRENCH_REFACTOR_RELATIVE_V0_ENVIRONMENT.md) · [검증 기록](../02_implementation/logs/2026-11-06_wrench_refactor_relative_v0.md).

2026-11-06: **Refactor v0 기반 수동 조작**은 `scripts/manual_wrench_refactor.py`다. world XYZ/RPY + 기존 Hand2D, 전체/선반/로봇 reset·선반 상태 snapshot 저장/복원. 부모 환경 파일·Gym·PPO는 보존한다. [실행·검증 기록](../02_implementation/logs/2026-11-06_wrench_refactor_manual.md).

2026-11-06: **Refactor v0_1/v1_1/v2_1/v3_1** 추가. 각 원본v0/v1/v2/v3 직접 상속, Action Rate를raw정책출력변화로변경·Arm cap제거·계수0.03유지. [계약](../02_implementation/environments/WRENCH_REFACTOR_POLICY_RATE_ENVIRONMENTS.md).

2026-11-06: **Inspire-Wrench-Refactor-v3-Test** 임시 환경 추가. v3 직접 상속, 왼쪽(world −Y) 목표만 생성; 나머지 환경·PPO 수치 보존. [계약·검증](../02_implementation/logs/2026-11-06_wrench_refactor_v3_test_left.md).

2026-11-06 수치 후속: Refactor 공통 목표 거리는 **6–12cm**다. 기존5–10cm에서 수치만 바꾸고 방향·샘플링·OSC·보상은 유지했다.

2026-11-06 후속: **Refactor v0 및 모든 파생 환경 목표 거리를5–10cm로 제한**. 방위/조건부 거리 균등과 방향 deadzone 커리큘럼 유지. [최종 영역·검증](../02_implementation/logs/2026-11-06_wrench_refactor_goal_annulus.md).

2026-11-06 정정: **v2←v0**(별도 접촉 보상·거리weight5×누적변위 cosine, root OSC), **v3←v2**(EEF task-space OSC). v0/v1 보존. [v3 계약](../02_implementation/environments/WRENCH_REFACTOR_V3_ENVIRONMENT.md) · [검증](../02_implementation/logs/2026-11-06_wrench_refactor_v2_fix_v3.md).

2026-11-06 후속: **Refactor-v0 기반 직접 수정**. OSC를 Final·Revision 공통 root-frame 구현으로 전환하고 목표 중심은 시작점에서5cm 이상 떨어진 곳만 샘플링한다. 오른손 USD·EEF offset·Hand·F/T는 보존하며 v1/v2도 상속한다. [변경·검증](../02_implementation/logs/2026-11-06_wrench_refactor_root_osc_min_goal.md).

2026-11-06: **Inspire-Wrench-Refactor-v2**는 사용자 정정으로 v0 직접 상속. 별도 접촉 보상·거리weight5를 유지하고 거리 항에 XY signed cosine을 곱한다. [계약](../02_implementation/environments/WRENCH_REFACTOR_V2_ENVIRONMENT.md).

2026-11-06: **Inspire-Wrench-Refactor-v1** 추가. v0직접상속,접촉유지보상제거·현재step접촉조건부거리보상weight25. [계약](../02_implementation/environments/WRENCH_REFACTOR_V1_ENVIRONMENT.md).

2026-11-06 후속: Refactor의 Hand 관절속도 페널티는 원본 URDF 독립 구동6축만 합산하며 미믹6축을 제외한다. 계수·Arm비용·동작제어·관측·종료·커리큘럼은 유지한다.

2026-11-06 **Refactor GUI32환경 검증 완료**: startup event 인자 오류·주차 물체 중력 갱신/wake 오류 수정. 최종7168배치에서 공중낙하 없음, 주차 drift3.82µm,140만goal방위 편향 검출 없음. 사용자 후속으로 Wrist3−π/2·Arm속도종료3rad/s. 최종32/32목표도달,21/32안정유지성공,실패0. 왼쪽앞면ch0/오른쪽뒷면ch17·접촉F/T약1.2N을확인했다. [시험·실패 이력](../02_implementation/logs/2026-11-06_wrench_refactor_gui_validation.md). 초기 “GPU driver부재”는 sandbox 접근 제한 오판으로 정정한다.

2026-11-05 Refactor 후속: 선반30kg MassAPI 생성 순서 수정, 오른손 공식 촉각형 총790g에 mass/inertia 비례 보정, EEF task frame·Jacobian·velocity 통일, tactile.05N. CPU159개 및 문서에서114파일 복원/import/USD 검사 통과. GPU물리 미검증. [상세 명세](../02_implementation/environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [변경/검증 기록](../02_implementation/logs/2026-11-05_wrench_refactor_mass_eef_spec.md).

2026-11-05: **`Inspire-Wrench-Refactor-v0` 독립 CFG/runtime 추가**. 오른손 ZIP 원본·실제17물체(8종×2장애물+원통타겟), 초기 물성 고정/높이 캐시·reset0–3/0–3, 방향/조건부 거리 균등, 앞뒤 tactile34, Actor/Critic raw74/MLP90을 구성했다. 출력 토크 정규화·목표 내부도 EEF14cm 제한·거리weight5·진입+15·speed/acceleration 제거를 반영했다. CPU/오른손USD/실제 설정 import 통과, GPU driver 부재로 PhysX/학습 미검증. [전체 계약](../02_implementation/environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [검증 로그](../02_implementation/logs/2026-11-05_wrench_refactor_v0_implementation.md).

2026-11-05: [**Wrench v0 계열 상세 명세**](../02_implementation/environments/WRENCH_V0_FAMILY_ENVIRONMENTS.md)를 작성했다. v0~v0_4의 상속·Scene/reset·관측·pose OSC·전체 보상·커리큘럼·종료·PPO·로그 해석을 현재 코드로 대조했다. 접촉 weight0.1, Hand raw rate, 정규화 OSC 토크 rate의 상한/기대값 차이를 명시한다. 문서 작업이며 환경 코드·검증 상태는 변경하지 않았다.

2026-11-05: **Inspire-Wrench-v0_3 → v0_4 추가**. v0_2→v0_3→v0_4 직접 상속. v0_3은 Gray/White 각각0–4 균등 reset·population/free-speed 커리큘럼 제거·속도 기준0.02m/s·EEF14cm·OSC 출력 토크 정규화 변화량·최초 진입 무감쇠4cm/s다. v0_4는 높이 조건을 둔 Holding 최단 거리 개선량으로 교체하며 weight3.7을 유지한다. 실제 부모 접촉 weight0.1도 보존했다. CPU103개 통과, GPU/학습 미실행. [환경·검증 계약](../02_implementation/environments/WRENCH_V0_3_V0_4_ENVIRONMENTS.md).

2026-11-05 후속: Wrench-v0_2 Contact Count를 최대10으로 제한하고 임시 print 블록 전체를 주석 처리했다. 접촉 인정·불인정5회 초기화 조건과 weight1.45는 유지한다. 기본dt0.02초에서 접촉 보상 상한은 step당0.29다. CPU89개 통과, GPU/play 미실행.

2026-11-05: **Inspire-Wrench-v0_2** 추가. v0 직접 상속, 접촉 조건 없는 cosine 거리 보상(3cm 미만1), 2-of-3 누적 접촉·불인정5회 초기화, −1/−1 장애물 기준에서2k 시작3k 교대·reset±1 랜덤화. CPU87개 통과, GPU/학습 미검증. [환경·검증 계약](../02_implementation/environments/WRENCH_V0_2_ENVIRONMENT.md).

2026-11-04: **Inspire-Wrench-v0_1** 추가. v0 직접 상속, 독립 contact 보상 제거·거리 보상에 연속 접촉과 signed cosine 적용. 사용자 후속 지시로 거리3cm 미만 alpha=1, 기존 높이/계수 유지. Deadzone40° 고정·목표 허용 거리4.0–7.5cm. CPU78개 통과, GPU/학습 미검증. [환경 계약](../02_implementation/environments/WRENCH_V0_1_ENVIRONMENT.md) · [개발 기록](../02_implementation/logs/2026-11-04_wrench_v0_1_implementation.md).

2026-11-04: **Inspire-Wrench-v2** 추가. v1 직접 상속, Arm 목표 ±10N/±0.5Nm·보정 후 제한 ±12N/±0.6Nm로1/10 축소. 범위 정규화 action-rate와 Hand/나머지 환경은 상속한다. CPU46개 통과, GPU 미검증. [v2 계약](../02_implementation/environments/WRENCH_V0_V1_ENVIRONMENT.md#13-inspire-wrench-v2-v1의-arm-범위를110로-축소).

2026-11-04 문서 통합: [Wrench-v0 전체 명세와 v1 변경점](../02_implementation/environments/WRENCH_V0_V1_ENVIRONMENT.md). 현재 코드 기준 랜덤화·관측·액션·15개 보상·커리큘럼·종료·PPO 및 sensor wrench 제어와 정규화 action-rate를 한 문서에 정리했다. 문서 작업이며 환경 코드 변경 없음.

2026-11-04 후속: Wrench-v1의 robot_action_rate_penalty는 Arm Desired Wrench를 정책 목표 범위로 정규화한 [-1,1] 변화량을 사용한다. Hand raw 계산과 계수는 유지하며 CPU44개 통과. v0는 보존했다.

2026-11-04: **`Inspire-Wrench-v1` 추가, v0 보존**. v0 직접 상속, OSC만 sensor-center6축 closed-loop wrench로 변경했다. `wrench_abs`, motion0/wrench1, P gain0.2, 목표 ±100N/±5Nm, 보정 후 명령 제한 ±120N/±6Nm, gravity True. 기본 Isaac OSC의 force3D-only 제한 때문에 full6D F/T feedback/J-transpose 경로를 로컬 구현했다. 기존 Scene·관측/보상 EEF frame·PPO 수치는 유지한다. CPU80개 통과, GPU 접촉 추종/학습·gain 안정성은 미검증. [환경·참고 구현·파라미터](../02_implementation/environments/WRENCH_V1_ENVIRONMENT.md) · [개발 기록](../02_implementation/logs/2026-11-04_wrench_v1_osc.md).

2026-11-04: **`Inspire-Wrench-v0` 독립 환경 추가**. Test-v2를 의미론적 기준으로 삼되 EnvCfg/runtime/Scene/Manager/PPO 설정 상속은 끊었다. EEF120mm·3cm/0.005m/s 연속3초 success termination/+75, RED20mm 확장·후방 Gray20mm 후퇴, startup 배치 bank·물성 고정, Dead Zone10k 첫−5°/이후3k 간격이다. CPU82개 통과·CUDA4개 skip. GPU 드라이버 불가로 실제 초기화/rollout/PPO와 collection1~2초는 미검증. [환경 계약](../02_implementation/environments/WRENCH_V0_ENVIRONMENT.md) · [구현·검증 로그](../02_implementation/logs/2026-11-04_wrench_v0_implementation.md).

2026-11-04: `Revision-Test-v2`에 임시 종료 원인 print를 추가했다. `runtime/revision.py`의 `_reset_idx` TEMP 블록에서 환경 ID·step·발동 term 전체를 출력하며, Test-v2-GT·부모 환경은 제외한다. 종료 판정은 유지한다. 후속으로 `shelf_failure`·`object_fall_or_tilt` 함수의 TEMP 블록에서 매 제어 step 현재 값·임계값·개별 판정을 출력한다. 기존 play 프로세스를 재시작하면 적용된다.

- 2026-11-03 **Test-v1 임시 계측 비활성화**: EEF 높이 print 설정·분기,90/95/100mm 시각화 생성 호출·helper 전체를 주석 처리했다. v2·Test-v2·Test-v2-GT에는 활성 출력·면 생성 코드가 없다. 보상 계산은 보존했으며 CPU회귀20개 통과. [기록](../02_implementation/logs/2026-11-02_revision_v1_implementation.md#2026-11-03-임시-높이-계측-주석-처리).

- 2026-11-03 **Test-v2-GT 추가**: `Isaac-Inspire-Revision-Test-v2-GT`, Test-v2 직접 상속. Actor에 기존 Critic의 noise-free root-frame 타겟 XYZ3D를 추가한다. Actor 초기 장애물·초기 타겟 정보와 Critic·보상·PPO는 유지한다. Actor 원시124D·MLP76D, GT 전용 새 학습용이다. CPU33개, GPU64 env32step·부분reset·JIT, PPO2iterations·checkpoint·GT 입력 가중치 갱신을 확인했다. [구현 계약](../02_implementation/environments/REVISION_V2_ENVIRONMENT.md#test-v2-gt-실시간-타겟-위치-대조-실험) · [검증 상태](../02_implementation/logs/2026-11-03_revision_v2_gt_implementation.md).

- 2026-11-03 **Revision-v2 / Test-v2 구현·smoke 완료**: [구현 계약](../02_implementation/environments/REVISION_V2_ENVIRONMENT.md). v1→v2→Test 직접 상속, 거리·Hold·접촉 EEF95mm 미만, Hold weight10·2.5~3.5cm Smoothstep·속도 감쇠 제거, 최초 진입 최대+25×속도 감쇠(free0.01·scale0.02m/s, 높이 무관), timeout+75, free acceleration15m/s²다. 최초 진입은 지급액과 무관하게 기회를 소진한다. 기존 속도 커리큘럼·PPO gamma0.98·부모 정의를 유지했다. Test는 타겟만 원통이며 임시 높이 출력·면은 포함하지 않는다. CPU86개, v2 GPU64/2048·Test64 rollout/부분reset, 실제 EEF·접촉·Hold 지급액, train.py PPO2iterations(v2 2048/Test64)와 유한 checkpoint·두 encoder 갱신 검증을 통과했다. 실제 검증 상태·명령·산출물은 [개발 로그](../02_implementation/logs/2026-11-03_revision_v2_implementation.md)를 따른다. 장기 성능은 미검증.

- 2026-11-02 **Revision-v1 독립 상세 문서 확장**: [환경 상세](../02_implementation/environments/REVISION_V1_ENVIRONMENT.md)에 Actor/Critic 관측 채널·noise·frame, 8D 제어, 형상/물성/reset, 15개 보상 수식·dt·경계, 종료·커리큘럼·PPO를 완결적으로 정리했다. 코드 변경·추가 GPU 실행 없음. [작성 기록](../02_implementation/logs/2026-11-02_revision_v1_standalone_document.md).

- 2026-11-02 **Revision-v1 / Revision-Test-v1 구현·리뷰·smoke 완료**: [구현 계약](../02_implementation/environments/REVISION_V1_ENVIRONMENT.md). v0→v1→Test 직접 상속, object 비용3분리, wrist budget 제거·cap 유지, 7개 schedule 정확한10k 값 고정, 장애물3/3→10k3/4→12k4/4→14k4/5, 3cm 내부 Gaussian Hold·5cm/s 무감쇠, 최초 진입+30/timeout+40을 구현했다. Test는 타겟 kind만 cylinder이며 scale·장애물 난수열을 보존했다. CPU111개, v1 GPU64/2048·Test64 초기화/rollout/부분reset, 실제70/40/30 지급·자동reset, train.py PPO2iterations(v1 2048/Test64)를 통과했다. 두 축 리뷰 잔여 지적0건. [개발·검증 기록](../02_implementation/logs/2026-11-02_revision_v1_implementation.md). 장기 성공률·정밀정지 개선은 미검증. `play.py`는 실행하지 않았고 `logs/rsl_rl`은 보존했다. [기존 개발 명세·그래프](environments/2026-11-02_REVISION_V1_SPEC.md)의 미구현 표기는 설계 당시 상태다.

- 2026-11-01 **독립 Revision-v0 구현**: 최신 사용자 지시에 따라 `Isaac-Inspire-Revision-v0`를 새로 등록했다. 기능 기준은 v0_2이며 기존 Final/Holding CFG·runtime 상속 없이 직접 구성했다. 기존 환경은 보존했다. [Revision 명세](../02_implementation/environments/REVISION_V0_ENVIRONMENT.md) · [구현·리뷰·검증 로그](../02_implementation/logs/2026-11-01_revision_v0_implementation.md).
- 중앙 크기 기준 단일 ±10%, 물리 물체 10개, Gray 65mm 고정 OBB 배치, Actor121D/Critic124D(별도 실시간 장애물), 성공3cm/Hold8cm, 실제 접촉 AND 고정 EEF 높이120mm를 적용했다. 120mm는 8종 기준 높이 평균118.1546mm 및 실제 손 collider의 바닥 여유를 기준으로 정했다. 종류·크기는 생성 시 고정하고 reset마다 배치·활성 구성을 바꾼다.
- CPU20개, 64 env의 8종×정확한 크기 양끝, 2048 env 초기화·sparse/dense35step·부분reset6회, `train.py` 2048 env PPO2iterations 및 유한 체크포인트·두 인코더 갱신 검증을 통과했다. PhysX found/lost aggregate pair 버퍼를 `2**28`에서 기본 `2**25`로 조정했다. 실제 PhysX 접촉 fixture도 EEF 약97~98mm에서 보상1, 약148.5mm에서 보상0을 확인했고 낮은 자세의 손 바닥 여유는 약37mm였다. 학습 후 상부 누르기 감소·장기 성능은 검증하지 않았다. 실험 범위와 재현 명령은 위 개발 로그를 따른다. 산출물은 `outputs/revision_validation`, `outputs/revision_training`에 있으며 `logs/rsl_rl`은 수정하지 않았다.

아래는 Revision 구현 전 요구 확정과 기존 환경의 이력이다.

- 2026-11-01 **최종 8항목 대조·계획 정정, 코드 미반영**: [통합 수정 예정](FINAL_YCB_SIZE_RANDOMIZATION_FIX.md)을 사용자 최종 의도에 맞춰 재작성했다. **v0_2 기준·v0_2_1 구현 참고 금지**는 유지한다. 이전 계획의 원통 알고리즘·size_fraction=1.0 기준·필수 1/8 균등/매 reset 전부 재추출·고정 125 mm 임계값은 이번 정정으로 대체한다.
- 배치 기준은 `outputs/bbox_scene_layout`의 **OBB 기반 텐서 배치**, 독립 구현 `mdp/common/bbox_scene_layout.py`다. `wrist_downward_v2`는 선행 원통 알고리즘이며 적용 대상으로 잘못 특정했던 설명을 정정했다. **Gray 패딩 65 mm 고정·패딩 커리큘럼 삭제**, 장애물 개수 커리큘럼 Gray 1~4 / White 1~5는 유지한다.
- 크기는 기존 YCB 3단계 0.8/0.9/1.0의 **중앙 0.9를 새 기준 크기**로 삼고 Mesh·에셋 모두 각 기준 대비 U(0.9,1.1)을 한 번 적용한다. 타겟·장애물 모두 8종 사용 가능하며 특별한 reset 방식은 강제하지 않는다. 다양한 종류·크기·배치 경험과 scale 반영 바닥 정렬을 검증한다.
- 관측은 조인트→EEF→초기 타겟→목표→이전 행동→센서→장애물 순서, 실제 Arm 값·Hand 2D·16슬롯을 유지한다. Critic은 현재 타겟 3D와 **실제 배치된 활성 장애물만** 현재 좌표로 관측한다. 미사용·주차 후보 제외, 가시성 필터/반전 없음. 기존 정렬·10% 인접 교환 유지, Critic 노이즈/갱신 주기는 구현 시 명시한다.
- 성공 3 cm·Hold 외곽 8 cm·접촉 AND 고정 EEF 높이 제한 계획을 유지한다. **높이는 중앙 크기 반영 후 평균을 재계산하고 바닥 충돌/상부 누르기를 함께 확인해 확정**한다. 공중 스폰·발사·비타겟 bbox 표시·과다 사전 등록을 재발 방지 항목으로 기록했다. **실제 2048 env 초기화·reset·rollout·짧은 학습 검증**이 필요하며 layout benchmark로 대체하지 않는다. 과거 구현 이력은 아래에 보존한다.

- 2026-10-31 추가: [GoalAccuracy v0_2_2](../02_implementation/environments/FINAL_GOAL_ACCURACY_V0_2_2_ENVIRONMENT.md)는 v0_2_1의 새 직계 파생이다. 물리 객체 36→12, prototype cache·전역 물리 재질 공유·텐서 역할 재할당을 사용한다. 기존 환경 정의 42개는 AST 대조로 보존을 확인했다. 보상·관측·OBB 규칙·Gray 4/White 5 일정은 유지하지만 환경별 초기 보유 형상이 고정되어 reset 간 종류 분포의 상관은 달라진다. CPU 109개 및 GPU 4/64 env 반복 reset 검증 통과. 원래 선반 서버가 응답하지 않아 GPU 실행은 로컬 대체 선반을 사용했으며 학습·대규모 collection은 미검증이다. [구현·비교 기록](../02_implementation/logs/2026-10-31_final_v0_2_2_compact_scene.md).

- 2026-10-31 후속 적용: 사용자 요청으로 [OBB 배치 규칙](../02_implementation/environments/BBOX_SCENE_LAYOUT.md)을 **FinalGoalAccuracyV0_2_1EnvCfg reset에 연결**했다. Gray 2500 / White 2000부터 각 1000마다 증가, 4/5 상한 유지. 최소 간격 20mm, Gray 바깥 padding 60→69mm. 주석 처리된 타겟 풀 Scene도 runtime 계약에 맞춰 복원했다. 회귀·기하 106개와 GPU 2 env의 부분 reset 40회·타겟 16종 검사 통과. 다른 환경은 유지하며 학습·대규모 collection은 미검증. [연결·검증 기록](../02_implementation/logs/2026-10-31_final_v0_2_1_obb_reset.md).

- 2026-10-31 구현: [GoalAccuracy v0_2_1 계약](../02_implementation/environments/FINAL_GOAL_ACCURACY_V0_2_1_ENVIRONMENT.md). v0_2 직계 파생으로 실제 타겟 접촉만 보상, timeout +75(2cm 경계 포함), 매 reset 기존 분포에서 타겟 종류를 재추첨한다. CPU 78개 및 GPU 2 env / 부분 reset 40회 / 전체 16후보 검사 통과. 고정 풀 때문에 물리 물체가 21→36개로 증가한다. 비선택 후보는 원격 배치·중력 해제·논리 제외하며 collider flag는 유지한다. 대규모 성능과 학습은 미검증. [개발·검증 기록](../02_implementation/logs/2026-10-31_final_goal_accuracy_v0_2_1_implementation.md).

[환경 안내](../02_implementation/08_ACTIVE_ENVIRONMENTS.md) · [개발 지침](../00_guidelines/09_DEVELOPMENT_GUIDE.md)

2026-10-27 사용자 지정 범위: **`src/inspire_sweep_baseline`이 기반 패키지이며 Holding → Final 계열이 최신 중점 환경**이다. 

- 과업: 선반 위 타겟을 목표 XY 위치로 밀며 촉각·손목 F/T를 사용하는 조작 정책을 학습한다. 초기 장면 정보와 실행 중 현재 상태의 Actor/Critic·보상 사용 범위는 대상 버전에서 확인한다.
- 개발 흐름: Holding → Holding OSC → Holding OSC ObjectRandom의 구성을 바탕으로 Final을 개발했다. 이는 개발 흐름이며 모두 직접 Python 상속 관계라는 뜻은 아니다. Final v0는 독립 구성이고, Final v1과 그 파생 환경이 현재 핵심 비교 대상이다.
- 요청 대상: Final-v1, v1-1, Test-v1, GoalAccuracy-v0, v2/Test-v2 등을 서로 혼동하지 않는다. 등록 ID와 부모를 실제 코드에서 확인한다.
- 2026-10-27 추가: [GoalAccuracy-v1](../02_implementation/environments/FINAL_GOAL_ACCURACY_V1_ENVIRONMENT.md)은 Accuracy v0를 상속해 1cm 고정 반경을 유지하며 외곽 goal_hold·goal_speed_scale을 복원한다. object_free_speed는 v0에서도 활성이다. Final v1과의 잔여 차이·검증 범위는 해당 명세를 따른다.
- 계약: 목표 도달은 `d <= r`. 직접 수정 요청은 해당 버전에 적용하고 새 파생 요청은 부모를 보존한다. 완료 전 모든 설정·함수·커리큘럼·로그 차이를 요청과 대조한다.
- 실행: `scripts/train.py`와 `scripts/play.py`를 사용한다. 검증 상태·상세 명령은 대상 환경 설명과 해당 개발 로그에서 확인한다.

- 2026-10-30 후속: [Accuracy 물체 수 상한 변경](../02_implementation/logs/2026-10-30_goal_accuracy_population_cap.md). 공통 부모 및 모든 하위 환경(v0·v1·v0_1·v0_2·v0_3)의 최종 장애물 요청 수를 **Gray 4·White 5**로 고정했다. 5000 iteration까지 기존 일정, 이후 추가 증가 없음. 물체 용량·관측 슬롯·Gray padding 등 다른 설정은 유지한다.

- 2026-10-30: 수락된 [Accuracy v0_3 개발 명세](environments/2026-10-30_FINAL_GOAL_ACCURACY_V0_3_SPEC.md)대로 v0_2를 직접 상속하여 구현했다. 접촉 OR 목표 점유 유지·weight 1/4, 최단 거리 갱신 보상·허용 거리 0·weight 100, timeout +100, 목표 반경 3cm다. [구현 계약](../02_implementation/environments/FINAL_GOAL_ACCURACY_V0_3_ENVIRONMENT.md)에 CPU·실제 설정 검증과 독립 리뷰 결과를 기록했다. GPU 부재로 실제 물리·학습은 미검증이다. Reaching은 현재 부모 코드 10cm를 보존한다.

- 2026-10-28: [Accuracy v0_1 구현 계약](../02_implementation/environments/FINAL_GOAL_ACCURACY_V0_1_ENVIRONMENT.md)을 추가했다. v0를 상속하여 2cm 목표, 타겟 Contact, 고정 20cm Reaching, 6cm 외곽 Hold, 지수 거리 weight 3.7, 0.06×0.08×0.10m 큐브 타겟을 적용한다. 기존 ±10% 크기 랜덤화와 reset은 유지한다. Manager 이름은 [개발 사양 8.3절](environments/2026-10-28_FINAL_GOAL_ACCURACY_V0_1_REWARD_SPEC.md)의 대상별 명칭으로 교정했다. 기존 v0/v1은 Gym ID의 Accuacy→Accuracy 이름만 교정하고 동작은 보존했다. 설정·USD·CPU 검증과 미완료 물리 검증을 구현 로그에서 구분한다.
