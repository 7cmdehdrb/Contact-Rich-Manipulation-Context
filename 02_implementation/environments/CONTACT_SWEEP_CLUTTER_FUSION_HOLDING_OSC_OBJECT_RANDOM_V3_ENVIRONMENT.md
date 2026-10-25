# Holding-OSC-ObjectRandom-v3 환경

기준일: 2026-10-25. [계열·버전 비교](FUSION_HOLDING_FAMILY.md) · [공통 보상 상세](FUSION_HOLDING_V4_FAMILY.md) · [환경 목록](README.md)

## 목적과 등록

OSC와 물체·환경 랜덤화 결합. Task ID는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v3`다. `FusionHoldingOSCObjectRandomV3EnvCfg`는 `FusionHoldingOSCV4EnvCfg`를 직접 상속한다. [EnvCfg 코드](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/envs/contact_sweep_clutter_fusion_holding_osc_object_random_envs.py)에 기존 버전과 함께 정의한다. experiment는 `inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v3`다. Runtime은 `ContactSweepClutterFusionV1_0Env`, runner는 `CurriculumOnPolicyRunner`다.

## 제어·관측·장면

Arm은 UR10OperationalSpaceControllerActionCfg, Robot Base 기준 상대 pose 6D, 회전은 RPY 입력이다. 위치/회전 scale 0.03/0.15, stiffness 100/50, damping ratio 1, 관성 분리·중력 보상 true, effort_limit_scale 1, Arm 관절 PD 0이다. Hand 2D와 EEF offset을 유지한다. configure_reach_osc는 OSC-v2/v3/v4가 공유한다.

sim dt 0.01초, decimation 2, 정책 step 0.02초(50Hz), episode 10초다. Actor는 policy 55D + 초기 장애물 64D = raw 119D, Critic은 현재 타겟 XYZ 3D를 더한 122D다. 독립 장애물 encoder 64→32→16 이후 71D/74D다. Actor에 실행 중 타겟 GT나 goal 트리거를 추가하지 않는다.

타겟은 실린더로 유지한다. 장애물은 NVIDIA YCB 4종×3크기, 1.5배 확대, yaw·질량·마찰 reset, 평평한 상자/32각 원통 충돌 프록시와 OBB 비겹침·선반 경계 검사를 사용한다. 물리 슬롯 8/8·관측 16슬롯, 활성 최대 6/6이며 replicate_physics=False다. ObjectRandom-v2와 동일한 scene·events·ObjectRandomV2CurriculumCfg를 사용한다. White는 3000, Gray는 4000부터 각각 2000 iteration마다 증가한다. Gray 내측 확장은 6000 이후 250 간격으로 증가해 12000에 15%가 된다. 자세한 일정·배치 제약·검증은 [공통 문서](FUSION_HOLDING_FAMILY.md#objectrandom-v2-개수와-gray-영역)를 따른다. 활성 개수·배치 변경은 다음 reset에 적용한다. 초기 가림 관측은 반경 근사이며 실제 형상 실루엣을 계산하지 않는다.

## 보상·종료·커리큘럼

Goal Distance는 새 최단 XY 개선량×100이며 r을 사용하지 않는다. Goal Hold는 유효한 타겟의 d≤2r에서 거리·속도로 보상하고 d<r에서 중심을 최대 2배 강화한다(weight 4). Contact는 실제 접촉 또는 유효한 d≤r일 때 weight 1.45의 rate다. Reaching은 새 EEF 접근 기록×30이며 유효한 d≤r에서 접근 인정 반경을 0.10m에서 1.0m로 늘린다. r은 5000까지 0.02m, 10000에 0.01m, 20000에 0.005m다. 수식·유효성·다른 비용·커리큘럼 연결은 [v4 공통 계약](FUSION_HOLDING_V4_FAMILY.md)을 기준으로 한다.

success 종료와 max_hold_time은 없다. 10초 timeout과 기존 drop·과속·선반 충돌·Arm 관절 속도·선반 변위 실패 종료를 유지한다. 중심에서 오래 유지할수록 보상하며 timeout 비율 100% 달성 여부는 장기 학습으로 확인해야 한다.

## 실행과 검증 범위

Workspace 루트에서 Isaac Lab Python과 선반 USD 접근이 필요하다. Random 환경은 NVIDIA YCB 자산도 필요하다. 환경 수는 실행 예시다.

```powershell
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/train.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v3 --num_envs 256 --headless
.\IsaacLab\isaaclab.bat -p src/inspire_sweep_baseline/scripts/play.py --task Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-OSC-ObjectRandom-v3 --num_envs 1 --checkpoint "<checkpoint.pt>" --real-time
```

최초 v4 구현은 실제 Isaac Sim에서 2환경·seed 42·10step과 강제 timeout을 검사했다. 이후 d≤2r 확장은 CPU 회귀 검사로 확인했으며 해당 변경 이후 시뮬레이터를 다시 실행하지 않았다. 장기 학습·처리량·실기 성능은 미검증이다. [개발·검증 기록](../logs/2026-10-25_fusion_holding_v4.md).
