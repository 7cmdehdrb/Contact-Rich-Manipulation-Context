# test_pdfs 3편의 Review 질문별 횡단 비교

[데이터셋 안내](../README.md) · [Master CSV](../tables/paper_comparison.csv) · [Excel](../tables/paper_comparison.xlsx) · [Manifest](../manifest.csv)

분석일: 2026-09-18. 이 문서는 **형식 검증용 3편만** 비교한다. `260918` 전체 PDF 집합에 대한 결론이나 체계적 문헌고찰의 포괄성 주장이 아니다. 기존 상세 노트·기존 조사본의 논문별 결과를 이 비교의 증거로 재사용하지 않았다. 각 비교의 근거는 이번에 읽은 제공 PDF와 아래의 독립 분석 파일이다.

| ID | 신규 분석 | 관련성 | 비교에 제공하는 정보 |
| --- | --- | --- | --- |
| T01 | [Visual–Force Residual RL Assembly](../papers/2024-zhang-residual-rl-visual-force-assembly.md) | Relevant | 연속 RGB actor와 별도 F/T controller, geometry-based reward, controller 비교 |
| T02 | [SRL-VIC](../papers/2024-zhang-srl-vic.md) | Partially Relevant | Vision 없는 F/T+EEF position task actor, F/T 기반 safety/recovery, VIC/recovery 비교 |
| T03 | [Tactile Reach and Grasp](../papers/2025-zhang-tactile-reach-grasp.md) | Relevant | Binary/magnitude/vector·coverage 비교, current object pose/vision, fingertip total force 결합 |

## 1. Object information 제공 방식

### Current Pose

| 조건 | 논문·실험 | 실제 제공 정보 | 병용 정보와 해석 경계 |
| --- | --- | --- | --- |
| Tracking | T03 주요 simulation·실물 실험 | Simulation GT/noisy GT position·orientation; 실물 FoundationPose estimate | TCP pose, gripper opening, tactile, visual history. 축약 tactile만의 독립 state 추정이 아님 |
| Initial | 해당 사례 없음 | 초기 Pose만 주고 이후 갱신하지 않는 실험은 확인되지 않음 | 이 조건의 부족분을 비교할 표본이 없음 |
| 미제공 | T02의 maze/obstacle object pose | Object pose 없음. Current EEF position은 task actor에 제공 | F/T, VIC, learned maze task prior. Object state 미관측과 robot position 미관측을 구분 |
| 기타: 연속 시각 특징 | T01 reaching/searching; T03 RGB 일반화 실험 | T01은 상대 Pose를 나타낸다고 설명하는 CNN latent feature; T03은 image encoder feature | Explicit pose vector가 없다는 사실은 시각 갱신 부재를 뜻하지 않음 |

근거: T01 §4.2·4.4, PDF pp.5–7; T02 §III-B, p.3; T03 §III-A·IV-A/B/D/E, pp.2·4–6. 각 논문의 상세 observation·source 표는 위 신규 분석 링크를 따른다.

T01의 최종 insertion은 force-only지만 앞선 RGB 탐색·정렬이 완료된 이후의 단계다. 이를 전체 episode의 pose-free/vision-free manipulation으로 집계하지 않는다. T03의 GT/noisy GT pose는 **Actor에 실제 제공되는 입력**이므로 training-only privilege에 숨기지 않는다.

### Shape

| Shape 제공 범주 | 이번 표본 | 제공·미제공의 의미 |
| --- | --- | --- |
| 명시적 full geometry 제공 | 확인된 실행 Actor 사례 없음 | Full mesh/CAD/point cloud를 Actor에 직접 제공하는 명세 없음 |
| 제한적 제공 | T01의 RGB 외형 특징; T03의 one-hot identity 또는 RGB | Object identity는 known-object prior이며 full shape 관측이 아님. 영상 갱신을 mesh Tracking으로 분류하지 않음 |
| 미제공 | T02 실행 Actor | Maze mesh는 simulator 구축에 존재하고 task policy는 한 maze shape에서 학습됨. 입력 미제공이 학습 prior 부재를 뜻하지 않음 |

