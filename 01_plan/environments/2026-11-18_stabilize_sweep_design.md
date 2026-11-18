# 독립 Stabilize → Sweep 환경 설계 인터뷰

2026-11-18. 상태: **Q1–Q33 답변 반영 완료**. 최종 계약은 [통합 명세](2026-11-18_stabilize_sweep_spec.md)에 모았다. 이 문서는 질문과 정정 이력이며 앞선 라운드의 후속 결정 표시는 이후 답변으로 해결되었다. 기존 valid+XYZ 형식을 보존하고 XYZ의 내용만 대표 표면점으로 변경한다. 신규 weight는 사용자 요청으로 유보했다. Q34에서 통합 설계와 Gym ID `Inspire-Stabilize-Sweep-v0`의 공유 이해를 사용자가 최종 확정했다. 설계 인터뷰는 완료했으며 구현·등록·학습은 시작하지 않는다. `grill-with-docs`의 `grilling` 및 `domain-modeling` 절차를 적용한다.

## 사용자 요구와 기준

활성 패키지 `src/inspire_sweep_baseline` 내부에 기존 환경 Cfg 상속을 끊은 새 환경을 설계한다. 기능 참고 기준은 `Inspire-Sweep-Simple-Finger-ForceDirection-v0`다. UR5e + Axia80-M8 + RH56E2, F/T·촉각 피드백을 유지한다. 초기 손을 타겟 옆에 IK로 배치하고 XY·yaw 오차를 준다. 로봇 진입 전 대표 표면점을 EEF 기준으로 관측한다. Reaching 삭제, Stabilize 이후 Sweep gate, 거리 감소량·접촉 카운트·힘 방향의 곱 보상, 거리 증가 비용 1.5배, 기존 기타 비용·종료·Runner clip 유지, Deadzone curriculum 삭제를 요청했다.

첨부 후반 제안식의 Reaching은 앞부분 삭제 지시와 충돌했으나 Q2 답변으로 삭제를 확정했다. ‘5시로 밀 때 1시에 손’은 사용자가 11시의 오기였다고 정정했다. ‘로봇 공간도 스폰 가능 영역’은 Q7 답변으로 밀기 위한 최소 공간과 초기 로봇 점유 공간을 장애물 배치 금지영역으로 확보한다는 뜻으로 확정했다.

## 현재 코드로 확인한 사실

경로는 workspace 루트 기준이다. 정적 독서 결과이며 신규 실행 검증 결과가 아니다.

