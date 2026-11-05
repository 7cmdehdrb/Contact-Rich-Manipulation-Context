# Refactor-v0 선반/손 질량, EEF OSC, 촉각 및 재구성 명세

2026-11-05. 대상은 `Inspire-Wrench-Refactor-v0`다. [환경 명세](../environments/WRENCH_REFACTOR_V0_ENVIRONMENT.md) · [재구성 소스 부록](../environments/WRENCH_REFACTOR_V0_RECONSTRUCTION.md) · [최초 구현 기록](2026-11-05_wrench_refactor_v0_implementation.md).

## 요청과 변경 전후

| 요청 | 확인한 변경 전 | 수정/최종 상태 |
| --- | --- | --- |
| 선반 질량 속성 적용 순서,30kg | scene mass100 선언; `spawn_from_usd`는 기존 MassAPI만 수정하여 없는 자산에서 무시됨 | Refactor 전용 spawner에서 reference 생성→단일 rigid body 탐색→MassAPI 생성→30kg author→material bind |
| 공식 Hand 총질량 | 오른손 원본 URDF30바디 합.8783kg | RH56E2 촉각형 명목.790kg에 맞게30바디 mass/inertia에.790/.8783 곱함 |
| EEF 기준 OSC | offset pose는 EEF였으나 task frame은 root; upstream Jacobian이 body-local lever를 root axes와 혼용; velocity는 COM alias | policy마다 EEF task pose clone, decimation 동안 고정; root axes로 회전한 lever로 Jacobian shift; link velocity에서 EEF velocity 계산 |
| tactile 접촉 인정.05N | actor/critic RightHandTactile.01 및 direct sensor.01 | 두 관측/term default/direct tactile sensor를.05로 설정, equality 포함 |
| 문서+자산만으로 재구성 | 초기 환경 요약 문서 |532행 상세 명세 +114파일 복원 가능한 소스/해석된 cfg/asset SHA 부록, 별도 빈 디렉토리에서 실제 복원/import 검증 |

