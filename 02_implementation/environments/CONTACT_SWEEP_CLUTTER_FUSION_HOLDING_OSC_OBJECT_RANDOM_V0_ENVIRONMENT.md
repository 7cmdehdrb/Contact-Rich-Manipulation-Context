# Holding OSC ObjectRandom v0

[환경 목록](README.md) · [상속 계층](ENVIRONMENT_EVOLUTION.md) · [부모 Holding OSC](CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_V0_ENVIRONMENT.md) · [검증 로그](../logs/2026-10-23_holding_osc_object_random_v0.md)

등록 ID: `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v0`. `FusionHoldingOSCObjectRandomV0EnvCfg`는 Holding OSC v0을 직접 상속한다. EEF 로컬 OSC·Hand·보상·종료는 부모를 유지한다. Scene·물체 spawner·물체별 관성을 확장하며 개수 커리큘럼은 테스트를 위해 비활성화했다. runtime은 기존 v1_0이며 PPO는 Holding OSC를 상속하고 experiment 이름과 장애물 관측 슬롯 수를 지정한다.

## 물체 자산

NVIDIA Isaac 자산 서버의 `ISAAC_NUCLEUS_DIR/Props/YCB/Axis_Aligned/`를 직접 참조한다. 크래커 상자 `003_cracker_box`, 설탕 상자 `004_sugar_box`, 수프 캔 `005_tomato_soup_can`, 커피 캔 `002_master_chef_can`를 사용한다. 자산·텍스처는 NVIDIA 원격 참조이며 이 저장소에 복제하지 않는다. 최초 실행에는 해당 서버 접근이 필요하고 자산을 읽지 못하면 원통으로 조용히 대체하지 않고 실패한다.

**타겟은 부모의 실린더(반경4cm·높이10cm·기존 저중심 질량 분포)를 유지한다.** 장애물만 종류4개×크기3단계의12개 variant 중 환경별·슬롯별로 생성 시 무작위 선택한다. 종류·크기는 물리 Scene 생성 후 고정하고, **매 reset에는 배치·yaw·질량·마찰을 다시 뽑는다.** 실행 중 collider 크기나 topology를 변경하지 않는다. 종류·크기를 매 episode 교체하는 기능은 구현하지 않았다. seed와 선택 결과는 검증 로그에서 추적한다.

네 자산의 실제 윗면 방향인 −Y를 X축 −90° 회전으로 +Z에 맞추고 밑면 중심을 rigid root로 맞춘다. 따라서 기존 높이·goal·낙하·정착 판정에서 사용하는 물체 위치가 계속 밑면 기준점이다. 시각 mesh는 유지하고 충돌은 별도의 밑면이 평평한 볼록 프록시를 사용한다. 상자는 직육면체, 캔은32각형 단면의 원통 근사이며 각각 실제 시각 OBB의 XYZ 크기에 맞춘다. 캔 XY bound 차이는 타원 단면으로 반영한다. 프록시의 밑면은 rigid root의Z=0 평면이다. 스캔 원본의 미세 요철·찌그러짐·오목부는 충돌 형상에 포함하지 않는다.

## 균일 크기와 겹침 방지 — 1.5배 확대

후속 사용자 요청으로 장애물 variant의 모든 축을 정확히1.5배 확대했다. 실제 USD bound 크기를 dx,dy,dz라 할 때 scale은 `1.5 × fraction × min(0.04 / (sqrt(dx²+dy²)/2), 0.12/dz)`이며 fraction은0.8/0.9/1.0이다. XYZ에 같은 scale을 적용해 원본 종횡비를 보존한다. 수평 외접반경 상한은6cm, 높이 상한은18cm다. 질량 분포는 확대 전과 같다.

기존 Red/Gray/White 배치 생성기가 후보 중심을 만들고, 실제 각 물체의 USD 바운딩 박스 크기와 후보 yaw를 사용한 OBB SAT(분리축 검사)로 최종 배치를 검증한다. 모든 물체 쌍 사이에2mm 여유를 요구하며 회전된 모서리가 선반40×100cm 경계 안에2mm 여유로 남아야 한다. 형상과 convex hull은 OBB 내부에 있으므로 OBB 비겹침은 초기 형상의 비겹침을 보수적으로 보장한다. 기존4cm 원 기준 중심 간격만으로 합격시키지 않는다.

