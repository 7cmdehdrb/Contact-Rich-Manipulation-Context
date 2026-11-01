# 2026-11-01 Revision v0 독립 환경 구현·검토

## 요청과 기준

사용자는 [통합 수정 계획](../../01_plan/FINAL_YCB_SIZE_RANDOMIZATION_FIX.md)을 구현하되 **Final 계열이 아닌 새 Revision 계열**, 기존 custom CFG·runtime·command·model 상속 제거, 함수 재사용 허용, 구현 후 코드 리뷰와 요구 대조를 요청했다. 최신 요청이 계획 문서의 v0_2 직접 수정 방식을 대체한다. 기능 대조 기준은 여전히 `Isaac-Inspire-Final-GoalAccuracy-v0_2`다. 다른 후기 버전의 환경 구현은 기준으로 사용하지 않는다.

- 루트 시작 커밋: `e2ace682083970760e1e0e32fe7a681b483d2199`.
- 문서 저장소 시작 커밋: `10f1a941f6b381e75be1032bad671aa890b86d5c`.
- 새 task: `Isaac-Inspire-Revision-v0`; 상세 계약은 [Revision v0 환경 문서](../environments/REVISION_V0_ENVIRONMENT.md).
- 작업 방식: 역할별 `revision.py` 파일과 독립 EnvCfg·PPO·스포너 추가, 패키지 Gym 등록 추가. 기존 파일 구조와 기존 환경 정의는 보존한다.
- 학습에는 `scripts/train.py`를 사용하며 학습 로그 정리는 수행하지 않는다.

## 사용자 요구와 변경 전후 대조

| 요청 | 기능 기준 또는 이전 상태 | Revision 구현·검증 상태 |
| --- | --- | --- |
| 새 계열·상속 분리 | Final 내부 CFG·runtime 상속 | Isaac Lab/RSL 기본 클래스 직계 선언. 기존 센서·계산·제어 함수는 재사용 |
| 중앙 크기와 단일 랜덤화 | YCB 0.8/0.9/1.0 선택 후 추가 scale | YCB 중앙 0.9 하나, Mesh는 자체 기준. 단일 U(.9,1.1). 별도64 env probe에서 정확한 8종×.9/1.1 collider·활성 물리 참여 검증 |
| 8종 역할 가용성 | 타겟/장애물 후보 분포 차이 | 동일한 8종 추출. 64 env 실제 활성 target/Gray/White 모두8종 |
| 다양한 reset 경험 | 구체적 reset 방식은 최종 지시에서 강제하지 않음 | 형상·scale은 생성 시 고정, reset은 배치·활성 구성·질량·마찰 변경. 64 env 역할별 커버리지 확인, 장기 조합 편향은 미검증 |
| 관측 순서 | Hand가 뒤에 있고 Arm default 차감 | Arm12→Hand2→EEF7→초기 타겟3→목표2→이전 행동8→촉각17→F/T6. 실제 Arm 값 사용 |
| 관측 용량 | 장애물20슬롯/80D | 장애물16슬롯/64D, 초과 용량 거부. 미사용 `[0,0,0,0]` |
| Critic 현재 장애물 | Actor와 동일한 초기 장애물 캐시 | 별도 `critic_obstacles`, active mask의 현재 비타겟 물체만. occlusion/반전/좌표 noise 없음 |
| 네트워크 | 초기 장애물 encoder | 양쪽 독립 64→32→16 encoder, 본체73/76D. CPU PPO·checkpoint·export 통과 |
| OBB 배치 | 원형 존·기존 배치 조합 | 지정 독립 `bbox_scene_layout` 호출, 최종 scale·중심 offset 반영. CPU 기하 검사 통과 |
| Gray padding | 변화하는 padding 조건 | 65 mm 고정, padding 커리큘럼 없음 |
| 물체 수 | 21개 collection 물체 | 실제10개: 타겟1+Gray4+White5. 8개 off-stage geometry prototype은 physical body 아님 |
| 성공 반경 | 2 cm | `d<=3 cm` 성공/실패 timeout·bonus·Hold·marker 일치, 반경 갱신 없음 |
| Hold 범위 | 2~6 cm | 내부3 cm·외곽8 cm, 정확히8 cm는0. weight8·speed scale 유지 |
| 접촉 인정 | 실제 접촉 OR 목표 점유 | 실제 접촉 AND EEF 고정 높이 미만. force≥.01 N·fresh·finite·weight1.45 유지. 통제된 실제 PhysX 접촉에서 낮은10표본 reward1·높은2표본 reward0 확인 |
| timeout bonus | +30, 별도 엄격 경계 | +30 유지, 동일 inclusive 성공 term 사용 |
| 스폰·시각화 | 보고된 위험을 예방적으로 검증 | 64 env sparse5/dense30 policy steps, 주차 sample2270개, 실제 active 위치·bbox64개·부분reset6회 검증 |
| 2048 env | 성공을 가정하지 않음 | 실제2048 초기화·sparse/dense35steps·부분reset6회 통과. 2 iterations·147456 transitions 학습 및 유한값·encoder 갱신 검증 완료 |

