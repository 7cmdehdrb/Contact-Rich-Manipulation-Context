# GoalAccuracy v0_3 명세·구현 기록

[개발 명세](../../01_plan/environments/2026-10-30_FINAL_GOAL_ACCURACY_V0_3_SPEC.md)

## 요청·기준·범위

2026-10-30 사용자는 접촉 보상 축소, 거리 감소형 복원, timeout +100, 목표 반경 3cm의 v0_3을 요청했으며 개발 전에 명세만 작성하도록 지정했다. 접촉 보상의 목표 점유 분기 확인 후 사용자는 OR 조건을 유지하고 weight만 1/4로 줄이도록 확정했다.

코드 기준은 workspace `main`, HEAD `5404f2a8143baccaaa9528a6588abc28164f04bf`다. 문서 submodule HEAD는 `3c27e0751f0911745bc5a390f3a15f7e0d4cb341`이며 시작 시 내부 작업트리는 clean이었다. 상위 workspace의 문서 submodule 변경 표시는 기존 상태다. 활성 패키지는 workspace 저장소에 포함된다.

## 변경 전후·의도·영향

- 신규 명세에 v0_2 기준, 사용자 결정, 수식, 상속·보존 범위, 구현 위치와 검증 기준을 기록했다. v0_3은 미구현이다.
- 센서 filter와 target_id 선택을 확인했다. Contact의 실제 접촉 분기는 타겟–손 전용이지만 보상 전체는 목표 점유도 포함한다. 후속 지시에 따라 OR 유지, 1.45→0.3625로 명세했다.
- 거리 보상은 `DexPlanarGoalProgress(position_tolerance=0.0)`로 지정했다. weight 100은 기존 감소형 복원이라는 설계 선택이다.
- 목표 3cm 경계 포함, 거리 보상 tolerance 0, Hold 외곽 6cm를 구분했다. v0_2의 성공/보너스 경계 불일치는 v0_3에서 기존 `success_event` 재사용으로 해소하도록 설계했다.
- 기존 문서 Reaching 20cm와 현재 코드 10cm 불일치를 명시했다. 요청 밖인 Reaching은 현재 부모 10cm를 유지한다.
- v0_2 상세 문서는 현재 checkout에 없으므로 README의 끊어진 링크 대신 실제 등록·EnvCfg·RewardsCfg·테스트를 근거로 삼았다.
- 인계에 명세 링크와 미구현 상태를 추가한다. 활성 환경 목록에는 미구현 환경을 추가하지 않는다.

영향은 계획·인계·개발 로그 문서에 한정한다. 환경·테스트 소스, 학습 로그, checkpoint, submodule HEAD는 보존한다.

## 실제 검증

소스에서 등록·상속·보상 callable/params/weight·접촉 filter·반경 소비·종료·보상 순서·PPO·runtime metric·목표점 표시를 확인했다. 기존 CPU 테스트로 접촉 대상 선택, 무접촉 목표 지급, v0_2 보너스 경계/순서/Wrench 예산, 거리 기록 및 부분 reset을 재확인했다.

workspace 루트 실행:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_final_accuracy_v0_1.py \
  src/inspire_sweep_baseline/tests/test_dex_rewards.py \
  -k 'contact or v0_2 or goal_records or partial_reset'