장애물 전체를6cm 원으로 배치하는 대신 각 형상의 OBB를 사용한다. 실린더 타겟은 반경4cm를 포함하는 정사각형으로 보수적으로 검사한다. 후보 생성의 역할 영역·접근 공간 규칙은 기존 것을 유지하되 실제 형상 검사를 추가했다. 타겟 복원에 맞추어 목표 생성은 부모의4cm 반경과2cm 가장자리 여유를 사용한다. 목표를 바꿔 실패를 감추지 않으며, 최대200개 전체 배치/yaw 후보에서도 유효 배치를 얻지 못하면 명시적으로 오류를 낸다. 유효 배치만 선택하므로 최종yaw 분포는 충돌·경계 조건에 의해 편향될 수 있다. 가림 모델은 타겟4cm·장애물6cm의 원형 근사다.

## reset 방식과 임시 최대 population

물체 종류·크기와 충돌체는 **환경 생성 시 미리 준비**한다. 매 reset마다 USD 생성·삭제·원격 다운로드를 반복하지 않는다. 동일 rigid body에 새 pose와0속도를 기록하여 텔레포트하고 초기 관측·물성·상태 이력을 갱신한다. 종류·크기를 매 episode 다시 선택하지 않는 기존 방식은 유지한다.

ObjectRandom 전용 CurriculumCfg에서 `obstacle_population=None`으로 임시 비활성화했다. 부모 초기화가 시작 개수를1/1로 되돌리므로 파생 EnvCfg의 마지막 초기화에서 Gray/White를각 최대7로 지정한다. **iteration0부터 타겟1+Gray7+White7=15개**가 활성화되며 checkpoint iteration을 바꿔도 개수는 같다. 다른 커리큘럼과 부모 Holding/OSC 환경은 변경하지 않았다. 임시 테스트 종료 후에는 이 override와 시작 개수 override를 함께 복구해야 한다.

## 14개 장애물의 관측과 학습 모델

장애물 관측을10슬롯40D에서14슬롯56D로 확장한다. 각 슬롯은 `[present, x, y, z]`이며 기존 초기 가림·노이즈·정렬 규칙을 유지한다. 정책 입력55D와 Critic 추가 타겟 위치3D는 그대로다. Actor/Critic 장애물 encoder는 각각 `56 → 32 → 16`이며 최종 MLP 입력은 기존71D/74D다. Actor export raw 입력은111D다.

공용 capacity·물성·가림·encoder 코드는 슬롯 수를 받도록 확장하되 기본값10을 유지한다. ObjectRandom만14를 지정하므로 부모 환경의 관측·네트워크 크기는 바뀌지 않는다. 예전40D encoder checkpoint와는 첫 layer 크기가 달라 그대로 resume할 수 없으며 새 학습을 사용한다.

## 질량·마찰·관성

기존 episode 질량 분포(0.345~0.75kg 제한, mass_scale1.5 반영)와 물체·선반·Hand 마찰 샘플링을 그대로 사용한다. 한 환경의 활성 물체에는 동일한 질량·물체 마찰 표본을 적용한다. 크기 변화로 질량 분포를 자동 변경하지 않는다.

부모 물성 함수는 동일 원통을 전제로 타겟 관성을 모든 물체에 복사한다. 파생 환경은 같은 질량·마찰 표본을 적용한 뒤 각 형상의 최초 관성에 `새 질량 / 최초 질량`을 곱해 물체별 관성을 복원한다. 장애물 COM·관성은 PhysX가 평평한 충돌 프록시에서 계산하며 원통 전용 저중심 가정은 장애물에 적용하지 않는다. 타겟은 부모 실린더의 저중심 COM과 관성을 유지한다. 바닥이 고르지 않거나 가늘고 긴 물체의 전도 특성은 원통과 다를 수 있다.

서로 다른 형상을 위해 `replicate_physics=False`를 사용한다. 기존 최대 병렬 환경 수의 처리량과 메모리 성능이 그대로 유지된다고 가정하지 않는다.

## 실행

Windows PowerShell, workspace 루트:

```powershell
.\IsaacLab\isaaclab.bat -p .\src\inspire_sweep_baseline\scripts\train.py `
  --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v0 `
  --num_envs 256 --headless --max_iterations 90000
```