## 구현 결정과 영향

종류·scale은 PhysX가 시작하기 전에 각 env의 10개 슬롯에 독립 추출한다. reset마다 live geometry를 바꾸는 방식 대신, 벡터 환경에 분산된 크기·종류와 reset별 배치·활성 구성으로 다양성을 제공한다. **한 env 내부의 타겟 종류·scale은 고정**되므로 1 env playback을 매 episode의 형상 재선택으로 설명하지 않는다. 64 env에서 실제 활성 역할별 8종 커버리지를 확인했으며, 학습 전체 조합의 장기 편향까지 입증한 것은 아니다.

Critic 좌표 noise는 0으로 선택했다. Y 내림차순 정렬 뒤 10% 인접 교환을 매 관측 호출마다 새로 추출한다. Actor는 초기 관측 cache를 유지하며 현재 장애물 정보가 Actor나 export로 전달되지 않는다. 기존의 목표·촉각·F/T noise 및 행동 피드백 계약은 유지한다.

root Z 차이에 따라 Hold·낙하 판정이 왜곡되지 않도록 최종 scale을 포함한 bbox 꼭짓점의 실제 최저점을 사용한다. 관측 위치는 계속 해당 물체의 root XYZ다. 성공 XY 반경, Hold 외곽, EEF–타겟 접근 반경은 각각 3 cm, 8 cm, 10 cm로 구분한다. 연속 거리 보상의 scale 5 cm나 물체 간격 2 cm를 성공 반경 변경에 포함하지 않는다.

접촉 높이는 **초기 작업면 위 0.12 m 고정값**으로 결정했다. 초기 shelf origin과 EEF Frame을 사용하고 현재 타겟 종류·scale·pose에 따라 변하지 않는다. 최종 8종 기준 bounds 높이 평균은 실제 USD 측정으로 **0.118154574 m**다. 후속 actual collider 기하 검사에서 바닥 여유 1 mm와 최소 scale8종의 옆면 높이 중첩이 양립하는 열린 손의 가상 자세를 확인했다. 추가 물리 probe에서는 고정 로봇 root의95/150 mm IK 자세와 실제 cylinder 접촉의 AND gate를 확인했다. 모든 종류의 동적 밀기와 학습 후 상부 누르기 억제는 별도 검증 범위다.

물리 메모리 최적화 과정에서 Revision의 `gpu_found_lost_aggregate_pairs_capacity`를 `2**28`에서 Isaac Lab 기본 `2**25`로 낮췄다. 16 env 실행의 CUDA free memory가 약 1051 MiB에서 8666 MiB로 증가했다. 다른 환경 설정은 그대로다. free memory는 시점 측정치이며 peak 메모리로 기록하지 않는다.

## CPU 검증

`env_isaaclab`에서 다음 실제 명령으로 **20 tests passed, 최종 실행 4.22 s**를 확인했다. 시간은 해당 합산 실행의 pytest 결과이며 GPU 성능 측정이 아니다.