```

결과: **12 passed, 23 deselected**. 최초 기본 Python은 pytest 미설치로 실패했다. Isaac Lab Python 재시도는 자동 로드된 ROS 플러그인의 `lark` 미설치로 실패했다. 위 명령에서 외부 플러그인 자동 로드를 끄고 완료했다. 의존성 설치나 코드 변경은 하지 않았다.

## 최종 대조·미검증

사용자 요청 4개 및 접촉 조건 후속 답변을 명세 변경 표와 세부 절에 대응시켰다. 감소형 weight 선택, 목표 경계 통일, Hold 외곽 보존, 전체 설정 대조와 부모 회귀 요구를 명시했다.

변경한 명세·로그·인계 3개 파일을 대상으로 `check_markdown_math.py` 통과, `check_document_links.py --check-external` 오류 0(내부 링크 10, 외부 workspace 링크 5)을 확인했다. workspace와 문서 저장소의 `git diff --check`도 통과했다. 최종 status에는 문서 3개만 변경/추가되어 있으며 환경·테스트 소스 변경이 없다. Markdown 렌더링의 육안 확인은 수행하지 않았다.

v0_3 설정 인스턴스 대조, 실제 Isaac Sim reset/step·물리 접촉, 학습·play·성공률 검증은 미실행이다. 개발 전 명세 요청이므로 환경을 생성하거나 학습하지 않았다. CPU 검사 통과는 물리 센서 검증이나 신규 환경의 성공을 의미하지 않는다.

## 2026-10-30 후속: 명세 수락 후 구현

사용자는 명세를 수락하고 구현 및 완료 후 코드 리뷰를 요청했다. 위 단락은 명세 작성 시점의 이력이다. 아래는 구현 후 상태다. 기준 HEAD와 부모는 동일하며, 기존 명세 작업의 문서 변경을 보존했다.

### 실제 변경과 최종 대조

| 대상 | 변경 전 → 변경 후 | 의도·영향 |
| --- | --- | --- |
| Gym·EnvCfg | 미등록 → v0_3, v0_2 직접 상속 | 독립 task 제공, runtime 재사용 |
| `target_contact` | 1.45 → 0.3625 | 기존 접촉 OR 목표 점유를 1/4로 축소 |
| `target_goal_distance` | exp/3.7 → DexPlanarGoalProgress/100, tolerance 0 | 중심까지 최단 거리 갱신량 지급 |
| `target_goal_hold` | 내부 반경 2cm → 3cm | Contact·timeout 성공/미달의 반경도 기존 공통 조회로 반영 |
| `target_goal_timeout_bonus` | strict 거리 검사/+30 → success_event/+100 | 단일 성공 term을 사용하여 3cm 경계 포함 |
| PPO | 부모 설정 → experiment_name만 v0_3 | 학습 로그 구분, 하이퍼파라미터 보존 |

코드는 기존 역할 파일 4개에만 환경 정의를 추가했다. 공유 보상 함수·종료 함수·커리큘럼 함수·runtime은 수정하지 않았다. Scene·Command·Event·Observation·Action·Termination·Curriculum의 모든 중첩 값과 순서를 실제 EnvCfg에서 대조했다. 부모와의 차이는 rewards 네 term뿐이며 PPO는 experiment_name만 달랐다. Hold 외곽 6cm·speed_scale 0.05·weight 8, Reaching 10cm, 기타 계수·일정·로그 키를 보존했다.

기존 보상 post-init을 상속하여 term 순서를 유지한다. timeout 보너스는 Wrench보다 먼저 집계되며 +100에 따른 기존 예산 변화도 검사했다. 기존 v0/v0_1/v0_2/v1 설정 격리와 작업 전 HEAD의 기존 정의 불변성을 확인했다. [실제 설정 대조 산출물](../../03_assets/artifacts/2026-10-30_goal_accuracy_v0_3/config_report.json)에 네 보상의 최종 callable·params·weight를 남겼다.

### 실행한 검증

workspace 루트에서 실행했다.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_final_accuracy_v0_1.py \
  src/inspire_sweep_baseline/tests/test_final_configuration.py \
  src/inspire_sweep_baseline/tests/test_final_versions.py \
  src/inspire_sweep_baseline/tests/test_dex_rewards.py
```

결과: **93 passed**. 최초 실행은 신규 테스트의 mock 위치 Y/Z가 속도 텐서를 잘못 참조하여 속도 변경 시 위치도 바뀌는 문제로 3건 실패했다. mock 좌표와 속도를 분리한 후 위 전 범위가 통과했다. 실제 환경 코드 결함은 아니었다.

접촉 힘 0.01N 바로 아래/위 사례를 추가 보강한 후 다음만 재실행했다.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_final_accuracy_v0_1.py -k contact
```

결과: **6 passed, 24 deselected**. 기존 대상 선택·stale·NaN·상쇄·무접촉 목표 점유와 함께 v0_1/v0_3에서 확인했다. 변경되지 않은 나머지 검사는 중복 실행하지 않았다.

실제 Isaac Sim 등록·전체 설정 검사는 다음과 같다.

```bash
timeout 90s /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/tests/_final_accuracy_v0_3_probe.py \
  --headless --device cpu > /tmp/final_accuracy_v0_3_probe.log 2>&1