| 항목 | 실제 코드와 설계 영향 |
| --- | --- |
| 등록·Cfg | `inspire_sweep_baseline/__init__.py:1505`, `envs/sweep_simple_envs.py:164` 부근. ForceDirection → Finger-v0-Test → Finger → Simple-v1 → Simple-v0. 새 환경에서 어느 수준까지 독립 선언할지 결정 필요 |
| runtime | `runtime/sweep_simple.py`의 `SweepSimpleFingerForceDirectionEnv`는 Finger runtime을 상속하고 physics substep마다 타겟 접촉력을 수집 |
| 정책 주기 | Simple Cfg의 physics dt 0.01초, decimation 2, episode 10초. 새 환경도 Stabilize 포함 총10초로 확정 |
| 제어·PPO | 손6축을 포함한 총12D, Runner clip ±π/2. `agent/sweep_simple_ppo_cfg.py`는 Actor/Critic 모두 policy·obstacles 입력을 사용 |
| 기존 관측 | `mdp/observations/sweep_simple.py`는 초기 타겟·장애물 위치, 현재 자기 상태·촉각·wrench·Last Action. Critic 전용 현재 타겟 GT 입력 없음 |
| 기존 거리 개선 | `mdp/reward_functions/dex_rewards.py:37`의 `DexPlanarGoalProgress`는 역대 최선 개선분만 반환. 이전 step 대비 감소량과 다름. 내부에서 step_dt로 나누어 Manager dt와 상쇄 |
| 기존 멀어짐 | `mdp/reward_functions/wrench_refactor.py:293`의 `RelativeInverseDistance`는 이전 step 대비 XY 거리 증가량/step_dt. 기준 weight −25.94, 1.5배는 −38.91 |
| 기존 접촉 카운트 | `TargetContactDecayMaintenance`는 최근3회 중2회 인정, +1/불인정−2, 0–20. 동시 접촉 지점 수가 아님. ForceDirection은 목표1cm 내부에서 실제 접촉 없이20 지급하는 별도 예외가 있음 |
| 방향 | `mdp/reward_functions/sweep_simple.py:173`의 `cosine_force_direction`은 현재 타겟→목표 XY 방향과 3D 합력의 signed cosine. 실제 접촉·수평 합력1N 필요, 목표1cm 미만은 방향점수1 |
| 힘·모멘트 | `mdp/common/sweep_simple_force.py`는 타겟–손 필터의 법선·마찰 합력을 physics step에서 수집해 평균. 접촉점별 모멘트와 개별 하중 크기 합은 현재 출력에 없음. 손목 F/T만으로 손–타겟 전용 모멘트를 대체할 수 있다고 전제하지 않음 |
| 기타 비용 | Action 항은 action 자체의 L2가 아니라 current−previous의 제곱합. `WrenchMagnitudeChangePenalty`는 충격량 적분이 아니라 힘·모멘트 크기의 변화이며 양의 누적 보상5% 예산에 연동. 기존 함수·계수·일정 유지 범위 확인 필요 |
| 종료 | `mdp/terminations/sweep_simple.py`: 물체 낙하/기울기, 선반 실패, 팔1rad/s 초과, timeout 및 timeout 성공. 목표 반경3cm |
| Deadzone | curriculum 삭제만 하면 reset 인자의 30도 제외각이 남을 수 있음. `mdp/events/sweep_simple.py`의 `excluded_x_half_angle`도 함께 결정 필요 |
| reset | `mdp/event_functions/wrench_refactor_relative_ik_test.py:232`는 layout을 먼저 추출하고 손 목표 위치를 정함. IK 방향은 default_quat이며 새 목표 방향 yaw 정렬이 아님. IK 실패 시 예외 |
| 대표점 | `src/surface_point/surface_point/mesh.py:73`의 `MeshObserver`: 실제 시각 메쉬, 정면 직교 광선, 연결 가시 조각별 mask 중심에 가장 가까운 내부 픽셀의 표면 교점. 원래 중심/질량중심이 아님 |
| 벤치 통합 한계 | GPU ray 결과를 numpy로 읽고 SciPy 연결요소로 처리. 현재 API는 한 장면 기준이며 수천 환경 배치 reset 성능을 보장하지 않음. 실제 RGB-D noise·segmentation 오류·원근 관측은 별도 설계 대상 |

## 결정 트리와 첫 라운드

다음 Q1–Q7은 모두 사용자가 수용했다. Q5는 현실에서 동일 물체로 판단할 근거가 부족하므로 분리된 조각을 다른 관측 물체로 취급한다는 근거를 명시했다. Q6는 정확한 반대편 기하, Q7은 최소 밀기 공간과 현재 로봇 점유 공간의 배치 금지를 재확인했다.

| 질문 | 확정 결정 | 후속 하위 결정 |
| --- | --- | --- |
| Q1 독립성 경계 | EnvCfg/Scene/MDP/PPO Cfg 및 runtime을 기존 환경 상속 없이 선언, Isaac Lab 기반·자산·검증된 계산 함수 재사용 허용 | 파일별 책임, 공유 함수 격리, 새 ID·검증 대조표 |
| Q2 단계 구조 | 하나의 정책이 Stabilize→Sweep 수행, 조건 연속 충족 후 단방향 전환, 단계 관측 제공. Reach 제거, setup·초기 이동/회전 비용은 Stabilize 전용 | gate 임계값·유지 시간·전환 step·복귀·단계별 시간/성공/보상과 squeeze 적용 범위 |
| Q3 초기 관측 계약 | 진입 전 표면점은 world 고정, 매 step 현재 EEF로 좌표변환. 움직인 물체를 GT로 추적하지 않음. Actor/Critic 동일 시각 정보 | 목표점 의미, 정책 정보와 reward GT 경계, noise·padding·마스크·관측 차원 |
| Q4 관측 생성 방식 | 첫 환경은 surface_point의 실제 메쉬 직교 광선 방식을 시각 센서의 기하 대용으로 사용 | 카메라 영역·해상도·노출 필터·batch reset·성능 기준·실제 센서와의 차이 |
| Q5 관측 단위 | 기존 용어집대로 가시 연결 조각마다 독립 대표점, 같은 물체의 조각을 GT ID로 합치지 않음 | 타겟 조각 지정, 가림/미검출, 슬롯 초과·정렬, 실제 물체와 관측 물체 구분 |
| Q6 손 시작 기하 | 목표 밀기 방향 정반대편에 손, 손바닥 법선은 밀기 방향. 타겟 표면과 마주보는 손 표면 간격 약5cm | 중심/COM/관측점 기준, 손바닥 축·roll/pitch·높이, XY/yaw 범위·분포, 충돌 검사·재추출 |
| Q7 스폰 공간 | sweep 통로와 초기 로봇 점유 공간을 장애물 금지영역으로 예약하고 나머지 선반에 장애물 배치 | 통로 폭, 로봇 링크별 점유 근사·안전거리, 이동 경로 예약 여부·밀도·실패 처리 |