```powershell
python -m pytest src\inspire_sweep_baseline\tests\test_revision_cfg.py src\inspire_sweep_baseline\tests\test_revision_layout.py src\inspire_sweep_baseline\tests\test_revision_observations.py -q
```

| 검사 | 확인한 범위 |
| --- | --- |
| 관측 12개 | 실제 관절값, inactive zero·visibility flip, 현재 장애물 이동·target 제외·부분 역할 변경, root 좌표 회전, 슬롯 초과 거부, 선언 순서 |
| 실제 RSL CPU 모델·PPO | 73/76D latent, Actor privileged gradient 없음, 양쪽 encoder gradient·갱신, checkpoint 저장/복원, 121D JIT export |
| 목표·물리 경계 5개 | 3 cm 안/같음/밖 성공 분할과 +30, Hold3/8 cm 경계, 접촉 force·strict height·stale·finite, root offset·현재 회전을 반영한 최저점, 독립 CFG |
| 배치 3개 | 합성 비대칭 bounds의 바닥·경계·물체 간격, 요청 상한·주차, seed 재현·0장애물, 목표 방향 제외각 |

CPU 기하 검사는 실제 USD collider, 최초 PhysX step의 반응, GPU 메모리나 2048 env 성능을 입증하지 않는다. 기존 2cm 값 전체를 일괄 치환하지 않았고 요청 밖 환경의 코드는 변경하지 않았다. Manager·계수·schedule의 최종 계약은 환경 문서에 기록했고 실제 GPU 검증 결과는 아래에 별도로 기록한다.

## 두 축 코드 리뷰

리뷰 비교점은 루트 `e2ace682083970760e1e0e32fe7a681b483d2199`이며 미커밋 diff와 새 Revision 파일을 모두 대상으로 했다. 구현 에이전트와 별도의 검토 역할로 Standards·Spec을 구분했다.

| 축 | 보고 결과 | 현재 처리 상태 |
| --- | --- | --- |
| Standards | 명백한 문서화 규칙 위반 0건, 근거 있는 smell 지적 0건 | 개발 로그·검증 기록 보완 완료. Standards 통과를 물리 검증의 대체 근거로 사용하지 않음 |
| Spec | 스폰 안정성 probe가 최대 속도·변위를 기록만 하고 발사·침투·주차 이탈을 실패로 판정하지 않음 | 판정·초기 step·자동 reset 이전 상태 capture 추가. 64 env sparse/dense 및 주차 sample2270개 통과 |
| Spec | 사전 등록 kind 합계는 실제 활성 target/Gray/White 8종 커버리지를 입증하지 못함 | 실제 역할 집계 추가. 64 env target/Gray/White 각8종, 8종×scale끝값 실제 활성 물리 참여 확인 |
| Spec | 접촉 높이 .12의 평균·바닥 여유·실제 접촉 분기 근거 미완료 | 평균 .118154574 m·열린 손 side-height/floor 기하·고정 root의 IK·실제 접촉 AND gate 확인. 120 mm 고정값과 구현 분기 검증 완료. 학습 후 상부 누르기 억제는 미검증 |

Spec 리뷰는 중앙 scale·OBB 좌표 변환·active mask·독립 상속·3/8 cm 보상 분기에 별도의 명백한 구현 불일치를 보고하지 않았다. 첫 두 검증 지적은64 env 및2048 env 증거로 보완됐고, 세 번째 지적도 실제 접촉·높이 AND gate의 구현 검증 범위에서 해소했다. 짧은 학습 실행·저장·encoder 갱신도 확인했다. 학습 후 상부 누르기 억제와 장기 성능은 미검증이며 구현·분기 검증 완료와 구분한다.

## 초기 실제 실행 경과

VPN과 NVIDIA 환경이 연결된 Windows의 `env_isaaclab`을 사용한다. 최초 16 env probe에서는 초기화 이후 예외가 발생했고 `finally app.close()`의 simulation-stop/render callback 대기로 traceback이 가려졌다. watchdog으로 종료 경로를 확인하고 `env.close()` 선행 및 예외 traceback 출력으로 진단 경로를 보강했다. 후속 실행은 종료까지 성공했다. 초기 실패와 후속 성공을 구분해 보존한다.