T03에서 실제 FoundationPose에 어떤 mesh/template가 제공되는지는 해당 PDF에 미명시다. 외부 알고리즘에 대한 일반 지식으로 채우지 않았다. 세 논문 모두 Actor의 물체 mass/friction 입력은 확인되지 않으며, simulator·controller의 물성/모델 설정은 별도로 기록했다.

## 2. 축약 Tactile의 보완 구조

축약 tactile을 직접 비교한 것은 T03 한 편이다. 공통적으로 TCP pose·gripper opening·시각 정보를 사용한다.

| 실제 비교 구조 | 표현에 남는 정보 | 빠지는 정보 | 증거가 말하는 범위 |
| --- | --- | --- | --- |
| B/BK + pose/ID + proprioception + visual history | 손가락/영역 접촉 여부 | 연속 force magnitude·direction | Binary 조건이 이런 보조 입력을 사용했다는 사실. 보조 입력 각각이 Binary 손실을 복원했다는 검증은 아님 |
| M/MK + 같은 공통 입력 | 힘 크기 | 힘 방향 | V/VK와 비교하므로 방향 정보 차이를 분석 가능 |
| V/VK + 같은 공통 입력 | 3D force 크기·방향 | Total V는 센서 내부 분포 미제공; VK는 선택 영역 내 세부 분포 미제공 | Imperfect vision에서 force vector가 유용한 결과가 있으나 알고리즘·noise 조건에 의존 |
| MK/VK + V | 선택 영역 정보 + 손가락 전체 force | 직접 contact configuration 출력은 없음 | Fig.8의 representation combination 비교. 별도의 wrist F/T sensor를 추가한 결과가 아님 |

근거: T03 §III-C·IV-B/C, PDF pp.3–5, Table III, Figs.7–8. B는 2개, BK는 2K개 접촉 bit이므로 같은 “Binary tactile” 안에서도 남는 공간 정보가 다르다. K=5/9/12는 coverage와 수량을 함께 바꾸므로 순수 해상도 하나의 효과로 해석하지 않는다.

**Binary tactile + tactile history**를 검증한 사례는 이 3편에서 확인되지 않는다. T03의 명시적 memory는 **visual history**다.

## 3. Pose가 없을 때 무엇으로 보완하는가?

| 부족한 정보 | 대신 사용하는 정보 | 저자가 확인한 역할 | 남는 미확인점 |
| --- | --- | --- | --- |
| T01의 명시적 peg–hole pose 입력 | Current RGB feature | 공간 탐색과 정렬 | 독립적인 pose 추정 정확도 및 시각 없는 수행은 미검증 |
| T01 시각 정책만의 접촉 처리 | F/T + 해석적 force/admittance control | 법선 힘 유지·외란 대응·탐색 공간 감소 | Force sensor 자체의 효과와 controller 구조 효과를 완전히 분리하지 않음 |
| T02 maze/obstacle pose와 시각 | F/T + EEF position + VIC + 학습 경험 | 접촉하면서 이동하고 위험 action을 회피 | Explicit contact localization 없음. Maze shape-3에서 task 실패 |
| T03의 부정확한 current pose | Tactile + visual history | Noisy vision 보완을 직접 비교 | Current pose를 제거한 경우의 충분성은 미검증 |

이 표본에서 반복되는 것은 접촉 센싱과 **로봇 상태 또는 시각 상태가 함께 쓰인다**는 사실이다. Proprioception, history, dynamics prior가 서로 대체 가능하거나 어느 하나가 충분하다고 결론 낼 수 없다. T02의 안전 모델 일반화와 task 일반화도 구분해야 한다. [T01 §4.4·7; T02 §IV-C, pp.7–8; T03 §IV-B]

## 4. F/T-only 접근의 성립 조건과 한계