## 두 번째 라운드 — 사용자 답변 반영

| 질문 | 확정 내용 및 명료화 사항 | 후속 의존 결정 |
| --- | --- | --- |
| Q8 과업 기준·GT 경계 | 정책 입력은 EEF 기준 표면점, 실제 위치 계산은 Centroid. Q16으로 형상 중심을 의미함을 확정. 모멘트 원점은 별도 실제 COM. 현재 GT 물체 상태를 정책에 넣지 않음 | 목표점 생성·표현, IK 기준점·충돌 검사, 접촉 하중 계측 |
| Q9 Gate 판정 | 접촉·작은 목표 힘·방향·각 모멘트·초기 위치/자세 유지·현재 선속도/각속도를 각각 만족해야 함. setup 종합 점수 하나로 통과하지 않음. 모든 조건 연속0.3초, 불만족 시 유지 시간0 | 물리 임계값, 테스트 힘과 마찰·질량, 계측 집계, 전환 시점 |
| Q10 접촉 카운트 | 기존 시간 누적0–20와2-of-3/+1/−2 유지, 곱셈에는 count/20. 불인정 step 계수0, 실제 접촉 없는 목표 내부 full-count 예외 제거. Gate 통과 시 이력과 count를0으로 시작. 사용자는 정규화가 weight의20배 재매개화와 동등함을 지적했고 weight 결정은 추후로 유보 | positive weight·왕복 방지 조건, 접촉 threshold·높이 조건과 gate의 관계 |
| Q11 방향 인자 | 현재 타겟→목표 XY 방향과3D 손→타겟 합력 cosine을0–1로 제한. 실제 접촉·유효 힘 필요. 기존 목표1cm 내부 방향점수1 예외 제거, 목표와 정확히 일치해 방향 미정이면 인자0 | 최소 힘 threshold, near-goal 수치 안정성, signed cosine 대안·거리 보상 계수 |
| Q12 시간·성공 | 기존 총10초 안에 Stabilize 포함. timeout 성공에는 기존 위치/실패 조건에 Gate 통과를 추가. Gate 미통과는 timeout 실패, 도달 즉시 조기 성공 종료 없음 | 성공 경계 < 또는 <=, phase 계측, 시간 제한·bootstrap |
| Q13 압착 비용 | 단계와 무관한 공통 압착 비용으로 적용. 별도의 단계별 압착 구조를 도입하지 않음. 초기 위치/자세 이탈 비용만 Stabilize 전용 | 공통 S_max·계수 및 기존 tilt 비용과 중복 |
| Q14 Deadzone·목표 | 0도 권고를 거부. Push/Pull 구현이 현 단계에서 애매하므로 기존30도 제외각을 고정하고 해당 curriculum만 삭제. 목표 거리6–12cm는 기존 계약 유지 | 허용 방향 안의 IK/배치 실패 재시도·분포·장애물 통로 |
| Q15 기타 비용 보존 | 기존 action-rate L2·관절속도·wrench 크기 변화 비용과 계수/일정은 유지하되 양의 보상 연동5% 상한은 제거. 사용자 판단으로 기존5% 상한 설계가 잘못됨. 새 충격량 비용 추가 안 함. 기존 환경 수정 권한으로 확대하지 않음 | 새 환경에서5% 예산·보상 순서 의존 제거 확인, 물리 raw cap은 유지 |

