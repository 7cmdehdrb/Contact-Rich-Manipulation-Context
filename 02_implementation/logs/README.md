# Holding · Final 개발 로그

- 2026-11-13 **Finger-ForceDirection-v0 추가**: Finger-v0-Test 직접 자식. 기존 힘 방향 보상0.33 추가(방향 무시1cm·실제 접촉/수평1N 필요), 목표 내 접촉 간주3→1cm. 성공 종료/메트릭3cm·Clip·Last Action·PPO·기존 보상 보존. 장기 학습 개시 보고 없음. [계약·리뷰·검증](2026-11-13_finger_test_force_direction.md).

- 2026-11-13 **Simple 학습 현황 정정(사용자 보고)**: 기존 Finger-v1/v2·Semi-Prof-v0는 실패·방안 잠정 폐기. 과도한 손 동작 대응을 우선하며 현재 .180에서 Finger-v0-Test, .250에서 Prof-v2 학습 중. v1 실패 후 Test를 수정한 네이밍 혼선은 기록만 보존한다. 실제 Prof 변경 대상은 Prof-v1 자식 Prof-v2이며 Prof-v0 직접 수정이 아니다. [상태·경위](2026-11-13_simple_training_status.md).

- 2026-11-13 **Prof-v2 손6축 후속 변경**: 해당 ID에만 Finger와 같은 drive6관절 관측·절대 rad 제어를 적용했다. 액션12D·policy66D+obstacles64D, PPO 모델·action-rate 손6채널·zero-radian reset 연동. Runner Clip±π/2·raw Last Action·팔1rad/s 종료·접촉 높이12cm 유지. Prof-v1/Finger 유지, 구8D Prof-v2 checkpoint 직접 재개 불가. [변경·검증](2026-11-13_sweep_simple_prof_v2.md#후속-변경-prof-v2-손6차원-관측제어).

- 2026-11-13 **Simple Prof-v2 추가**: Prof-v1 직접 상속. 팔 속도 종료1.0rad/s 고정·해당 커리큘럼 제거, Runner `clip_actions=π/2`, 접촉 조건부 Goal Distance/방향 비용의 EEF 높이15→12cm. Last Action은 Clip 후 raw 입력·tanh 제거, 보상식/계수 보존. CPU69개·GPU64환경/2iterations 검증, 장기 행동 개선 미검증. [변경·검증](2026-11-13_sweep_simple_prof_v2.md).

- 2026-11-13 **Finger-v0-Test Runner Clip**: 해당 ID에만 `clip_actions=π/2`를 적용한다. 12축 공통 Clip은 OSC scale 전이며, Last Action은 manager 입력 그대로(tanh·추가 Clip 없음), action-rate는 Clip 후 current/previous 값의 제곱합·cap 없음. 부모·v1·Wrench 유지. [변경·검증](2026-11-13_finger_v0_test_runner_clip.md).

- 2026-11-13 **wr4 Finger 수치 중단 진단**: v0-Test의 F/T 입력 증폭→raw action-rate→value loss와 v1의 raw Gaussian entropy·실행 clip 불일치에 따른 분포 확대를 구분. 저장 덤프로 CPU/RTX 3090 양쪽 오류 재현, 환경·PPO 변경 없음. [기록](2026-11-13_wr4_numerical_diagnosis.md).

- 2026-11-11 **Finger 네 환경 최종 리뷰**: v0/Wrench/Test/v1의 최신 계약·상속 격리·실행/PPO 경로 대조. Standards/Spec 결함 발견 없음, 관련 CPU 테스트 46개 통과. GPU 물리 실행 미검증. [기록](2026-11-11_finger_final_review.md).

- 2026-11-11 **전체 환경 Action 변화 비용 상한 제거**: 활성 inspire_sweep_baseline 전 계열의 action-rate 출력 cap과 관련 설정 제거. 가중치·입력 처리·다른 비용 상한 유지. 과거 문서의 action-rate cap100 설명보다 이번 계약이 우선한다. [기록](2026-11-11_action_rate_uncapped.md).

- 2026-11-11 **Finger-v1 속도 조건 변경**: 팔 속도 종료1.0rad/s 고정·해당 커리큘럼 제거·팔 비용−0.03. v2/Semi-Prof 및 세 Raw 자식에도 상속. 액션·Last Action·PPO 및 다른 일정 유지. [기록](2026-11-11_finger_v1_fixed_velocity.md).

- 2026-11-11 **Wrench 실행·관측 Clip 적용**: 참고 예제와 같은 센서 범위 Clip→Scale→모멘트 보정, 손6축 URDF Raw Clip, Last Action은 tanh 없이 Clip된 Raw12D. PPO 원본 샘플·기존 action-rate·고정1rad/s 종료 유지. [계약·검증](2026-11-11_finger_wrench_action_clipping.md).

- 2026-11-11 **Wrench 팔 속도 종료 수정**: 기존 Finger-v0-Wrench ID의 임계값을1.0rad/s 고정으로 변경하고 해당 커리큘럼만 비활성화했다. 부모·제어기·보상·다른 일정 보존. [후속 기록](2026-11-11_finger_v0_wrench_osc.md#후속-변경-팔-속도-종료10rads-고정).

- 2026-11-11 **Simple 최종 환경 문서 갱신**: Test/Wrench를 포함한15개 ID와 Finger 제어·종료 비교표, 프레임 차이 및 검증 범위를 정리했다. 코드 변경 없음. [기록](2026-11-11_sweep_simple_final_documentation.md).

- [2026-11-11 Finger-v0-Wrench 센서 Wrench OSC](2026-11-11_finger_v0_wrench_osc.md): Finger-v0 직접 상속·팔 제어만 변경·모멘트 원점 보정·부모 보존.

- [2026-11-11 Finger-v0-Test 고정 속도 종료](2026-11-11_finger_v0_test_velocity_termination.md): Finger-v0 직접 상속·팔1.0rad/s 고정 종료·관련 커리큘럼만 제거.

- [2026-11-11 Raw 환경 분리·원환경 play 복원](2026-11-11_finger_raw_environment_split.md): 기존3개 ID 롤백·Raw3개 ID 추가, Semi-Prof5% 상한 제거 유지.

- [2026-11-11 Finger Raw Action 복원](2026-11-11_finger_raw_action_restore.md): 추가 Clip 제거·Last Action tanh·속도 비용−0.03 복원, 터미네이션 보존.

- [2026-11-11 Semi-Prof 보상 순서 오류](2026-11-11_semi_prof_reward_order_incident.md): Wrench 활성화 시 중단 재현·사용자 지시에 따른5% 상한/순서 제약 제거·실제 RewardManager 커리큘럼 회귀.

- [2026-11-11 중대 이슈: Gaussian 액션 클리핑 전환](2026-11-11_gaussian_action_clipping_incident.md): Finger-v1/v2·Semi-Prof 공유 정책의 gradient 오류 재현·tanh/atanh 제거·원본 PPO 샘플과 실행 명령 분리·회귀 검증.

현재 계열과 공통 작업 기록을 안내한다. 이전 환경의 로그 색인은 [정리 전 백업](../history/2026-10-27_agent_context/README.md)에 보존했다. 개별 과거 로그는 변경하지 않는다.

- [2026-10-28 Final GoalAccuracy v0_1](2026-10-28_final_goal_accuracy_v0_1.md): 2cm 인정·타겟 접촉·외곽 Hold·지수 거리 보상·직육면체 타겟·명칭 정리, 부모 보존·CPU 및 USD 검증·물리 실행 제한.

- [2026-10-27 에이전트 컨텍스트 정리](2026-10-27_agent_context_cleanup.md): 활성 범위 축소, 원문 백업, 링크·문서 검증.

- [2026-10-27 환경 수정 공통 지침](2026-10-27_environment_change_policy.md): 현재 구조 유지, 직접 수정·파생 환경 생성 구분, 부모 보존, 전체 대조와 수정 의도 기록.

- [2026-10-27 Final GoalAccuacy v0](2026-10-27_final_goal_accuracy.md): 1cm 고정 반경·엄격한 인정 조건·장애물 일정·TensorBoard 지표, 검증 범위.

- [2026-10-27 Final v1-Test object_penalty 분리](2026-10-27_final_v1_test_object_penalty.md): 세 RewardManager term, v1 checkpoint 재개 경로, CPU 수식 검사·GPU reset/step·checkpoint 로드.

- [2026-10-27 Final v1 3000·9500 보상 재생 진단](2026-10-27_final_v1_reward_play_diagnostics.md): checkpoint 확인, 보상 내부 분해용 play 분석기, CPU 물리 실행 제한과 GPU 재현 명령.

- [2026-10-27 Final v1-1 Goal Distance](2026-10-27_final_v1_1_goal_proximity.md): v1 상속·지수형 XY 근접 보상, 지정 TEMP 로그 근거, 실행 검사와 학습 미검증 범위.

- [2026-10-26 Final v1·v2](2026-10-26_final_v1_v2.md): 이전 환경 보존,57D 정책·20슬롯, 배치 fallback·USD 자산·CPU/PPO 검증과 GPU 물리 실행 제한.

- [2026-10-26 ObjectRandom-v3 마지막500 iteration 보상 비중](2026-10-26_reward_share_last500.md): step11500~11999, 양의 보상·페널티와 전체 절댓값 기여.

- [2026-10-26 Python 캐시 정리](2026-10-26_python_cache_cleanup.md): Inspire 패키지 내부 캐시 47개 디렉터리·339개 파일 삭제, 나머지 파일 보존 검사.

- [2026-10-26 Final v0 독립 구성](2026-10-26_final_v0.md): 기존 task 상속 제거, 설정·lifecycle 동등성 검사와 GPU 검증 제한.

- [2026-10-25 Holding 계열 문서 최신화](2026-10-25_holding_documentation_refresh.md): v3 통합·최신 세 환경·r 기반 보상·정적 검증.

- [2026-10-25 Holding v4 · OSC v4 · ObjectRandom v3](2026-10-25_fusion_holding_v4.md): success 제거·중심 holding 강화·goal 연동 reaching, 이전 제어·랜덤화 보존과 검증.

- [2026-10-25 ObjectRandom-v2 success 임시 출력](2026-10-25_object_random_v2_success_debug.md): 현재/필요 거리·속도, 유효성·실패·연속 유지 시간·판정 출력과 CPU 검증.

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
