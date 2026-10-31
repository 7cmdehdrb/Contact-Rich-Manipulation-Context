# 2026-10-31 Final GoalAccuracy v0_2_1 구현·검증

[구현 계약](../environments/FINAL_GOAL_ACCURACY_V0_2_1_ENVIRONMENT.md) · [승인 명세](../../01_plan/environments/2026-10-31_FINAL_GOAL_ACCURACY_V0_2_1_SPEC.md)

## 근거와 범위

사용자가 작성된 명세 기반 실제 구현을 승인했다. 실행 시 Windows 11의 conda `env_isaaclab`을 사용하라는 지시를 적용했다. 시작 코드 HEAD는 `eaf1e5dc2fb0a8d3e75374110c65d93e65c7c71a`, 문서 HEAD는 `397fe5480dd0fdb31e5cc68cfe3991bab20e98e5`다. 기존 IsaacLab 작업트리, `.playwright-cli`, 앞서 작성한 명세와 인계 변경을 보존했다. 커밋·학습·학습 로그 정리는 수행하지 않았다.

## 변경 전후와 구현 위치

기존 v0_2를 직접 상속하여 실제 타겟 접촉만 보상하도록 변경했다. weight 1.45와 임계값 0.01N을 보존하고 목표 점유 대체 조건을 제거했다. timeout 보너스는 +30에서 +75로 변경하며 승인 명세대로 2cm 경계를 포함한다. `success_event`와 기존 성공 종료 term을 연결하여 dt와 무관한 일회성 보너스를 구현했다.

패키지의 기존 역할 디렉토리를 유지했다. `mdp/reward_functions/final.py`, `mdp/rewards/final.py`에는 전용 함수·설정, `assets/scenes/final.py`에는 고정 타겟 풀, `mdp/event_functions/final.py`, `mdp/events/final.py`에는 타겟 재선택 이벤트를 추가했다. `mdp/common/final_target_pool.py`는 논리 타겟/물성/센서 매핑을 담당한다. `runtime/final.py`에서 manager 초기화 전에 이 매핑을 설치한다. `envs/final_envs.py`, `agent/final_ppo_cfg.py`, 패키지 `__init__.py`에 자식 설정과 등록을 추가했다. 기존 부모 함수 구현은 수정하지 않았다.

16개 후보의 물리 상태를 유지하고 매 reset 하나를 선택한다. 기본 질량·관성과 geometry bounds도 선택된 후보로 전환한다. 장애물 20슬롯과 논리 21물체, 관측 차원, PPO 구조와 값은 보존한다. 물리 물체 수는 21에서 36으로 증가한다. cylinder/cube/other 각 1/3 분포와 기타 14개 균등 선택을 유지하며 반복 추첨은 허용한다.

## 구현 중 검증으로 조정한 사항

- Procedural spawner에 regex 경로를 직접 넘길 수 없어 각 단일 후보를 `MultiAssetSpawnerCfg`로 감쌌다.
- EventManager의 인수 검사에 맞춰 이벤트 함수에 부모와 동일한 명시적 signature를 사용했다.
- Windows NumPy 정수 폭 차이로 선택 결과의 tensor dtype을 명시적으로 `torch.long`으로 변환했다.
- GPU 후보 전환 probe의 actor disable 방식에서 위치 불일치, live collider 변경 방식에서 CUDA 700 오류가 관찰됐다. 초기 probe의 환경 간 배치 겹침도 수정했다. 각 실패의 원인을 완전히 분리한 진단은 아니므로 모든 GPU backend에서 해당 API가 불가능하다고 일반화하지 않는다.
- 채택한 방식은 안정된 actor 인덱스 + 원격 배치 + 속도 초기화 + 중력 비활성화 + 논리 제외다. 수정된 probe에서 12회 전환이 통과했다. collider flag를 끄지는 않으며 이 차이를 구현 계약에 명시했다.
- Windows 기본 pytest 임시 디렉토리 권한 문제는 task 전용 `outputs` basetemp로 해결했다.

## 최종 대조 및 검증

| 대상 | 결과 |
| --- | --- |
| CPU 회귀 | 78 passed: 새 보상·경계·dt·추첨 분포·seed·부분 매핑 및 기존 버전 테스트 |
| 실제 Isaac Lab 설정 | 직접 부모, 보상 2개만 변경, 이벤트 함수만 변경, 부모들 생성 전후 격리, PPO 이름만 변경 확인 |
| CUDA smoke | 2 env, 40회 부분 reset, 0/4000/4500/5000 iteration 순환, 3 step/reset, 보상 finite 확인 |
| 후보 전체 | 16종 각각 강제 선택 후 reset·step 통과, 선택 pose 매핑 일치 |
| 비선택 후보 | 원격 위치 유지, 16종 전체 검사에서 비선택 후보–손 force matrix가 모두 0 |
| 관측 | policy 57 / obstacles 80 / privileged 3 유지 |

부분 reset 측정 평균은 약 0.03688초다. CUDA 동기화 및 부모와의 동일 조건 비교를 포함한 성능 벤치마크가 아니므로 collection 시간 추정에 사용하지 않는다.

재현 명령은 workspace 루트에서 실행한다.

```powershell
conda run --no-capture-output -n env_isaaclab python -m pytest src/inspire_sweep_baseline/tests/test_final_accuracy_v0_2_1.py src/inspire_sweep_baseline/tests/test_final_accuracy_v0_1.py src/inspire_sweep_baseline/tests/test_final_versions.py --basetemp outputs/pytest_v0_2_1_review -q
conda run --no-capture-output -n env_isaaclab python -u src/inspire_sweep_baseline/tests/_final_accuracy_v0_2_1_probe.py --headless --device cuda:0 --smoke
```

증거는 workspace `outputs/final_accuracy_v0_2_1_cpu.log`, `outputs/final_accuracy_v0_2_1_probe.log`, `outputs/final_accuracy_v0_2_1_validation/config.json`, `smoke.json`에 남겼다. 별도 backend probe와 로그는 `tests/_target_pool_backend_probe.py`, `outputs/target_pool_backend_probe.log`, `outputs/target_pool_collision_probe.log`다. 출력물은 로컬 검증 산출물이며 커밋하지 않았다.

미검증 범위: 학습 수렴·성공률·실제 정책의 선반 마찰 행동, 대규모 env collection 시간 및 GPU 메모리, 장시간 물리 안정성, 실접촉을 의도적으로 발생시킨 센서 양성 통합 테스트. 접촉 조건의 양성/음성 사례는 CPU 테스트로 확인했다. 문서 렌더링은 확인하지 않았다.

문서 검사: 변경한 문서 저장소 Markdown 5개의 수식·링크 검사 통과(링크 오류 0), 패키지 README 수식 검사 통과, 양쪽 저장소 `git diff --check` 통과. README 전체 링크 검사에서는 기존 v0_2 환경 문서 링크의 대상 파일 부재 1건이 발견됐다. 새 v0_2_1 링크는 유효하며 기존 누락 문서의 신규 작성은 이번 구현 범위에 포함하지 않았다. 최종 CPU 재검사는 78 passed in 15.10s다.