| 경로 | F/T로 하는 일 | 함께 필요한 정보·조건 | Contact locality 및 multi-contact |
| --- | --- | --- | --- |
| T01 insertion/단계 판정 | 접촉 상태 전환, 삽입 force regulation, 완료 판단 | 앞선 시각 정렬, 평면/법선·task frame, gravity compensation, 미리 설정한 gains·force threshold | Contact-point 역추정 없음. 일반적인 multiple-contact 분리 미논의 |
| T02 safety/recovery | 후보 action의 risk 평가와 안전 action 생성 | Critic에는 후보 action, collision pretraining, VIC 구조. 전체 task actor에는 EEF position | Contact map/location 출력 없음. Multi-contact simulator 사용은 locality 복원 증거가 아님 |
| T03 fingertip V | 파지에 필요한 force cue를 Actor에 제공 | Current pose/vision·proprioception과 2-finger task 구조 | 저자의 stability 설명에 finger가 대상 물체에만 접촉한다는 조건이 있음. Wrist wrench localization이 아님 |

T01은 noise/drift 처리와 force precision 요구를, T02는 sim-to-real F/T 부정확성을, T03은 contact ambiguity 및 sensor deformation 모델의 한계를 논의한다. 그러나 **이 표본에는 F/T-only contact localization의 식별 가능 범위를 직접 분석한 논문이 없다.** 따라서 single-contact, known geometry, multi-contact ambiguity에 관한 일반 정리를 이 표본의 검증 결과로 만들 수 없다.

## 5. F/T + Tactile의 실제 역할 분담

**서로 독립적인 wrist F/T와 distributed tactile를 함께 평가한 사례는 이번 3편에서 확인되지 않는다.**

- T01은 RGB + 손목 F/T이며 tactile 없음.
- T02는 F/T + EEF position이며 tactile 없음. F/T 센서의 정확한 실물 장착 위치·모델은 미명시.
- T03은 fingertip tactile에서 만든 local feature와 total force를 비교·결합한다. V는 손가락별 3D force이며 6D wrist wrench가 아니다.

T03은 “영역별 force magnitude/vector에 전체 force vector를 추가할 수 있다”는 **representation 수준의 근거**를 제공한다. 이 비교는 MK/VK+V이며 BK+V의 검증이 아니다. 반대로 “F/T만으로 부족한 contact locality를 tactile가 복원했다”는 방향의 직접 실험은 제공하지 않는다. Fig.8의 이득을 영역별 Binary + 손목 F/T의 검증 결과로 인용할 수 없다. [T03 §IV-C, PDF p.5]

## 6. Privileged Information과 학습·실행의 경계

| 구분 | T01 | T02 | T03 |
| --- | --- | --- | --- |
| Actor object GT | 없음, RGB latent | 없음, F/T+EEF position | 주요 sim 조건에 GT/noisy GT pose 있음. 실물 estimated pose, RGB variant는 별도 |
| Critic만의 추가 GT | 없음. Actor와 CNN feature 공유 | Safety critic은 F/T+action. Task SAC critic 상세 미명시 | Critic 입력 상세 미명시 |
| Reward 정보 | 상대거리·yaw·height·hole depth, force completion | EEF–goal distance·force constraint·구역/goal 판단 | Finger–object distance·접촉·force, stability check |
| Termination | Force/action/time와 단계 상태 | Force constraint, entrance departure, goal, horizon | Episode horizon; 이후 stability check. 추가 조기 종료 GT는 미명시 |
| Data generation | Relative reset·형상/clearance·카메라 randomization | Maze 안의 6개 사전 위치에서 scripted collision data | Geometry 기반 grasp/stable pose 사전계산·demo injection·image encoder 학습 |

T01의 reward 기하량 사용은 명확하지만 simulator GT API와 실물 변수별 측정 경로가 모두 명시된 것은 아니다. T02의 reward에 위치가 쓰인다고 object pose GT를 사용한다고 기록하지 않는다. T03은 E/B tactile 조건에서도 reward가 contact/force를 활용하므로 **Actor sensing의 단순화와 학습 정보의 단순화는 별개**다.

