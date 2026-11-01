# 2026-10-31 Final v0_2_2: 물체 역할 공유와 재질 재사용

[구현 계약](../environments/FINAL_GOAL_ACCURACY_V0_2_2_ENVIRONMENT.md)

## 근거와 범위

사용자는 v0_2_1을 보존한 새 `FinalGoalAccuracyV0_2_2EnvCfg`를 요청했다. 목적은 벡터 환경에서 메모리와 씬 생성 비용을 함께 줄이는 것이며, 구체적 구현 방식은 재량을 허용했다. 이를 위해 12개 물리 물체의 역할 재할당, prototype cache, 복제 전 전역 재질 공유를 선택했다. 단일 env의 보유 형상이 고정되는 차이를 사용자에게 작업 중 설명하고 문서에 명시했다.

기준 코드 HEAD는 `b0116a7b3d384dd58e4a3f5909a5ecfa9b90d4e6`, 문서 HEAD는 `50f075a12b06a572980cbd8d4c7bb864279d2f5e`다. 시작 시 root의 기존 IsaacLab 미추적 변경만 있었고 보존했다. 학습·커밋·로그 정리는 수행하지 않았다.

## 전후와 최종 차이

부모의 타겟 16 + 장애물 20 = 36물체에서 원통·직육면체 + 기타 10 = 12물체로 변경했다. 논리 물체는 21→10, 활성 상한은 동일하게 타겟 1 + 장애물 9다. 장애물 관측 슬롯 20개·80D는 유지한다. 타겟 그룹 확률은 1/3씩이며 기타 물체는 초기 보유 목록 내에서 재선택한다. 장애물은 기타 물체만 사용하므로 부모 후보군을 보존한다. 종류의 환경별 지원 범위와 reset 간 상관은 부모와 다르다.

기존 메서드를 수정하지 않고 역할별 기존 파일에 v0_2_2 Scene/EnvCfg/Event/runtime/PPO/등록을 추가했다. 새 helper는 `assets/final_compact_spawners.py`, `mdp/common/final_compact_pool.py`다. 동일 geometry를 슬롯마다 다시 authoring하지 않도록 prototype을 재사용하며 물리 재질은 전체 속성 signature가 같을 때 공유한다. 비활성화 대신 로컬 material의 물리 API를 제거하여 visual shader를 보존한다.

물체 역할 전환은 device tensor mapping으로 수행한다. pose 쓰기는 전체 물리 buffer scatter 한 번으로 처리한다. 관성·질량 기본값, 마찰 buffer의 restitution 등 형상 관련 값도 재매핑한다. 센서 bank는 같은 mapping을 사용하고 한 번 모은 force matrix를 재사용한다. 부모의 보상·종료·action·PPO 값·OBB 배치·수량 일정은 변경하지 않았다. PPO experiment 이름만 새 버전으로 분리했다.

## 개발·검증 경과

CPU fake physical buffer와 실제 코드로 타겟 그룹 분포, 역할 중복 금지, 부분 쓰기, 질량 mapping, 센서 mapping/cache를 검증했다. 전체 회귀는 **109 passed in 33.00s**였다. `outputs/check_compact_parent.py`로 기존 production 정의 42개의 AST가 HEAD와 같음을 확인했다. 첫 stdin 파이프 방식은 conda가 stdin을 전달하지 않아 검사하지 못했으므로 별도 파일 실행으로 다시 확인했다.

원래 선반 자산 `omniverse://192.168.0.13/.../speedrack_shape.usd`가 응답하지 않아 본 작업이 시작한 probe만 중단했다. 다른 학습 프로세스는 건드리지 않았다. 이후 동일 작업판 크기·높이의 로컬 선반 USD로 검증했으며 production 자산 경로는 변경하지 않았다. 이 대체는 원래 선반의 세부 충돌 형상까지 검증했다는 뜻이 아니다.

첫 GPU 시도에서 cylinder prototype에 contact reporter가 활성화되지 않은 문제를 발견했다. 원인은 custom spawner가 기존 MultiAsset wrapper의 `activate_contact_sensors` 전달을 재현하지 않은 것이었다. prototype 생성 시 이를 명시하여 수정했다. 재실행에서 정상 환경 생성 및 reset/step을 통과했다.

4 env와 64 env 각각 30회 full/partial reset을 수행했다. reset pose를 독립 NumPy polygon 검사로 검증했으며, 미reset env 상태 보존·센서 역할 매핑·관측 57/80/3·finite reward를 확인했다. 64 env에서는 PhysX material/mass buffer를 직접 읽어 역할 변경 후 episode 값과 대조했다. 64 env 전체에서 타겟 종류 0–15가 모두 관찰됐다. 초기 USD 물리 재질은 4 env와 64 env 모두 5개였고 reset으로 USD 재질이 추가되지 않았다. 실제 PhysX 내부 material handle 수와 USD material prim 수는 구분한다.

