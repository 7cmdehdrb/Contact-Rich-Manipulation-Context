# 2026-10-31 최종 환경 State and Privileged Information 문서 작성

## 요청과 의도

사용자가 최종 환경의 State Space, Observation Space, 환경 상태, Actor 관측, Critic 관측의 설명을 요청했다. 현재 인계와 실제 코드의 최신 `Isaac-Inspire-Final-GoalAccuracy-v0_2_2`를 기준으로 [상태·관측 문서](../../04_article/environment_reference/FINAL_STATE_AND_PRIVILEGED_INFORMATION.md)를 작성하고 [활성 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)에 연결했다.

학습 네트워크 문서와 장면 생성 문서에 분산된 관측 설명을 바탕으로, 이번 문서는 전체 환경 상태와 제한된 관측의 차이, 좌표계·차원·시간 특성·노이즈·정보 접근 범위를 중심으로 작성했다. 네트워크 손실과 배치 기하의 상세는 기존 문서를 연결했다.

## 변경 전후와 영향

| 변경 전 | 변경 후 | 영향 |
| --- | --- | --- |
| 상태·관측을 종합해 설명하는 전용 문서 없음 | State와 Observation, Actor와 Critic의 차이를 정리한 문서 추가 | Critic 140D를 전체 상태 차원으로 오해하는 문제 방지 |
| 관측 목록의 세부 의미는 함수별 확인 필요 | policy의 정확한 slice, 초기 캐시·현재 감각·privileged 구분, 정보 접근 표 | 재현·논문 기술에 필요한 의미와 제한을 확인 가능 |
| 활성 환경 안내에 상태·관측 링크 없음 | 기존 두 문서 링크를 보존하고 새 안내 추가 | 최신 환경 설명으로 접근 가능 |

production 코드·설정·자산·테스트는 수정하지 않았다. root 및 독립 문서 submodule의 기존 미커밋 작업과 HEAD를 보존했다. 학습 로그는 읽거나 정리하지 않았다.

## 확인 근거와 주요 결론

작업트리 기준 root HEAD `b0116a7b3d384dd58e4a3f5909a5ecfa9b90d4e6`, 문서 HEAD `50f075a12b06a572980cbd8d4c7bb864279d2f5e`. 미커밋 compact 환경 구현을 포함한다.

Final EnvCfg의 상속과 등록, FinalV1ObservationsCfg, 실제 observation 함수, compact reset과 가시성·packing, FinalV1Model 및 상속 인코더, PPO obs_groups, runtime reset, 보상·종료 구성, Isaac Lab ManagerBasedRLEnv와 RSL-RL wrapper를 확인했다. 현재 직접 의존하는 코드만 참조했으며 과거 환경 역사 문서는 조사하지 않았다.

- 환경 내부 상태는 물리 상태·과업·물성·이력에 분산되어 있으며 별도의 고정 차원 전체 state vector가 아니다.
- policy 57D, obstacles 80D, privileged 3D. Actor 원시 137D, Critic 원시 140D. 압축 후 본체 입력은 73D/76D.
- 현재 타겟 위치만 Critic 전용이다. 같은 파일에 있는 13D pose·속도 helper는 현재 privileged term으로 선택되지 않는다.
- 초기 타겟과 장애물은 reset snapshot이며 관측 오차도 고정된다. goal 극좌표는 실제 초기 타겟 기준으로 고정되어 현재 타겟 위치를 누출하지 않는다.
- 장애물 present는 물리 활성 mask가 아니라 초기 가시성·오류 처리를 거쳐 보고된 슬롯이다. 정렬·교환 후 슬롯 번호는 물리 ID가 아니다.
- 실제 물리 객체 12개, 논리 역할 10개, 관측 슬롯 20개를 구별했다.
- 촉각 17D·F/T 6D는 새 관측 노이즈가 적용된다. Critic도 동일 noisy 그룹을 받는다.
- 손 12관절 상태 전체 대신 측정 손 개방도 2D를 받으며, 이전 행동은 raw action의 tanh다.
- reward·done·extras와 내부 보상 계산용 상태는 자동으로 Actor/Critic 입력이 되지 않는다.
- Actor와 Critic 모두 완전한 Markov state를 직접 받는다고 보장할 수 없으며, 자동 reset된 행의 반환 관측은 새 에피소드에 해당한다.

