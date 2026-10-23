# Fusion Holding v0 — 2026-10-23

[개발 로그](README.md) · [활성 환경](../08_ACTIVE_ENVIRONMENTS.md)

사용자 승인한 정착 보상·충격 커리큘럼을 v1_0 직접 파생 환경으로 추가했다. 등록 ID는 `Isaac-Inspire-Contact-Sweep-Clutter-Fusion-Holding-v0`, EnvCfg는 `FusionHoldingV0EnvCfg`, runtime은 기존 `ContactSweepClutterFusionV1_0Env`, runner 설정은 `FusionHoldingV0PPORunnerCfg`다. 패키지는 `src/inspire_sweep_baseline/inspire_sweep_baseline/contact_sweep_clutter_fusion_holding_v0`다.

관측 순서·차원·GT 경계·8D Action·제어 주기·Scene·reset·기존 실패 종료는 v1_0을 상속한다. 최대 장애물Gray3/White3, push_fast0.8, hand_contact0.29/fade0을 유지하며 v1_4의 물체 수·가중치·종료값을 추가로 가져오지 않는다. 단 속도 세 커리큘럼은 사용자가 유지하기로 한 논의 당시 v1_4의 값을 독립적으로 재현한다. 물체 수·방향 deadzone 일정은 v1_0을 상속한다. 기존 환경 파일은 변경하지 않았다.

Goal progress는 tolerance0·weight100, 정착 보상은 거리와3D 속력의 Gaussian 곱·weight2다. 초기 정상 거리가12~15cm이고 최대 지원 반경이6cm이므로 처음부터 움직이지 않는 상태는 정착 보상이0이다. 위치 척도1→2→1→0.5cm, 속도 척도0.05→0.02m/s를 사용한다. 선반 평면 중심 범위·높이·기울기·finite 조건으로 이탈 상태를 배제한다. 성공은 보상 bool 변환 없이 오차0.5cm·속력0.01m/s·실패 없는 정상 상태3초로 독립 판정한다.

Wrench/가속도/장애물 합력 비용은1000까지weight0이며250주기 보간으로1250부터 켜진다. 6000~10000에는 규제를 고정하여 정착 조건을 좁히고,10000~12000에는 정착 조건을 고정하여 규제를 강화한다. Wrench 최종free20N/2Nm·weight−0.1, 가속도20m/s²·−0.05, 장애물30N·−0.1이다. 비용 함수와 상한은 기존과 같고 Wrench의 양수 예산 제한도 유지한다. weight0이면 RewardManager가 term 호출을 생략하므로 활성화 전환 시 과거 차분 이력을 초기화한다.