Q8의 실제 타겟과 관측의 정보 경계 및 Q16 기준점은 확정됐다. weight는 사용자 요청에 따라 추후 조정한다. 첨부의 step 차분 요구를 최단 거리 갱신 방식으로 임의 변경하지 않는다. 남은 노이즈·빈 관측 슬롯과 안정화 수치 등을 후속 설계에서 확정한다.

코드 추가 확인: `success_at_timeout`은 현재 실제로 `distance < .03`이다. 개발 지침의 일반 `<=` 계약과 차이가 있으므로 종료를 유지한다는 표현만으로 새 환경의 경계를 자동 확정하지 않는다. 현재 Simple Scene의 실제 타겟은 cylinder 고정이며, 별도 요청 없이 타겟 종류 확장을 전제하지 않는다.

## 세 번째 라운드 — 사용자 답변 반영

| 질문 | 확정 내용·정정 | 의존 후속 사항 |
| --- | --- | --- |
| Q16 Centroid 정의 | 타겟 위치·거리·이동량은 실제 형상 중심, 모멘트는 실제 COM 기준으로 구분. 현재 cylinder에서는 형상 중심은 밑면에서0.5H, COM 설정은0.2H, root는 밑면 중심 | IK 높이·기준점, goal 생성, 이동 허용량·접촉 모멘트 검증 |
| Q17 관측 타겟 지정 | 타겟 물체는 면적 최대 유효 조각 하나만 사용. 현실에서도 하나만 사용할 것이므로 다른 타겟 조각을 장애물 목록으로 재사용하지 않음. 비타겟 물체의 분리 조각은 독립 관측 유지 | 타겟 미검출 재추출·배치 편향 |
| Q18 관측 입력 형식 | 모든 물체 위치의 XYZ를 EEF 기준 대표 표면점으로 변경. Q23 최신 정정으로 기존 valid+XYZ 형식은 유지한다. 앞서 valid 제거로 해석한 것은 철회. 실제 중심·크기·원본ID·대응 정보 제외 | 기존16슬롯·64D 인코더 유지, 단계 비트·기존 자기 상태 |
| Q19 시각 필터·오차 | 20% 상대 노출 필터 제거 권고를 거부. 그 정도도 노출되지 않으면 현실 모델이 인식하지 못할 것이라는 가정으로 유지. 기존1mm·mask중심·최소폭2cm도 보존. 노이즈 추가 여부는 답변에서 명시하지 않아Q24로 분리 | GT 전체폭 기반 인식가능성 근사와 정책 정보의 구분, Q24 시각 오차 |
| Q20 초기 자세 오차 | 명목 표면 간격5cm에 선반 X/Y 각각 독립 균등±1cm, yaw 독립 균등±10도. Z/roll/pitch 랜덤화 없음, 기존 손6축 초기0rad 유지. 최종 자세 비중첩·관절/IK 유효성 검사 | 명목 높이는Q16 뒤 결정, yaw 회전 후 손 표면거리·안전간격 검사 |
| Q21 최소 배치 금지영역 | 사용자 정정: 최소 공간은 기존RED ZONE 그대로다. 타겟 직선 이동 통로로 축소하지 않음. 기존RED와 현재 로봇 팔 점유 공간을 합집합으로 처리. 기존Q7의 손 포함 로봇 비중첩 요구도 보존 | 추가 로봇 공간의충돌형상·안전여유, shelf/robot self-collision, 기존RED불변 대조 |
| Q22 Gate·reward 시간 집계 | Gate는100Hz physics 샘플마다 검사해30회 연속 통과. reward는 각 substep의 비선형 setup·squeeze 점수를 계산한 뒤50Hz policy step에서 평균. 반대 모멘트/압착이 평균 합력에서 상쇄되는 오류 방지. 전환은 통과를 확인한 policy step 다음부터 | 전환 step의 old-phase 보상·현재 observation·거리 이력 reset, physics hook와 부분reset |

### 이번 추가 코드 사실

`assets/mass_cylinder.py`는 밑면 root와 하부 질량 편중을 명시한다. `bottom_heavy_mass_properties`는 하부20% 높이에80% 질량, 나머지80% 높이에20% 질량이 있어 COM 높이가0.2H다. nominal H=10cm이면 root0cm·형상 중심5cm·COM2cm이며, 실제 root scale과 PhysX COM readback은 구현 검증에서 대조해야 한다. 직립 상태 XY가 같아도 기울어진 상태에서는 세 기준점이 달라진다.

