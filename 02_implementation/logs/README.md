# 개발·실험 진행 로그

- [2026-10-20 Contact Sweep Clutter v1](2026-10-20_contact_sweep_clutter_v1.md): 초기 타겟 Actor·현재 XYZ Critic, 목표 유지·촉각·장애물 이동 보상, 지정 v0 로그 기반 계수 산정과 CPU·GPU 검증.

- [2026-10-20 Contact Sweep 통합 문서](2026-10-20_contact_sweep_documentation.md): 두 환경의 최신 구성·차이·실행·검증 범위를 하나의 설명으로 정리.

- [2026-10-20 Clutter v0 RED 확대·장애물 감소](2026-10-20_clutter_red_expansion.md): RED 제외 반경 8.3→10.3 cm, 장애물 6→3개(뒤쪽 GRAY 1·WHITE 2), 40D 관측 유지.

- [2026-10-20 Contact Sweep Clutter](2026-10-20_contact_sweep_clutter.md): Contact Sweep 상속, 목표 확정 후 장애물 6개 배치, 전체 물체 tilt·낙하와 초기 장애물 40D→16D 학습 임베딩.

- [2026-10-20 Contact Sweep 독립 기준 환경](2026-10-20_contact_sweep_reference.md): 기존 v3 보존, 독립 Env·Manager/PPO Cfg 구성, 설정·가중치 동등성 및 CPU 131개·GPU 검증.

- [2026-10-20 Dex Tactile Renewal v3](2026-10-20_renewal_v3_reward_mass.md): v1 직접 상속, 경험적 goal weight=94, 질량 1.5배, pushing speed 비용 강화와 CPU·GPU 검증.

[문서 안내](../../01_plan/README.md) · [현재 상태](../07_CODE_AND_HARDWARE_STATUS.md) · [현재 활성 환경](../08_ACTIVE_ENVIRONMENTS.md) · [로그 작성 지침](../../00_guidelines/09_DEVELOPMENT_GUIDE.md)