정확한 전체 일정과 실행 명령은 [패키지 README](../../../../src/inspire_sweep_baseline/README.md#fusion-holding-v0)를 따른다.

## 검증

CPU 명령:

```bash
env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider \
  src/inspire_sweep_baseline/tests/test_fusion_holding_v0.py \
  src/inspire_sweep_baseline/tests/test_clutter_fusion_v1_4.py
```

초기 무동작·빠른 목표 통과·비정상 높이·비유한 상태, dense reward와 strict success 분리,149/150스텝 경계, 실패·부분 reset, warmup·rewind·이력 초기화,0~17000의 속도 일정 일치와 모든 schedule endpoint를 검증한다. 첫 실행에서 테스트 fixture import 누락을 발견해 수정했다.

GPU 명령: `env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B outputs/fusion_holding_v0_validation/smoke.py`. 2환경에서 iteration0/1000/1250/3000/6000/10000/12000/16000/0을 적용하고 각8스텝,총72제어스텝을 실제 실행하여 finite 보상·가중치·정착 설정 복원을 검사한다. 테스트는 학습이나 학습된 정책의 성능 검증이 아니다. 장시간 학습·비발사 행동·목표 성공률 개선은 미검증이다.

최종 정상 높이 범위 1.04~1.07m 적용 후 재검증: CPU 18 passed (2.59s), GPU exit 0 및 `HOLDING SMOKE PASSED`. 실행 증거는 Workspace의 `outputs/fusion_holding_v0_validation/smoke.py`, `smoke.log`, `result.json`에 보존했다. 변경 Markdown 4개 수식 검사와 두 저장소의 `git diff --check`를 통과했다.

## 상세 환경 문서 추가

2026-10-23 후속 요청으로 [Holding 상세 환경 설명](../environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V0_ENVIRONMENT.md)을 추가했다. Workspace 기준 commit은 `870750df2520a5e486240fa498677dfcd0494532`이며 이 작업은 문서만 변경했다. 공통 Scene·Observation·Action과 Holding의 17개 보상·7개 종료·14개 curriculum을 구분하고, 초기 목표 거리 하한·정착 척도·성공 기준·warmup 경계를 실제 코드와 대조했다. 환경 계층 Mermaid·등록 표, 활성 환경 등록·상속 설명, 부모 문서와 두 단계 색인을 함께 연결했다. 기존 2026-10-14 HTML UML은 초기 네 환경만 다루는 자료이므로 본 작업의 전체 계층 갱신은 `ENVIRONMENT_EVOLUTION.md`에서 수행했다. 새 학습·GPU 실행은 수행하지 않았다.

문서 검증은 Workspace 루트에서 아래와 같이 실행했다. 대상은 이번에 추가·수정한 Markdown 7개뿐이다.

```bash
python - <<'CHECK'
from pathlib import Path
import subprocess
root = Path('example/Contact-Rich-Manipulation-Context')
files = [root / p for p in [
    '02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_HOLDING_V0_ENVIRONMENT.md',
    '02_implementation/environments/ENVIRONMENT_EVOLUTION.md',
    '02_implementation/environments/README.md',
    '02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_V1_0_ENVIRONMENT.md',
    '02_implementation/README.md',
    '02_implementation/08_ACTIVE_ENVIRONMENTS.md',
    '02_implementation/logs/2026-10-23_fusion_holding_v0.md',
]]
subprocess.run(['python', str(root / '00_guidelines/scripts/check_markdown_math.py'), *map(str, files)], check=True)
subprocess.run(['python', str(root / '00_guidelines/scripts/check_document_links.py'), '--root', '.', *map(str, files)], check=True)
subprocess.run(['git', '-C', str(root), 'diff', '--check'], check=True)
CHECK
```

결과: Markdown math 7개 통과, 링크 311개 검사·오류 0, diff 공백 검사 통과. 외부 웹 URL 2개는 fetch하지 않았다. 브라우저의 GitHub 수식·Mermaid 렌더링은 미검증이며 문서 검사기 통과와 구분한다.

## Holding v0 후속 변경 — 장애물 변위·population

사용자 요청으로 동일 Holding v0 등록 ID의 `object.params.displacement_ratio`를 2.5→5.0으로 변경했다. 전체 object weight−30, 변위 제곱합 상한0.04 및 기울기 식은 유지한다. 변위 부분 최대 비용은−3→−6/초, 장애물 하나10cm 변위 비용은−0.75→−1.5/초다.

EnvCfg 최대 Gray/White를 각각5로, population 최종값을각5로 override했다. 시작1/1, White3000·Gray4500 시작과3000 간격은 유지하여 White12000/Gray13500에서각5개에 도달한다. 최대 타겟 포함11개를 생성하고 다음 reset부터 활성 mask를 적용한다. 직접 부모 v1_0 설정은 최대3/3·변위계수2.5를 유지하는지 실제 config에서 검사했다. 상속은 바뀌지 않으며 v1_4는 부모가 아니다.

실행한 검증:

```bash
env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1   /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider   src/inspire_sweep_baseline/tests/test_fusion_holding_v0.py

env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1   /home/min/miniconda3/envs/env_isaaclab/bin/python -B   outputs/fusion_holding_v0_validation/population_smoke.py   > outputs/fusion_holding_v0_validation/population_smoke.log 2>&1
```

결과: CPU6 passed(2.04s). GPU2환경·seed42에서 0/2999/3000/4499/4500/6000/7500/9000/10500/11999/12000/13499/13500/16000/0의15단계를 reset 후각8step,총120step 실행했다. 11개 물체 용량·Gray/White별 활성 mask·변위 계수5.0·부모 설정 보존·finite reward·커리큘럼 복원을 검사하여 exit0 및 `HOLDING SMOKE PASSED`를 확인했다. 결과는 `outputs/fusion_holding_v0_validation/population_result.json`에 보존했다. 장기 학습과 다수 seed의 배치 성공률은 미검증이다.

Holding 상세 설명의 population 표·관측 활성 물체 수·비용 상한, 활성 환경·계층 안내 및 패키지 README를 갱신했다. 기존 위쪽 구현 기록의3/3·최대7개는 최초 구현 당시 값이며 현재 계약은 이 후속 변경과 상세 문서를 따른다.

## 학습 실행 정책 변경

2026-10-23 사용자 요청에 따라 자동 복구 후에도 중단이 반복되는 `train_resilient.py` 사용을 중단하고 `train.py`를 실행·안내 기준으로 명시했다. Workspace/문서 AGENTS, 개발 지침, 결정 목록, 패키지 README와 Holding 상세 실행 명령을 갱신했다. 위의 자동 복구 관련 내용은 당시 기록이다. 코드 삭제·변경·학습 실행은 하지 않았다. 원인은 사용자 보고만으로 확정하지 않았다.

검증: 변경 Markdown 7개에 `check_markdown_math.py`와 `check_document_links.py --root .`를 실행하여 수식 검사 통과·내부 링크165개 오류0을 확인했다. 두 저장소의 `git diff --check`도 통과했다. 문서 변경만 수행하여 시뮬레이터·학습 테스트는 실행하지 않았다.

## Holding v0 후속 변경 — 접촉 보상·과속 종료

사용자 요청으로 Hand contact weight를0.29→1.45(5배), 타겟 과속 종료를0.8→1.0m/s로 변경했다. 접촉 fade0과 다른 조건은 유지한다. TerminationsCfg override 외에 EnvCfg의 부모 post-init 완료 후에도1.0을 적용하여 v3 초기화의0.8 덮어쓰기를 방지한다. 부모 v1_0은0.29·0.8을 유지한다.

검증 명령: `env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_fusion_holding_v0.py` — 6 passed(2.12s).

GPU 명령: `env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 /home/min/miniconda3/envs/env_isaaclab/bin/python -B outputs/fusion_holding_v0_validation/contact_speed_smoke.py > outputs/fusion_holding_v0_validation/contact_speed_smoke.log 2>&1` — 2환경·seed42, iteration0/13500 각각8step. 실제 RewardManager weight1.45·TerminationManager 기준1.0·부모 설정 보존·유한 보상을 확인하여 exit0 및 HOLDING SMOKE PASSED. 장기 학습 성능은 미검증이다. 상세 환경·상속 안내·패키지 README를 동기화했다.
