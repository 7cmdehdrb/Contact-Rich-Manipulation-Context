# Refactor-Relative-v0 구현·대조·검증

2026-11-06. [최종 환경 계약](../environments/WRENCH_REFACTOR_RELATIVE_V0_ENVIRONMENT.md).

## 요청·기준

사용자는 Refactor-v3_1을 계승하는 새 Refactor-Relative-v0를 요청했다. EEF OSC·2-of-3 접촉·cosine 거리·_1 action rate를 유지하고, Actor 관측을 Critic과 storage에도 동일하게 사용하며, 초기 물체 정보의 EEF 좌표변환·촉각17D·URDF actuator 한도·최초 진입 보너스10만 바꾼다. 스폰/리셋·다른 보상·일정의 변경을 금지했다.

기준 workspace HEAD는 `947e58d5ea200d951a1b2b46e1ec0d3ebab830e9`다. 시작 시 README의 수동 조작 설명, manual runtime/script/test, PLAN13, 문서 저장소의 인계·활성 안내·v0 설명·그림·manual/collection 로그 변경이 이미 존재했다. 이를 보존하고 이번 변경과 분리했다. 기존 커밋·서브모듈 포인터를 변경하거나 학습 로그를 정리하지 않았다.

## 의도와 전체 차이 대조

| 항목 | v3_1 → Relative-v0 | 요청 대응 |
| --- | --- | --- |
| 등록 | 새 Gym ID·EnvCfg·PPO 이름 | 새 환경 |
| runtime | 동일 WrenchRefactorEnv | reset/step 수명 보존 |
| Scene | Hand effort0.20→10 외 동일 | 원본 URDF 반영 |
| Command/Event/스폰 | 전체 동일 | 생성 규칙·시점·중력·높이 보존 |
| Action | 전체 동일 | 현재 EEF OSC·Hand2D 보존 |
| Observation | policy58 + obstacles64만 존재 | Actor/Critic 동일 tensor, 초기 데이터 EEF 표현 |
| Reward | 최초 진입 weight15→10 외 동일 | 최종 요청10, 부모 실제15와 요청문25의 차이 명시 |
| Termination | 5개 term 전체 동일 | arm3rad/s·success·timeout 보존 |
| Curriculum | 방향 deadzone 전체 동일 | 대상·일정·값 보존 |
| PPO | 입력 라우팅·model class·experiment_name만 변경 | 공통 관측, 새 입력 차원 |
| 저장·export | 공통58+64=122D | GT critic 저장 제거 |
| 로그 | 기존 환경 metric/reward 키 유지 | 신규 experiment 이름만 추가 |

설정의 깊은 복사와 실제 Isaac config `to_dict()`를 이용해 위 허용 차이 이외가 없음을 검사한다. Observation은 그룹 전체 비교에 더해 개별 term의 func/noise/params만 허용한다. 부모 인스턴스와 신규 부모 인스턴스가 변경 전 dictionary와 같은지도 확인한다. Scene 자산·Event·Command·runtime·reward 함수·curriculum·termination 소스에는 수정이 없다.

원본 URDF ZIP SHA256은 `b7997a6087e8c0cded03aff557e07ca82b8793b2b5b3f95ec3566318a13f5f7f`이며 기존 오른손 asset metadata의 출처와 대조한다. 모든12개 joint의 effort10, velocity1을 XML에서 읽었다. gain 등의 추가 추정은 적용하지 않았다.

타겟 noise를 EEF 변환 후 적용하면 기존 reset 고정 오차가 EEF 회전에 따라 world에서 바뀐다. 따라서 초기 base snapshot에 기존±1cm bias를 적용한 뒤 변환한다. 장애물은 기존 관측 snapshot을 변환만 하며 가시성/노이즈/정렬을 재계산하지 않는다. tactile은 flip 전후 네 상태의 의미를 유지하도록 비트 단위 noise를 재사용한다.

## 검증 실행