공식 자료는 [Inspire Robots RH56E2](https://en.inspire-robots.com/product/rh56e2/)를2026-11-05에 조회했다. 촉각형790±10g, 비촉각형770±10g을 구분했다. 로컬 `RH56E2-R-T1.zip`과12관절17촉각 구성에 근거해T1을 기준으로 삼았다. 파츠별 공장 질량은 확보하지 못했으므로 URDF의 상대 분포를 유지하는 비례 보정이다. Axia80 별도1g과 UR5e는 이 합계에서 제외한다.

기존 user 결정인 출력 토크 기준 action-rate와 목표 내부에도 EEF<.14m 조건은 보존했다. tactile.05N은 센서 관측의 인식 문턱이며 reward target contact.01N은 변경하지 않았다. 각 기존 Wrench 환경 설정/공유 계산 함수는 수정하지 않고 Refactor 전용 함수를 추가했다.

## 구체적 적용과 영향

- `assets/wrench_refactor_spawners.py`: shelf single-body 계약. body가 없으면 root에 생성, 여러 개면 명시적 오류. 기존 dynamic/kinematic flag 보존. 기존 explicit inertia는 old mass를 알 때 비례 보정하고, density-derived old mass이면0 diagonal로 PhysX 재계산 요청.
- `scripts/build_wrench_right_hand.py`: mass 보정 상수/공식 URL/원본mass/보정비율을 USD customData 및 tactile JSON에 기록. 모든 part inertia eigenvalue도 동일 비율로 조정. source geometry/COM/axes/원본 왼손 자산 보존.
- 생성된 `ur5e_inspire_right.usda`/`tactile_regions.json`을 재생성했다. 손 mass/inertia는 PhysX 및 F/T reader cache 생성 전에 확정한다.
- `mdp/action_functions/wrench_refactor.py`: 기존 bounded torque OSC 계산과 RPY 전처리를 재사용하면서 EEF task frame, Jacobian, velocity만 override. upstream 공용 코드는 변경하지 않았다. 본 환경은 fixed base이므로 root velocity0 계약이다.
- `mdp/actions/wrench_refactor.py`: 새 action class 선택. gain/torque limit/6D motion mask 그대로.
- `mdp/observations/wrench_refactor.py`, `mdp/observation_functions/wrench_refactor.py`, scene direct tactile sensor: threshold.05. whole-hand reward sensor는 기존.01.
- `pyproject.toml`: 새 오른손 USD/JSON을 package-data에 추가하여 wheel에도 포함되도록 수정. 기존 directory 구조 유지.
- 실제 GPU probe에 PhysX shelf mass30 및 hand30body sum.790 readback assertion을 추가했다. config-only probe는 해석된 cfg를 JSON에 저장한다.

예상 영향: 선반의 동적 응답은 실제 적용된30kg에 의해 달라진다. 손 중력/관성 하중과 F/T support cancellation도 함께790g 기준으로 바뀐다. Arm action의 방향은 EEF 자세를 따라가므로 기존 root-frame 정책과 동일 행동을 기대하면 안 된다. tactile.01.. .05 미만 신호는 raw bit0이 된다. 보상·termination·curriculum 수치는 위 요청 외 그대로다.

## 검증

1. 오른손 총질량.790 assertion을 기존 생성 자산에 적용했을 때 실패했다. builder 보정 후 통과했다.
2. 실제 checked-in Isaac Lab `modify_mass_properties`의 AST leaf를 real USD fixture에 적용하여 MassAPI가 없는 body에서False 반환을 재현했다. 전용 helper 후 root/child/mass100 body 세 경우 모두30kg, 단일body, 기존관성100→30 비례 갱신을 확인했다.
3. USD-only 조립 probe: hand30개, aligned right joints29개, paired regions17개, mass 합`0.7899999982328154`kg(float32 authoring 오차), measurement child identity 통과.
4. 실제 upstream OSC set_command와 새 action을 연결한 CPU 검사: EEF90° 회전에서 localX→rootY, 회전 right multiplication, task frame clone/freeze, 다음policy 재샘플, bounded torque apply 경로 보존을 확인했다.
5. 추가 Jacobian/velocity 검사: body pitch90°와localZ.1427m에서rootX lever가 되며, baseZ 각속도2rad/s에 대해 EEF Y속도.2854m/s. `J*qdot`와 계산속도가 일치하고 COM alias를 쓰지 않는다.
6. tactile.049999/.05/.050001N에서0/1/1, stale행0, actor/critic threshold동일을 확인했다.
7. Refactor23 + 기존 Wrench/tactile/F/T 회귀를 합해 **159 passed,21.47s**. 결과 `outputs/wrench_refactor_validation/tests_mass_eef.txt`.
8. 실제 Isaac AppLauncher config import 성공. driver가 없는 호스트의 CUDA 오류와 config import 성공을 구분한다. 결과 `config_mass_eef.log`, `resolved_config.json`.
9. 부록 추출 스크립트로 `/tmp/wrench_refactor_doc_rebuild`에114파일 복원,112Python AST 통과. 실제 소스90개 byte 일치(namespace/단일등록 init 제외). 자산 복사 후 새패키지 경로에서 config import 및USD-only probe 모두 통과. 결과 `document_rebuild_import.log`.
10. package-data 패턴에 새 USD/JSON이 포함되는지 확인했다. wheel 빌드/설치는 수행하지 않았다.
11. 기존 tracked Wrench 파일19개는 HEAD와byte동일. 기존공유 OSC/robot/shelf spawner는 수정하지 않았다. `logs/rsl_rl` 및 기존 학습 로그는 건드리지 않았다.

회귀 실행 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_wrench_refactor.py \
  src/inspire_sweep_baseline/tests/test_wrench.py \
  src/inspire_sweep_baseline/tests/test_wrench_v0_1.py \
  src/inspire_sweep_baseline/tests/test_wrench_v0_2.py \
  src/inspire_sweep_baseline/tests/test_wrench_v0_3.py \
  src/inspire_sweep_baseline/tests/test_wrench_v1.py \
  src/inspire_sweep_baseline/tests/test_tactile_projection.py \
  src/inspire_sweep_baseline/tests/test_clutter_v2_wrench.py
```

## 미검증 범위와 문서 계약

NVIDIA driver/CUDA device 부재로 actual PhysX mass readback, dynamic rollout, source shelf collider topology/kinematic 여부, 오른손 무접촉 동적 F/T residual, 실제 multi-contact/overflow,2048환경 처리량 및학습은 미검증이다. 실제 source shelf/YCB assets는 원격 참조이며 이번 작업에서bundle하거나hash확보하지 않았다. 따라서 오프라인 재구성에는 본문manifest의 외부자산 closure도 전달해야 한다.

문서는 기존 ‘변경 없음’ 표현만 복사하지 않고 현재 leaf 수식을 대조했다. 특히 wrench cost는 norm크기의 변화, shelf−3은 collision component만, hold는 별도bounds validity, goal2D는polar, tactile과reward threshold는별개임을 명시했다. 내부반경/엄격부등호/dt상쇄/부분reset/난수seed/오류경로를 포함했다. source 부록은114개 code/config record의 SHA와 안전한빈디렉토리추출 스크립트를 제공한다. 수정할 때는 본문과부록record를함께갱신하고복원검사를다시해야한다.

최종 문서 검사: 변경 Markdown6개에 math checker 통과, 링크 검사 errors0(내부115, workspace외부1, URL2), 양 저장소 `git diff --check` 통과. Markdown 실제 렌더링 검사는 별도 수행하지 않았다. 변경 Refactor Python22개 AST/공백 검사도 통과했다.