아래 16 env 수치는 초기 물리 probe의 이력이다. 최종 기하·scale끝값 근거는 후속 [64 env 보고서](../../../../outputs/revision_validation/probe_64_endpoints.json)를 사용한다. 실행 경로는 [probe](../../../../src/inspire_sweep_baseline/tests/_revision_probe.py)다.

```powershell
python src\inspire_sweep_baseline\tests\_revision_probe.py --num_envs 16 --steps 30 --resets 6 --headless --bbox
```

| 16 env 결과 | 측정 |
| --- | --- |
| 초기화 / 전체 probe | 6.7715 s / 12.5440 s |
| 전체 reset 일정 | 0, 2000, 2500, 5000, 10000 iteration; 실제 평균 수 모두 요청과 일치 |
| 부분 reset / rollout | 6회 / 30 steps, 자동 reset 0회 |
| 실제 object body | USD 160 / PhysX 160, 환경 밖 추가 rigid body 없음 |
| 전체 USD enabled rigid body | 784; 로봇·선반 포함 수로 object 수와 구분 |
| 최대 활성 속도 / 변위 | 0.0103323 m/s / 0.0000138082 m |
| 최소 활성 물체 바닥 | 1.04999495 m, 기준 작업면 1.05 m |
| 첫 5 step 최대 속도 / 변위 | 0.0101071 m/s / 0.00000707465 m |
| collider·placement metadata | 종류별 관측 최소/최대 scale 총16개 일치 |
| 실제 scale 범위 | 0.9004311~1.0996909 |
| 타겟 bbox | 16개 모두 `mass_cylinder` 자식 |
| 역할별 종류 | target6종, 최종 Gray8종·White8종 |
| PyTorch peak allocated/reserved | 10.41/24.00 MiB; Isaac Sim 전체 GPU 메모리 peak가 아님 |

이 초기 16 env 결과에서 주차 물체 최대 속도·변위 0은 최종 Gray4/White5의 **10개 모두 활성 상태**에서 얻었으므로 격리 성공의 근거로 사용하지 않는다. 타겟 표본에는 sugar box와 master chef can이 없었다. 이 두 제한은 후속64 env 검사에서 sparse phase와 역할별8종 집계로 보완했다.

접촉 기하 helper의 초기 버전은 CollisionAPI가 붙은 Xform의 빈 bounds를 실제 geometry로 취급하는 문제가 있었다. USD의 유한 ±FLT_MAX sentinel을 배제하고 descendant Mesh/primitive geometry를 읽도록 수정했으며, live body transform은 Fabric과 동기화되지 않은 USD pose 대신 PhysX tensor를 사용한다. 잘못된 초기 기하 수치는 근거로 사용하지 않는다. 앞선16 env의 실제 물리 reset/rollout 결과와 이 기하 계산 오류는 구분한다.

## 후속 64 env 끝값·접촉 기하 검증

다음 검증은 정확한 scale0.9/1.1를 사용하는 별도 probe이며 학습 설정의 연속 균등 추출을 바꾸지 않는다.

```powershell
python src\inspire_sweep_baseline\tests\_revision_probe.py --num_envs 64 --steps 30 --resets 6 --headless --bbox --scale_endpoints
```

| 전체 결과 | 측정 |
| --- | --- |
| 초기화 / 전체 probe | 7.3795 s / 14.1655 s |
| policy step / physics step | sparse5+ dense30 =35 / 70 |
| 부분 reset | 6회, 비대상 env state 보존 및 zero padding·배치 기하 확인 |
| object body | USD640 / PhysX640; 추가 World rigid body 없음 |
| 전체 enabled USD body | 3136; 로봇·선반 포함 |
| 타겟 bbox | 64개 모두 타겟 슬롯 자식 |
| 실제 종류 | target/Gray/White 각8종, scale0.9/1.1의 16개 종류×끝값 조합 실제 활성 물리 참여 |
| 비활성 sample | 총2270개; 최대 변위3.8147 μm, 최대 속도0 |
| PyTorch peak allocated/reserved | 18.04/32.00 MiB; 전체 GPU peak 아님 |
| CUDA free / total | 8590.91/12281.50 MiB, 보고 시점의 가용량 |

