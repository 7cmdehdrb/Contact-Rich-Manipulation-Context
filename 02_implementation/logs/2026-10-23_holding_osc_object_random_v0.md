# Holding OSC ObjectRandom v0 — 2026-10-23

[개발 로그](README.md) · [환경 설명](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_OSC_OBJECT_RANDOM_V0_ENVIRONMENT.md)

사용자 요청으로 Holding OSC v0 직접 파생 환경을 등록했다. NVIDIA 서버의 YCB 크래커·설탕 상자·수프 캔·커피 캔을 사용한다. 기존 mass/friction 분포·EEF 로컬 OSC·보상·종료·관측 차원·최대11개 population을 유지한다. 부모의 동일 원통 관성 복사만 물체별 초기 관성/질량 비율을 보존하도록 교체했다.

원본 Y축 상방을 Z축으로 세우고 밑면 중심을 rigid root로 재정렬했다. 실제 USD bound를 측정하여 수평 외접반경4cm·높이12cm 안으로 들어가는 단일 균일 scale을 구하고0.8/0.9/1.0 크기 변형을 생성한다. 각 mesh의 convex hull도 이 envelope 안에 있으므로 부모 배치가 원끼리 겹치지 않으면 새 형상도 겹치지 않는다. 기존 yaw[-π,π] reset을 계승하며 원형 가림 근사는 유지한다.

형상·크기는 Scene 생성 시 환경/슬롯별 무작위 선택이며 매 reset 재선택은 아니다. 위치·yaw·질량·마찰은 reset마다 갱신한다. MultiAssetSpawner와 replicate_physics=False를 사용한다. 최초 원격 자산 접근이 필요하다. 에셋 다운로드 실패 시 대체 원통을 사용하지 않는다.

## 검증 과정

NVIDIA Isaac5.1의 Axis_Aligned USD를 실제 열어 바운딩 박스를 측정했다. 초기 시도에서 MultiAssetSpawner의 activate_contact_sensors 기본값이 하위 설정을 덮어써 contact reporter를 찾지 못했다. 상위 wrapper에도 True를 지정해 해결했다. 이후 실제 GPU에서 초기 물체 간 최소8cm 간격과 모든USD의 bottom Z0·수평 외접반경≤4cm·높이≤12cm를 검사했다.

머스터드 용기는 정지 명령에서도 기울어져 0.32~0.36초에 object_drop을 유발했으므로 기본 후보에서 제외하고 커피 캔으로 대체했다. 보상·종료 임계값이나 질량을 바꿔 실패를 숨기지 않았다.

CPU 명령:

```bash
env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_object_random_geometry.py
```

13 passed. 네 가지 형상 비율×세 scale, 360개yaw의 모든XY꼭짓점 envelope·밑면정렬·높이·비율보존·잘못된 bound 거부를 검사했다.