CPU 명령:

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q src/inspire_sweep_baseline/tests/test_wrench_refactor.py src/inspire_sweep_baseline/tests/test_wrench_refactor_relative.py
```

65개 통과. 부모 layout·goal 분포·gravity/부분 reset·접촉/goal 경계·cosine·policy action rate·model PPO 갱신·export 회귀와 새 EEF 변환·초기 snapshot 격리·부분 reset bias·4상태 촉각/동일 noise·58D/64D 공통 storage·encoder gradient·JIT를 검사했다.

GPU 검증 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python -u src/inspire_sweep_baseline/tests/_wrench_refactor_relative_probe.py --num_envs 64 --headless --device cuda:0
```

실제 config 허용 차이 및 부모 isolation 검사는 통과했다. 초기 sandbox 안의 `nvidia-smi` 실패는 드라이버 부재가 아니라 접근 제한이었다. 권한 있는 실행에서 RTX3090이 확인됐다. 첫 GPU probe는 환경 초기화 후 검증 스크립트의 `positions[parked, 2]` 마스크 인덱싱 오류로 중단됐다. `positions[..., 2][parked]`로 검사만 고쳤으며 production 환경은 변경하지 않았다. Kit 종료가 미출력 예외를 가릴 수 있어 traceback을 close 전에 출력하도록 보완했다. exit code만으로 성공을 판정하지 않고 결과 JSON을 확인했다.

64 env 검증은 최종 통과했다. 실제 기존 선반 경로를 사용했고 asset 대체는 없다. iteration0/9999/10000/13000/25000에서 각각 reset 후36step, 총180step을 실행했다. 초기 활성 물체 바닥 정렬 최대 오차0m, 주차 물체 drift 최대0.00000762939453125m였다. 부분 reset 시 비대상 물체 state·관측 snapshot이 보존됐다. 질량·마찰·bbox cache는 동일했고, 각 step reward/관측 finite, 숨긴 장애물 슬롯0, 촉각 상태집합−1/0/1/2를 확인했다. 실제 actuator effort10·velocity1과 OSC의 EEF축 명령도 확인했다. 결과는 workspace `outputs/wrench_refactor_relative_validation/probe_64.json`이다.

