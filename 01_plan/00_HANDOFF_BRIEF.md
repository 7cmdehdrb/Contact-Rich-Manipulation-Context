# 현재 개발 인계

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