T02 safety critic은 배포 시에도 필요하다. 모든 critic을 training-only로 분류하면 실행 요구 정보를 빠뜨리게 된다. [T01 §4.4–5.3; T02 §III-B; T03 §III-A–B·IV]

## 7. Evidence의 종류와 해석 범위

| 근거 유형 | 이번 표본의 사례 | 해석할 수 있는 내용 | 확대할 수 없는 내용 |
| --- | --- | --- | --- |
| Input/Sensor ablation | T01 RGB masking; T03 tactile E vs 입력 variants 및 visual history 길이 비교 | 입력 유무·이력 길이에 따른 해당 task 성능 차이 | 모든 환경에서의 센서 필요성 |
| Representation ablation | T03 B/M/V/BK/MK/VK | 같은 task에서 정보 형태·coverage의 차이 | Binary가 항상 열등/우수하다는 주장 |
| Representation combination | T03 MK/VK+V | 전체 finger force 추가의 효과 | 독립 wrist F/T+tactile modality 조합 효과 |
| Controlled controller comparison | T01 FM/VA/VF; T02 VIC/recovery 제거 | 제어·안전 구조의 효과 | 센서 입력 한 가지만의 인과 효과 |
| Failure analysis | T01 No Vision; T02 새로운 maze 실패; T03 실물 local tactile shift | 성공 조건과 일반화 한계 | 전체 문헌의 보편적 실패 조건 |
| Author explanation only | T03 total force가 유사 상태의 인과적 차이를 구분한다는 가설 | 저자의 결과 해석 | Contact configuration 복원 정확도를 입증한 실험 |

비교 예시는 T01 square/0.1 mm 조건의 FM/VA/VF 100/5/0%(각 20회; Table 2, p.13), T02 최초 실물 4/5에서 OU-noise 재학습 후 6/6(§IV-C, p.7), T03 can 무교란 policy-only의 E/B/M/V/BK/MK 0/35/45/65/20/5%(각 20회; Table V, p.6)다. **Task·학습량·평가 절차가 달라 논문 간 우열 순위나 평균 성공률을 계산하지 않는다.**

T03 Table V의 괄호 수치는 hard-coded gripper closing을 추가한 결과다. 이를 policy-only 수치와 합치지 않는다. T01 시뮬레이션 성능과 실물 fine-tuning 이후 성능도 별도다.

## 8. 현재 표본만으로 충분히 뒷받침되지 않는 주장

1. **영역별 Binary tactile + wrist 6-axis F/T가 각 단독 입력보다 우수하다.** 해당 조합의 동일 task ablation이 이 표본에는 없다.
2. **현재 object pose가 없을 때 Binary tactile와 history만으로 충분하다.** Binary를 비교한 T03은 현재 pose/vision을 사용하며 history도 visual이다.
3. **Wrist F/T의 multiple-contact locality ambiguity를 영역별 tactile가 해결한다.** Contact localization·configuration 복원의 정답 비교가 없다.
4. **F/T-only로 일반적인 contact 위치를 추정할 수 있다.** 이번 F/T 연구는 제어·안전·단계 인식이며 localization 역문제의 조건을 검증하지 않는다.
5. **단순 force vector가 모든 manipulation에서 고해상도 tactile보다 낫다.** T03 결과는 2-finger antipodal grasp, vision noise, 알고리즘, sensor model에 제한된다. 저자도 blind grasping·multi-finger 확대를 후속 질문으로 남긴다.
6. **Actor에 object GT가 없으면 학습에도 object/geometry 정보가 필요 없다.** T01의 reward와 T03의 demo generation 등이 반례가 되는 사용 구조를 보인다. 다만 미명시된 GT 취득 경로를 임의로 확정하지 않는다.

이는 **이번 세 편의 근거 범위**에 대한 판단이다. 관련 연구가 전 세계 문헌에 존재하지 않는다거나 프로젝트의 novelty·최종 sensor specification이 확정되었다는 뜻은 아니다.