| phase | 실제 Gray/White 평균 | 최대 활성 속도 | 최대 활성 변위 | 최소 물체 바닥 | 비활성 sample | 자동 reset |
| --- | --- | --- | --- | --- | --- | --- |
| sparse, iteration0 | 1/1 | .0097973 m/s | .011001 mm | 1.0499954 m | 2240 | 0 |
| dense, iteration10000 | 3.984375/5 | .2598948 m/s | 4.645498 mm | 1.0497968 m | 30 | 0 |

별도 일정 검사 actual mean은 iteration0 `1/1`, 2000 `1/2`, 2500 `2/2`, 5000 `4/4.984375`, 10000 `3.96875/5`였다. phase의 reset은 별도 추출이므로 iteration10000 dense 결과와 같을 필요가 없다. 요청 대비 부족한 슬롯은 `active=false`로 처리하는 명세상 허용된 부분 배치다.

probe는 자동 reset 전 terminal 상태를 capture해 발사 상태가 reset으로 가려지지 않도록 한다. 판정은 최대 활성 속도≤1 m/s, 변위≤50 mm, 최소 바닥≥1.04 m, 비활성 변위≤0.1 mm·속도≤0.001 m/s다. dense 최대속도 .2599 m/s와 이동4.65 mm까지 관측됐으므로 “전혀 움직이지 않음”으로 보고하지 않는다. 실제 측정값과 유한 시간의 판정 범위를 보존한다.

[기하 helper](../../../../src/inspire_sweep_baseline/tests/revision_contact_geometry_probe.py)는 실제 collider mesh 정점, primitive의 보수적 bbox와 현재 tensor body/EEF pose를 사용했다. 열린 손의 관절 형상을 고정하고 손바닥 법선을 수평으로 놓는 가상 강체 회전에서, 바닥 여유1 mm와 최소 scale0.9 8종의 옆면 높이 중첩을 함께 만족하는 EEF 높이는 **47.3986~99.4931 mm**, 예시 공통 높이는 **73.4458 mm**였다. 기준8종 평균 높이118.1546 mm와 함께 작업면 위120 mm 고정 문턱의 근거로 사용한다.

이 결과는 **기하학적 floor/side-height feasibility만** 확인했다. 이 기하 검사만으로 팔 전체 IK, 동적 측면 접촉 및 밀기, 다른 Hand 관절 형상, 학습 정책의 상부 누르기 억제를 검증한 것은 아니다. 초기 “높이가 낮으면 물리적으로 손이 반드시 바닥에 겹친다”는 우려에 대한 기하 반례이며, 실제 밀기 동작 성공을 뜻하지 않는다. 아래 별도 접촉 물리 실험에서 두 IK 자세와 실제 접촉의 높이 분기를 보완했다.

## 후속 2048 env 검증

[2048 env 보고서](../../../../outputs/revision_validation/probe_2048.json)를 확인했다. 장비는 NVIDIA GeForce RTX 4070, 총12282 MiB, driver621.01이다. 다음 실행은 학습과 별도의 물리·관측·reset probe다.

```powershell
python src\inspire_sweep_baseline\tests\_revision_probe.py --num_envs 2048 --steps 30 --resets 6 --headless
```

| 전체 결과 | 측정 |
| --- | --- |
| 초기화 / 전체 probe | 66.4078 s / 80.8699 s |
| policy step / 부분 reset | sparse5+dense30 =35 / 6회 |
| object body | USD20480 / PhysX20480 |
| 전체 enabled USD body | 100352 |
| 자동 reset | 0회, 모든 종료 원인0 |
| 실제 역할별 종류 | target/Gray/White 모두8종 |
| 비활성 sample | 71950개, 최대 변위7.6294 μm·속도0 |
| PyTorch peak allocated/reserved | 325.93/392.00 MiB |
| CUDA free / total | 보고 시6514.91/12281.50 MiB |
| bbox | 비활성화,0개; 실제 타겟 전용 표시는64 env에서 확인 |