`initialize_physics`의 질량은 startup uniform0.345–0.750kg이다. 정적 마찰 pool 범위는 바닥0.213–0.417, 물체0.235–0.395, 손0.295–0.875(유한 bucket의 midpoint 사용)이며 startup 이후 reset마다 바꾸지 않는다. 이는 테스트 힘을 보장하는 물리 검증 결과가 아니며, 접촉 형상·모멘트·재질 결합을 포함한 타당성 검사가 별도 필요하다.

`CircleResetLayout.red_distance`는 시작→목표 구간을 선반 앞쪽+X까지 확장하므로 순수 타겟 이동 통로보다 넓다. `surface_point.MeshObserver.observe`의 상대 노출20%는 원본 메쉬 전체 폭을 사용한다. 이 사실을 설명한 뒤 변경을 제안했으나 사용자는 두 기존 계약을 모두 유지하도록 정정했다.

## 네 번째 라운드 — 사용자 답변 반영

| 질문 | 확정 내용·정정 | 비고 |
| --- | --- | --- |
| Q23 XYZ 슬롯 | 사용자 정정: 기존 방식이 맞으며 XYZ가 Centroid 대신 관측 가능한 대표점이라는 의미. valid+XYZ4×16=64D 및64→32→16 인코더를 유지.48D 제안 철회. valid0슬롯은 기존대로0 처리 | 별도 valid 제거·네트워크 개편을 하지 않음. 초과/미검출 처리는Q30 |
| Q24 시각 오차 | 첫 버전은 대표점에 추가 좌표 noise·visibility flip·swap을 넣지 않음. 메쉬 가림과 확정 노출 필터만 적용. 기존 F/T·촉각 noise 유지 | 사용자 수용 |
| Q25 명목손높이 | 기존reset의명목EEF높이(default_local Z +0.01m)와roll/pitch유지. 확정대로Zjitter없음. 형상중심/COM높이에EEF를자동배치하지않으며정책이접촉자세를조정 | 손전체의shelf간섭검사필수. 물체기준높이설계를택하면재검토 |
| Q26 Stabilize 초기 수치 | Ftest0.5N, sigmaF0.2N, sigma_perp0.2N, sigma_tau_z0.005Nm, sigma_tau_xy0.01Nm, delta_p3mm(형상중심3D), delta_R3deg(SO3), gate선속도≤5mm/s·각속도≤0.05rad/s, 공통Smax5N. Gate는각force/moment오차≤해당sigma와변위·회전·속도·S조건을모두만족. 초기anchor는episode시작상태 | 물리검증전권고초기값. 모든질량·마찰·형상에서달성가능하다는주장아님. reward weight는별도유보 |
| Q27 Sweep 기존접촉조건 | Sweep방향인자최소수평합력1N, 접촉유지의EEF높이<선반+12cm·접촉0.01N기준유지. setup의0.5N테스트힘과분리 | 실제접촉없는목표1cm예외는삭제확정. 작은힘으로움직여도1N미만이면positive Sweep0 |
| Q28 reset 실패처리 | 사용자 요청: 장애물 수 감축을 고려. 반복 재추출로 Reset/Iteration time이 과도해지는 것을 피해야 함.32회 고정 재추출·감축 금지 권고 철회 | 구체적 감축 알고리즘은Q30, 장애물 감축으로 해결할 수 없는 IK는Q33 |
| Q29 단계경계의거리이력 | Stabilize의 거리 감소·멀어짐 비활성 확정. Sweep 진입 이력에서 시작해 소급 지급 없음. 단, Gate 시 setup 보상이0이 되어 정책이 통과 직전에서 계속 보상을 받는 유인을 방지하라고 명시 | 후속 Q31에서 Gate 이후 완료 보상 확정. 기존 단방향 Gate 유지 |

기존보존요청에따라새비용추가없이기존tilt비용은양단계에서유지한다. 성공경계는현재코드의`distance < .03`를유지하는것을기준으로대조하며,일반문서의`<=`와차이가있음을명시한다. 변경을원하면최종대조때별도결정한다. 환경명·구현파일목록·검증기준·weight결정은최종명세단계에남아있다.

