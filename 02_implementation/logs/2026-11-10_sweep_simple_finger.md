# Simple Finger-v0 개발·검증

[환경 계약](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md#finger-v0-독립-손가락-제어) · [환경 안내](../08_ACTIVE_ENVIRONMENTS.md)

## 요청과 기준

사용자는 Simple-v1 직접 상속 환경 `Inspire-Sweep-Simple-Finger-v0`를 요청했다. 손 상태와 명령을2D 압축에서 mimic 제외6개 구동관절로 확장하고 Last Action tanh를 유지한다. 목적은 독립 손가락 위치 제어와 기존 압축 제어의 비교다. 작업 시작 root commit은 `f456f75`였다. 기존 사용자 변경 `docs/plan/PLAN14.md` 및 문서 submodule의 Simple 설명서 변경을 보존했다. 과거 환경·학습 로그·자산은 수정하지 않았다.

사용자가 명시하지 않은 액션 수치 표현은 **절대 목표 각도(rad), scale1, offset0, URDF 범위 clamp**로 결정하고 작업 중 알렸다. 관측은 명령이나 정규화 값이 아닌 현재 `robot.data.joint_pos`다. 순서는 엄지 굽힘·검지·중지·약지·소지·엄지 대립이다.

## 변경과 전체 대조

| 항목 | 부모 Simple-v1 → Finger-v0 | 검토 결과 |
| --- | --- | --- |
| 등록/상속 | `SweepSimpleFingerEnvCfg(SweepSimpleV1EnvCfg)` | 직접 부모 유지, 별도 Gym ID·runner 등록 |
| Scene/자산/물성 | 동일 | 부모 설정 전체 비교, 자산 변경 없음 |
| Commands/Events/Fast reset | 동일 | 목표6–12cm·Warp IK·장애물0–6 및 초기 물체 관측 유지 |
| Observation | hand2→6, Last Action8→12 | term 순서와 나머지 callable/params/noise 유지; policy58→66, obstacles64 동일 |
| Action | arm6 동일, hand2→6 | raw rad 유지·처리 단계 clamp·URDF follower 목표12개 전달 |
| Runtime | 공통 runtime 직접 상속 | 부모 reset 이후 선택한 환경의 손6채널 current/previous action을0으로 보정 |
| Rewards | arm/hand action-rate만12D 입력에 대응 | raw 변화 제곱합·cap100·weight−0.03 유지, 손은6채널 전부 포함; 다른 callable/params/weight 동일 |
| Reach/Contact | 동일 | 현재3D 거리 inverse Reach, 목표 XY<3cm 풀 카운트 상속 |
| Termination/Curriculum | 동일 |10초 timeout/성공 분류·최근10,000개 집계·모든 일정 유지 |
| PPO | class_name·입력66D/출력12D·실험명 변경 |64→16 encoder,256/128/64 MLP, Gaussian std1 및 나머지 하이퍼파라미터 동일 |
| 부모 보존 | 기존 클래스 본문 변경 없음 | 기존 Simple/Prof/Hard 및 과거 기준 환경 CPU 회귀 통과 |

기존 `goal_rewards.action_rate_l2`는8D만 받으므로 Finger 전용 callable을 추가했다. weight를 다시 튜닝하거나 손 채널 수로 평균화하지 않았다. 손 속도 비용은 부모와 같이 물리12관절에 적용한다.

기존 액션은12개 관절에 개방도를 기반으로 목표를 전달한다. USD를 CPU로 열어12개 손 관절 schema를 조회했으며 native mimic 제약이 없음을 확인했다. 새 term도12개 물리 관절을 그대로 제어하되, 입력은6개 독립 drive이고 follower는 원본 오른손 URDF 비율로 확장한다. 엄지3=엄지2×0.8024, 엄지4=엄지3×0.9487, 나머지 각 finger2=finger1×1.0843. 목표 전체 닫힘 결과가 기존 `CLOSED_POSITIONS`12개와 일치함을 검사했다. 기존 이름 `inspire_left_*`는 오른손 USD 호환 이름이며 변경하지 않았다.

## 파일

역할별 기존 `sweep_simple.py`/`sweep_simple_envs.py`/`sweep_simple_ppo_cfg.py`에 자식 Cfg/runtime을 추가했다. 신규 파일은 `assets/hand_kinematics.py`(drive 순서·URDF 한계·mimic 비율), `mdp/action_functions/sweep_simple.py`, `mdp/observation_functions/sweep_simple.py`, `agent/sweep_simple_models.py`, `tests/test_sweep_simple_finger.py`다. 폴더 이동이나 구조 변경은 없다.

## 검증

workspace root에서 아래 환경으로 실행했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple_finger.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_sweep_simple_hard.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  -q -p no:cacheprovider
```

76개 통과. 별도 동일 옵션의 `tests/test_fast_reset.py`는10개 통과·2개 skip. 합계 **86개 통과·2개 skip**.

- 실제 tensor 실행: 뒤섞인 articulation 인덱스에서 joint 이름 순서, 독립 채널·follower 매핑, 상/하한 clamp와 raw 명령 보존, 전체/부분 action reset, measured joint observation,12D tanh Last Action,6개 손 채널 비용·cap.
- 설정: 공식 configclass/Manager term을 사용하고 Sim/Scene 일부 leaf는 double로 대체했다. 부모 전체 구성·callable·파라미터·weight·일정·순서·격리, 자식 직접 상속, 등록과 PPO 변경 범위를 대조했다. 기존 AST 동일성 검사는 신규 자식 정의를 제외한 부모 정의 전체를 계속 비교한다. 모델의 공유 계산 상속은 환경 Cfg/runtime의 역사 상속 검사와 구분한다.
- 실제 RSL-RL 모델: actor12D/critic1D 출력, latent82D, 두 encoder 역전파, JIT script 출력 일치, ONNX exporter 입력130D 확인. ONNX 런타임 실행은 하지 않았다.
- USD stage: installed USD Python 바인딩으로 오른손 합성 자산을 읽고 hand joint schema를 조회했다. 물리 simulation 실행은 아니다.
- 문서: 수정 Markdown 수식 검사 통과, 문서 저장소 전체 내부 링크 오류0. 외부 링크 추가 검사에서는 README의 기존 `FINAL_GOAL_ACCURACY_V0_2_ENVIRONMENT.md` 누락1건이 나왔으며 새 링크 오류는 없었다. 변경 범위 whitespace 검사도 수행했다. source 패키지 diff는 통과했다. root 전체 diff의 기존 사용자 `docs/plan/PLAN14.md` EOF blank-line 경고와 문서 설명서의 기존 사용자 Prof-Hard 행 trailing whitespace는 보존했다.

초기 pytest 명령 한 번은 잘못된 Fast 테스트 파일명으로 수집되지 않았고, 실제 파일 `test_fast_reset.py`로 바로잡아 실행했다. USD 조회는 기본 Python에서 바인딩/공유 라이브러리 경로가 없어 실패했으며, 설치된 omni.usd.libs와 conda lib 경로를 제공한 뒤 성공했다.

## 미검증과 실행

`nvidia-smi`가 NVIDIA driver와 통신하지 못했다. 따라서 native Isaac Sim 환경 import·PhysX reset/step·렌더·GPU 학습·Collection 시간·실물 추종은 미검증이다. CPU contract/model 검사를 물리 제어 성능 확인으로 해석하지 않는다. 차원 확장으로 기존8D 액션 checkpoint와 직접 호환되지 않는다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Finger-v0 --headless
```

GPU 복구 후6개 drive의 개별 명령 추종, 실제 측정 hand observation 순서, reset 직후0rad 상태 및 PPO rollout을 확인한다.

## 후속 문서 반영 요청

사용자가 Simple 계열 설명서에 Finger 내용을 반영하도록 요청했다. 기존 Finger 상세 절·상속도·등록표를 확인하고, 상단 요약과 파생 환경 실험 의도 비교표에 Finger를 추가했다. 모든 파생 모델/체크포인트 구조가 같다고 읽힐 수 있는 공통 문구를 수정하고, Finger 구현 파일·차원 변경·비용 규모 비교 시 고려할 점·검증 범위를 보완했다. 환경 코드는 변경하지 않았다. 수정 문서 수식·링크 검사를 수행했으며, GPU 검증 범위는 기존 기록 그대로다.