| phase | 실제 Gray/White 평균 | 최대 활성 속도 | 최대 활성 변위 | 최소 물체 바닥 | 비활성 sample |
| --- | --- | --- | --- | --- | --- |
| sparse, iteration0 | 1/1 | .0181546 m/s | .030845 mm | 1.0499918 m | 71680 |
| dense, iteration10000 | 3.995605/5 | .0328386 m/s | 1.450674 mm | 1.0488784 m | 270 |

별도 일정 검사에서 iteration5000/10000의 Gray 평균은3.997559/3.997070, White는5였다. dense phase의 별도 reset과 구분한다. 요청4개보다 적게 배치된 Gray는 물리적으로 격리하고 Actor/Critic에서 제외했으며, 일부 `complete=False`는 실패를 숨긴 것이 아니라 명세상 허용한 탐색 예산 내 부분 배치다.

전체 GPU 메모리는 종료 전19초에19개 표본을 수집해 최대5490 MiB를 관측했다. 모니터 시작이 늦었으므로 전체 실행의 peak로 주장하지 않는다. PyTorch peak도 PhysX·renderer 전체 사용량을 포함하지 않는다. 초기화66.4초와 전체 probe80.9초의 차이를 학습 처리량으로 환산하지 않는다.

## 2048 env 짧은 학습 검증

[`scripts/train.py`](../../../../src/inspire_sweep_baseline/scripts/train.py)로2048 env·2 iterations의 학습을 완료했다. 다음 명령으로 workspace의 `outputs/revision_training`에 결과를 저장했으며 `logs/rsl_rl`은 건드리지 않았다.

```powershell
python src\inspire_sweep_baseline\scripts\train.py --task Isaac-Inspire-Revision-v0 --num_envs 2048 --headless --max_iterations 2 --experiment_name C:/python/Contact-Rich-Manipulation/outputs/revision_training --run_name smoke_2048
```

근거는 [학습 요약](../../../../outputs/revision_validation/training_summary.json)과 [전체 학습 로그](../../../../outputs/revision_validation/train2048.log)다. 체크포인트는 `outputs/revision_training/2026-11-01_18-53-18_smoke_2048/model_0.pt`, 같은 폴더의 `model_1.pt`에 있다.

| 검증 항목 | 측정·결과 |
| --- | --- |
| transitions | 2048 env×36 steps×2 iterations =147456 |
| 학습 시간 | 로그 `Training time`16.99 s; 초기화 시간 제외 |
| iteration0 / iteration1 처리량 | 8797 / 11735 steps/s |
| iteration0 수집 / 최적화 / iteration 시간 | 7.874 / .506 / 8.38 s |
| iteration1 수집 / 최적화 / iteration 시간 | 5.957 / .325 / 6.28 s |
| 체크포인트 | model0·model1 모두 optimizer 포함 각각100개 tensor가 유한 |
| encoder 최대 가중치 변화 | 두 체크포인트 사이 Actor .276063 / Critic .137532 |
| 오류 | fatal error·OOM·PhysX capacity overflow 없음 |
| GPU 사용량 표본 최대 | 1초 간격 `nvidia-smi` 전체 장치5689 MiB; 다른 프로세스 포함, 실제 allocator peak 아님 |

로그에는 MaterialX·deprecated dynamic control·debug marker prototype 등 경고가 남아 있으므로 무경고 실행으로 기록하지 않는다. 임의 초기 정책에서 선반 실패 종료율이 iteration0/1 각각 .0781/.4230이었고, 물체 낙하·기울기 및 target 속도 종료는0이었다. 이 결과는 로봇을 정지한 앞선 sparse/dense spawn probe와 구분한다. 두 iteration 모두 목표 접촉·Hold·timeout 성공 보너스 평균은0이었다. 유한한 loss·encoder 업데이트·저장을 확인한 것이며 물체 밀기 학습에 성공했다는 근거는 아니다.

