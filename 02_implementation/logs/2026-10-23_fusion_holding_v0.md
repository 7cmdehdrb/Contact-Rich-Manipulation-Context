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