## 다섯 번째 라운드 — 사용자 답변 반영

사용자가 Q30–Q33에 모두 동의했다. 아래 계약은 확정이며 신규 weight 유보와 구현 미착수는 유지한다.

| 질문 | 확정 내용 | 근거·제한 |
| --- | --- | --- |
| Q30 장애물 감축 | 기존0–6개 요청 표집 유지. 초기 로봇 자세와 RED를 확정한 뒤 후보를 한 번씩 배치하며, 유효 공간 없는 후보만 건너뛰고 작은 후속 후보도 검사. 성공한 물체만 활성화하고 actual count 기록. 관측16슬롯 초과/타겟미검출 시 장애물을0개로 줄여 한 번만 재관측. 타겟 단독도 미검출이면 오류 | 같은 장면을32회 재추출하지 않음. 일반 배치1회·관측최대2회. 실제 장애물 수는 기하에 따른 분포가 되므로 요청수/실제수/감축이유·빈장면 비율·reset시간 로그 필요 |
| Q31 Gate 회피 방지 | setup 자세 평가는 Gate 전만 지급. Gate 후에는 동일 weight로 원점수1의 별도 안정화 완료 보상을 매 policy step 지급하고 episode 종료 시 중단. 즉 단계 관련 원점수는 Gate 전 R_setup∈[0,1], Gate 후1 | Gate를 열어서 setup 보상 지급률을 잃는 직접 유인을 제거. Sweep 중 초기 위치/자세 유지를 요구하지 않음. 통과 즉시 미래 보상을 선지급하는 bonus는 조기 실패 이득을 만들 수 있어 권고하지 않음. 전체 정책의 성공/정지 유인은 Sweep 계수·종료 포함 별도 검증 |
| Q32 압착 계측 | 압착 비용용 S는 개별 법선 접촉력 크기 합으로 정의하고 공통상한5N 유지. 합력·모멘트에는 법선+마찰 모두 포함. 모멘트는 법선 접촉점과 마찰 anchor 각각에서 계산 후 합산 | 첨부의 각 접촉점 총3D힘 norm합과 다른 정의로 변경하는 데 동의. API가 법선과 마찰을 별도배열로 제공하며 동일index가 같은 점이라는 계약 없음. 최종 합력 norm으로 대체하거나 임의 대응하지 않음 |
| Q33 IK 한도 | 장애물 배치 전에 target/goal을 유지한 채 XY/yaw jitter 후보를 최대4개까지 시도. 전부 실패하면 해당 초기 장면의 원인을 기록하고 중단. 장애물 감소로 타겟·선반·자기충돌 또는 팔 도달 불가능을 해결하려 하지 않음 | 한 번씩 시도하되 가능하면 batch 연산. 무제한재추출 없음. 목표 재표집·범위 축소 없음. 로봇 점유공간은 손 포함 충돌형상에1cm 여유를 두는 것으로 확정 |

### 구현 가능성 추가 확인

현재 `CircleResetLayout.sample`은 큰 후보부터 순회하고 빈 셀이 없으면 complete를False로 만든 뒤 전체 batch에 예외를 낸다. 새 환경의 요청은 예외 대신 실패 후보 생략·실제 count 반환으로 별도 구현할 수 있다. 기존 환경용 함수를 직접 변경하지 않는다.

로컬 설치된 `omni.physics.tensors`107.3.26 API의 `get_contact_data`는 법선 힘 크기·점·법선·counts/starts, `get_friction_data`는 마찰 힘 벡터·마찰점·별도counts/starts를 제공한다. Isaac Lab의 집계 contact_pos는 점의 평균이므로 총힘과 평균점의 외적으로 원래 접촉 모멘트를 복원하지 않는다. 두 API는 같은 view의 counts/starts 버퍼를 공유할 수 있으므로 법선 자료를 먼저 축약하거나 필요한 인덱스를 복사한 뒤 마찰 호출을 해야 한다. API 소스 독서이며 실제 센서 부호·누락·buffer capacity·physics 실행은 미검증이다.

Reset 시간은 장애물 배치뿐 아니라 현재 MeshObserver의 CPU 연결요소 처리·GPU→CPU 전송도 포함해 측정해야 한다. 장애물 수 감축만으로 전체 iteration 성능을 보장하지 않는다. 구현 시 일부환경 reset과전체환경 reset의시간/전송/관측실행 횟수를 분리 계측한다.

