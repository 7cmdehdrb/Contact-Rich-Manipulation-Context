# 2026-11-14 Simple 환경 RH56E2 오른손 설정 점검

## 요청·결론

사용자는 sweep_simple_envs.py가 outputs/data에 제공된 RH56E2 오른손의 Effort, Joint Velocity Limit, Mass, Inertia를 올바르게 적용하는지 점검을 요청했다. 코드 수정 요청은 없으므로 환경·자산·학습 설정은 변경하지 않았다. 점검 JSON과 이 로그만 추가했다.

결론: 오른손 자산 선택 자체는 맞지만, 제공된 RH56E2_R_2025_9_11.urdf의 물리 모델과는 일치하지 않는다. 현재 모델은 다른 공급자 오른손 URDF의 30바디를 사용하고 전체 질량을 0.79 kg으로 보정했다. 신규 압축 모델은 32링크·0.7766626733019238 kg이다. 손 관절 Effort와 엄지 속도 상한도 다르다.

## 실제 적용 경로

- [Simple EnvCfg](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/sweep_simple_envs.py): scene.robot의 hand actuator를 effort_limit_sim=10.0, velocity_limit_sim=1.0으로 덮어쓴다. 이 파일 내 모든 파생 클래스가 베이스 설정을 상속하며 이 값을 재변경하지 않는다.
- [Simple Scene](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/sweep_simple.py): make_robot_cfg()에서 제어기를 받고 spawn만 wrench_right_hand/ur5e_inspire_right.usda를 사용하는 RevisionRobotSpawnerCfg로 교체한다.
- [공유 로봇](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/robot.py): 스포너는 USD 참조를 로드하고 Axia80 바디와 고정 관절을 추가한다. sensor_mass=0.28은 추가 Axia80의 질량이며 손 전체 질량을 설정하는 값이 아니다.
- [오른손 생성기](../../../../src/inspire_sweep_baseline/scripts/build_wrench_right_hand.py): 오른손 원본 형상·프레임·질량·관성을 사용한다. HAND_MASS_KG=0.790, mass_scale=0.790/source_mass이며 mass와 관성 고유값에 같은 scale을 곱한다.
- [Isaac Lab articulation](../../../../IsaacLab/source/isaaclab/isaaclab/assets/articulation/articulation.py): actuator 초기화 시 effort_limit_sim 및 velocity_limit_sim을 시뮬레이터에 기록하므로 이 값들이 USD 원래 limit보다 우선한다.
- startup initialize_physics의 mass_scale=1.5는 object_collection 질량·관성에만 적용한다. 손 질량을 이 값으로 다시 보정하지 않는다.

## 핵심 비교

| 항목 | 현재 Simple | 제공 RH56E2 오른손 URDF | 판정 |
| --- | --- | --- | --- |
| 손잡이성 | right metadata·공급자 오른손 geometry | 오른손 | 일치 |
| 회전 관절 Effort | 전 관절 10 N·m | 전 관절 1 N·m | 10배 차이 |
| 엄지 4관절 Velocity | 1 rad/s | 2 rad/s | 불일치 |
| 나머지 8관절 Velocity | 1 rad/s | 1 rad/s | 일치 |
| 손 전체 Mass | 0.789999998233 kg | 0.776662673302 kg | 분포·합계 불일치 |
| Mass 원본 | 원본 합계 0.8783 kg에 0.899464875327337 배 | 링크별 원문 선언값 | 다름 |
| Inertia | 기존 오른손 URDF 관성에 0.899464875327337 배 | 신규 URDF 관성 | 다름 |
| 손 링크 수 | 30 | 32 | 구성 다름 |

## 좌우 이름 해석

inspire_left_*는 기존 제어·접촉·F/T와 연결하는 호환 슬롯이다. 생성기의 slot()은 right_를 left_로 이름만 매핑하며 geometry·joint frame·COM·inertia는 오른손 원본에서 가져온다. 따라서 left 문자열만으로 왼손을 사용한다고 판정하면 안 된다.

## 링크별 확인

동일 vendor link 이름이 있는 13개 링크의 선언 질량과 관성 고유값을 비교했다. 고유값은 좌표축 회전에 의존하지 않지만 서로 다른 링크 분해를 보정하지는 않는다. 특히 새 모델은 palm이 별도 링크로 분리되어 base_link 단독 질량을 전체 손바닥 질량으로 해석할 수 없다. 질량 단위 kg, 고유값 단위 kg·m².