재현 명령은 workspace 루트, conda `env_isaaclab`에서 실행한다.

```powershell
conda run --no-capture-output -n env_isaaclab python -m pytest src/inspire_sweep_baseline/tests/test_final_compact_pool.py src/inspire_sweep_baseline/tests/test_final_obb_layout.py src/inspire_sweep_baseline/tests/test_bbox_scene_layout.py src/inspire_sweep_baseline/tests/test_final_accuracy_v0_2_1.py src/inspire_sweep_baseline/tests/test_final_accuracy_v0_1.py src/inspire_sweep_baseline/tests/test_final_versions.py -q --basetemp outputs/pytest_compact_final
conda run --no-capture-output -n env_isaaclab python -u src/inspire_sweep_baseline/tests/_final_compact_probe.py --headless --device cuda:0 --version v0_2_2 --num_envs 64 --local-shelf --output outputs/compact_fixture_64_final
conda run --no-capture-output -n env_isaaclab python -u src/inspire_sweep_baseline/tests/_final_compact_probe.py --headless --device cuda:0 --version v0_2_1 --num_envs 64 --local-shelf --output outputs/parent_fixture_64_final
```

원래 선반 검증에는 `--local-shelf`를 빼고 자산 서버 접근을 확보한다. 테스트/대체 선반 파일과 JSON은 `outputs`에만 저장했다. 원본 선반 실패 로그는 `outputs/compact_4.log`, 통과 결과는 `compact_fixture_4`, `compact_fixture_64` 및 최종 비교 디렉토리에 보존한다.

## 최종 비교 측정

같은 probe·로컬 선반·64 env·CUDA 조건에서 부모 실행 종료 후 자식 실행을 순차 수행했다. 이 비교 중 별도 회귀 테스트는 병행하지 않았다. 초기화는 AppLauncher 이후 env 생성과 최초 reset까지, reset은 30회 full/partial 교대 중 각 15회의 평균, step은 별도 20회의 평균이다. GPU 시간을 포함하도록 측정 경계에서 동기화했다. 각 버전 1회 실행의 비교이며 OS의 다른 부하까지 통제한 통계적 벤치마크는 아니다.

| 측정 | v0_2_1 | v0_2_2 | 감소 |
| --- | --- | --- | --- |
| 물리 물체/env | 36 | 12 | 66.7% |
| 초기화 | 20.925s | 10.373s | 50.4% |
| 전체 reset 평균 | 280.42ms | 241.33ms | 13.9% |
| 부분 reset 평균 | 277.93ms | 238.29ms | 14.3% |
| step 평균 | 136.35ms | 118.15ms | 13.3% |
| PyTorch peak allocated | 29.98MiB | 19.42MiB | 35.2% |
| 초기 USD 물리 material prim | 2434 | 5 | — |

PyTorch 메모리는 PhysX·RTX 등을 포함한 총 GPU 메모리가 아니다. USD material prim 수도 PhysX 내부 material handle 수와 동일하다고 해석하지 않는다. 실제 학습 collection·PPO 시간 개선율은 측정하지 않았다. 원본 JSON은 `outputs/parent_fixture_64_final/result.json`, `outputs/compact_fixture_64_final/result.json`에 있다. 두 실행 모두 `status: passed`, 전체 타겟 종류 0–15 관찰, 기존 설정 보존 및 PPO experiment 이름 외 값 동일 검사를 통과했다.

문서 최종 대조: 변경 Markdown 5개의 수식/코드 fence 검사는 통과했다. 링크 168개 중 기존 README의 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 경로 1개를 발견했고, 기준 HEAD에도 같은 링크가 있음을 확인했다. 이번 추가 링크의 오류는 없으며 기존 누락 문서는 범위 밖으로 보존했다. workspace와 문서 저장소의 `git diff --check`는 통과했다. Markdown 실제 렌더링은 별도 수행하지 않았다.

## 미검증

원래 선반 자산 실행, 2048/4096 env 총 VRAM 및 실제 64K 한도 재현, 정책 수렴·성공률, 장시간 동역학 안정성은 미검증이다. 실물 손 접촉 양성 동작은 의도적으로 만들지 않았으며 센서 역할 mapping은 CPU 비영 force와 GPU 물리 센서 데이터 대조로 검사했다. 박스의 초기 배치 안전과 동작 중 물리적 무충돌은 구분한다. 단일 환경의 형상 다양성이 줄어든 영향은 학습 실험으로 평가해야 한다.