| 기록일 | 문서 | 기록의 범위 |
| --- | --- | --- |
| 2026-10-19 | [v1 Arm 속도 제한](2026-10-19_v1_arm_velocity_limits.md) | 앞 3개 2 rad/s·손목 3개 4 rad/s, v2·OSC 상속 및 CPU 검증 |
| 2026-10-19 | [종료 이벤트 print](2026-10-19_v1_termination_prints.md) | 공통 환경의 reset 직전 모든 종료 원인 출력·동시 발생·timeout·환경 번호·episode step |
| 2026-10-18 | [v2의 v1 상속 전환](2026-10-18_v2_inherits_v1.md) | v0→v1→v2→OSC v2 체인·비용 상한·손목 높이·목표 방향 상속·기존 양의 보상 유지 |
| 2026-10-18 | [Omni 제곱합 비용 출력 상한](2026-10-18_omni_squared_cost_caps.md) | action_rate_l2·joint_vel_l2 반환 [0,100], 입력·그룹·가중치 유지 및 CPU 경계 검증 |
| 2026-10-18 | [v2 성공 후 timeout까지 목표 유지](2026-10-18_v2_goal_hold_until_timeout.md) | 성공 종료 제거·episode당 +100 한 번·성공 후 유지 보상 계속 지급·OSC 상속 적용 |
| 2026-10-18 | [Dex Tactile OSC v2](2026-10-18_dex_tactile_renewal_v2_osc.md) | v2 상속·OSC stiffness 100·5 mm/0.025 rad 명령 제한·GPU 속도 대조 및 안정성 한계 |
| 2026-10-18 | [Dex Tactile v2 목표 유지·성공 보상](2026-10-18_dex_tactile_renewal_v2_goal_hold.md) | v0 직접 상속, 0.5초 안정 유지 성공, +100 일회성 보너스와 증가하는 양의 체류 보상 |
| 2026-10-09 | [OSC와 Hand 이식 진행](1009.md) | Reach·Sweep 실패 관찰, 참고 환경의 Hand 교체·2D action·센서·무거운 물체 확장 |
| 2026-10-10 | [무거운 물체·센서·도달 스킵 환경](1010.md) | 참고 환경 변형의 구현·CPU 검증, 목표 높이·정렬축 수정 |
| 2026-10-12 | [Inspire Hand 단계별 학습 기록](2026-10-12_inspire_hand_training.md) | 원격에 추가된 Hand·센서·관측 제한별 학습 보고와 후속 검증; [구현·검증 TODO](../../01_plan/TODO.md) |
| 2026-10-12 | [당시 src Hand 환경과 재생 명령](1012_src_robot_hand_environments.md) | 현재 보관된 12개 환경의 당시 구성, 저장 설정·checkpoint 비교; 이번 정리의 활성 목록과 구분 |
| 2026-10-12 | [당시 최신 checkpoint와 재생 명령](1012_latest_checkpoints_play.md) | 10월 12일까지 확인한 모델 경로·차원·재생 옵션; 파일 존재가 정책 성공을 입증하지 않음 |
| 2026-10-14 | [Workspace 정리](2026-10-14_workspace_cleanup.md) | 활성 범위·보관 이동·문서 역할 정리와 검증 |
| 2026-10-14 | [문서 네 폴더 재구성](2026-10-14_document_reorganization.md) | 지침·계획·실제 코드 기록·정적 자산 분류, 내부·workspace·CSV/XLSX 참조와 검증 |
| 2026-10-14 | [Baseline 환경 UML](2026-10-14_inspire_sweep_uml.md) | Isaac Lab·PPO 실행 연결, 환경 Cfg 상속·callable 연결과 HTML 검증 |
| 2026-10-14 | [Omni 첫 스텝 종료 진단](2026-10-14_omni_immediate_termination.md) | 4,138개 iteration의 Arm 속도 종료·1스텝 에피소드 확인, 제어 경로와 GPU 재현 미실행 범위 |
| 2026-10-14 | [Omni v1 Arm 속도 기준](2026-10-14_omni_v1_arm_velocity.md) | v0 상속·종료 기준 2.0 rad/s·새 task 등록과 CPU 경계·격리 검증 |
| 2026-10-14 | [Omni Arm 비용 복원](2026-10-14_omni_arm_costs_baseline.md) | Arm action 변화·속도 비용의 Baseline 동등성, v0/v1 공통 적용과 CPU 검증 |
| 2026-10-14 | [ContactSensor 계약 대조](2026-10-14_contact_sensor_contract.md) | USD의 17개 sensor body/collider와 현행 1D palm bit 관측의 차이·CPU 검증 |
| 2026-10-14 | [Baseline 17채널 Tactile 구현](2026-10-14_baseline_tactile17.md) | 기존 자산·물리 유지, 독립 Binary·부모 접촉 영역 분류·57D policy 및 CPU·USD 검증 |
| 2026-10-15 | [Omni 재생 속도 기준 차이](2026-10-15_omni_play_threshold_mismatch.md) | 최근 checkpoint 학습 기준 100.0과 v0 기본값 1.0의 차이, 학습 종료 통계와 재생 미확인 범위 |
| 2026-10-15 | [Tactile GPU 필터 경고 수정](2026-10-15_tactile_gpu_filter_fix.md) | 미지원 Shelf·ground filter 제거, 17개 독립 입력 유지·디버그 marker 분리와 센싱 범위 명시 |
| 2026-10-15 | [Tactile·F/T 구현 Flow](2026-10-15_sensor_flow_diagrams.md) | 직접 접촉·영역 투영·6축 반력 변환의 HTML 흐름도, 코드 근거와 검증 범위 |
| 2026-10-15 | [패드·F/T 코드 구현 상세](2026-10-15_sensor_code_flow_diagrams.md) | 기존 Flow 유지, USD 패드 구성·영역 생성·PhysX view·텐서 계산·F/T authoring의 상세도와 실제 소스 발췌 |
| 2026-10-15 | [Dex Omni 기록 갱신 보상](2026-10-15_dex_omni_rewards.md) | DexTouch 거리 개선량 shaping, OmniV2 페널티·종료·스폰 보존, 새 task 등록과 CPU 회귀 검증 |
| 2026-10-15 | [환경별 구성 문서 작성](2026-10-15_environment_contract_notes.md) | Sweep Omni v3·Dex Omni v0 독립 설명, 현재 작업트리 기준·CPU 및 문서 검증 |
| 2026-10-15 | [Omni v4 속도 비용과 종료 조건](2026-10-15_omni_v4_speed_penalty.md) | V3 상속·Arm/물체 속도 기준 변경·외곽/성공 종료 제거·제곱 속도 비용과 CPU 검증 |