GPU 명령:

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  outputs/object_random_validation/smoke.py > outputs/object_random_validation/smoke.log 2>&1
```

스크립트는 seed42·2환경에서 최대population(13500iteration)을 적용하고 실제 USD bound·22개 활성 물체·중심간격을 검사한다. Arm0명령·Hand열림에서 보상/관절 상태/토크finite 및 종료 원인을 기록한다. `outputs/object_random_validation/metadata.json`에는 환경·slot별 원격자산·uniform scale·bound, `states.json`에는 물체 상태 시계열을 보존한다. 최종 실행 결과는 아래 후속 기록을 따른다.

대규모 환경 처리량·다수 seed의 접촉/정착 안정성·장기 PPO 학습·실물 성능은 미검증이다. 기존 원통 저중심과 달리 형상별 COM/관성을 사용한다. CPU/GPU 검증을 장기 학습 성공으로 해석하지 않는다. 기존 사용자 TODO 변경과 다른 작업트리 변경은 보존했다.

## 최종 결과

기준 Workspace commit `63cc8b53dfe6f3e9e5a853a1c5f973b7dbb60711`에 파생 패키지를 추가했다. 최종4종 목록으로 GPU2환경·최대22개 활성 물체·100제어step(2초)을 실행하여 exit0, finite 보상·관절 위치·토크, 종료0회를 확인했다. 모든 물체의 실제 USD bound·8cm 중심간격 검사를 통과했다. PhysX 질량0.345~0.75kg, 환경 내 동일 질량 표본, 물체별 최초 관성×질량비 적용도 실제 버퍼에서 확인했다. `metadata.json`에는 최종4종이 모두 포함되었다. 출력의 `HOLDING OSC SMOKE PASSED`는 재사용한 검증 스크립트의 성공 표식이며 대상 Gym ID는 ObjectRandom이다.

변경 Markdown8개에 `check_markdown_math.py`와 `check_document_links.py --root .`를 실행하여 수식 통과·내부 링크438개 오류0을 확인했다. 두 저장소의 `git diff --check` 통과. 외부 URL fetch와 렌더링 검사는 문서 검사기에 포함하지 않았다.

## 후속 변경 — 1.5배 확대·최대 개수 고정·reset 검토

사용자 요청으로 동일ObjectRandom v0의 uniform scale을 기존 대비1.5배로 확대했다. 모든축 동일 배율이며 최대 외접반경6cm·높이18cm다. 물체 수 curriculum은 파생Cfg에서None으로 임시 비활성화하고 부모 post-init 이후 시작 개수를각 최대5로 지정했다. 부모 환경의 population 일정은 유지한다.

reset 경로를 확인한 결과 USD·collider 생성은Scene 초기화에만 있고, reset은 `write_object_link_state_to_sim`으로 기존 rigidbody pose·0속도를 기록한다. 따라서 새 물체를 매번 스폰하도록 바꿀 필요가 없다. 종류·크기는 생성 시 선택한 값을 계속 사용한다.

6cm 원 근사로 기존 생성기에11개를 요청하는 CPU 사전 검사에서 일부 목표 방향의 Gray/Rear 배치 실패를 확인했다. 이를 해결하기 위해 ObjectRandom 전용reset에서 기존4cm기준 역할별 후보 생성기를 재사용하고, 실제USD bound·yaw에 대한2D OBB SAT와 선반경계 검사를 추가했다. 물체간·벽면2mm 여유를 검사하고 실패시 후보배치/yaw를 최대200회 재추출한다. 타겟·목표는 재추출하지 않는다. 목표 생성의 가장자리 여유와 가림 반경은6cm envelope를 사용한다. 초기 OBB 비겹침을 보장하지만 큰 물체의 전체 이동 경로 충돌 없음까지 보장하는 것은 아니다. 목표·정착·실패 보상식은 그대로 유지한다.

검증 명령:

```bash
env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1   /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q -p no:cacheprovider   src/inspire_sweep_baseline/tests/test_object_random_geometry.py

env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python   outputs/object_random_validation/enlarged_smoke.py   > outputs/object_random_validation/enlarged_smoke.log 2>&1
```

결과: CPU14passed(0.12s), uniform scale·360yaw envelope·OBB 겹침/회전/벽넘침 검사. GPU4환경·seed42·iteration0부터44개 활성 물체, population term 없음 확인. 5회 반복reset에서 실제 위치·yaw·USD크기로 OBB 비겹침을 재검사했다. 이후100제어step(2초)에서 finite보상·관절/토크·종료0회 및 질량범위/물체별 관성 검사를 통과했다. exit0 및 HOLDING OSC SMOKE PASSED. `outputs/object_random_validation/enlarged_metadata.json`, `enlarged_states.json`, `enlarged_result.json`에 근거 보존. 다수seed·장기학습·대규모병렬환경 처리량은 미검증이다.

## 후속 변경 — 상하 방향 수정·실린더 타겟·Gray7/White7

기준 commit은 `63cc8b53dfe6f3e9e5a853a1c5f973b7dbb60711`이며 기존 미커밋 변경을 보존했다. 사용자 보고는 물체 윗면이 바닥에 닿는 것이었다. 물리를 진행하지 않는 실제 spawner 렌더링에서4종 모두 라벨이 거꾸로인 것을 재현했다. 따라서 reset 후 전도가 아니라 원본 semantic top 방향 해석의 오류였다. NVIDIA 자산의 실제 상방은−Y이며 기존X축+90°는 이를−Z로 보냈다. −90°로 수정한 재렌더링에서 라벨이 바로 서고 캔 뚜껑이 위에 있음을 확인했다. 이전 검사의 root tilt·바닥 bound만으로는 내부 시각 geometry의 상하 반전을 잡지 못했다.

`mass_cylinder` 슬롯의 spawn을 교체하지 않도록 하여 부모 실린더(반경4cm·높이10cm·저중심 COM)를 복원했다. 목표 가장자리 여유·target_width는4cm로 복원하며 장애물은 이전1.5배 크기를 유지한다. 가림은 타겟4cm·장애물6cm의 원 근사다. Gray/White는각7, 타겟 포함15개를 iteration0부터 활성화하며 개수 curriculum은 비활성화 상태다.

10개 제한은 Scene capacity 외에도 물성 초기화·layout·관측 buffer·가림 reshape·encoder·export에 있었다. 공용 구현에 기본10인 슬롯 인자를 추가하고 ObjectRandom만14로 지정했다. 장애물56D, encoder56→32→16, Actor export111D다. 부모 환경의 기본10슬롯과 기존 네트워크는 유지한다. 구40D encoder checkpoint의 직접 resume는 지원하지 않는다. 형상 OBB 검사는 실린더 타겟을 포함하며 실패한 후보만 재추출하고 목표를 변경하지 않는다.

수정 전후 시각 확인 명령:

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  outputs/object_random_validation/orientation_preview.py \
  outputs/object_random_validation/orientation_after.png
```

