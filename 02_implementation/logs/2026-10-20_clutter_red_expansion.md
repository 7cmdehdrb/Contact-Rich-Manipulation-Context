# Clutter v0 — RED 확대와 장애물 수 감소

[로그 목록](README.md) · [최초 구현](2026-10-20_contact_sweep_clutter.md) · [활성 환경](../../03_assets/archives/2026-10-27_agent_context/example/Contact-Rich-Manipulation-Context/02_implementation/08_ACTIVE_ENVIRONMENTS.md.txt)

## 요청·확인·적용값

사용자는 방금 만든 Clutter 환경의 v0 ID를 유지하면서 RED Zone을 확대하고 장애물 수를 절반으로 줄이도록 요청했다. 확장량과 홀수 개수의 구역 배분을 질문했고 **RED 제외 반경 10.3 cm**, **뒤쪽 GRAY 1개·WHITE 2개**를 선택했다.

| 항목 | 이전 v0 | 현재 v0 |
| --- | --- | --- |
| RED 반경 | 8.3 cm | 10.3 cm |
| `red_margin` | 0.3 cm | 2.3 cm |
| 장애물 | 6개 | 3개 |
| GRAY / WHITE | 3 / 3 | 1 / 2 |
| 뒤쪽 GRAY | 최소 1개 | 1개 |
| 물리적 실린더 총수 | 타겟 포함 7개 | 타겟 포함 4개 |
| 장애물 관측 | 실제 6칸·더미 4칸 | 실제 3칸·더미 7칸 |

RED는 장애물 중심의 배치 금지 영역이다. 기존 경로·전면 확장 형태를 유지하고 `2 × radius + red_margin`만 키웠다. 물체 자체의 크기나 충돌 형상을 키우지 않는다. GRAY 외곽 반경 14 cm 및 다른 간격·밀도·접근 경로 제약은 유지한다.

Task는 **`Isaac-Inspire-Contact-Sweep-Clutter-v0`**다. 상속 관계는 `ContactSweepClutterEnvCfg(ContactSweepEnvCfg)` 및 `ContactSweepClutterEnv(ContactSweepEnv)` 그대로다. 관측 40D→MLP 16D→기존 57D와 결합하는 73D 모델과 Action 8D를 유지한다. 기존 보상 계수·물성·물리적 관절 제한·타겟과 목표 분포·초기 관측 노이즈는 유지한다. 전체 물체 tilt 합과 any-drop은 실제 4개 물체에 적용한다.

[`layout.py`](../../../../src/inspire_sweep_baseline/inspire_sweep_baseline/assets/scenes/contact_sweep_clutter_layout.py)의 `DEFAULT_LAYOUT_CONFIG`에 값을 모으고 Scene과 reset이 그 장애물 수를 참조하도록 수정했다. 촉각 필터는 타겟 포함 4개다. 원본 `src/scene_randomization`의 기본값 6개·RED 여유 0.3 cm는 수정하지 않았다.

작업 기준 workspace HEAD는 `457c3674c1993daaec8b8062f64f5d368bc7dcd6`, 문서 HEAD는 `e8aba3abbb6a321fdbae0ddc137d1ffee3ff59a4`다. 앞선 Clutter 구현의 미커밋 변경 위에서 수정했으며 사용자 작업과 독립 기준 환경·Renewal v3는 보존했다. commit·원격 반영은 수행하지 않았다.

## 검증

실제 CPU 명령:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_clutter_layout.py \
  src/inspire_sweep_baseline/tests/test_clutter_reset.py \
  src/inspire_sweep_baseline/tests/test_contact_sweep_clutter_mdp.py \
  src/inspire_sweep_baseline/tests/test_clutter_models.py \
  src/inspire_sweep_baseline/tests/test_contact_sweep.py \
  src/scene_randomization/test_generator.py
```

**57 passed, 9 subtests passed**, 4.09초. 기존 Torch ONNX deprecation warning 1건. 부모 분포의 4,096개 장면에서 타겟·목표 보존, 장애물 3개 배치, RED 10.3 cm 및 최소 손목 투영 표면 여유 2.3 cm를 원본 독립 검증기로 확인했다. reset·초기 관측 마스킹·물성·전체 물체 tilt/drop·MLP 학습 및 export 회귀도 통과했다. [CPU 출력](../../03_assets/artifacts/clutter_red_expansion_2026-10-20/cpu.log).

실제 GPU 명령:

```bash
/home/ssu/miniconda3/bin/conda run --no-capture-output -n jd_isaaclab \
  python -u src/inspire_sweep_baseline/tests/_clutter_lifecycle_probe.py \
  --headless --num_envs 4 --output /tmp/clutter_reduced_lifecycle.json
```

종료 코드 0. 4개 환경 각각에 물체 4개, policy 57D·obstacles 40D, 실제 슬롯 3·더미 7을 확인했다. 실제 PhysX 질량·관성·마찰 동일성, 관절 속도 제한, 동일 seed 재현, 초기 관측 고정, 부분 reset 보존, 장애물 전도·낙하 종료를 통과했다. 12개 부모 촉각 센서의 필터 열 수는 모두 4다. 타겟 접촉 없이 장애물 접촉만으로 palm bit가 활성화됐으며 접촉 열별 누적 수는 `[0,12,0,0]`이다. [결과 JSON](../../03_assets/artifacts/clutter_red_expansion_2026-10-20/lifecycle.json) · [GPU 출력](../../03_assets/artifacts/clutter_red_expansion_2026-10-20/lifecycle.log).

장기 PPO 학습이나 새 배치의 학습 성능 비교는 수행하지 않았다. GPU 검증의 전도·접촉 검사는 명시적으로 상태를 조작한 계약 검사다.

변경 Markdown 7개의 `check_markdown_math.py`와 양쪽 저장소의 `git diff --check`를 통과했다. `check_document_links.py --check-external`는 기존 TEMP 로그 3건·DexTouch PDF 1건의 누락만 보고했으며 새 링크 오류는 없었다.

## 실행

기존 v0 명령을 그대로 사용한다.

```bash
./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/train.py \
  --task Isaac-Inspire-Contact-Sweep-Clutter-v0 --num_envs 2048 --headless
```
