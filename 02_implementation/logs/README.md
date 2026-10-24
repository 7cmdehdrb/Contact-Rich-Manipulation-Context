# 개발·실험 진행 로그

- [2026-10-24 ObjectRandom-v2 상한 선택](2026-10-24_object_random_v2_population_cap.md): 7/7 반복 reset 불통과에 따라 최대6/6으로 변경, 반복 검사와 한계 기록.

- [2026-10-24 Holding v3 · OSC v3 · ObjectRandom v2](2026-10-24_fusion_holding_v3.md): goal hold 누적3초, 같은OSC, 개수1000간격과 Gray 내측15% 커리큘럼·검증.

- [2026-10-24 Three-view 녹화 대상 설정](2026-10-24_three_view_recording_config.md): 환경·checkpoint·시간 기본값, Windows D3D12,720p와 녹화용 PhysX 버퍼 제한, 세MP4·10초 검증.

- [2026-10-24 TEMP 전체 학습 감사·action 피드백 발산 수정](2026-10-24_temp_training_stability.md):4개 run·50개 checkpoint 감사, 실제 실패 입력 포착과 모델 replay, 이전 action 관측 제한·PPO 수치 검사.

- [2026-10-24 Holding OSC v2 resume 발산 재조사](2026-10-24_holding_osc_resume_crash_audit.md): 정정된 TEMP run에서 value loss1.94e21 및 원본 run의NaN 확인, checkpoint5개 유한성 검사.

- [2026-10-24 Holding v0 PPO 표준편차 오류 조사](2026-10-24_holding_v0_std_crash_audit.md): 두 run·24개 checkpoint 감사, scalar std와 음수/NaN 오류 구분의 한계.

- [2026-10-24 Windows Vulkan 초기화 크래시](2026-10-24_windows_vulkan_startup.md): Sweep 미사용 최소 재현, RTX SceneDB 접근 위반 및 train/play의 D3D12 기본 선택.

- [2026-10-23 환경 파일 구조 통합](2026-10-23_environment_structure_migration.md): 역할별 배치·복구 commit,45개 설정 동등성·초기 GPU/PPO·대표 train.py 검증. ObjectRandom 후기 배치 실패는 이관 전 원본에서도 재현.

- [2026-10-23 Holding ObjectRandom Test v0](2026-10-23_holding_object_random_test_v0.md): Joint Position 제어·랜덤 물체 테스트 환경 추가.

- [2026-10-23 ObjectRandom-v1 개수 일정](2026-10-23_object_random_v1_population.md): 부모의 교대 증가 일정 복원, 초기1/1→최대8/8,16슬롯 사용.

- [2026-10-23 Fusion Holding v2](2026-10-23_fusion_holding_v2.md): 공통 목표 반경·목표 내 접촉 보상·OSC-v2와ObjectRandom-v1 상속 변경.

- [2026-10-23 Holding OSC v2](2026-10-23_fusion_holding_osc_v2.md): Holding v1 직접 상속, UR10 Reach RPY·effort 제한 제어와 로컬 EEF 기준점.

- [2026-10-23 Fusion Holding v1 계열](2026-10-23_fusion_holding_v1.md): 장애물16슬롯·64→32→16D, OSC v0/v1 Robot Base 기준·stiffness100, ObjectRandom v1 직접 상속과 기존 v0 보존.

- [2026-10-23 Fusion Holding v0](2026-10-23_fusion_holding_v0.md): v1_0 직접 파생, 정착 보상·충격 warmup·독립 성공 판정.

- [2026-10-23 Fusion v1_0 학습 진행별 물리 측정값](2026-10-23_fusion_v1_0_training_trend.md): checkpoint1000~15000, 각각16환경·30초, 환경별 평균·중앙값·최대값의16환경 평균 및 추이 그래프.

- [2026-10-23 Fusion v1_4 환경 문서화](2026-10-23_clutter_fusion_v1_4_documentation.md): 설명·직접 상속 계층·문서 검사.

