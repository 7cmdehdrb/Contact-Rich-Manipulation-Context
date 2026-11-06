# Relative-v2: Actor 현재 타겟 / Critic 초기 타겟

2026-11-06. [환경 계약](../environments/WRENCH_REFACTOR_RELATIVE_V2_ENVIRONMENT.md).

## 요청과 변경

Relative-v0를 직접 상속하고 Actor의 초기 물체 XYZ만 현재 물체 XYZ로 변경하라는 요청이다. EEF 기준은 유지하며 Critic은 v0 초기 위치를 유지한다. 사용자가 테스트 학습을 실행 중이므로 Sim·Lab 실행을 요구하는 검증은 생략했다.

기준 HEAD는 `093627fdf232360eeac4bf540be833888b1b89a4`다. 작업 시작 시 이전 Relative-v1 추가 변경 및 문서 submodule의 사용자 상태가 있었다. 해당 변경·커밋·포인터·학습 로그를 보존했다.

`CurrentObjectPositionInEEF`는 기존 초기 관측 함수에서 받은 noisy XYZ에 EEF 기준 초기→현재 변위를 더한다. 따라서 초기 위치만 현재 위치로 바뀌고 reset-fixed base bias 규칙은 유지된다. V2 observations는 policy의 해당 callable만 교체하고, v0 PolicyCfg 그대로 critic 그룹을 추가한다. 그룹별 corruption 설정은 동일하되 각 그룹의 노이즈 표본은 독립이다.

새 EnvCfg는 v0 직접 상속이며 observations만 재정의한다. 새 model은 Relative model을 상속하여 critic의 직접 입력 키만 분리한다. PPO도 v0를 상속하며 새 model class, critic 관측 키, experiment_name만 변경한다. Gym 등록 ID는 `Inspire-Wrench-Refactor-Relative-v2`다.

## 전체 대조와 영향

| 범위 | 변경 내용 |
| --- | --- |
| Actor 타겟 `[21:24]` | 초기→현재 XYZ, EEF 유지 |
| Critic | v0 PolicyCfg 기반 별도 58D 그룹, 초기 타겟 유지 |
| Rollout Storage | policy58 / critic58 / 공유 obstacles64 |
| 장애물·encoder | v0 EEF snapshot·mask·가시성·확률·64→32→16 유지 |
| Scene / Event / Command / Action / Reward / Termination / Curriculum / runtime | 변경 없음 |
| PPO 수치 / 네트워크 크기 / export | 변경 없음, Actor export122D 유지 |
| 등록 / 실험명 | v2로 구분 |

전체 EnvCfg를 CPU 대역 환경에서 생성해 observations 외 모든 항목이 부모와 같은지 비교했다. observations도 policy target callable과 critic 그룹 추가 외에는 부모와 일치한다. PPO 전체 dictionary 역시 위 연결 항목·실험명 외 동일하다. 부모 인스턴스가 자식 생성으로 변하지 않는지도 확인했다. AST 대조로 HEAD에 있던 환경·관측·관측 함수·모델·PPO의 모든 기존 함수/클래스 정의가 불변임을 확인했다. 스폰/초기화/제어/보상/종료/커리큘럼 코드를 수정하지 않았다.

## 검증 및 미검증

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench_refactor_relative.py
```

최종 CPU 검사 **70개 통과**. 새 검사는 타겟 ID 선택, 물체 이동, EEF 이동·회전, 고정 bias, 부분 reset, corruption 비활성화, Actor/Critic 입력 격리, encoder gradient, 저장소 차원, TorchScript Actor export, 전체 EnvCfg·PPO 대조를 포함한다. 실제 Sim 객체 대신 기존 CPU harness의 leaf 대역을 사용했으며 AppLauncher나 SimulationApp을 실행하지 않았다.

정적 등록 확인 스크립트의 첫 시도는 최상위 literal ID 호출만 검색하여 조건문 안의 상수 ID 등록을 놓쳤다. 조건문·상수 참조를 확인하여 정적 등록 검사를 수정했다. production 등록 자체의 오류는 없었다.

변경 Markdown 수식 검사와 양쪽 저장소 `git diff --check`가 통과했다. 문서 저장소의 변경 4개 문서 링크 검사도 오류 0개다. 패키지 README 전체 링크 검사는 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크 1개를 보고했다. HEAD에도 같은 링크가 있음을 확인했고 요청 범위 밖이므로 수정하지 않았다. 새 v2 링크는 정상이다. Markdown 렌더링은 확인하지 않았다. Sim·Lab 초기화, 실제 환경 rollout, GPU, 학습, 성능 수렴, 실제 물체 스폰 결과는 이번 v2에서 검증하지 않았다. 이전 v0/v1 실행 결과를 v2 검증 결과로 간주하지 않는다. 실행 중 프로세스와 `logs/rsl_rl`은 건드리지 않았다.