```

결과: **exit 0**. 실제 Gym 등록·EnvCfg/PPO 로딩, 전체 설정과 순서 대조, Scene 재구성 용량 (10,10)/(0,0)/(3,4), 기존 환경 4종의 인스턴스 격리 검사 통과. `outputs/final_accuracy_v0_3_validation/config_report.json`을 문서 산출물로 복사했다. GPU 미검출 및 user.config 저장 불가 메시지는 있었지만 설정 검사와 정상 종료는 완료했다.

추가로 Python AST로 변경된 runtime 패키지 파일의 기준 HEAD와 현재 파일을 비교했다. 기존 클래스·함수 정의 **29개** 및 기존 모든 Gym 등록 구문이 동일했다. `nvidia-smi`는 드라이버 통신 실패였다. 따라서 `--smoke`는 실행하지 않았다.

### 독립 코드 리뷰

`code-review` 스킬의 두 검토 축을 별도 리뷰 에이전트로 수행했다. 사용자 요청의 기준은 이번 작업 시작 HEAD `5404f2a8143baccaaa9528a6588abc28164f04bf`이며 커밋을 만들지 않았으므로 다음 작업트리 diff 및 새 probe 파일을 검토했다.

```bash
git diff 5404f2a8143baccaaa9528a6588abc28164f04bf -- src/inspire_sweep_baseline
```

| 검토 축 | 결과 | 검토 근거 |
| --- | --- | --- |
| Standards | 규칙 위반 0, 조치할 코드 냄새 0 | 역할별 파일·부모 상속·공유 함수 보존·변경 범위·검증 코드 |
| Spec | 명세 불일치 0 | 네 보상, dt, 목표 반경 모든 소비자, reset, term 순서/Wrench, 부모·PPO 보존 |

리뷰에서는 실제 물리 검증과 설정 검증을 구분하도록 확인했다. 새 probe의 선택적 smoke도 성공 위치나 접촉 대상을 강제로 만들지 않으므로, 실행만으로 실제 성공 지급·센서 대상 분리를 검증했다고 주장할 수 없다.

최종 문서와 접촉 임계값 테스트 보강 후 두 리뷰 에이전트가 다시 확인했다. Standards는 규칙 위반·조치할 코드 냄새·추가 correctness 지적 모두 0건, Spec은 명세 불일치 0건이다. 검토자는 소스와 결과 기록을 검토했으며 테스트를 독립 재실행한 것은 아니다.

문서 최종 검사: 수정 Markdown 6개(문서 저장소 5개와 패키지 README)의 수식 검사 통과. 문서 저장소 5개 링크 검사 오류 0(내부 41, 외부 5). README 포함 전체 링크 검사에서는 기존 v0_2 환경 문서 누락 1건만 발견했다. 기준 HEAD의 README 마지막 줄에도 같은 링크가 있음을 `git show`로 확인했으며 이번에 추가한 v0_3 링크는 정상이다. 두 저장소의 `git diff --check` 통과. 이전 버전의 미확보 문서를 새 환경 검증 근거로 사용하지 않았다.

### 미검증 범위와 다음 확인

실제 물리 reset/step, 실센서 동적 접촉 대상 분리, 성공 위치에서의 timeout transition 지급, 학습 수렴·성공률은 **미검증**이다. 현재 호스트에서 NVIDIA/CUDA 장치를 사용할 수 없어 물리 검사를 수행하지 않았다. 장기 학습이나 checkpoint 재개도 실행하지 않았다. 기존 학습 로그와 checkpoint는 수정하지 않았다.

GPU 환경에서 선택적 smoke를 실행하고 별도로 목표 위치·실제 접촉 대상을 제어한 물리 사례를 검증할 수 있다. 구현·CPU·실제 설정·소스 리뷰는 완료했으며, 명세의 물리 검증 항목까지 통과한 상태로 표시하지 않는다.