- [2026-10-23 Fusion 3카메라 동기화 녹화](2026-10-23_fusion_three_view_recording.md)

- [2026-10-23 Fusion v1_4 직접 계승 환경](2026-10-23_clutter_fusion_v1_4.md): v1_0 기반 250 간격·후반 페널티·11개 물체·3초 성공 종료와 CPU 검증.

- [2026-10-23 Fusion v1_0 체크포인트 이미지 모음](2026-10-23_fusion_v1_0_checkpoint_figures.md): model_10000·model_16400 환경별 측정 그래프.

- [2026-10-23 Fusion v1_0 체크포인트 비교](2026-10-23_fusion_v1_0_checkpoint_comparison.md): model_10000/model_16400, 각각16환경·60초, 타겟 제외 접촉력과 EEF·가속도·RAW F/T 환경별 통계 및 이미지.

- [2026-10-23 Fusion v1_3_1 환경별 측정 통계](2026-10-23_fusion_v1_3_1_measurement_statistics.md): threshold 적용 후 EEF 속력·물체 힘/가속도·RAW F/T 중앙값/평균/최대와 그래프.

- [2026-10-23 Fusion v1_3_1 페널티 입력 계측](2026-10-23_fusion_v1_3_1_reward_inputs.md): model_14500, 후속 요청으로16환경·162.14초에서 중단, EEF 속력·물체별 힘/가속도·RAW/보정 F/T와 reset257건.

- [2026-10-23 Fusion v1_0 마지막 5% 보상 구성](2026-10-23_fusion_v1_0_last5pct_rewards.md): iteration 15612~16433, 822개 기록의 17개 보상 평균·전체/군내 비중.

- [2026-10-23 Fusion v1_0 종료 원인 출력](2026-10-23_fusion_v1_0_termination_prints.md): timeout 포함 활성 종료 항목·환경 ID·동시 원인 출력과 CPU 검증.
- [2026-10-23 스폰 규칙 고도화와 Event 개발 계획](2026-10-23_clutter_spawn_event_plan.md): 영역별 개수·불변 제약·유효 부분 배치·reset Event·고밀도 용량 확장 계획, 코드 변경 없음.

- [2026-10-23 후속 연구·개발 TODO 구체화](2026-10-23_workspace_todo.md): OSC·고밀도·실사용 에셋·물성 비교·가제본 작업과 완료 기준 정리.

- [2026-10-22 Fusion v1_3_1 Goal·접촉 fade 커리큘럼](2026-10-22_clutter_fusion_v1_3_1.md)

- [2026-10-22 Fusion v1_3 선형 커리큘럼](2026-10-22_clutter_fusion_v1_3.md)

- [2026-10-22 Fusion v1_1_2 힘 커리큘럼 실험 분기](2026-10-22_clutter_fusion_v1_1_2.md)

- [2026-10-22 Fusion v1_1_1 가속도 실험 분기](2026-10-22_clutter_fusion_v1_1_1.md)

- [2026-10-22 Fusion v1_1 / v1_2 파라미터 커리큘럼](2026-10-22_clutter_fusion_v1_1_v1_2.md)

- [2026-10-22 Fusion v1_0 접촉 감쇠·Goal 반경·가속도 기준 수정](2026-10-22_clutter_fusion_v1_0_reward_thresholds.md)

- [2026-10-22 전체 환경 독립 문서·계층도](2026-10-22_environment_catalog.md): 등록 29종 대조, 기존 7개 유지·간략 문서 22개 추가, 변경 의도·상대 링크와 문서 검증.

- [2026-10-22 Fusion v1_0 장애물 관측 정렬·압축·순차 교환](2026-10-22_clutter_fusion_v1_0_observation_order.md)

- [2026-10-22 Fusion v1_0 독립 설명·버전 비교 문서](2026-10-22_clutter_fusion_v1_0_documentation.md)