## 후속 검토 목록의 이력

아래는 인터뷰 중 관리한 검토 목록이다. Q30–Q33까지 반영한 현재 계약·구현 검증 항목·유보 weight는 [통합 명세](2026-11-18_stabilize_sweep_spec.md)를 따른다. 이 목록을 미답변 질문으로 다시 제시하지 않는다.

- Sweep은 요청대로 이전 step 기준 거리 차분, 접촉은 확정된 시간 누적/20, 방향은확정된0–1 cosine. 힘1N·접촉높이12cm 유지 확정. 거리차분항의dt상쇄와setup/압착등지급률항의dt1회적용을 최종명세에 명시한다.
- 단순 차분×가변 카운트는 왕복으로 양의 보상을 얻을 수 있음. 예: 기존 weight100에 raw count20을 그대로 곱하면 정방향1mm 보상2에 비해 1.5배 멀어짐 비용은0.03891. 이는 잠정 수치 대입의 위험 예시이며 새 weight가 확정됐다는 뜻이 아님. 보상 계수와 무접촉/역방향/왕복 사례를 함께 결정.
- 카운트 정규화는 weight 재매개화일 뿐 왕복 방지책이 아님. 정규화된 두 인자의 곱이0–1이고 거리 감소계수가w인 경우, 같은 거리L의 왕복에서 거리 항은 최대(w−38.91)L이다. 기존 positive weight100을 그대로 쓰면1cm 왕복에서최대+0.6109. 최종 weight는 사용자 요청대로 유보하며 반복 gate 통과가 불가능한 확정 구조와 거리 보상 자체의 순환 유인을 구분한다.
- Gate의 조건·연속0.3초·Q26수치는 첫검증용으로 확정. 힘을 물체 이동 없이 형성할 수 있는지 mass/friction 분포별 검증 필요. 수치 변경은 별도 승인 없이 하지 않는다.
- COM·접촉 위치·법선/마찰 힘의 물리 API, 접촉점/마찰 anchor별 모멘트 합산, 힘 합산 전에 norm을 취하는 squeeze 정의. 수집 오버플로·누락·부호·좌표·시간 집계의 검증 기준.
- 손목 F/T 변화 비용의5% 예산은 제거 확정. 기존 tilt와 setup rotate의 중복 의도·계수만 후속 검토. action-rate 유지 확정, action-magnitude 새 비용 없음.
- 총10초·gate 통과 성공 전제는 확정. 성공3cm 경계 < 또는 <=, gate 전 이동 기준 anchor, gate 이후 거리 이력 초기화와 소급 지급 금지 명시.
- Deadzone30도 고정·해당 일정 삭제 확정. 목표 거리6–12cm 유지. 허용 방향에서 IK 불가능할 때 재표집 한도·분포 편향 기록.
- reset 순서, IK 실패 재시도 한도, 초기 안정화 물리 step과 관측 snapshot 시점, training step 제외 범위, RNG 재현성·부분 reset.
- 파일 구조는 기존 역할별 구조를 유지. 실제 구현 착수 전 요구-계약 표와 경계 사례를 사용자와 대조하고 공유 이해 확인을 받음.

## 용어·ADR 상태

기존 [용어집](../../GLOSSARY.md)의 관측 물체 정의를 사용자가 확인했다. 대표 표면점·안정화 단계·밀기 단계·안정화 통과·장애물 배치 금지영역을 추가했다. 조각을 동일 실제 물체로 합치지 않는 정보 경계와 그 근거는 [ADR](../adr/0001-visible-fragments-as-independent-objects.md)에 기록한다. 기존 OBB 관측 잔여 형상·높이 무관 가림 정의를 새 표면점 알고리즘의 가정으로 확대하지 않는다.

[분석·검증 기록](../../02_implementation/logs/2026-11-18_stabilize_sweep_design_interview.md)

## Q34 — 최종 설계 확정

사용자가 “확정합니다.”라고 답했다. 통합 명세를 설계 확정본으로 삼고 Gym ID를 `Inspire-Stabilize-Sweep-v0`로 확정한다. 신규 reward weight의 추후 조정과 구현 미착수 조건은 유지한다. 추가 설계 질문 없이 인터뷰를 종료한다.