2048 env에서도 같은 검사180step을 통과했다. 초기 바닥 오차0m, 최대 parking drift0.00000762939453125m로 같았다. 실제 scene 생성은 약38.8초, 초기화 완료는 프로세스 시작 약155초 후였다. 결과는 `outputs/wrench_refactor_relative_validation/probe_2048.json`이다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python -u src/inspire_sweep_baseline/tests/_wrench_refactor_relative_probe.py --num_envs 2048 --headless --device cuda:0
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python -u src/inspire_sweep_baseline/scripts/train.py --task Inspire-Wrench-Refactor-Relative-v0 --num_envs 64 --headless --device cuda:0 --max_iterations 2 --resilient-attempt-dir outputs/wrench_refactor_relative_training --resilient-target-iterations 2
```

`train.py` seed42·64 env·2 iteration이 완료됐다. 36step/iteration, PPO8epochs/4minibatches 등 부모 수치를 그대로 사용했다. 실제 학습 구간은14.87초였으나 2048 probe와 일부 동시 실행했으므로 성능 benchmark로 해석하지 않는다. `training_status.json`은 completed·last_iteration1이고 `model_1.pt`에 Actor/Critic/optimizer 텐서가 모두 finite였다. `model_0.pt`와 비교하여 Actor와 Critic 각각의 encoder 두 Linear 층 weight/bias4개가 모두 갱신됐음을 확인했다. 결과는 `outputs/wrench_refactor_relative_training/checkpoint_validation.json`이다. 실제 agent.yaml에서도 양쪽 그룹이 policy/obstacles인 것을 확인했다. 기존 `logs/rsl_rl`은 수정하지 않았다.

검증 stdout은 `outputs/wrench_refactor_relative_validation/probe_64.log`, `probe_2048.log`, `outputs/wrench_refactor_relative_training/train.log`에 보존했다. GPU의 두 관측 그룹 및 모델 생성, 학습 완료를 실제 출력과 JSON으로 확인했다. 스폰/중력/readback 검사는 정상이며 장기간 접촉·학습 성능의 증명으로 확대하지 않는다.

## 코드리뷰·정적 보존 대조

`code-review` 스킬로 두 독립 검토를 수행했다. Standards는 저장소 지침·역할별 구조·부모 보존을, Spec은 사용자 요구와 실제 구현을 검토했다. **Standards 0건, Spec 0건**이며 두 검토는 실행 검증과 구분되는 읽기 전용 리뷰다.

HEAD와 작업트리 AST 비교로 기존 EnvCfg9개, ObservationCfg1개, observation 함수 파일의 기존 class2개, PPO 설정10개가 수정되지 않았음을 확인했다. 공유 모델의 입력 라우팅/차원 상수만 확장했으며 기존 모델 기본값74D·그룹 매핑·encoder/PPO/JIT 회귀가 통과했다. 오른손 metadata의 ZIP SHA256도 위 원본과 일치했다.

변경 Markdown5개 수식 검사 및 두 저장소 `git diff --check` 통과. 문서 저장소 변경4개 상대 링크134개 오류0. README까지 포함한 검사에서는 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락 링크1건이 검출됐으며 이번 범위에서 수정하지 않았다. 새 Relative 링크는 정상이다.

## 미검증 범위

장기 학습 수렴·최종 성공률·실물 성능은 이 작업의 검증 대상이 아니다. Hand effort 상향의 장기 접촉 동작 영향은 학습 실험으로 판단해야 한다. 2048 env의 실제 rollout은 검증했지만 PPO 학습은64 env의2 iteration까지만 수행했다. GUI/play·ONNX export는 실행하지 않았으며 JIT export는 CPU에서 검증했다. 초기화·부분 reset·짧은 rollout/학습 결과와 구분한다.

## 2026-11-06 후속: 독립 환경 명세 작성

사용자는 다른 문서를 읽지 않고 환경 구성·초기화·목표 설정·관측 차원·액션·리워드·터미네이션·커리큘럼을 이해할 수 있는 문서를 요청했다. 기존 Relative-v0 환경 문서를 부모 대비 차이 중심 요약에서 독립적인 전체 명세로 확장했다. 다른 환경 문서로 설명을 위임하는 링크와 “부모와 같음” 표현을 최종 수치·동작 설명으로 대체했다. 구현 이력과 부모 대비 차이는 이 개발 로그에 보존한다.

실제 EnvCfg·Scene·Event/배치·Command·Observation·Action 및 상속된 보상/종료 callable을 읽고 설명을 대조했다. 생성 시 한 번 고정되는 물성/크기와 reset마다 바뀌는 배치를 구분하고, OBB 구역·목표의 방향/조건부 거리 분포·주차 중력·부분 reset을 기록했다. policy58D·obstacles64D·raw122D·encoder 결합74D, 초기 snapshot의 현재 EEF 변환, bit별 noise 후 촉각 인코딩을 명시했다.

보상13개 모두에 weight·실제 step 지급식·dt 상쇄 여부·gate·경계를 작성했다. 특히 누적 변위 cosine, 2-of-3와 goal 내부 즉시 인정, Hold 유효성, 선반 비용의1.05/1.06m 기준 차이, 최초 진입과3초 유지 성공의 조건 차이를 설명했다. 종료5개와 유일한 방향 curriculum의 iteration별30→0도 일정도 명시했다.

검증: AST에서 활성 기본 보상13개·종료5개·curriculum1개 이름을 추출해 문서 수록을 대조했고 관측 차원 합계를 재계산했다. 문서 수정 전후 production 코드의 `git diff`가 byte 단위로 같은 것을 확인했다. 변경 문서의 수식·링크 검사와 문서 저장소 `git diff --check`를 통과했다. 문서 변경만 수행했으며 새 물리/학습 실행, 기존 사용자 변경 수정, 학습 로그 변경은 없다. 앞 절의 GPU·학습 결과는 이전 구현 시 검증으로 명확히 구분했다.