`orientation_before.png`와 `orientation_after.png`에 실제4종 renderer 결과를 보존했다. 두 preview 프로세스는 이미지 저장 후 종료 대기가 지속되어 해당 검증 프로세스만 종료했다. 최종 smoke는 `app.close(skip_cleanup=True)`를 사용한다.

CPU 검증:

```bash
env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_object_random_geometry.py \
  src/inspire_sweep_baseline/tests/test_clutter_layout.py \
  src/inspire_sweep_baseline/tests/test_clutter_models.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_models.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_population.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_contacts.py \
  src/inspire_sweep_baseline/tests/test_realistic_physics.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_0_cfg.py \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v0.py
```

96 passed, ONNX deprecation warning 2건, 5.38초. 14번째 장애물 위치의Actor gradient,14슬롯 실제CPU PPO update와JIT export, 기존10슬롯 모델/설정 회귀를 포함한다. 초기 추가 테스트의 rollout buffer 길이 오류는 검증 코드가 fixture의 실제 storage 길이를 사용하도록 수정했다.

GPU 검증 명령:

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  outputs/object_random_validation/upright_7x7_smoke.py \
  > outputs/object_random_validation/upright_7x7_smoke.log 2>&1
```

첫 실행에서 물성 초기화의 기존10개 제한을 발견해 설정 capacity를 따르도록 수정했다. 다음 실행에서는5회 reset·기하를 통과한 뒤 검증 스크립트의 존재하지 않는 `get_observations` 호출이 실패했다. ObservationManager의 실제 관측을 TensorDict로 받도록 수정했다. 이들은 아래 최종 검증과 구분한다.

최종 GPU 실행은 seed42·4환경에서 총60개 물체, 각 환경 실린더 타겟1개·장애물14개,5회 반복 reset의 OBB 비겹침·2mm 경계 여유, 자산−Y→root+Z 변환, 기존 질량 범위·형상별 관성을 통과했다. 실제56D 관측을 받는 Actor/Critic과 JIT export 일치도 통과했다. `upright_7x7_scene.png`에서 실제 선반의 파란 타겟 실린더와 정립한 상자·캔을 확인했다.

100제어step(2초) 실행의 보상·관절 상태·토크는 finite였다. 그러나 step63,env1에서 `object_drop`이1회 발생하여 **무전도 assertion은 실패했고 최종 exit1**이다. `upright_7x7_states.json`을 확인하면 시작 시 root+Z는 정상이며 이후 `obstacle_2` 크래커 상자의 tilt가 증가하여0.9rad 기준을 넘었다. 이 실행은 초기 상하 반전 수정·관측/리셋 검증이며, 물리 실행 중 전도까지 해결했다는 결과가 아니다. 종료 기준·질량·마찰·원본 장애물 형상을 변경해 결과를 숨기지 않았다. `upright_7x7_metadata.json`, `upright_7x7_states.json`, `upright_7x7_result.json`, `upright_7x7_smoke.log`에 실제 결과를 보존했다. 장기 PPO 학습·대규모 환경 성능·다중seed 전도 안정성은 미검증이다.

변경 Markdown5개 수식 검사 통과, 문서4개 내부 링크184개 오류0(외부URL3개 미조회), 양 저장소 `git diff --check` 통과.

## 후속 변경 — 초기 흔들림 수정

사용자는 배치를 유지하면서 스폰 직후의 흔들림을 없애도록 요청했다. 이전4환경 검증에서 관측한 박스 전도와 연결하여, 먼저 로봇·선반 없이 평평한 정적 바닥 위에서 실제 spawner의4종×3크기,12개 물체를4초간 실행했다. 초기 속도0,외력 없이 원본 scan convex hull에서 최대5.509° 기울기·0.08801m/s 선속도가 재현됐다. 2°·0.02m/s 정지 허용치를 검사한 assertion이 실패했다. COM은 중심 부근이었으며 로봇이나 다른 물체 접촉이 없어도 증상이 발생했다.

충돌 근사만 boundingCube로 바꾸고 질량·마찰·솔버를 유지한 대조 실험에서는 최대0.758°·0.01205m/s로 감소했다. 이로부터 불규칙한 scan 바닥과 원본 변환에 의한 지지면이 주된 원인으로 판단했다. 최종 수정은 boundingCube를 캔까지 일괄 적용하지 않고, rigid root 좌표에서 밑면Z=0인 별도 convex proxy를 만든다. 상자는 실제 시각 OBB와 같은 XYZ 크기의 상자, 캔은 같은 bound를 갖는32각 타원 단면 원통이다. 원본 scan의 미세 요철·찌그러짐은 충돌에서 생략하지만 시각 geometry와 균일 크기는 보존한다.

`spawn.py`에서 원본 자산의 모든 CollisionAPI를 비활성화하고 `/Collision` 프록시 한 개만 활성화한다. `collision_props` 적용도 해당 경로로 한정하여 부모 경로를 통한 원본 collider 재활성화를 방지한다. COM·관성은 새 충돌 형상에서PhysX가 계산하며 기존 episode 질량비 갱신을 유지한다. 질량·마찰 분포,타겟 실린더,배치·yaw·Gray7/White7,제어·보상·종료는 변경하지 않는다. damping 추가,강제sleep,속도clamp,reset warm-up은 사용하지 않는다.

기하 단위 검증은 바닥 평면·시각 bound 내부·닫힌 면/반대방향 edge·양의 체적을 검사한다.

```bash
env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_object_random_geometry.py
```

16 passed,0.13초. 개발 중 신규 mesh 면 목록의 괄호 오류를 CPU 검사에서 발견해 수정한 뒤 재실행했다.

평면 대조 실험 명령과 결과:

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  outputs/object_random_validation/support_probe.py \
  outputs/object_random_validation/support_after.json
```

