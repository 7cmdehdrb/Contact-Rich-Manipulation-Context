# Sweep Simple 환경 계열

2026-11-11 **Action 변화 비용 상한 제거**: 활성 패키지의 모든 환경에서 Action 변화 페널티의 출력 상한을 제거했다. 팔/손 제곱합에 cap100을 적용하지 않는다. 가중치·각 환경의 Raw/Clip/정규화 입력 방식·실행 Action Clip은 유지한다. Joint Velocity 등 다른 비용의 상한은 이번 변경 대상이 아니다. [전체 범위·검증](../logs/2026-11-11_action_rate_uncapped.md).

2026-11-11 최종 갱신: 등록된15개 환경을 기준으로 한다. **Finger-v0-Test와 Finger-v0-Wrench는 모두 Finger-v0의 직접 자식이며 서로 독립된 비교 실험**이다. Test는 팔 속도 종료1.0rad/s 고정, Wrench는 센서 기준 힘·모멘트 제어·센서/손 입력 Clip·Clip된 Last Action과 팔 속도 종료1.0rad/s 고정을 적용한다. [현재 Finger 제어·종료 비교](#현재-finger-계열-제어종료-비교) · [Wrench 상세](#finger-v0-wrench-센서-프레임-wrench-osc) · [Test 상세](#finger-v0-test-고정-팔-속도-종료-실험).

2026-11-11 **최신 계약 — Finger-v1 속도 조건 변경**: Finger-v1의 팔 속도 종료 커리큘럼을 제거하고1.0rad/s로 고정했으며, 팔 속도 비용을−0.06에서−0.03으로 복구했다. Finger-v2·Semi-Prof-v0와 세 Raw 자식에도 상속된다. 기존 Clip/Last Action 방식과 다른 보상·일정은 유지한다. Raw와 원환경의 팔 속도 비용은 이제 동일하다. [개발·검증](../logs/2026-11-11_finger_v1_fixed_velocity.md).

원환경/Raw 분리는 유지한다. Finger-v1/v2·Semi-Prof-v0는 실행 Clip·Clip된 Last Action, 대응 Raw ID는 실행 Clip 없음·Last Action tanh다. Semi-Prof5% 상한 제거는 양쪽에 유지한다. [비교·play](#raw-파생-환경과-원환경-play).

2026-11-11 **중대 이슈 수정 — Finger-v1/v2·Semi-Prof-v0**: 정책의 tanh/atanh 변환을 제거하고 일반 Gaussian으로 변경했다. PPO는 Clip 전 샘플, 제어·Last Action·action-rate는 Clip 후 raw 명령을 사용한다. 정규화 없음. 이전 tanh 정책 checkpoint의 직접 Resume는 거부하며 신규 학습이 기준이다. [원인·변경·검증·미검증 범위](../logs/2026-11-11_gaussian_action_clipping_incident.md). 아래 상속도의 학습 현황 메모는 기존 사용자 기록이며, 수정 후 학습 검증을 뜻하지 않는다.

2026-11-11 기준 실제 코드에 근거한 환경 설명서. 베이스 전체 구성과 파생 환경의 변경·실험 의도를 함께 정리한다. 기존 실험 환경에서 상속을 분리한 계열이며, 실제 코드의 후속 변경도 반영한다. [환경 안내](../08_ACTIVE_ENVIRONMENTS.md) · [개발·검증 기록](../logs/2026-11-10_sweep_simple_family.md).

2026-11-10 후속 변경: **Simple-v0·Simple-v1·Simple-Hard-v0는 타겟 root와 목표의 XY 거리가3cm 미만이면 접촉 유지 count/reward를 즉시20으로 인정한다.** 접촉·이력·EEF 높이 조건을 우회한다. Prof 계열은 접촉 유지 보상이 없어 영향이 없다. 따라서 Simple-v0/v1은 이제 과거 v0_2_2_4/6와 이 한 가지 차이가 있다. [변경 기록](../logs/2026-11-10_simple_goal_full_contact.md).

2026-11-10 추가: **Simple-Finger-v0는 Simple-v1을 직접 상속하여 손 관측과 제어를 독립 구동6관절로 확장한다.** Last Action의 tanh를 유지하며, 목표 내부 풀 카운트도 상속한다. [Finger 비교·관절 순서·실행](#finger-v0-독립-손가락-제어).

2026-11-11 추가: **Finger-v1은 일반 Gaussian의 초기 분포·실행 입력 Clip·Last Action과 속도 종료를 변경하고, Finger-v2는 로그 Distance와 2cm·3초 달성 후 후퇴를 적용한다.** [v1/v2 계약](#finger-v1v2-출력-범위와-정밀-이동후퇴) · [검증 기록](../logs/2026-11-11_sweep_simple_finger_v1_v2.md).

2026-11-11 추가: **Semi-Prof-v0는 Finger-v1을 직접 상속한다. 접촉 조건부 로그 Distance와 현재 목표 방향 대비3D 접촉 합력 정렬 보상을 사용하고 접촉 유지 보상은 제거한다.** [Semi-Prof 계약](#semi-prof-v0-접촉-조건부-정밀-이동과-힘-방향) · [개발·검증](../logs/2026-11-11_sweep_simple_semi_prof.md).

## 등록과 상속

```text
ManagerBasedRLEnvCfg
└── SweepSimpleEnvCfg                         Inspire-Sweep-Simple-v0
    ├── SweepSimpleProfEnvCfg                 Inspire-Sweep-Simple-Prof-v0
    │   └── SweepSimpleProfV1EnvCfg           Inspire-Sweep-Simple-Prof-v1  -> .250 학습 종료
    │       └── SweepSimpleProfHardEnvCfg     Inspire-Sweep-Simple-Prof-Hard-v0 
    └── SweepSimpleV1EnvCfg                   Inspire-Sweep-Simple-v1
        ├── SweepSimpleFingerEnvCfg           Inspire-Sweep-Simple-Finger-v0 -> .30 학습 종료
        │   ├── SweepSimpleFingerWrenchEnvCfg Inspire-Sweep-Simple-Finger-v0-Wrench
        │   ├── SweepSimpleFingerV0TestEnvCfg Inspire-Sweep-Simple-Finger-v0-Test
        │   └── SweepSimpleFingerV1EnvCfg     Inspire-Sweep-Simple-Finger-v1 -> .30 학습 중
        │       ├── SweepSimpleFingerRawV1EnvCfg Inspire-Sweep-Simple-Finger-Raw-v1
        │       ├── SweepSimpleFingerV2EnvCfg Inspire-Sweep-Simple-Finger-v2 -> .180 학습 중
        │       │   └── SweepSimpleFingerRawV2EnvCfg Inspire-Sweep-Simple-Finger-Raw-v2
        │       └── SweepSimpleSemiProfEnvCfg Inspire-Sweep-Simple-Semi-Prof-v0 -> .250 학습 중
        │           └── SweepSimpleSemiProfRawEnvCfg Inspire-Sweep-Simple-Semi-Prof-Raw-v0
        └── SweepSimpleHardEnvCfg             Inspire-Sweep-Simple-Hard-v0 -> .180 학습 종료. Finger-v0이 우수함
```

| 새 task ID | 동작 기준 | 직접 부모와 차이 | PPO experiment_name |
| --- | --- | --- | --- |
| `Inspire-Sweep-Simple-v0` | Relative-IK `v0_2_2_4` | 과거 환경 상속 없는 독립 기준 | `inspire_sweep_simple_v0` |
| `Inspire-Sweep-Simple-Prof-v0` | Relative-IK `v0_2_2_5` | Goal Distance·방향 이탈·접촉 유지 보상 | `inspire_sweep_simple_prof_v0` |
| `Inspire-Sweep-Simple-v1` | Relative-IK `v0_2_2_6` | Reach만 변경 | `inspire_sweep_simple_v1` |
| `Inspire-Sweep-Simple-Prof-v1` | Prof-v0 + `v0_2_2_6` Reach | Prof-v0에서 Reach만 변경 | `inspire_sweep_simple_prof_v1` |
| `Inspire-Sweep-Simple-Hard-v0` | Simple-v1 | 목표 거리 확대·DeadZone 삭제 | `inspire_sweep_simple_hard_v0` |
| `Inspire-Sweep-Simple-Prof-Hard-v0` | Simple-Prof-v1 | 동일한 목표 샘플링 변경 | `inspire_sweep_simple_prof_hard_v0` |
| `Inspire-Sweep-Simple-Finger-v0` | Simple-v1 | 손 관측·명령을 독립 구동6관절로 확장 | `inspire_sweep_simple_finger_v0` |
| `Inspire-Sweep-Simple-Finger-v0-Wrench` | Finger-v0 | 센서 wrench OSC·실행/Last Action Clip·팔 속도 종료1rad/s 고정 | `inspire_sweep_simple_finger_v0_wrench` |
| `Inspire-Sweep-Simple-Finger-v0-Test` | Finger-v0 | 팔 속도 종료1.0rad/s 고정·해당 커리큘럼 제거 | `inspire_sweep_simple_finger_v0_test` |
| `Inspire-Sweep-Simple-Finger-v1` | Finger-v0 | Gaussian 정책·실행 Clip·Clip된 Last Action, 팔 속도 종료1rad/s 고정 | `inspire_sweep_simple_finger_v1` |
| `Inspire-Sweep-Simple-Finger-v2` | Finger-v1 | 로그 Distance, 연속 체류 게이트, 후퇴 Reach 및 성공 판정 | `inspire_sweep_simple_finger_v2` |
| `Inspire-Sweep-Simple-Semi-Prof-v0` | Finger-v1 | 접촉 조건부 로그 Distance120·멀어짐−31.128·3D 힘 방향0.33, 접촉 유지 삭제 | `inspire_sweep_simple_semi_prof_v0` |
| `Inspire-Sweep-Simple-Finger-Raw-v1` | Finger-v1 | Clip 제거·Last Action tanh; 팔 속도 비용은 부모와 동일 | `inspire_sweep_simple_finger_raw_v1` |
| `Inspire-Sweep-Simple-Finger-Raw-v2` | Finger-v2 | 동일 제어 변경, v2의 정밀 이동·후퇴 유지 | `inspire_sweep_simple_finger_raw_v2` |
| `Inspire-Sweep-Simple-Semi-Prof-Raw-v0` | Semi-Prof-v0 | 동일 제어 변경, Semi-Prof 보상·5% 상한 제거 유지 | `inspire_sweep_simple_semi_prof_raw_v0` |

공통 런타임 `SweepSimpleEnv`는 `ManagerBasedRLEnv`를 직접 상속한다. EnvCfg·SceneCfg·Manager Cfg·PPO도 과거 테스트 Cfg를 상속하거나 인스턴스화하지 않는다. 보상/종료/리셋 함수, Warp IK, OSC 구현, 자산 스포너, 정책 모델 구현은 그대로 공유한다. 따라서 독립성의 범위는 **환경 구성과 런타임의 과거 상속 제거**이며, 모든 연산 함수와 자산을 복제한 계열은 아니다.

## 현재 Finger 계열 제어·종료 비교

아래 ID는 공통 접두사 `Inspire-Sweep-Simple-`를 생략했다. 모든 행은 손6축·전체12D 액션을 사용한다. Clip은 정책의 Gaussian 샘플 자체를 제한하는 것이 아니라, 제어기에 전달하는 raw 명령의 제한을 뜻한다. 손 목표의 URDF 제한과 팔 effort 한계는 별개로 유지한다.

| 환경 | 팔 제어·명령 프레임 | 실행 raw Clip | Last Action | 팔 속도 비용 | 팔 속도 종료 임계값 |
| --- | --- | --- | --- | --- | --- |
| `Finger-v0` | pose_rel·EEF | 없음 | tanh(raw) | −0.03 | 4→2rad/s |
| `Finger-v0-Test` | pose_rel·EEF | 없음 | tanh(raw) | −0.03 | **1rad/s 고정** |
| `Finger-v0-Wrench` | **wrench_abs·AXIA80 센서** | 센서 범위·손 URDF | Clip된 raw | −0.03 | **1rad/s 고정** |
| `Finger-v1` | pose_rel·EEF | 있음 | Clip된 raw | −0.03 | 1rad/s 고정 |
| `Finger-v2` | pose_rel·EEF | 있음 | Clip된 raw | −0.03 | 1rad/s 고정 |
| `Semi-Prof-v0` | pose_rel·EEF | 있음 | Clip된 raw | −0.03 | 1rad/s 고정 |
| `Finger-Raw-v1` | pose_rel·EEF | 없음 | tanh(raw) | −0.03 | 1rad/s 고정 |
| `Finger-Raw-v2` | pose_rel·EEF | 없음 | tanh(raw) | −0.03 | 1rad/s 고정 |
| `Semi-Prof-Raw-v0` | pose_rel·EEF | 없음 | tanh(raw) | −0.03 | 1rad/s 고정 |

종료는 팔 관절 중 하나라도 속도 절댓값이 현재 임계값을 **초과**할 때 적용한다.4→2 일정은10000 iteration부터250마다0.05씩 감소한다.Finger-v1과 그 자식, Test와 Wrench는1rad/s 고정으로 이 임계값 커리큘럼을 사용하지 않으며, 다른 보상·DeadZone 커리큘럼은 부모에서 유지한다.

Wrench의 센서 기준 액션과 기존 EEF 기준 `wrist_wrench` 관측을 구분한다. Wrench는 Last Action만 Clip된 Raw 관측으로 바꾸고 나머지 관측·보상은 유지하며, Test와 동일한 고정1rad/s 종료를 사용한다. Semi-Prof 및 Semi-Prof-Raw의 양의 보상 연동 Wrench5% 상한은 제거된 상태다.

## 학습 현황과 후속 방향

2026-11-11 사용자 보고 기준이다. 아래는 사용자가 관찰한 학습 결과와 연구 방향이며, 이번 문서 갱신에서 학습 로그나 영상을 별도로 분석한 결과는 아니다.

| 환경 | 상태 | 관찰 결과·판단 | 후속 방향 |
| --- | --- | --- | --- |
| `Simple-Prof-v1` | 학습 종료 | 목표에 가까워지는 보상을 극대화하는 과정에서 다른 보상 요구를 사실상 무시하고, 물체를 위에서 누르면서 목표점 근처에서 매우 빠르게 왕복하는 행동이 관찰됨. 사용자는 거리 보상 자체의 구조 문제로 판단 | 후속 Semi-Prof-v0 구현 완료. 최고 기록 개선만 보상하는 접촉 조건부 로그 Distance와 힘 방향 보조를 시험할 예정이며, 학습 효과는 미검증 |
| `Simple-Finger-v0` | 학습 종료 | 손가락 독립 제어 결과는 유망하지만, 목표 도달 정확도가 부족하고 움직임이 지나치게 빠름 | 이를 개선할 Finger-v1/v2 구현 완료. v1에서 액션 범위·속도를 제한하고, v2에서 정밀 접근·체류·후퇴를 유도. 개선 효과는 후속 학습으로 확인 |
| `Simple-Hard-v0` | 학습 결과 확인 중 | 결과 검토를 계속하고 있으나, 사용자 판단으로 Finger 계열의 결과가 좋아 후속 연구를 Finger 중심으로 진행할 예정 | Hard 결과 확인은 유지하며, 개발·학습의 우선 방향은 Finger 계열로 이동 |

Prof-v1의 왕복 현상은 관찰된 결과이고, 거리 보상 구조가 원인이라는 것은 사용자의 현재 판단이다. 원인 분리 실험이나 정량 비교로 확정한 결론과 구분한다. Finger-v1/v2는 이미 구현되었지만, 이 보고만으로 해당 문제의 해결이나 학습 완료를 의미하지 않는다.

## 베이스 환경: Inspire-Sweep-Simple-v0

목표는 선반 위 타겟을 손으로 밀어 지정된 XY 목표점에 가까이 옮기면서, 선반·장애물에 과도한 영향을 주지 않는 정책을 학습하는 것이다. 초기 물체 배치 관측 이후에는 로봇 상태·촉각·손목 F/T를 활용한다. 아래 내용은 베이스의 전체 구성이고, 파생 환경에서 명시적으로 바뀌는 항목은 뒤 비교표에 정리했다.

### 환경 구성과 시뮬레이션

| 구성 | 설정과 역할 |
| --- | --- |
| 환경 구조 | Isaac Lab Manager-based RL. EnvCfg가 Scene·Observation·Action·Command·Event·Reward·Termination·Curriculum을 조합하고, 별도 runtime이 reset/step과 통계를 관리 |
| 로봇 | UR5e 6축 팔 + Inspire 오른손 12관절 + Axia80 손목 F/T. 팔은 OSC 토크 제어, 손은 위치 목표 제어 |
| 선반·배경 | 40×100cm 선반 표면, 표면 높이1.05m. 선반 질량30kg, 초기 위치(−0.7,0,0). 지면과 조명 포함 |
| 물체 구성 | 타겟 cylinder1개 + 장애물16개를 생성해 고정 유지. 장애물8종을2개씩 보유: cylinder, cube, mug, bottle, cracker box, sugar box, tomato soup can, master chef can |
| 활성 물체 | 타겟은 슬롯0 고정. 에피소드마다 장애물0–6개 균등 추첨 후 활성화. 나머지는 선반 밖 높은 위치에 격리 |
| 병렬 실행 | 기본2,048환경, 간격2.5m, `replicate_physics=False` |
| 시간 | physics dt0.01초(100Hz), decimation2, policy dt0.02초(50Hz). 에피소드 최대10초=500 policy steps |
| 물리 설정 | 마찰 재질을 로봇·선반·물체 스포너에 전달. PhysX 접촉 버퍼 용량, bounce threshold0.2, friction correlation distance0.00625 설정 |
| 제어 프레임 | `ee_frame`은 손목 센서 링크에 고정된 EEF. 별도로 finger/wrist frame을 두어 선반 근접도를 평가 |
| 시각화 | 목표와 EEF 프레임 표시 설정 포함. IK 초기화 박스 기본 OFF. 물체 스폰 가능·금지·점유 영역 표시는2026-11-11 삭제 |

### 초기화·랜덤화·리셋

| 시점/항목 | 동작 |
| --- | --- |
| 최초 자산 생성 | 물체 스케일을0.9–1.1 균등 추출. 각 슬롯의 종류·크기는 이후 reset에서 유지 |
| prestartup | 스케일 반영 BBOX·바닥 정렬 높이·외접원·배치 셀 등 불변 기하를 캐시 |
| startup 물성 | 물체별 질량0.345–0.750kg 균등 추출(원래0.230–0.500kg에1.5배), 관성 비례 조정. 선반 접촉면·물체·손의 마찰은 역할별 범위에서 추출. 물성은 reset마다 다시 뽑지 않음 |
| 타겟 시작점 | 선반 중앙의 반경2cm 원판 안에서 균등 배치, yaw −90도, 물체 바닥이 선반에 맞도록 높이 설정 |
| 목표 거리 |6–12cm. 선택한 방향에서 물체가 선반 가장자리2cm 여유를 지키는 최대 거리까지 상한을 제한한 후 범위 내 균등 추출 |
| 목표 방향 | 선반 로컬 +X는 로봇 쪽 Pull, −X는 Push. 초기에는 ±X 주변 각30도 반각의 DeadZone을 제외하고 나머지 각도에서 균등 추출. 이후 curriculum으로 축소 |
| RED 금지 구역 | 타겟의 외접원 이동 궤적을 선반의 로봇 쪽 앞 경계까지 연장한 영역. 장애물이 밀기 경로를 막지 않도록 제외 |
| WHITE 배치 구역 | 나머지 선반 영역. 물체 외접원 반지름에1cm를 더한 영역끼리 겹치지 않도록 배치.5mm 안전 셀 사용. GRAY 없음 |
| 로봇 초기 자세 | 타겟·이동 방향으로 초기 EEF 위치를 결정. 선반 앞 경계 바깥8–10cm, 타겟 좌우10–18cm 범위와 높이 jitter 사용. Warp IK로 팔 관절 자세 계산 |
| reset 적용 | 새로운 목표와 배치·IK를 계산한 뒤 선택된 환경의 최종 상태 기록. 손은 펼친 자세로 초기화. 보상 이력·접촉 카운트·에피소드 통계·초기 물체 관측 스냅샷 갱신 |
| 난수 | 배치·IK·startup 물성의 난수 스트림을 분리하며 reset seed에 따른 재현성 유지 |

재배치 때 USD 자산을 다시 생성하지 않는다. 새 목표·배치를 사용하되, 고정 기하 캐시와 통합 상태 기록으로 reset 부담을 줄이는 Fast 방식이다. IK/배치 실패 시 성공한 것처럼 대체 상태를 기록하지 않는다.

### 관측과 센서

Actor와 Critic은 동일한 `policy` 58차원 + `obstacles` 64차원 그룹을 사용한다. 별도의 특권 Critic 관측은 없다(`critic=None`, `critic_obstacles=None`). 초기 물체 위치는 월드에 고정된 스냅샷을 현재 EEF 좌표계로 바꾸므로, 로봇이 움직이면 관측 좌표는 변하지만 물체의 실제 이동을 새로 관측하는 것은 아니다.

| 그룹/term | 차원 | 의미 |
| --- | ---: | --- |
| policy / `joint_pos` |6| 팔6관절 위치 |
| policy / `joint_vel` |6| 팔6관절 속도 |
| policy / `hand_configuration` |2| 손의 굽힘과 엄지 opposition 상태를0–1로 요약 |
| policy / `ee_pose` |7| 로봇 root 기준 EEF 위치3 + quaternion4 |
| policy / `target_obs_state` |3| 초기 타겟 위치를 현재 EEF 좌표계로 표현 |
| policy / `goal_pos` |3| 고정된 에피소드 목표 위치를 현재 EEF 좌표계로 표현 |
| policy / `actions` |8| 직전 액션 명령을 tanh 처리한 값 |
| policy / `tactile` |17| 손바닥·손등 대응 영역의 접촉 상태를 결합. 무접촉0, 손바닥1, 손등−1, 양쪽2 |
| policy / `wrist_wrench` |6| 손목 힘3 + 모멘트3 |
| obstacles / `initial_positions` |64|16슬롯×(가시성1 + 초기 위치3). 위치는 현재 EEF 기준, 비가시 슬롯은0 |

촉각용 손 접촉 센서, 손 전체 접촉 센서, 손 부위별 물체 필터 센서, 물체별 손 필터 센서를 구성한다. 관측의 촉각 임계값은0.05N이고, 보상의 타겟 접촉 임계값0.01N과 구분한다. 접촉 센서는 history length0이며 필요한 보상 이력은 term 내부에서 관리한다.

관측 오차도 학습 구성에 포함한다. 타겟 초기 위치는 에피소드별 좌표 편향 ±1cm, 장애물 초기 관측은1cm 위치 노이즈·가시성 기준0.35·가시성 반전 확률1%·관측 순서 교환 확률10%를 사용한다. 촉각은 원래 접촉 bit별1% 반전 후 결합한다. 손목 wrench는 힘 표준편차0.05N, 모멘트0.005Nm의 Gaussian noise를 더하고 각 축을 ±150N/±8Nm로 제한한다. 장애물 그룹은 reset에서 만든 노이즈를 유지하며 매 step 추가 corruption은 없다.

보상·종료·평가 함수는 시뮬레이터의 **현재 타겟/장애물 상태**를 읽는다. 이는 정책에 현재 물체 위치를 제공한다는 뜻이 아니다.

### 액션과 제어

| 항목 | 구성 |
| --- | --- |
| 총 액션 |8차원: 팔6 + 손2 |
| 팔 | 로봇 root 기준 상대 EEF pose 명령(병진3·회전3). 위치 scale0.03m, 회전 scale0.15rad |
| OSC | fixed impedance, 위치/회전 전 축 제어, 관성 decoupling 및 중력 보상 ON, nullspace 제어 OFF. stiffness=(100,100,100,50,50,50), damping ratio 전 축1 |
| 토크/속도 제한 | 팔 토크 앞3관절150Nm·뒤3관절28Nm, 속도 제한3.14rad/s. OSC effort limit scale1 |
| 손 | 채널0은 굽힘, 채널1은 엄지 opposition의 열림 정도.0–1로 clamp 후 open/closed 관절 자세 사이 보간,1은 펼침 |
| 손 제한 |12관절에 effort10Nm·속도1rad/s |

물리 액추에이터의 속도 제한과 뒤의 episode 종료용 관절 속도 임계값은 서로 다른 설정이다.

### 목표 명령

`target_goal_pos`는 reset에서 정한 에피소드 목표를 전달한다. command의 resampling interval은1,000,000초로 설정되어10초 에피소드 중 별도 목표 변경은 없다. 성공 반경 설정은3cm이며, 방향 기준은 초기 타겟→목표 벡터다. 목표 지점 도착만으로 조기 종료하지 않는다.

### 보상 전체 목록

아래 weight는 설정값이다. RewardManager는 일반적으로 term 출력에 weight와 policy dt를 곱한다. 단, 거리 증가분 기반 term과 `shelf_failure`는 함수 내부에서 dt를 나눠 이를 상쇄한다. 따라서 서로 다른 term의 weight 숫자만으로 실제 기여도를 비교하면 안 된다.

| 활성 term | weight | 의미와 핵심 조건 |
| --- | ---: | --- |
| `reaching` |30| 현재 EEF–타겟 root 3D 거리에서10cm를 뺀 값의 **에피소드 최솟값 개선분**. 기존 기록까지 복귀하거나 정지하면 추가 보상 없음 |
| `goal_distance` |100| 타겟–목표 XY 거리의 에피소드 최고 접근 기록 개선분. 접촉 조건 없음, tolerance0 |
| `hand_contact` |0.1| 타겟 접촉 유지 카운트. 목표 XY 거리<3cm이면 무조건20, 그 밖에서는 아래 접촉 인정 규칙 적용 |
| `arm_action_rate` |−0.03| 팔 액션 변화 제곱합, 출력 상한 없음 |
| `hand_action_rate` |−0.03| 손 액션 변화 제곱합, 출력 상한 없음 |
| `arm_joint_velocity` |−0.03| 팔 관절 속도 비용, max_cost100 |
| `hand_joint_velocity` |−0.01| 손 관절 속도 비용, max_cost100 |
| `shelf_collision` |−0.5| 선반 움직임 및 EEF가 가까울 때 가상 손가락/손목 프레임의 표면 근접 비용 |
| `shelf_failure` |−3| 선반 속도·손목 높이 실패 판정에 대한 비용. 종료의 선반 변위 조건 전체와 동일한 함수는 아님 |
| `obstacle_contact` |초기0| 장애물 접촉력 비용. free_force80N, max_cost100에서 curriculum 적용 |
| `wrench_change` |초기0| 손목 힘/모멘트 크기 변화 비용. 초기 free_force_change50N·free_moment_change5Nm, curriculum 적용 |
| `object_tilt` |−30| 활성 물체 기울기 비용. free angle5도, fail angle0.9rad |
| `obstacle_displacement` |−150| 활성 장애물 변위 비용. displacement_max_cost0.04 |
| `target_inverse_distance` |−25.94| 직전 policy step보다 목표 XY 거리가 늘어난 부분만 비용. 이름과 달리 거리의 역수 보상이 아님 |

목표 XY 거리<3cm에서는 count와 term 출력을20으로 설정한다. 접촉 없음·EEF 높이15cm 이상이어도 지급하며, 실패/성공 종료 조건 자체는 바꾸지 않는다. weight0.1과 dt0.02에서 이 term의 step 기여는0.04다. 목표 내부를 실제 접촉 이력으로 꾸미지는 않는다. 목표에서 벗어나면 저장된 count20에서 원래 접촉 인정/감쇠 규칙을 적용한다.

목표 밖의 접촉 유지에서는 타겟–손 접촉력0.01N 이상·유효 센서·EEF가 초기 선반 표면 위15cm 미만인지를 매 step 기록한다. 최근3회 중2회 이상 만족하고 현재 높이도 유효하면 인정한다. 인정 시 count+1(상한20), 불인정 시 count−2(하한0). 인정 step만 남은 count에 비례한 보상을 지급하며, 불인정 step은0이다. 따라서 현재 순간 접촉이 끊겼더라도2-of-3 이력상 인정될 수 있고, 목표 밖에서 높이15cm 이상이면 이력에 관계없이 불인정이다.

비활성 term도 명시한다: `goal_hold`(Holding), `object`(통합 물체 비용; tilt/변위로 분리), `pushing_speed`, `eef_linear_speed`, `eef_orientation`, `object_acceleration`. 베이스에는 `direction_deviation`도 없다.

### 터미네이션 전체 목록

| term | 조건 | 처리 |
| --- | --- | --- |
| `object_fall_or_tilt` | 활성 타겟/장애물 중 물체 바닥 높이가 선반 표면보다1cm 넘게 낮거나, 기울기≥0.9rad, 또는 바닥 높이가 비유한 값 | 실패 종료 |
| `shelf_failure` | 선반 root의 선형/각속도를 합친6D norm>0.1, 손목 프레임의 선반 위 높이<3cm, 또는 선반 위치 변위>5cm | 실패 종료. 별도 손가락 높이 종료는 OFF |
| `arm_joint_velocity` | 팔 관절 중 절댓값 속도가 현재 임계값 초과(초기4rad/s) | 실패 종료 |
| `timeout` |10초 도달 | time-limit truncation, bootstrap 유지. 종료 전 평가 메트릭 기록 |
| `success` | timeout이면서 타겟 root–목표 XY 거리<3cm이고 위 실패3항목이 모두 거짓 | 성공 진단용 truncation 항목. 별도 조기 종료나 추가 성공 보상 없음 |

`success`는 `timeout`의 부분집합이므로 두 종료 항목은 동시에 참일 수 있다. 두 비율을 합쳐1로 해석하면 안 된다. 속도나 Holding 시간은 성공 조건에 포함하지 않는다.

### 커리큘럼 전체 목록

기준은 환경 step 수가 아닌 **학습 iteration**이다. 아래 보상 일정은 지정 지점 사이에서250 iteration 간격으로 값을 갱신하는 선형 일정이다. `(iteration:값)`으로 표시했다.

| 활성 term | 변경 대상 | 일정 |
| --- | --- | --- |
| `wrench_free_force_change` | wrench 변화 무비용 범위(N) |0:50, 3000:50, 6000:30, 10000:30, 12000:20 |
| `wrench_free_moment_change` | 모멘트 변화 무비용 범위(Nm) |0:5, 3000:5, 6000:3, 10000:3, 12000:2 |
| `obstacle_free_force` | 장애물 접촉력 무비용 범위(N) |0:80, 3000:80, 6000:50, 10000:50, 12000:30 |
| `wrench_weight` | wrench 변화 weight |0:0, 1000:0, 3000:−0.03, 6000:−0.1 |
| `obstacle_weight` | 장애물 접촉 weight |0:0, 1000:0, 3000:−0.02, 6000:−0.05, 10000:−0.05, 12000:−0.1 |
| `target_goal_direction_deadzone` | ±X 방향 제외 반각 |0–9999:30도, 10000:25도, 이후3000 iteration마다5도 감소, 25000부터0도 |
| `arm_joint_velocity_threshold` | 팔 관절 속도 종료 임계값 |초기4rad/s, 10000 이후250 iteration마다0.05 감소, 최저2rad/s |

비활성 일정: `eef_free_speed`, `pushing_free_speed`, `object_free_acceleration`, `acceleration_weight`, `goal_speed_scale`. 장애물 개수 증가나 성공 반경 축소 일정은 없다. checkpoint 재개 시 학습 iteration에 맞춰 활성 일정을 적용한다.

### 평가 메트릭과 학습 설정

| 메트릭 | 의미 |
| --- | --- |
| `target_goal_distance_xy_m_mean` | 에피소드 내 목표 XY 거리 평균 |
| `eef_linear_speed_m_s_mean`, `target_linear_speed_m_s_mean` | EEF/타겟 선형 속력의 에피소드 평균 |
| `target_within_goal_radius_fraction_mean` | 목표 반경 **이하(≤3cm)** 상태의 시간 비율. 성공 판정의 엄격한<3cm와 경계가 다름 |
| `eef_linear_speed_m_s_episode_max`, `target_linear_speed_m_s_episode_max` | EEF/타겟의 에피소드 최대 속력 |
| `target_goal_distance_xy_m_final`, `target_goal_distance_xy_m_min` | 종료 순간/에피소드 최솟값 목표 거리 |
| `timeout_episode_count` | 최근 완료N개 에피소드 중 timeout 시점까지 도달한 개수 |
| `timeout_success_count` | 같은 창 안에서 timeout 성공 조건을 만족한 개수 |
| `timeout_success_rate` | 위 성공 개수/timeout 개수. 분모0이면0 |

위 custom metric은 TensorBoard의 `Metrics/` 아래 기록한다. 평균/최대/최종 거리 통계는 해당 reset 배치의 에피소드 값들을 평균한다. timeout 집계는 기본N=10,000의 rolling window이며 조기실패도 창의 한 자리를 차지한다. 같은 step의 완료 순서는 env ID 오름차순이다. 이외 RewardManager/TerminationManager/CurriculumManager와 runner의 기본 보상·종료·학습 로그도 사용한다.

PPO는 actor/critic 각각 장애물 encoder(hidden32, embedding16, ReLU)와 MLP `[256,128,64]`(활성함수 ELU)를 사용한다. 입력 정규화는 OFF, Gaussian 초기 std1이다. 환경당 rollout36 steps, 최대90,000 iteration,50 iteration마다 저장한다. PPO는 epoch8·minibatch4, learning rate0.001(adaptive, desired KL0.02), gamma0.98, GAE lambda0.95, clip0.2, entropy0.005, value loss coefficient1, clipped value loss ON, gradient norm1을 사용한다. 모든 파생 환경에서 이 학습 하이퍼파라미터를 유지하고 로그 실험명을 구분한다. Finger-v0는 손 관측·액션 확장에 맞춰 모델 입출력 차원과 모델 클래스를 변경한다. Finger-v0-Test와 Finger-v0-Wrench는 이 PPO 설정을 유지하고 실험명만 구분한다. Finger-v1/v2·Semi-Prof-v0는 같은 입출력 차원과 일반 Gaussian을 사용하되, 아래에 명시한 축별 초기 평균·std를 적용한다. PPO는 원본 Raw Action, ActionManager·Last Action·action-rate는 Clip된 raw 명령을 사용한다. 별도 Raw ID는 실행 Clip을 제거하고 Last Action에만 tanh를 적용한다. 나머지 PPO 하이퍼파라미터는 위와 같다.

## 파생 환경 비교와 실험 의도

아래 의도는 **검증하려는 가설**이며 학습 결과로 확인된 우월성을 뜻하지 않는다. 표에 없는 구성은 직접 부모에서 유지된다.

| 환경(접두사 Inspire-Sweep- 생략) | 직접 부모 | 무엇이 어떻게 바뀌는가 | 무엇을 테스트하기 위한 변경인가 |
| --- | --- | --- | --- |
| `Simple-v0` | 독립 베이스 | Relative-IK v0_2_2_4에서 상속 분리 후, 목표3cm 미만의 접촉 풀 카운트 추가 | 독립 실험 기준을 관리하며, 목표 도달 후 접촉을 놓아도 접촉 유지 보상이 사라지지 않도록 설정 |
| `Simple-Prof-v0` | Simple-v0 | Goal Distance: 최고 기록 개선100→현재 step의 접촉 조건부 접근120. 고정 지시 방향 이탈 비용−6 추가. 접촉 유지 카운트 보상 제거 | 교수님 제안에 따라 직접 미는 동안의 목표 접근과 방향 정렬이 접촉 카운트 중심 구성보다 의도한 sweeping을 유도하는지 비교 |
| `Simple-v1` | Simple-v0 | Reach30의 최고 기록 개선분→현재3D 중심–EEF 근접도 역수 보상. 기존 규모에 맞춰 보정 | 한 번 접근한 뒤 후퇴해도 다시 접근할 보상이 없는 문제를 줄이고, 움직이는 타겟 근처에 머물며 추종하도록 유도할 수 있는지 확인 |
| `Simple-Prof-v1` | Simple-Prof-v0 | Prof 보상은 유지하고 Reach만 Simple-v1 방식으로 교체 | 접촉 조건부 접근/방향 보상과 지속 근접 보상을 결합했을 때 추종·밀기 행동이 개선되는지 확인 |
| `Simple-Hard-v0` | Simple-v1 | 목표6–12cm→7–15cm 또는 방향별 최대 가능 거리. DeadZone curriculum 제거, 처음부터0도 | 접촉 유지 보상+v1 Reach 정책이 더 긴 이동과 Pull/Push 포함 전방향 과제를 초기부터 학습할 수 있는지 확인 |
| `Simple-Prof-Hard-v0` | Simple-Prof-v1 | Simple-Hard와 동일한 목표·DeadZone 변경 | 같은 어려운 목표 분포에서 Prof 보상 구성이 어떻게 작동하는지, Simple-Hard와 비교 |
| `Simple-Finger-v0` | Simple-v1 | 손 관측2→6D 실제 관절 위치, 손 액션2→6D 독립 절대 위치 제어. Last Action tanh 유지 | 압축된 전체 굽힘 대신 손가락별 자유도를 제공하면 접촉 자세 선택과 타겟 추종·밀기 행동이 개선되는지 비교 |
| `Simple-Finger-v0-Wrench` | Finger-v0 | AXIA80 센서 기준 힘·모멘트6축 명령·센서/손 Clip·Clip된 Last Action, 팔 속도 종료1rad/s 고정 | Test와 같은 종료 임계값에서 pose OSC와 wrench OSC의 접촉 조작 특성을 비교 |
| `Simple-Finger-v0-Test` | Finger-v0 | 팔 관절 절댓값 속도>1.0rad/s에서 실패 종료, 속도 종료 커리큘럼만 제거 | 기존 Finger-v0에서 고정 속도 종료 조건만 강화한 효과를 비교 |
| `Simple-Finger-v1` | Finger-v0 | 일반 Gaussian·축별 초기 분포, 실행 Clip·Clip된 Last Action, 팔 속도 비용−0.03과 속도 종료1rad/s 고정 | 과도한 순간 밀기를 줄이는 제어·학습 조건을 시험 |
| `Simple-Finger-v2` | Finger-v1 | 가까운 거리 개선을 강조하고, 목표2cm 안에서3초 유지 후 역방향 Reach로 전환 | 중심 정밀 접근과 충분한 체류를 달성한 뒤 손을 조금 후퇴시키는 행동을 시험 |
| `Simple-Semi-Prof-v0` | Finger-v1 | 현재 Reach 유지, 접촉 조건부 로그 Distance120, 멀어짐−31.128, 접촉 유지 삭제, 현재 목표 방향 대비3D 합력 정렬0.33 | 왕복 접근 보상 반복 수령을 막고 접촉을 통한 정밀 이동과 수평 방향 힘을 유도하는지 시험 |

Prof-v0/v1의 접근 보상과 방향 비용은 현재 타겟 접촉·EEF15cm 미만을 요구한다. 접촉 유지의2-of-3 이력을 사용하지 않는다. 방향 이탈 비용은 각 step의 XY 이동거리에서 초기 지시 방향 성분을 뺀 양으로, 측면·역방향 이동을 비용화한다. 접근은 과거 최고 기록을 넘지 않아도 이전 step보다 가까워지면 보상한다. 비접촉 동안의 이동은 나중에 재접촉할 때 소급 보상하지 않는다.

비교 실험에서는 Simple-v0↔v1 및 Prof-v0↔v1이 Reach 단독 변경이다. Simple-v0↔Prof-v0는 세 보상 변경의 묶음이며, v1↔Hard는 목표 거리와 방향 curriculum 두 변경의 묶음이다. 후자에서 관찰된 차이를 단일 요인의 효과로 단정하지 않는다. Simple-v1↔Finger-v0는 손 상태·제어 표현의 변경을 비교한다. Finger는 action-rate의 계수를 유지하지만 손 채널 수와 명령 단위가 달라지므로 실제 비용 규모까지 같다는 뜻은 아니다.

## 보상 차이

| 항목 | Simple-v0 | Simple-v1 | Prof-v0 | Prof-v1 |
| --- | --- | --- | --- | --- |
| Reach weight | 30 | 30 | 30 | 30 |
| Reach 함수 | `DexReachProgress` | `InverseDistanceReach` | `DexReachProgress` | `InverseDistanceReach` |
| Goal Distance | `DexPlanarGoalProgress`, 100 | 동일 | `ContactConditionedSweep`, approach, 120 | 동일 |
| 방향 이탈 | 없음 | 없음 | `ContactConditionedSweep`, direction, −6 | 동일 |
| 접촉 유지 | `GoalContactMaintenance`, 0.1 | 동일 | 없음 | 없음 |
| 목표에서 멀어짐 | `RelativeInverseDistance`, −25.94 | 동일 | 동일 | 동일 |

Simple의 접촉 유지 보상은 목표3cm 미만에서 무조건20이다. 그 밖에서는 기존과 같이 상한20, 인정 시+1, 불인정 시−2(최소0), 최종 불인정 step의 보상0이다. 기존2-of-3 접촉 인정과 초기 선반 표면 기준 EEF 높이15cm 미만 조건을 보존한다. 목표 내부 예외는 Simple-v1/Hard/Finger-v0/Finger-v1에도 상속된다. Finger-v2는 이3cm 예외를 삭제하고, 아래의 연속3초 게이트 달성 후에만 무조건 풀 카운트를 적용한다. Prof의 접근/방향 이탈은 현재 타겟 접촉·EEF 높이15cm 미만 조건을 사용한다.

v1 Reach는 현재 타겟의3D BBOX 중심과 EEF 프레임 사이 거리에서10cm를 뺀 값을0으로 하한 처리한다. 이 값을 `g`, 기존 reset 시 Reach 예산 거리를 `g0`, 에피소드 길이를 `T=10초`라 하면, weight 적용 전 보상 함수는 다음과 같다.

```math
r_{reach} = \frac{g_0}{T}\frac{0.1}{0.1 + g}
```

RewardManager의 policy dt 곱을 그대로 사용한다. 초기 `g0`는 기존 Reach reset 구현을 유지하므로 현재 BBOX 중심 거리와 기준이 다를 수 있다. 처음부터 기존 초기 거리 기준10cm 안이면 `g0=0`이고 해당 에피소드 Reach 보상도0인 기존 v0_2_2_6 동작을 보존한다. Holding·물체 가속도 보상/커리큘럼은 모든 버전에서 비활성이다.

## Hard-v0 공통 변경

2026-11-10 추가. Simple-Hard-v0는 Simple-v1, Simple-Prof-Hard-v0는 Simple-Prof-v1를 직접 상속한다. [개발·검증 기록](../logs/2026-11-10_sweep_simple_hard.md).

- 기존6–12cm 목표를7–15cm 목표로 확대한다. 방향은 전체360도 균등분포로 추출하며 Pull(+X), Push(−X)를 처음부터 포함한다.
- 해당 시작점·방향에서 타겟 전체가 선반 안전 영역 안에 머무는 최대 이동거리를 `L`이라 한다. `L≥15cm`면7–15cm 균등 추출, `L<15cm`면 `L`을 선택한다. `L<7cm`도 그대로 `L`이다. 짧은 방향을 버리거나 방향을 다시 추출하지 않는다.
- 타겟의 고정 yaw −90도와 스케일 반영 BBOX, 기존 선반 가장자리 여유2cm로 root 위치의 유효 사각형을 startup에 캐시한다. 실제 `L`은 무작위 시작점·연속 방향에 따라 달라지므로 reset에서 ray와 캐시된 경계의 교점을 닫힌 수식으로 한 번 산출한다. 후보 반복·사후 유효성 검사·추가 기하 스캔·목표 sampler의 GPU→CPU readback이 없다.
- `target_goal_direction_deadzone` curriculum을 `None`으로 제거하고, spawn의 `excluded_x_half_angle=0`으로 고정한다. 다른 보상/팔 종료 커리큘럼은 유지한다.
- 변경된 목표를 기존 RED 계산·장애물 배치·Warp IK·goal command 생성 전에 전달한다. 목표 거리 계산 외의 Fast reset 흐름은 그대로다. 부모의 보상·관측·제어·종료·메트릭·PPO 하이퍼파라미터를 유지한다.

## Finger-v0: 독립 손가락 제어

`Inspire-Sweep-Simple-Finger-v0`는 **Simple-v1 직접 상속**이다. 2차원 손 개방도 제어와 실제 핸드의 독립 구동6축 위치 제어를 비교한다. Hard 목표 분포는 적용하지 않는다. [개발·검증](../logs/2026-11-10_sweep_simple_finger.md).

| 항목 | Simple-v1 | Finger-v0 |
| --- | --- | --- |
| Hand Config | 실제12관절에서 추정한 개방도2D | mimic 제외 구동관절의 실제 `joint_pos`6D, rad, 정규화 없음 |
| Hand Action | 개방도2D, [0,1] | 독립6관절의 절대 목표 각도, rad; 아래 범위로 clamp |
| 순서 | 전체 굽힘·엄지 대립 | 엄지 굽힘 → 검지 → 중지 → 약지 → 소지 → 엄지 대립 |
| 전체 Action | 팔6 + 손2 = 8D | 팔6 + 손6 = 12D; 팔 OSC 동일 |
| Last Action | raw action의 tanh, 8D | raw action의 tanh, 12D; clamp 전 명령 기준 |
| Actor/Critic 원시 입력 | policy58 + obstacles64 = 122D | policy66 + obstacles64 = 130D |
| 장애물 압축 후 MLP 입력 | 74D | 82D; encoder64→16 및 hidden256/128/64 유지 |
| 손 리셋 명령 | 펼침 개방도1 | 펼침 목표0rad, Last Action도0 |
| 액션 변화 비용 | 팔6/손2 각각 raw 변화 제곱합 | 팔6/손6 각각 동일 제곱합·상한 없음·weight−0.03; 평균화/재가중 없음 |

모든 손 관절명은 오른손 자산의 기존 호환 이름 `inspire_left_`를 유지한다.

| 채널 | 관절명 suffix | 목표 범위(rad) |
| --- | --- | --- |
| 0 | `thumb_2_joint` | 0–0.5864 |
| 1 | `index_1_joint` | 0–1.4381 |
| 2 | `middle_1_joint` | 0–1.4381 |
| 3 | `ring_1_joint` | 0–1.4381 |
| 4 | `little_1_joint` | 0–1.4381 |
| 5 | `thumb_1_joint` | 0–1.1641 |

USD의12개 손 관절에는 native mimic 제약이 없으므로, follower 위치 목표를 원본 오른손 URDF 비율로 계산한다. 엄지3=엄지2×0.8024, 엄지4=엄지3×0.9487; 나머지 각 손가락2=해당 손가락1×1.0843. 이는 명령 목표 연결이며 물리적으로 측정된 관절값을 덮어쓰지 않는다. 관측에는6개 drive의 실제 위치만 제공한다.

`SweepSimpleFingerEnvCfg`는 Action/Observation과12D 대응 action-rate callable만 교체한다. `SweepSimpleFingerEnv`는 공통 runtime을 상속하고 부분 리셋한 행의 손 명령 이력을0으로 맞춘다. 그 외 Scene·스폰/Fast reset·Reach·목표 내부 풀 카운트·종료·커리큘럼·센서·물성·제어주기는 Simple-v1 그대로다. 손 stiffness1.2, damping0.06, effort10Nm, velocity1rad/s도 유지한다.

PPO 모델은 입력66D와 출력12D에 맞춘 `SweepSimpleFingerModel`을 사용한다. 입력/출력 차원이 바뀌므로 기존8D 액션 체크포인트를 그대로 resume할 수 없다. 학습 성공률과 실제 물리 추종은 미검증이다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Finger-v0 --headless
```

## Finger-v0-Wrench: 센서 프레임 Wrench OSC

`Inspire-Sweep-Simple-Finger-v0-Wrench`는 **Finger-v0 직접 상속**이며 센서 기준 팔 제어와 고정1rad/s 속도 종료를 적용한다. 참고 레포의 `SensorFrameWrenchAction`처럼 Isaac Lab의 `wrench_abs` OSC를 사용한다. 원 레포를 import하지 않고 활성 패키지 안에 필요한 모멘트 기준점 보정을 구현했다.

| 항목 | Finger-v0 | Finger-v0-Wrench |
| --- | --- | --- |
| 팔 액션6D | EEF 상대 위치·RPY 증분 | `[Fx, Fy, Fz, Mx, My, Mz]` 절대 목표 wrench |
| 액션 기준 | offset EEF 원점·축 | `Robot/axia80_link` 센서 원점·축, `body_offset=None` |
| 액션 스케일 | 위치0.03m, 회전0.15rad | 힘10N, 모멘트1N·m; 각각 raw 값에 곱함 |
| OSC target | `pose_rel` | `wrench_abs` |
| motion / wrench 제어 축 | motion6축 | wrench6축, motion0축 |
| 관성 분리 | 활성 | 비활성 |
| 중력 보상 / nullspace | 활성 / 없음 | 동일 |
| 내부 힘 피드백 | 사용하지 않음 | `contact_wrench_stiffness_task=None`; 측정 F/T를 오차로 되먹임하지 않음 |

정책 step 시작의 센서 자세로 wrench를 root 축으로 변환하며, 해당 명령을 decimation2의 물리 step 동안 유지한다. native OSC의 root 원점 모멘트 변환과 PhysX COM Jacobian 사이의 기준점 차이를 보정한다. 센서 원점 모멘트가 원치 않는 위치 의존 토크로 바뀌는 것을 방지하기 위한 처리다. 기존의 관절 effort 한계와 비유한 effort 방어는 유지한다. 참고 레포와 동일하게 센서 원점의 힘·모멘트 범위로 Raw 입력을 Clip한 뒤 scale과 모멘트 보정을 적용한다.

손6관절 절대 위치 제어·전체12D 액션·66+64D 관측 차원·기존 Gaussian/PPO·보상과 action-rate 계수·reset·나머지 종료·나머지 커리큘럼은 Finger-v0 그대로다. 후속 요청으로 팔과 손의 실행 Raw 입력을 Clip하고, Last Action의 tanh를 제거하여 Clip된 Raw 입력12D를 그대로 관측한다. **관측/보상의 EEF 프레임도 변경하지 않는다.** 따라서 기존 `wrist_wrench` 관측은 계속 EEF 원점·축으로 표현되며, 새 팔 액션의 센서 원점·축과 구분해야 한다. 제어 명령의 의미가 바뀌므로 동일 차원의 기존 pose 정책 checkpoint가 동일한 동작을 재현하는 것은 아니다.

### Wrench 실행 입력과 Last Action

| 채널 순서 | Raw 클리핑 범위 | Scale 적용 후 센서 원점 목표 |
| --- | --- | --- |
| Fx, Fy | 각각−20~20 | 각각−200~200N |
| Fz | −36~36 | −360~360N |
| Mx, My, Mz | 각각−8~8 | 각각−8~8N·m |
| 엄지 굽힘 | 0~0.5864rad | 동일 관절 목표 |
| 검지·중지·약지·소지 | 각각0~1.4381rad | 동일 관절 목표 |
| 엄지 대립 | 0~1.1641rad | 동일 관절 목표 |

팔은 참고 예제의 SI-200-8 범위와 같은 `(200,200,360,8,8,8)`을 wrench scale로 나눠 Raw 한계를 생성 시 캐시한다. 이는 목표 명령 제한이며 실제 접촉력의 상한을 보장하는 것은 아니다. 손은 현재 환경의 절대 관절 위치 단위를 유지하여 URDF의 최소0·각 최대값으로 제한하고 mimic 목표를 생성한다.

Last Action은 각 Action term이 수락한 **Clip 후·Scale 전** Raw 값이다. tanh나 정규화, 센서→COM 모멘트 보정은 관측에 적용하지 않는다. 예를 들어 Fx Raw100은 실행 시200N, Last Action에서는20이다. reset 후에는0이다. PPO와 ActionManager는 원본 샘플을 보존한다. 요청 범위가 제어 입력과 Last Action이므로 기존 action-rate 보상의 원본 Raw 차이 계산 및 계수는 유지한다. 이 보상까지 참고 레포와 동일하게 변경한 것은 아니다.

[클리핑 후속 변경·검증](../logs/2026-11-11_finger_wrench_action_clipping.md).

Finger-v0-Test와는 별도 자식이다. 후속 사용자 요청으로 기존4→2rad/s 일정을 제거하고 팔 속도 종료를 **1.0rad/s로 고정**했다. 팔 관절 하나라도 절댓값 속도가1.0rad/s를 초과하면 실패 종료한다. 정확히1.0rad/s는 이 조건으로 종료하지 않으며 손 관절은 제외한다. `arm_joint_velocity_threshold`만 비활성화하고 다른 커리큘럼은 유지한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Finger-v0-Wrench --headless
```

[설계 근거·전체 대조·검증](../logs/2026-11-11_finger_v0_wrench_osc.md).

## Finger-v0-Test: 고정 팔 속도 종료 실험

`Inspire-Sweep-Simple-Finger-v0-Test`는 **Finger-v0 직접 상속**이다. 팔 관절 중 하나라도 절댓값 속도가 **1.0rad/s를 초과**하면 실패 종료한다. 정확히1.0rad/s이면 이 조건으로 종료하지 않는다. 손 관절은 이 판정에 포함하지 않는다.

부모의 초기4rad/s·최저2rad/s 종료 임계값과 감소 커리큘럼을 대신하여 처음부터 끝까지1.0rad/s로 고정한다. `arm_joint_velocity_threshold` 커리큘럼만 제거하며, DeadZone과 보상 커리큘럼은 유지한다. 관측·6축 손 액션·Last Action tanh·팔 속도 비용−0.03·Gaussian 정책·물리 관절 제한·나머지 종료는 Finger-v0 그대로다. 이는 속도 초과를 사전에 차단하는 제어기 제한이 아니라, 관측된 팔 속도에 따른 에피소드 실패 조건이다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Finger-v0-Test --headless
```

[개발·부모 대조·검증](../logs/2026-11-11_finger_v0_test_velocity_termination.md).

## Finger-v1/v2: 출력 범위와 정밀 이동·후퇴

두 환경은 `Finger-v0 → Finger-v1 → Finger-v2` 순서로 직접 상속한다. 부모와 이전 Simple 환경은 보존한다. 관측66+64D, 액션12D, 손 구동관절 순서와 물리 자산은 동일하다.

### 버전별 핵심 비교

| 항목 | Finger-v0 | Finger-v1 | Finger-v2 |
| --- | --- | --- | --- |
| Last Action | raw 액션에 tanh | Clip 후 raw 액션, tanh 없음 | v1 유지 |
| 정책 출력 | Gaussian | 일반 Gaussian. 환경 입력에서 raw Clip | v1 유지 |
| 팔 관절 속도 비용 | −0.03 | −0.03 | v1 유지 |
| 팔 속도 종료 일정 | 부모 일정 | 1rad/s 고정, 관련 커리큘럼 없음 | v1 유지 |
| Goal Distance | 선형 최고 기록 개선 | v0 유지 | 가까울수록 민감한 로그 최고 기록 개선, 누적 곡선 면적 보정 |
| 접촉 무조건 풀 카운트 | 현재 목표 XY<3cm | v0 유지 | XY<2cm 연속3초 달성 후 에피소드 끝까지 |
| Reach 목표 | 현재 물체3D 중심, 최대 보상 반경10cm | v0 유지 | 게이트 후 고정 후퇴점으로 전환, 최대 보상 반경2cm |
| timeout 성공 | 종료 시 XY<3cm | v0 유지 | 해당 에피소드에서 게이트를 한 번이라도 달성 |

성공 조건은 모든 버전에서 동시 실패가 없다는 조건을 함께 요구한다. Finger-v2의 게이트는 성공 이력이며, 후퇴 완료 판정은 아니다.

### Finger-v1

| 항목 | 변경 |
| --- | --- |
| 정책 출력 | 일반 Gaussian Raw Action. PPO는 원본 샘플과 Gaussian log probability를 저장·계산. tanh/atanh 없음 |
| 초기 분포 | Arm 평균0 부근·Hand 평균관절중앙 부근. std: 병진0.2, 회전0.5rad, 손 관절 범위 폭/6. 마지막 Linear 가중치를 초기값의0.01배로 하여 평균의 초기 상태 의존성을 작게 설정 |
| Action 페널티 | 현재·직전 Clip된 raw 명령 차이 제곱합. 각 Arm/Hand weight−0.03·출력 상한 없음 |
| 병진 명령 | 각 축 raw±0.5로 Clip 후 scale0.03. 상대 목표는 각 축±1.5cm |
| 회전 명령 | 각 축 raw±π/2로 Clip 후 scale0.15. RPY 명령은 각 축±13.5도 |
| 손 명령 | URDF6개 drive 한계로 raw Clip. 최종 관절 목표 한계·mimic 매핑 유지 |
| 입력 경로 | runtime에서 ActionManager 이전에 Clip. Arm/Hand term의 방어 Clip 유지 |
| Last Action | Clip 후·Scale 전 raw 명령12D. tanh 없음 |
| 팔 관절 속도 비용 | `arm_joint_velocity`: −0.03, 함수·cap100 유지 |
| 속도 종료 |1rad/s 고정, arm_joint_velocity_threshold 커리큘럼 비활성 |
| 그 외 | 손 속도 비용−0.01, action-rate 비용, 물리 속도 제한 Arm3.14/Hand1rad/s와 OSC gains 등 보존 |

현재 원환경은 **일반 Gaussian 정책 + 실행 명령 Clip**이다. PPO 저장 액션과 log probability는 원본 Gaussian 샘플을 사용하며, tanh/atanh 정책 변환은 복원하지 않는다. 표준편차는 학습 가능한 log parameter의 exp이고, log probability·entropy·KL은 일반 Gaussian 계산이다. 초기 분포도 위 설정 그대로다. 관측 정규화는 없다.

원환경의 ActionManager에는 Clip된 명령을 전달한다. Last Action과 action-rate는 이 명령 이력을 사용한다. 손 목표의 URDF 처리, reset 손 명령0, OSC 토크 한계, NumericalPPO 수치 검사·업데이트 복구/중단은 유지한다.

원환경은 축별 `PolicyAction/clip_fraction/<axis>`, `PolicyAction/mean/<axis>`, `PolicyAction/std/<axis>`를 기록한다. Raw 파생 환경에는 실행 Clip이 없으므로 평균·std만 기록한다.

JIT/ONNX export 자체는 일반 Gaussian 평균인 Raw Action을 출력한다. 외부 소비자는 해당 ID의 제어·Last Action 처리 계약을 적용해야 한다. 기존 ID는 Clip 경로로 복원되어 직전 Gaussian Clip 버전의 체크포인트를 동일 ID로 play할 수 있다. 과거 tanh 변환 정책 checkpoint는 출력 의미가 달라 여전히 직접 로딩을 거부한다.

### Finger-v2

| 항목 | 변경 |
| --- | --- |
| Distance | 현재 타겟 root–목표의 노이즈 없는 GT XY 거리. 에피소드 최고 기록 개선에 로그 변환 적용, 중심0cm까지 계속 지급 |
| 크기 보정 | 초기 거리별로 누적 보상 곡선 아래 면적을 기존 선형 곡선과 일치시킴. weight100·epsilon1cm |
| 게이트 진입 | XY 거리 **2cm 미만**에서 연속3초. policy dt0.02에서150회 연속 표본.2cm 이상/비유한 거리는 달성 전 timer 초기화 |
| 게이트 유지 | 한 번 달성하면 해당 에피소드 끝까지 유지. 이후 이탈해도 해제하지 않음 |
| Reach 전환 | 게이트 전: 물체3D 중심의 기존10cm 최대 보상 구간. 게이트 후: 고정 후퇴 목표의 **3D 거리2cm 이내** 최대 보상 |
| 후퇴 목표 | 지정된 목표점에서 초기 물체 위치 방향으로 XY5cm 이동. Z는 초기 선반 윗면+8cm. reset 때 캐시 |
| Contact | 기존3cm 무조건 인정 삭제. 게이트 전 실제 접촉 카운트 규칙, 게이트 후 접촉/높이와 무관하게 count/reward20 |
| Success |10초 timeout에서 게이트 달성 여부로 판정. 동시 물체/선반/팔속도 실패 우선. 목표에서 이후 이탈해도 달성 이력은 유지 |

게이트는 reward/termination에서 공유하며 같은 policy step에는 한 번만 갱신한다. reset 시 선택한 환경의 타이머·게이트·후퇴 좌표를 초기화하고, 직전 에피소드 성공 집계를 먼저 완료한다. 게이트 순간에 조기 종료하지 않는다. success는 **후퇴 완료 여부를 요구하지 않으며**, 게이트 달성 후 다른 실패로 조기 종료한 에피소드는 기존 timeout 성공 집계에 포함하지 않는다.

초기 거리 `d0`, 현재까지 최소 거리 `b`, epsilon `e=0.01m`에 대해 weight 적용 전 누적 접근 보상은 다음이다.

```math
A=\frac{d_0^2}{2[d_0-e\log(1+d_0/e)]},\qquad
P(b)=A\log\frac{e+d_0}{e+b}
```

step 보상은 `100 × 새 P − 100 × 이전 P`이며 기존과 같이 내부에서 dt를 나누어 RewardManager의 dt 곱을 상쇄한다. 시작9cm에서는 중심 도달 총 보상13.92398, 기존9와 다르지만 곡선 면적은 양쪽40.5 reward·cm로 같다. 왕복 재접근은 최고 기록을 갱신하지 않으면 지급하지 않는다. `target_inverse_distance`의 선형 멀어짐 비용−25.94는 이번 요청에서 변경하지 않았다.

후퇴 Reach는 부모의 초기 Reach 예산·weight30·distance_scale0.1을 유지한다. 기존 초기 Reach 예산이0인 특수 에피소드에서는 후퇴 Reach도0이다. 게이트·후퇴 좌표·현재 물체 GT를 새 관측으로 추가하지 않는다. 따라서 입력은 기존 초기 물체 스냅샷·센서·로봇 상태 그대로이며, 후퇴 학습 성능은 실제 학습으로 확인해야 한다. Holding·가속도 보상이나 보상 커리큘럼을 복원하지 않았다. 목표3cm 점유 시간 metric과 목표 표시 반경은 그대로여서, v2의 success 의미와 구분해야 한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Finger-v1 --headless
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Finger-v2 --headless
```

v0와 v1은 차원이 같아도 Last Action 의미와 std 저장 parameter(scalar/log)가 달라 기존 v0 checkpoint의 무변환 resume을 지원하지 않는다. v1과 v2의 모델 구조는 같다. CPU 검증 범위와 GPU 미검증 사항은 [개발 로그](../logs/2026-11-11_sweep_simple_finger_v1_v2.md)를 따른다.

## Raw 파생 환경과 원환경 play

분리 목적은 기존 ID의 정책을 기존 제어/관측 조건으로 play하면서, Clip 제거 실험을 별도 학습·로그로 비교하기 위함이다. 각 Raw EnvCfg는 같은 버전의 원환경을 직접 상속한다. Raw-v2는 Raw-v1이 아니라 **Finger-v2**를 상속하여 후퇴 게이트·성공 판정을 보존한다.

| 항목 | 원환경3개 ID | 대응 Raw ID3개 |
| --- | --- | --- |
| Gaussian 정책·초기 분포 | 기존 값 | 동일 |
| PPO 저장/확률 | 원본 Raw Action | 동일 |
| 실행 액션 | 축별 Clip 후 Scale | 추가 raw Clip 없이 부모 Scale |
| Last Action | Clip 후 raw 값, tanh 없음 | 원본 Raw Action에 tanh |
| Action 변화 비용 | Clip 후 명령 차이 | Raw Action 차이; 기존 weight 유지·출력 상한 없음 |
| 팔 Joint Velocity 비용 | −0.03 | −0.03 |
| 속도 종료·커리큘럼 | 1rad/s 고정, 관련 커리큘럼 없음 | 부모와 동일 |
| 보상·성공·후퇴·힘 수집 | 각 원환경 계약 | 동일 |
| Semi-Prof Wrench5% 상한 | 제거됨 | 제거됨 |

`clip_raw_actions=True/False`로 runtime 진입 Clip 여부만 선택한다. Raw EnvCfg는 Finger-v0의 Action/Observation Cfg를 선택하여 term 내부 추가 Clip도 제거한다. 기존 손 관절 목표 URDF 한계와 OSC 토크 한계는 두 구성 모두 유지한다. 같은 runtime을 사용하므로 v2 gate reset과 Semi-Prof의 physics-step 힘 수집도 보존한다. 각 Raw PPO 설정은 해당 부모를 상속하고 실험명 및 Clip 지표 여부만 바꾼다.

**Gaussian Clip 정책의 제어/관측 방식을 유지하려면 기존 ID를 사용한다.** 단, 이번 직접 수정으로 종료는1rad/s 고정·비용은−0.03이므로 과거 학습 당시의 종료/보상 조건까지 재현하는 것은 아니다. checkpoint 경로는 실제 파일로 바꾼다.

```bash
python src/inspire_sweep_baseline/scripts/play.py --task Inspire-Sweep-Simple-Semi-Prof-v0 --checkpoint "/absolute/path/model_XXXX.pt" --num_envs 16
```

Finger 모델이면 같은 명령의 task를 `Inspire-Sweep-Simple-Finger-v1` 또는 `Inspire-Sweep-Simple-Finger-v2`로 지정한다. 새 실험은 해당 Raw ID로 `scripts/train.py`를 실행한다. 예:

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Semi-Prof-Raw-v0 --num_envs 2048 --headless
```

원환경/Raw 모델의 차원·Gaussian 파라미터 구조는 같지만 제어와 관측 의미가 다르므로 Raw ID로 원환경 정책을 평가하면 조건이 바뀐다. 기존 tanh 변환 정책의 checkpoint 거부는 유지한다. 사용자 실제 checkpoint의 GPU play는 이번 작업에서 실행하지 않았다. [검증 범위](../logs/2026-11-11_finger_raw_environment_split.md).

## Semi-Prof-v0: 접촉 조건부 정밀 이동과 힘 방향

`Inspire-Sweep-Simple-Semi-Prof-v0`는 **Finger-v1 직접 파생**이다. 과거 Prof의 함수를 그대로 재사용하는 대신, 접촉 중 목표 접근과 방향 정렬이라는 의도를 새 보상 구조로 시험한다. [방향 보상 최신 명세](../../01_plan/FORCE_DIRECTION_REWARD_PLAN.md) · [개발·전체 대조·검증](../logs/2026-11-11_sweep_simple_semi_prof.md).

| 항목 | 최종 구성 |
| --- | --- |
| 관측·제어 | Finger-v1 그대로: policy66+obstacles64, 액션12D(팔6+손6), 일반 Gaussian 정책·실행 Clip, Last Action은 Clip 후 raw 값 |
| 속도·커리큘럼 | 팔 속도 비용−0.03, 속도 종료1rad/s 고정(관련 커리큘럼 없음). DeadZone·나머지 보상 일정은 Finger-v1 유지 |
| Reach | Prof-v1과 동일한 `InverseDistanceReach`, weight30. 현재 물체3D BBOX 중심–EEF 거리10cm 이내 최대, 부모 초기 예산·시간 보정 유지. 후퇴 목표 전환 없음 |
| Distance | Finger-v2의 면적 보정 로그 최고 기록 개선, epsilon1cm, **weight120**. 현재 GT XY 거리로 중심0까지 개선 가능 |
| Distance 지급 조건 | 타겟의 핸드 필터별 법선력 크기 합≥0.01N인 policy sample이 최근3회 중2회 이상, **현재 EEF가 초기 선반 표면+15cm 미만**. 이력은 접촉 bool만 저장하고 유지 count는 없음 |
| 소급 지급 방지 | 비접촉·높이 불인정 step도 최고 기록 갱신. 당시 개선분은 소멸하며 나중에 재접촉하거나 높이를 낮춰도 지급하지 않음. 같은 기록까지 왕복하는 동안 추가 Distance 없음 |
| 접촉 유지 | `hand_contact=None`. 목표3cm 무조건 풀 카운트 및 Finger-v2 체류 게이트 모두 없음 |
| 멀어짐 | 기존 `RelativeInverseDistance` 유지, **weight−31.128**(−25.94의1.2배). 접촉과 무관하게 직전 step보다 증가한 XY 거리 비용 |
| 방향 | 기존 Prof의 이동 방향 이탈 비용 대신 **`force_direction`, weight0.33**. 현재 타겟→목표의 평면 방향(Z=0)과 핸드가 타겟에 가하는 **3D 합력**의 각도를 비교 |
| 방향 유효 조건 | 해당 policy step 안에 실제 접촉 존재, 유한하고 신선한 힘 데이터, 평균 합력의 **수평 크기≥1N**. 속도·진행량·EEF 높이 조건 없음 |
| 근접 방향 예외 | 현재 목표 XY 거리 **1cm 미만**이면 방향 원점수1. 실제 접촉·최소 힘 조건은 계속 필요.1cm 이상으로 나가면 즉시 각도 계산 복귀.3cm 진입 후 영구 비활성화는 삭제 |
| 종료·성공 | Finger-v1 그대로:10초 timeout 시 XY<3cm이고 동시 실패가 없으면 success.1cm 방향 예외는 성공 반경 변경이 아님 |

힘은 기존 타겟 보고 body의 핸드 필터에서 얻는 법선력과 마찰력을 물체 쪽 부호로 합산한다. 선반 반력·중력·다른 물체 힘은 제외한다. policy step 안의 두 physics substep 벡터를 먼저 평균하고 각도를 계산한다. 타겟 위치는 policy step 마지막 현재 root 위치를 사용하며, 힘과 기준 방향을 초기 선반 좌표계에서 비교한다. 기준 벡터의 Z만0으로 만들고 **힘의 Z는 유지**한다.

1cm 밖의 원점수는 `max(0, 1 − angle/(π/2))²`이며90도 이상0이다. 목표 수평 방향 성분과 수직 성분의 크기가 같으면45도이므로 점수0.25이고, 같은 수평 힘에 수직 힘이 추가될수록 점수가 감소한다. 다만 **1cm 미만 예외 안에서는 수직 힘도 각도 평가를 우회**한다. 이 항은 힘 크기나 접촉 모멘트를 직접 최소화하지 않으며, 기존 물체 tilt 비용은 유지한다.

가중치0.33은 보상 비율을 강제로 제한하지 않는다. 초기9cm에서3cm까지 접촉하며2초 동안 수평으로 정확히 미는 비교 조건에서 Distance 약6.65, 방향 약0.66으로10% 수준이 된다. 이때의3cm/s는 가중치 산정 기준일 뿐 **실행 조건이 아니다**. 정체 중에도 유효한 힘 방향이면 보상하고,1cm 미만에서도 접촉·힘 조건이 유효하면 계속 지급한다. 최종 사용자 변경으로3cm 종료 조건이 없어졌으므로 전체 에피소드의 비율은 체류 시간에 따라 달라진다.

2026-11-11 후속 수정: 사용자 지시에 따라 Semi-Prof의 `wrench_change`에서 **양의 보상 연동5% 상한을 제거**했다(`max_positive_fraction=None`). 양의 보상이0이어도 실제 Wrench 변화에 따른 비용이 발생하며, 다른 보상의 계산 순서에 의존하지 않는다. 방향 보상을 앞으로 이동하는 임시 대응은 폐기했다. Wrench 자체의 변화량 함수·가중치·일정은 유지한다. 방향 보상의 약10% 수준도 강제 비율이 아니라 기존 고정 가중치0.33의 선정 근거다. [중대 이슈 후속 기록](../logs/2026-11-11_semi_prof_reward_order_incident.md).

runtime은 부모 `step`의 순서를 보존하며 해당 호출 동안 scene update 직후에만 힘을 수집한다. episode reset은 선택된 환경의 힘 누적값·접촉 이력을 비우고, 다음 policy step 시작에 전체 힘 누적값을 다시 비운다. 관측·센서 구성·Fast reset 기하·물리 자산은 변경하지 않았다. 추가 힘 읽기/집계에 따른 Collection Time 영향과 학습 성능은 GPU에서 미검증이다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-Semi-Prof-v0 --headless
```

로그 실험명은 `inspire_sweep_simple_semi_prof_v0`다. PPO 모델·분포·하이퍼파라미터는 Finger-v1과 같으며 실제 학습 체크포인트 전이는 검증하지 않았다.

## 공통 보존 계약

- physics dt0.01초, decimation2, policy dt0.02초, timeout10초, 기본2,048환경.
- 타겟 cylinder1개·물리 장애물16개 고정 roster, 활성 장애물0–6 균등 추첨, 관측 슬롯16개.
- 외접원 기반 RED/WHITE, 간격1cm, 안전 셀5mm, 기존 Warp IK 리셋과 시드 유지. GRAY 배치 없음. 호환 필드는 초기 구성 후 `None`으로 남는다.
- 센서·물리 관절 제한·자산·마찰/질량 설정 유지. pose OSC의 gains는 유지하며, Finger-v0-Wrench만 motion 제어를 사용하지 않는 센서 기준 wrench OSC로 변경한다. Finger-v0-Test와 Finger-v0-Wrench는 팔 속도 종료를1rad/s로 고정한다. Finger-v0는 손 관측·제어와 차원을 변경하고, Finger-v1/v2는 Gaussian 초기 분포·실행 Clip·고정1rad/s 종료를 사용한다. Raw ID는 Clip 제거·Last Action tanh를 적용하며 팔 비용은 원환경과 같은−0.03이다. 속도 종료 임계값은 물리 관절 속도 제한과 별개다.
- 기본은 목표 XY 거리3cm 미만이고 동시 실패가 없는10초 timeout을 success로 기록한다. Finger-v2와 이를 직접 상속하는 Finger-Raw-v2는 위 게이트 달성 이력으로 거리 조건을 대체한다. timeout과 success는 중첩되는 truncation 항목이며 기존 bootstrap 계약을 유지한다.
- 최근 완료 에피소드10,000개(조기실패 포함) 안의 timeout/success count와 rate 유지. 같은 step 완료의 순서는 env ID 오름차순.
- 물체 스폰 영역 시각화는2026-11-11 전체 삭제했다. Simple 베이스와 과거 Relative-IK v0_2_2_4의 marker·설정·표시 전용 계산·train/play 연결을 제거했으며, 실제 RED/WHITE 배치 계산은 유지한다. [삭제 기록](../logs/2026-11-11_remove_spawn_region_visualization.md).
- 나머지 보상, term 순서, 파라미터, 커리큘럼 일정, PPO 설정은 대응하는 기존 버전과 같다. Hard는 위 목표 이벤트와 DeadZone 변경, Finger는 각 버전 절에 명시한 제어·보상·종료 변경이 예외다. Semi-Prof는 Finger-v1을 기준으로 위 보상 변경과 힘 수집 경로가 추가되며, Wrench의 양의 보상 비율 상한은 적용하지 않는다. task ID·구성 클래스 이름·로그 실험명은 새 이름이다.

## 파일과 실행

활성 패키지 `src/inspire_sweep_baseline/inspire_sweep_baseline` 기준:

- `envs/sweep_simple_envs.py`: 열다섯 개 EnvCfg 조합.
- `runtime/sweep_simple.py`: 독립 런타임 및 최근 에피소드 통계.
- `assets/scenes/sweep_simple.py`: 독립 씬 구성.
- `mdp/{actions,commands,observations,events,rewards,curricula,terminations}/sweep_simple.py`: 역할별 구성.
- `mdp/common/sweep_simple.py`, `mdp/event_functions/sweep_simple.py`: Hard 목표 도메인 캐시와 startup 연결.
- `assets/hand_kinematics.py`: Finger의6개 drive 순서·관절 한계·mimic 비율.
- `mdp/action_functions/sweep_simple.py`, `mdp/observation_functions/sweep_simple.py`: Finger의 독립 위치 제어·실제 관절 위치 관측.
- `agent/sweep_simple_models.py`: Finger의66D 직접 관측과64D 장애물 입력을 받는 모델.
- `mdp/common/sweep_simple_force.py`: Semi-Prof의 타겟 법선·마찰 집계와 physics substep 평균.
- `agent/sweep_simple_distributions.py`: v1/v2·Semi-Prof 일반 Gaussian 초기화·액션 진단·구 tanh checkpoint 거부.
- `mdp/action_functions/sweep_simple_osc.py`: v1/v2 OSC 입력 방어와 Wrench의 센서 원점·COM 모멘트 보정.
- `mdp/termination_functions/sweep_simple.py`: v2 성공 판정. Test의 고정 임계값과 커리큘럼 제거는 각각 `mdp/terminations/sweep_simple.py`, `mdp/curricula/sweep_simple.py`에 정의한다.
- `agent/sweep_simple_ppo_cfg.py`: 독립 PPO 기본과 열다섯 개 로그 실험명.
- `__init__.py`: 열다섯 개 Gym ID 등록.

workspace root에서 기존 Isaac Lab Python 환경을 활성화한 뒤 실행한다.

```bash
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Simple-v0 --headless
```

나머지 버전은 위 표의 task ID로 교체한다. Finger-v0는 관측·액션 차원이 달라 기존8D 액션 체크포인트를 직접 재개할 수 없다. Finger-v0→v1도 정책 분포와 저장 parameter가 달라 무변환 resume을 지원하지 않는다. Finger-v1/v2의 모델 구조는 동일하지만 실제 학습 체크포인트 전이는 미검증이다.

Finger-v0 도입 당시 CPU 검사는86개 통과·2개 skip이었다([당시 검증](../logs/2026-11-10_sweep_simple_finger.md#검증)). Finger-v1/v2 구현 후 기존 환경 회귀를 포함한 당시 CPU 검사는 **110개 통과·2개 skip**이었다([당시 검증](../logs/2026-11-11_sweep_simple_finger_v1_v2.md#검증)). GPU 드라이버 문제로 PhysX·GPU rollout·렌더링·학습 성능은 미검증이다.

Semi-Prof-v0 추가 후 기존 계열 회귀를 포함한 CPU 검사는 **119개 통과·2개 skip**이다. 실제 GPU/PhysX·Collection Time·학습 효과는 미검증이다. [Semi-Prof 검증 범위](../logs/2026-11-11_sweep_simple_semi_prof.md#검증).

최신 추가 환경 검증은 Finger-v0-Test **65개 통과**, Finger-v0-Wrench 추가 후 관련 회귀 **67개 통과**다. 검사 대상 파일이 달라 이전110/119개 결과와 총수를 직접 비교하지 않는다. [Test 검증](../logs/2026-11-11_finger_v0_test_velocity_termination.md#최종-대조와-검증) · [Wrench 검증](../logs/2026-11-11_finger_v0_wrench_osc.md#검증). 이번 최종 문서 갱신에서는 환경 코드를 수정하거나 학습을 재실행하지 않았다.