Linux는 `./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v0 --num_envs 256 --headless`다. 256은 초기 실행 예시이며 해당 규모 처리량을 검증한 수치가 아니다. `train_resilient.py`는 사용하지 않는다.

## 코드

[환경·물성](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_osc_object_random_v0/env_cfg.py), [자산 spawner](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_osc_object_random_v0/spawn.py), [크기 계산](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_osc_object_random_v0/geometry.py).

[공식 NVIDIA 예제](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/replicator_tutorials/tutorial_replicator_isaac_snippets.html)의 YCB 자산 경로를 확인하고 실제 서버에서4개 USD를 열어 바운딩 박스를 검사했다. 장기 학습·실물 성능·대규모 다중 seed 안정성은 미검증이다.

## 상하 방향 교정 당시 검증 범위

CPU96개 검사, 실제 GPU4환경·15개 물체·5회 reset의 배치/자세/물성과14슬롯 모델·JIT export 검증을 통과했다. 물리 진행 전4종 렌더링으로 상하 반전 수정도 확인했다. 단,2초 Arm 정지 명령 실행 중 크래커 상자 전도로 `object_drop`이1회 발생했다. 초기 자세 교정과 이후 물리 전도 안정성은 구분하며, 전도 없는 초기 정착과 장기 학습 안정성은 추가 검증이 필요하다. 자세한 조건·실패 기록은 [검증 로그](../logs/2026-10-23_holding_osc_object_random_v0.md)를 따른다.


## 초기 흔들림 수정

로봇·선반을 제외한 평면 지지 시험에서도 원본 convex hull은 최대5.51° 기울기·0.0880m/s 선속도를 보였다. 스캔 바닥의 불규칙한 지지면을 제거하기 위해 충돌 프록시를 별도 생성한다. 원본 자산의 collider는 모두 비활성화하고 물체당 프록시 하나만 활성화한다. collider 속성은 프록시 경로에만 적용하여 원본 collider가 다시 켜지는 것을 방지한다.

질량·마찰 샘플링,1.5배 시각 크기,실린더 타겟,Gray7/White7 배치와 yaw 규칙은 유지한다. 추가 damping·속도 clamp·시작 시 강제 sleep·물리 warm-up을 사용하지 않는다. 동작 중 충격에 의한 물리적 전도는 기존처럼 가능하다. 최종 실행 결과는 [개발 로그](../logs/2026-10-23_holding_osc_object_random_v0.md)의 초기 흔들림 수정 절을 따른다.

수정 후12variant×4초 평면 GPU 회귀 검사에서 최대 기울기0.00430°·최대선속도0.002578m/s로 통과했다. 실제 선반4환경×4초는 최대 기울기0.01164°·물체 전도0회였다. 다만 로봇 선반 접촉 종료2회는 별도로 발생했으며 장기학습·로봇 정지 제어 안정성까지 검증한 결과는 아니다.

## 학습 시작 이후 네트워크

기본 로컬 TensorBoard 구성에서는 초기 Scene 자산 로딩과 첫 학습 iteration 이후 네트워크가 끊겨도 계속 학습할 수 있다. 자산 참조는 Scene 생성 때 구성하며 reset은 기존 물체를 재배치한다. 이후 반복해서 USD나 텍스처를 새로 내려받는 reset 경로는 없다. 로컬 checkpoint 저장에도 네트워크를 사용하지 않는다. 실제 단절 검증은 [개발 로그](../logs/2026-10-23_holding_osc_object_random_v0.md)의 해당 절을 따른다.

이 조건은 **처음부터 오프라인으로 새 프로세스를 실행할 수 있다는 보장과 다르다.** 최초 시작 때 원격 USD·텍스처가 캐시에 없으면 자산 서버 접근이 필요하다. W&B/Neptune 같은 온라인 logger를 별도로 선택한 경우도 이번 보장 범위에서 제외한다. 기본값을 명시하려면 학습 명령에 `--logger tensorboard`를 지정한다.

검증 조건은4환경·첫iteration 직후 프로세스의 모든thread에 kernel network 차단 적용이다. 차단 후12iteration(432step·8.64초),환경별 reset[4,2,3,2],로컬checkpoint 저장/재읽기,카메라 렌더링을 완료했다. 로딩 구조 변경 없이 통과했으며 단일프로세스·기본TensorBoard 조건의 결과다.