원본 구현의 `support_before.json`, boundingCube 대조의 `support_box_probe.json`, 최종 프록시의 `support_after.json`을 보존한다. 최종12variant×4초는 exit0이며 float32 quaternion으로 측정한 최대 tilt0°(검출 해상도 이내),최대 선속도0.002578m/s다. 이전 오류를 잡는 회귀 스크립트는 `src/inspire_sweep_baseline/tests/_object_random_support_probe.py`에 추가했다. quaternion을float64로 계산하고0.1°·0.005m/s의 더 엄격한 허용치와 물체당 활성 collider1개를 검사한다.

실제 환경 검증:

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  outputs/object_random_validation/stable_7x7_smoke.py \
  > outputs/object_random_validation/stable_7x7_smoke.log 2>&1
```

실제 선반 결과: seed42·4환경·각15개,5회 반복 reset의 비겹침·배치,물성/관성 및14슬롯 Actor/Critic/JIT 검증을 통과했다.200제어step(4초)에서 최대 기울기0.01164°,최대 선속도0.01094m/s,물체 전도/낙하 종료0회를 확인했다. 최초 실행은 모든 종료0회를 요구하는 기존 assertion에서 exit1이었다. 이유는 step142/env0과step162/env3의 `shelf_collision`2회였으며 `object_drop`은 모두False다. 이 결과를 무종료 실행 성공이라고 기록하지 않는다. 물체 지지 안정성 회귀 범위에 맞춰 assertion을 전도0회·최대tilt<0.1°·선속도<0.02m/s로 명확히 했고, 저장된4초 상태에 같은 검사를 다시 적용해 통과했다. 로봇의 정지 명령 중 선반 접촉은 이번 수정에서 다루지 않는다.

`stable_7x7_metrics.json`, `stable_7x7_result.json`, `stable_7x7_states.json`, `stable_7x7_scene.png`에 근거를 보존했다. 장기 학습 및 명령을 가한 밀기/전도 분포까지 검증한 것은 아니다. 해당 프록시는 scan 요철을 제거한 물리 근사이며 실제 물체의 세밀한 밑면 특성까지 재현하지 않는다.

추가한 엄격한 회귀 검사 명령:

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python \
  src/inspire_sweep_baseline/tests/_object_random_support_probe.py \
  > outputs/object_random_validation/support_regression.log 2>&1
```