| 링크 | 현재 Mass | 신규 Mass | 현재 관성 고유값(오름차순) | 신규 관성 고유값(오름차순) |
| --- | --- | --- | --- | --- |
| base_link | 0.5600607991 | 0.09 | 0.00013758361, 0.00021413446, 0.00025544735 | 2.6780539e-05, 2.7868356e-05, 3.6488859e-05 |
| right_index_1 | 0.02555379644 | 0.01869 | 4.8676941e-07, 1.0260521e-06, 1.0567255e-06 | 1.1356399e-06, 3.6699913e-06, 3.7968888e-06 |
| right_index_2 | 0.01095548179 | 0.01102 | 2.6246033e-07, 1.9276956e-06, 1.9696145e-06 | 2.5904147e-07, 2.4238401e-06, 2.4762085e-06 |
| right_little_1 | 0.02555379644 | 0.01869 | 4.8676873e-07, 1.026052e-06, 1.0567256e-06 | 1.13345e-06, 3.6716179e-06, 3.7963221e-06 |
| right_little_2 | 0.008607879281 | 0.01166 | 1.9184179e-07, 1.0348916e-06, 1.0792105e-06 | 3.2433368e-07, 2.3541776e-06, 2.4175687e-06 |
| right_middle_1 | 0.02555379644 | 0.01866 | 4.8676941e-07, 1.0260521e-06, 1.0567255e-06 | 1.1350042e-06, 3.658669e-06, 3.7852568e-06 |
| right_middle_2 | 0.01404064707 | 0.01767 | 2.8753297e-07, 2.365003e-06, 2.4078522e-06 | 5.3655743e-07, 5.0036727e-06, 5.0827999e-06 |
| right_ring_1 | 0.02555379644 | 0.01869 | 4.8676947e-07, 1.0260524e-06, 1.0567258e-06 | 1.1350805e-06, 3.6703875e-06, 3.796732e-06 |
| right_ring_2 | 0.01152214501 | 0.01102 | 2.6246047e-07, 1.9276949e-06, 1.969614e-06 | 2.5963574e-07, 2.4238376e-06, 2.4767966e-06 |
| right_thumb_1 | 0.006710007787 | 0.01537 | 6.0098216e-08, 9.8663428e-08, 1.2132929e-07 | 6.5504919e-07, 8.69962e-07, 9.914288e-07 |
| right_thumb_2 | 0.03835318238 | 0.11034 | 8.5158734e-07, 1.0064762e-06, 1.2159542e-06 | 1.3095246e-05, 3.9737501e-05, 4.3146873e-05 |
| right_thumb_3 | 0.01350096799 | 0.01779 | 3.6943612e-07, 4.7997156e-07, 5.5066141e-07 | 2.3654777e-06, 3.3014803e-06, 3.330022e-06 |
| right_thumb_4 | 0.008742799051 | 0.00766 | 3.7473984e-07, 8.0937178e-07, 8.6122571e-07 | 5.3119627e-07, 1.1592899e-06, 1.1974138e-06 |

## 관절 가동 범위 추가 차이

현재 USD의 각도 제한을 degree에서 radian으로 환산해 신규 URDF와 대조했다. Effort/Velocity 두 값만 바꾸어도 새 URDF와 동일한 모델이 되지는 않는다.

| 관절 | 현재 upper (rad, 근삿값) | 신규 upper (rad) |
| --- | --- | --- |
| thumb_1 | 1.1641 | 1.658 |
| thumb_2 | 0.5864 | 0.62 |
| thumb_3 | 0.5 | 0.5410520681 |
| thumb_4 | 3.14 | 0.4555309348 |
| index/middle/ring/little_2 | 3.14 | 1.476374 |

공유 HAND_CLOSED_TARGETS에는 thumb_1=1.1641, thumb_2=0.5864, 다른 손가락 2번 관절=1.55933183 등이 있다. 신규 모델로 교체한다면 actuator 제한뿐 아니라 관절 범위·mimic 연결·action 목표·관측/접촉 링크·촉각 geometry의 호환성을 함께 대조해야 한다. 현재 검토에서는 이를 수정하지 않았다.

## 검증·전후·미검증

- USD 라이브러리를 사용해 CPU에서 실제 참조 합성 stage를 열었다. 30개 손 rigid body와 12개 회전 관절, 총질량 0.7899999982328154 kg을 확인했다.
- source metadata: handedness=right, source_urdf_hand_mass_kg=0.8783, hand_mass_scale=0.899464875327337, source_zip_sha256=b7997a6087e8c0cded03aff557e07ca82b8793b2b5b3f95ec3566318a13f5f7f. 후속 질문에서 /tmp/inspire_urdf_right_with_force_sensor.zip이 실제로 남아 있음을 확인하고 SHA-256이 metadata와 일치함을 검증했다. 원본 robot name은 urdf_right_with_force_sensor이며 world 1개와 손 링크 30개다. 원본 URDF에는 RH56E2 등 제품 모델명이 명시되어 있지 않다.
- USD 관성은 diagonalInertia와 principalAxes를 함께 사용해 바디 프레임의 6성분으로 복원했다. 신규 URDF는 inertial rpy=0인 대응 링크와 대조했다.
- 전후: 환경 코드와 USD 모두 변경하지 않았다. 점검 결과는 모든 Simple 파생 환경에 공통으로 적용되는 베이스 설정에 관한 것이다.
- 미검증: Isaac Sim/PhysX 환경 초기화·step 후 runtime tensor, 실물 장비 수치·학습 성능은 확인하지 않았다. Effort/Velocity의 실제 적용 경로는 설치된 Isaac Lab 소스에서 확인했다.

[점검 원시 JSON](../../../../outputs/urdf_archive_comparison/sweep_simple_audit.json) · [압축 파일 기준 전체 비교](2026-11-14_urdf_archive_parameters.md)

문서 검증 결과: Markdown 수식 검사 통과, 대상 외부 링크 검사 오류 0(외부 6개·내부 1개), git diff --check 통과.

## 후속 질문: 오른손 및 제품 모델 식별

오른손 원본 ZIP과 생성 자산의 해시 출처가 연결되므로 오른손 자산인 점은 확인된다. 다만 RH56E2라는 제품 모델 식별은 별도다. 기존 환경 문서는 RH56E2-R-T1.zip 파일명과 12관절·17촉각 구성을 근거로 RH56E2 촉각형 질량을 선택했다고 기록한다. 원본 URDF 자체는 제품 모델명을 명시하지 않는다. 따라서 다른 제품 에셋이라고 판정한 것이 아니며, 현재 증거만으로 RH56E2의 특정 버전이라고 확정할 수도 없다. 앞의 신규 URDF와 불일치 판정은 파일·물리 파라미터·링크 구성 차이에 관한 것이다.