## 실제 접촉·높이 gate 검증

[접촉 물리 probe](../../../../src/inspire_sweep_baseline/tests/_revision_contact_probe.py)와 [최종 JSON](../../../../outputs/revision_validation/contact_physics.json)을 확인했다. 로봇 root는 변경하지 않고 실제 PhysX Jacobian을 이용한 관절 재설정으로 두 EEF 자세를 구한 뒤, 정상 OSC 토크 제어·실제 물리 substep·실제 접촉 센서 출력을 사용했다. EEF나 force를 가짜 값으로 덮어쓰지 않았다. IK 목표95/150 mm의 위치 오차는 각각68.754/1.862 μm이며 각15회 반복으로 도달했다. 관절 재설정에 의한 자세 도달 검사로, 초기 상태부터의 충돌 없는 로봇 이동 경로 검사는 아니다.

```powershell
python src\inspire_sweep_baseline\tests\_revision_contact_probe.py --num_envs 4 --headless
```

seed42의4 env 중 cylinder 타겟이 있는 env1만 접촉 대상으로 사용했다. scale은1.047294이며 손바닥 앞면에 대해 목표 침투량0/1 mm를 각각5 physics substeps 검사했다. 낮은 경우는 작업면에 놓고 중력을 켰고, 높은 경우는 높이 gate를 분리하기 위해 물체를 띄우고 중력을 껐다. 나머지 물체는 주차했다. 따라서 이 실험은 통제된 접촉 fixture이며 일반 reset의 스폰·배치 검증이 아니다. 탐색 과정의 최대12 mm 다종 침투 결과 대신 최소 침투량으로 재검증한 최종 JSON을 근거로 삼는다.

| 결과 | 낮은 접촉 | 높은 접촉 |
| --- | --- | --- |
| IK 직후 EEF 높이 | 약94.939 mm | 약149.999 mm |
| 실제 접촉 중 EEF 높이 | 97.072~98.016 mm | 148.524~148.526 mm |
| 실제 타겟-손 접촉 force norm | .966~5.733 N | 12.382~12.396 N |
| 유효 접촉 표본 | 10 | 2 |
| raw 접촉 보상 | 모두1 | 모두0 |
| hand/wrist collider 바닥 여유, IK 직후→접촉 후 | 36.955→39.137 mm | 92.016→91.841 mm |

총80개 env·physics-substep 표본에서 `force>=.01 N AND EEF<.12 m`와 보상 불일치는0이었다. 로봇 root는 유지됐고, 전체 손 접촉 합력에서 타겟 접촉 합력을 뺀 벡터의 norm은 모든 표본에서0이었다. 이 결과는 낮은 EEF에서 바닥 충돌 없이 실제 타겟 접촉 보상이 가능하고, 높은 EEF는 실제 타겟 접촉이 있어도 보상을 받지 않는다는 구현 분기를 확인한다.

최종 Spec 재검토의 접촉 분기 지적은 이 실제 물리 증거로 보완했다. 모든 종류·Hand 자세의 동적 밀기, 학습된 정책의 상부 누르기 억제와 장기 성공률은 미검증이다. 고정120 mm는 작은 물체의 윗면보다 높을 수 있으므로 높이 조건 하나가 모든 누르기 전략을 배제한다고 주장하지 않는다. 짧은2 iterations 학습 검증도 이러한 정책 행동의 증거로 사용하지 않는다.

## 문서 검증

본 환경 계약·로그 2개에 대해 Markdown 수식 검사 통과, 내부·외부 파일 링크 오류 0, `git diff --check` 통과를 확인했다. 이는 물리 또는 학습 결과를 대신하지 않는다. 인계·활성 환경 색인·계획 상태는 최종 실행 결과를 취합하는 담당자가 별도로 갱신한다.