엄격한 GPU 회귀 검사도 exit0:12variant×4초,활성 collider 각1개,최대tilt0.00430°·최대선속도0.002578m/s로0.1°·0.005m/s 기준 통과. `support_regression.json`에 결과 보존. Markdown5개 수식 검사 통과,문서4개 내부링크187개 오류0,양 저장소 diff 공백 검사 통과. 외부URL3개는 조회하지 않았다.

## 후속 검토 — 학습 시작 후 네트워크 단절

질문은 최초 Scene 로딩과 학습 시작 이후의 네트워크 단절이며, 새 프로세스를 처음부터 오프라인으로 실행하는 것과 구분한다. 코드 검토에서 원격 USD `AddReference`는 Scene 생성의 `spawn_prop`에서만 실행된다. 물체 종류·크기·collider는 생성 시 고정되며 이후 reset은 기존 PhysX body의 pose/속도/물성·초기 관측 갱신이다. 첫 reset에서 실제 크기를 얻는 USD BBoxCache 역시 로딩된 Stage를 읽는다. PPO 기본 로거는 로컬 TensorBoard이며 모델은 `torch.save`로 로컬 디스크에 저장한다. 온라인 로거를 선택한 경우는 별도 조건이다.

실제 검증 스크립트는 `src/inspire_sweep_baseline/tests/_object_random_offline_probe.py`다.4환경·seed42·기존 PPO36step/iteration·8epoch 설정으로 첫 iteration을 완료한 직후 커널 seccomp TSYNC를 사용해 **검증 프로세스의 기존 native thread까지** IPv4/IPv6 socket 생성과connect를 차단한다. 이미 열린 IP socket도shutdown한다. 호스트 방화벽·인터페이스·DNS·다른 프로세스는 변경하지 않는다. 차단 직전 실제 NVIDIA 자산 서버의443포트에 연결하고, 차단 후 새IPv4/IPv6 socket의ENETDOWN과 기존TCP 연결의송신 실패를 확인한다. 캐시를 지우거나 시스템 네트워크를 끄지는 않는다.

하나의 `runner.learn(13)` 호출 중 iteration0 직후 차단하여 iteration1~12의12회 PPO 업데이트를 수행한다. 매2iteration 로컬 checkpoint 저장을 검증하고 마지막에 전체 환경 reset 및 카메라 렌더링을 수행한다. 로그는 사용자 학습 로그가 아닌 `outputs/object_random_validation/offline_training/`에 쓴다.

```bash
env -u PYTHONPATH /home/min/miniconda3/envs/env_isaaclab/bin/python -u \
  src/inspire_sweep_baseline/tests/_object_random_offline_probe.py \
  > outputs/object_random_validation/offline_training.log 2>&1
```

첫 시도는 차단 후12iteration 및 model_12 저장을 완료했지만, 검증 코드의 마지막 명시적reset을PPO의inference_mode 밖에서 호출하여PyTorch inplace tensor 오류가 났다. 실제 학습 루프의 실패가 아니며 해당 호출과렌더링을inference_mode 안으로 이동해 재검증했다. 첫 시도 로그는 `offline_training_first_attempt.log`로 보존했다.

최종 결과: exit0, `OFFLINE PPO/RESET/RENDER/CHECKPOINT PASSED`. 첫 iteration 후 기존IP socket4개를shutdown했고 IPv4/IPv6 신규socket·기존TCP 송신 차단을 확인했다. 이후12iteration·432제어step·환경 내부시간8.64초 동안 PPO 업데이트를 완료했다. 차단 이후 환경별 reset 횟수는[4,2,3,2]이며 최종 전체reset에서도15개 물체/환경을 유지했다. Actor/Critic 파라미터finite,TensorBoard 로컬 기록과model_12.pt 저장/재읽기(iter12),차단 후 텍스처가 유지된 카메라 렌더링을 확인했다. 결과는 `outputs/object_random_validation/offline_training/result.json`,이미지는 `offline_preview.png`,학습 기록은 같은 폴더의 `tensorboard/`다.

따라서 현재 기본 로컬 TensorBoard·단일프로세스 환경은 로딩과학습 시작 후 네트워크가 없어도 계속 동작하며, 자산 로딩 구조를 변경할 필요가 없다. 이번 변경은 검증 스크립트와문서뿐이다. 새 프로세스의 캐시 없는 offline cold start,W&B/Neptune 업로드,다중노드 분산학습,장시간연속실행까지 검증한 것은 아니다. 최초 자산 로딩에는 네트워크가 필요할 수 있다. 수식 검사2문서와내부링크9개·양 저장소diff 공백 검사를 통과했다.
