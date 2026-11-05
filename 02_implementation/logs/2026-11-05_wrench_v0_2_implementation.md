# 2026-11-05 Wrench-v0_2 구현·검증

## 요청과 기준

사용자는 Wrench-v0을 직접 상속한 feasibility v0_2 추가를 요청했다. 거리×cosine(접촉 gate 없음), sparse obstacle curriculum·±1 랜덤화, 2-of-3 접촉 누적·5회 불인정 초기화·목표3cm 미만 접촉 인정을 구현했다. 후속 요청으로 거리3cm 미만 cosine=1도 추가했다. [최종 환경 계약](../environments/WRENCH_V0_2_ENVIRONMENT.md).

작업 시작 workspace HEAD는 `c313625fedd3e82263f60e95e5812a4fc026100f`, 문서 submodule HEAD는 `880d11912061dfa9f9b51a9cb58f7b828534e85c`다. 시작 시 `docs/plan/PLAN11.md`, 패키지 README·wrench_envs.py·test_wrench_v0_1.py·test_wrench_v1.py 및 문서 인계·환경 안내·v0_1 계약/로그·통합 계약에 기존 사용자 변경이 있었다. 모두 보존했으며 commit/submodule pointer를 변경하지 않았다. `logs/rsl_rl`은 접근·수정하지 않았다.

## 변경 전후와 의도

| 영역 | v0 | v0_2 | 근거 |
| --- | --- | --- | --- |
| EnvCfg | 독립 기반 | v0 직접 상속 | 부모 구성 보존 |
| 거리 함수 | 높이 제한 지수 근접도 | 기존 식×signed cosine,3cm 미만1 | 직선 밀기 유도·후속 요청 |
| 접촉 함수 | 실제 접촉 step당1 | 최근3개 중2개, 인정 카운트 누적 | 유지에 비례한 보상 |
| 접촉 중단 | 상태 없음 | 불인정5회째 count0, 불인정 step 지급0 | 짧은 접촉 후 이탈 억제 |
| 목표 내부 | 접촉 필요 |3cm 미만 즉시 인정 | 목표 진입 유도 |
| 장애물 |3/3에서10k/12k 교대 증가 |−1/−1,2k White부터3k마다 교대 | 초기 단독 밀기 |
| 개수 랜덤화 | 고정 요청 | reset별 독립 정수±1 후 clamp | 근접 난이도 경험 |
| 배치 bank |9조합 |75조합 | 보존한 방향 일정과 모든 랜덤화 개수 지원 |
| PPO |v0 실험명 |v0_2 실험명 | 학습 식별 |

거리·접촉 weight는3.7/1.45 그대로다. 기존 EEF 높이 조건도 유지한다. 목표 내부 접촉 예외는 요청의 “항상”에 따라 즉시 인정하며 기존 높이 조건도 우회한다. 초기 카운트0, 불인정1–4회 카운트 보존·보상0,5회째 초기화로 의미를 명시했다. White 먼저라는 선택은 부모의 순서를 따랐다. 상한 기준 도달은32000 iteration이며 최종 단계에도±1 랜덤화를 계속한다.

힘 조건을 센서 구성부터 재확인했다. `assets/scenes/wrench.py`의 물체별 센서는 손 body만 필터링한다. `target_hand_contact_force_w`는 현재 target ID의 normal force vector 합을 취하며 부모 `target_contact_below_height`가 norm≥0.01N을 판정한다. force finite·sensor freshness·EEF120mm 미만 조건도 있다. 접선 마찰은 포함되지 않고 반대 벡터는 상쇄된다.

## 최종 전체 대조

실제 configclass/Manager term과 EnvCfg post-init을 CPU harness에서 실행했다(시뮬레이터 자산은 대역). 두 reward callable, obstacle curriculum, reset callable·초기 기준 개수, startup stage 인자를 부모 값으로 돌린 뒤 전체 ordered config가 일치함을 검사했다. 따라서 Scene·Command·Observation·Action·Termination·다른13개 Reward·target speed/방향 Curriculum·수치·term 순서는 유지된다. Runtime은 같은 WrenchEnv 등록이며 PPO는 실험명만 다르다. 새 환경은 v0_1/v1/v2를 상속하지 않는다.