## 실행 검증

### 기존 관련 테스트

workspace root에서 다음을 실행했다. 기본 pytest 임시 경로의 이전 접근 문제를 피하기 위해 고유한 workspace 임시 경로를 사용했고, 기존 파일을 삭제하지 않았다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$stateDocTemp = Join-Path (Get-Location).Path ('outputs/final_state_doc_pytest_' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $stateDocTemp) { throw 'Temporary path already exists' }
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe -m pytest src/inspire_sweep_baseline/tests/test_initial_privileged.py src/inspire_sweep_baseline/tests/test_clutter_fusion_observations.py src/inspire_sweep_baseline/tests/test_final_versions.py -q -k 'actor_initial_position_stays_fixed or partial_reset_captures_new_command or initial_measurement_noise_is_fixed or clockwise_cardinal or root_rotation_and_translation or live_target_cannot_leak or goal_angle_range or action_feedback_bounds_large or action_feedback_override_is_scoped or tactile_observation_noise or wrist_wrench_observation_noise or hand_configuration_inverts or final_ppo_consumes' --basetemp $stateDocTemp
```

결과: **15 passed, 39 deselected in 4.56s**, exit 0. 초기 위치 고정·부분 reset·고정 bias, 목표의 좌표 변환과 live-target 정보 비유입, tanh 피드백, 촉각 양방향 반전, wrench 축별 표준편차, 실제 손 관절 투영을 검증했다. 실제 RSL-RL 모델 테스트는 73D/76D latent, PPO update, checkpoint 복원과 137D 입력 Actor export를 확인한다. 최신 v0_2_2가 이 구성과 모델을 상속하는 경로는 코드로 확인했으며, 이 테스트가 v0_2_2 물리 환경을 직접 실행한 것으로 보고하지 않는다.

### 문서 검사

문서 저장소에서 아래 명령으로 변경 파일의 수식·링크와 전체 문서 링크, diff 공백을 검사했다.

```powershell
python 00_guidelines/scripts/check_markdown_math.py 02_implementation/environments/FINAL_STATE_AND_PRIVILEGED_INFORMATION.md 02_implementation/logs/2026-10-31_final_state_privileged_document.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md
python 00_guidelines/scripts/check_document_links.py
python 00_guidelines/scripts/check_document_links.py --check-external 02_implementation/environments/FINAL_STATE_AND_PRIVILEGED_INFORMATION.md 02_implementation/logs/2026-10-31_final_state_privileged_document.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md
git diff --check
```

결과: 변경 Markdown 3개 수식 검사 통과, 전체 Markdown 422개 및 dataset 링크 검사 오류 0, 변경 문서의 workspace 소스 링크 29개를 포함한 검사 오류 0, diff 공백 검사 통과. Git의 기존 파일 LF→CRLF 안내는 있었지만 공백 오류는 없었다. 최종 작업트리의 production 변경 목록은 작업 시작 시와 동일하며, 이 작업에서는 새 설명·로그 파일과 색인 문단만 추가했다. 실제 UI의 Markdown/Mermaid 렌더링 검증은 수행하지 않았다.

## 최종 요청 대조와 미검증 범위

State Space는 내부 물리·과업·domain·이력의 분류와 전체 flatten vector 부재로 설명했다. Observation Space는 Gym Dict/Box와 batch shape, Actor/Critic의 실제 그룹 선택을 설명했다. policy 57개 성분과 obstacles 80개 성분의 의미·좌표계·시점·오류 모델, Critic 전용 3개 성분, 명시적으로 주지 않는 정보, 부분 관측의 강화학습적 의미까지 포함했다.

미검증: 이번 작업에서의 Isaac Sim 물리 실행, 신규 GPU rollout·학습·실제 로봇 성능, Markdown/Mermaid 실제 UI 렌더링. 단위·모델 테스트와 정적 소스 확인을 물리 성능 검증으로 확대 해석하지 않는다.
