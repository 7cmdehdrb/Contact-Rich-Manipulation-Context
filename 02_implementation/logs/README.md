# Holding · Final 개발 로그

현재 계열과 공통 작업 기록을 안내한다. 이전 환경의 로그 색인은 [정리 전 백업](../history/2026-10-27_agent_context/README.md)에 보존했다. 개별 과거 로그는 변경하지 않는다.

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