- [Omni v2 접근·목표 진전 보상](2026-10-15_omni_v2_rewards.md) — 로컬 구현·후속 보상 및 종료 변경 기록.
- [Omni v3 높이 조건부 XY Reaching](2026-10-15_omni_v3_height_gated_reaching.md) — 현재 v2 상속, Z gate와 XY 기록 갱신, CPU 83개 검사.

새 기록은 `YYYY-MM-DD_<topic>.md` 형식으로 만든다. 환경의 상속 관계·전체 task ID·실행 명령·기준 commit·변경과 검증·미확인 항목을 남긴다. 실험 조건과 정량 결과는 `02_implementation/experiments/`에 연결하고, 연구 방향의 변화는 결정·brief·다음 작업 문서도 갱신한다. 과거 로그의 당시 결론은 유지하며 새 관찰은 새 날짜의 기록으로 추가한다.

Pull/rebase 중 문서 이관 충돌의 처리 내역은 [충돌 해결 기록](2026-10-14_rebase_conflict_resolution.md)에 남겼다.

- [2026-10-15 Omni 공통 운동 페널티](2026-10-15_omni_penalty_contract.md): 모든 Omni 파생에 raw Action·관절 속도 제곱합과 필수 사용 규칙 적용.

- [2026-10-15 V4 초기 Arm 속도 종료](2026-10-15_omni_v4_early_termination.md): 로컬 V3/V4·보관 Dex·원격 TensorBoard 비교, 현재 코드와 run 저장 설정 구분 및 미확정 원인.

- [2026-10-15 V4에 저장 V3 파라미터 적용](2026-10-15_omni_v4_saved_parameters.md): 원격 정상 run의 Arm 속도 threshold 5.0을 코드 기본값에 반영하고 V4 전용 조건 유지.

- [2026-10-15 V4 최대 Arm 속도 추가 비용](2026-10-15_omni_v4_arm_speed_excess.md): 기존 비용 유지, 최대 절대속도 1.0부터 제곱 증가·2.0에서 weighted −0.03.

- [2026-10-15 Renewal 환경 재구성](2026-10-15_omni_renewal_environments.md): V4 동작과 동일한 명시적 환경 구성·Dex의 두 보상 교체·Gym 등록과 CPU 계약 검증.

- [Reaching 최고 기록 이탈 페널티](2026-10-15_reaching_regression.md)

- [Renewal OSC 환경 추가](2026-10-15_renewal_osc.md)

- [체크포인트 재생 배속 옵션](2026-10-16_playback_speed.md)

- [OSC 선반 종료와 목표 시각화](2026-10-16_osc_shelf_goal_visualization.md)

- [Inspire Hand 촉각 벡터 검증](2026-10-16_tactile_validation.md)

- [촉각 검증 결과 시각화](2026-10-16_tactile_visualization.md)

- [촉각 검증 루프 수정 및 배치 비교](2026-10-16_tactile_validation_correction.md)

- [Renewal 17채널 촉각 환경 두 종류](2026-10-16_tactile_renewal_environments.md)

- [Renewal Tactile v1 지수 속도 비용](2026-10-16_tactile_renewal_v1_exponential.md)

- [지수 속도 비용의 OSC·Dex 부모 적용 정정](2026-10-16_renewal_exponential_parent_scope.md)

- [촉각 v0 지수 비용 통합 및 중복 v1 삭제](2026-10-16_tactile_v0_exponential_cleanup.md)

- [Renewal 기본 속도 비용 exp 통일 및 중복 클래스 삭제](2026-10-16_renewal_only_exponential.md)

- [접근·목표 진행 보상 4종 수식 정리](2026-10-16_reward_formulas.md)

- [Dex Tactile Renewal v1](2026-10-16_dex_tactile_renewal_v1.md): 지수 비용 상한 100·손목 높이 3 cm·로컬 ±X 각각 ±15° 제외.

- [2026-10-19 Renewal v2 PPO 중단 진단](2026-10-19_renewal_v2_ppo_crash_audit.md): 두 실행의 12943 iteration·260 checkpoint, reward/termination 반환 범위와 CPU 합성 입력 조사.

- [2026-10-20 Pull/Rebase 충돌 해결](2026-10-20_rebase_conflict_resolution.md): 환경 설명·로그 색인의 양쪽 변경 보존과 문서 검증.