작업 시작 파일 snapshot과 AST를 대조하여 기존 production class/function40개가 그대로임을 확인했다. 부모와 기존 파생의 구성·수치·동작을 수정하지 않았다. 기존 테스트의 파생 클래스 허용 목록·EnvCfg namespace만 새 버전에 맞게 확장했고, 이미 있던 사용자 테스트 수정도 유지했다. 새 상태 테스트는 `tests/test_wrench_v0_2.py`에 있다. GPU probe에 v0_2 선택·설정 비교·일정 순회·초기0장애물 검사를 추가했다.

## 실행 검증

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q \
  src/inspire_sweep_baseline/tests/test_wrench_v0_2.py \
  src/inspire_sweep_baseline/tests/test_wrench.py \
  src/inspire_sweep_baseline/tests/test_wrench_v0_1.py \
  src/inspire_sweep_baseline/tests/test_wrench_v1.py
```

**87 passed in11.04s.** 첫 실행은 자동 로드된 ROS pytest plugin의 `lark` 미설치 때문에 collection 전에 실패했다. plugin autoload를 끈 위 명령으로 해결했으며 의존성은 설치·수정하지 않았다.

- 거리 cosine·3cm 바로 아래/동일/위·목표점·접촉 불필요·높이 제한.
- 접촉0.01N 경계·nonfinite/stale·상쇄 합력·목표 내부 높이/freshness 예외.
- 1/0/1 표본의 인정, 불인정4회 보존/5회 초기화, 재접촉·동일 step 중복·부분/전체reset·평가 step 누락.
- 0–90000 모든 iteration의 랜덤화±1 조합이 bank에 존재함을 검사, 일정 경계·되감기.
- reset별 독립 개수 표본, 초기0/0·상한·seed 재현·부분env IDs·빈reset.
- 75개 실제 OBB bank를2환경×1후보로 생성·샘플링하고 활성 개수·실제 개수·단독 타겟 상태 확인.
- v0/v0_1/v1/v2 회귀, v0_2 등록·전체 설정·부모 보존·PPO 비교.

RewardManager 실제 코드가 `func * weight * dt`를 적용함도 확인했다. term은 인정 카운트만 반환하므로dt를 이중 적용하지 않는다.

## 미검증과 후속 확인

`nvidia-smi`는 NVIDIA driver와 통신할 수 없다는 오류(exit9)다. 실제 Isaac Sim import/초기화·GPU contact fixture·reset/rollout·PPO 학습은 실행하지 않았다. CPU harness 결과를 물리·성능 검증으로 해석하지 않는다. GPU 호스트에서 환경 계약의 probe를 먼저 실행하고, 학습은 반드시 `scripts/train.py`를 사용한다.

75조합 startup bank는 부모9조합보다 약8.3배 많은 후보를 보유한다.2048환경의 초기화 시간·메모리와 grouped reset 속도는 미검증이다. 누적 접촉 보상은 요청대로 cap을 두지 않았다. 장기 접촉 경향·목표 도달·성공률 개선·거리 보상과의 상대 크기는 학습으로 검증해야 한다.

## 최종 정적 검사

변경 Python compileall 통과, 수정 Markdown5개 수식 검사 통과. 신규 계약·로그와 인계·환경 안내의 링크 검사는 통과했다. 패키지 README까지 포함한227개 링크 검사에서는 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1개가 발견됐다. 이번 신규 링크는 정상이며 과거 문서 링크는 수정하지 않았다. 패키지 범위·문서 submodule `git diff --check`는 통과했다. workspace 전체 검사에는 기존 사용자 문서 `docs/plan/PLAN11.md`의 trailing whitespace/EOF 경고가 남으며 사용자 원문을 보존했다. Markdown 렌더링은 별도 실행하지 않았다.