- [2026-10-22 Fusion v1.0 가속도 상한 점검·PhysX 직접 가속도](2026-10-22_clutter_fusion_v1_0_native_acceleration.md)

- [2026-10-22 Fusion v1.0 개수·접촉 감쇠·학습 복구](2026-10-22_clutter_fusion_v1_0_population_recovery.md): 같은 task의 장애물1/1→3/3, Goal tolerance와 동기화한 alpha, 가속·감속 대칭, 최신 checkpoint−500 자동 재개와 커리큘럼 복원.

- [2026-10-22 Fusion v1.0](2026-10-22_clutter_fusion_v1_0.md): v3 상속, 독립 보상·종료·커리큘럼 CFG, 손 전체 접촉 및 비타겟 힘, EEF wrench 크기 변화량, 물체별 가속도와 보상 계수 근거.

- [2026-10-22 Fusion v3 후반 보상 비중](2026-10-22_fusion_v3_reward_balance.md): 지정 run의 iteration 6000~7389, 14개 보상 평균과 전체·군내 비중, 원본 event 대조와 재현 CSV.

- [2026-10-22 Fusion v3 F/T·물체 선속도 수집](2026-10-22_fusion_telemetry.md): 지정 model_7200의 16환경 재생, 월드·EEF 보정 F/T와 Target·장애물 선속도 CSV, 종료 직전 표본과 reset 차분 경계.

- [2026-10-21 Clutter Fusion v3 재구성](2026-10-21_clutter_fusion_v3.md): v0 → v2 → v3, 기존 v1 커리큘럼을 v3으로 이동. 현재 push_fast는 v0·v2·v3 모두 0.8 고정. 별도 버전 비교 문서를 추가했다.

- [2026-10-21 Clutter Fusion v2](2026-10-21_clutter_fusion_v2.md): Fusion v0 직접 상속, EEF orientation 보상 제거. push_fast는 v0·v2·v3 모두 0.8 유지.

- [2026-10-21 Clutter Fusion v1](2026-10-21_clutter_fusion_v1.md): 최초 v1의 역사 기록. 현재는 v3으로 재작명했으며 당시 수치·명령과 현재 계약을 구분한다.

- [2026-10-20 Clutter v1 Curriculum](2026-10-20_clutter_v1_curriculum.md): Learning iteration 기반 물체·Arm free speed와 Arm 두 운동 비용 가중치 일정, checkpoint 재개·재생 연결과 CPU 검증·GPU 실행 제한.

=======
>>>>>>> e133c09 (feat: Add one-time penalty for shelf failure in Clutter v1 and update logs)
- [2026-10-20 Clutter v1 선반 실패 비용](2026-10-20_clutter_v1_shelf_failure.md): shelf 실패의 마지막 전이에 일회성 −3, reset 전 보상 반영과 시간 배율·다음 에피소드 반복 방지 검증.

- [2026-10-20 Contact Sweep Clutter v2](2026-10-20_contact_sweep_clutter_v2.md): Hand 중력·관성 하중을 제거한 6축 F/T 관측, 급격한 힘·모멘트 변화의 제곱 비용과 실제 양의 보상 대비 누적 5% 한도.

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

- [2026-10-21 TEMP 학습 로그 정리](2026-10-21_temp_training_log_cleanup.md): 명시적 요청에 따른 세 차례 정리 기록·환경별 이동과 500 iteration 미만 삭제·rsl_rl 보존 검증.

- [2026-10-22 TEMP 학습 로그 정리](2026-10-22_temp_training_log_cleanup.md): 17개 run 중 9개 이동·500회 미만 8개 삭제, 파일 보존 및 rsl_rl 불변 확인.

- [2026-10-23 Holding OSC v0](2026-10-23_fusion_holding_osc_v0.md): Holding 직접 상속·Arm OSC 교체와 설정 동등성·GPU 검증.

- [2026-10-23 Holding OSC ObjectRandom](2026-10-23_holding_osc_object_random_v0.md): NVIDIA 물체·균일크기·비겹침 배치.
