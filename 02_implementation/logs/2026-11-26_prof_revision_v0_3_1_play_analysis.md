# Prof Revision v0_3_1 방향별 실제 Play 분석 기록

[최종 보고서·7개 요청 지표·16항 의도 판정](../experiments/2026-11-26_prof_revision_v0_3_1_play_analysis.md) · [환경 계약](../environments/PROF_REVISION_V0.md#prof-revision-v0_3_1)

## 요청·시작 상태

사용자는 v0_3_1을 직접 Play하면서 방향별 성공률·최종 위치·접촉 유지·밀어낸 평균 각도·보상/페널티 비중·장애물 이동·손가락 자세를 수집하고 각 보상 의도가 실제 행동에 반영되는지 확인하도록 요청했다. 환경 수정·보상 변경·학습 요청은 아니다.

Workspace 시작 HEAD는 `4bff6449f2cbc8b7ee09abbe2a1956c86e2a060a`, 문서 저장소 HEAD는 `e35db19a646c0bbfe33de499f49f8ac4195a3b9f`였다. 시작 작업트리는 기존 IsaacLab untracked 상태 외 변경이 없었다. 작업 중 나타난 사용자 파일 `docs/plan/PLAN22.md`도 수정하지 않고 보존했다. 로그 폴더의 최신 수치 checkpoint를 직접 확인했다.

- Task: `Inspire-Sweep-Prof-Revision-v0_3_1`.
- Run: `logs/TEMP/2026-11-26/inspire_sweep_prof_revision_v0_3_1/2026-11-25_14-35-42`.
- Checkpoint: `model_15550.pt`, SHA256 `f3fae35906c15667a835e4f368c9be5642b5c29508e76850f0640648b26b3599`.
- 구현 계약: v0_3 직접 상속, `formation_mode=distance_angle_sum`,5개 손가락의 거리×양방향 cos² 합산·weight0.245. 원통·목표6–12cm·장애물0–6개·TCP4m/s 종료 유지.

## 변경 전후·영향

| 대상 | 이전 | 이후·의도 |
| --- | --- | --- |
| `collect_prof_revision_play.py` | 기존 terminal-inclusive 계측기 | 파일 변경 없이 두 seed와 원본 reference 실행에 재사용 |
| `report_prof_revision_play.py` | Formation을 거리 합 식으로 가정·일부 그림/사전에 seed43만 표기 | 저장된 Env YAML의 mode·scale에 따라 실제 거리×각도 합산도 독립 검산. raw0–5 축과 실제 수집 범위에 맞는 표기, 기존 거리식 경로 유지 |
| `analyze_prof_revision_directions.py` | 없음 | 방향/30° 세부 구간·실제 root 이동 각도·최종 오차·접촉/힘·손가락별 기여·장애물·예산 분리·cluster CI 생성 |
| `report_prof_revision_directions.py` | 없음 | 검토한 수치에서 저장소 형식의 방향별 최종 보고서 생성 |
| 활성 패키지·환경·Manager·물리·PPO | 기존 v0_3_1 | 코드/수치/상속/관측 변경0.326개 Python source manifest가 수집 후에도 모두 일치 |
| 학습 모델·로그 | 기존 파일 | 읽기만 수행. 두 실행 후 checkpoint hash 일치, `logs/rsl_rl` 정리/이동/삭제 없음 |
| 문서 | 기존 구현 설명 | 이번 보고서·본 로그 추가, 환경 설명·계통·현재 인계에 특정 checkpoint 평가 링크 추가 |

## 실제 실행·분모

Windows11·RTX4070 12GB·Isaac Sim5.1·`C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`에서 실행했다. 두 seed는 순차적으로 수집했고, 관측 noise는 원래 상태·정책 행동은 deterministic inference를 사용했다. GPU found/lost aggregate pair capacity만2^25→2^21로 평가 메모리 조건에 맞췄다. 물리·제어·보상 수치는 유지했다. Omniverse 자산·Sim/Warp 캐시 접근에는 승인된 외부 실행을 사용했다.

```powershell
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --task Inspire-Sweep-Prof-Revision-v0_3_1 --checkpoint logs/TEMP/2026-11-26/inspire_sweep_prof_revision_v0_3_1/2026-11-25_14-35-42/model_15550.pt --output-dir outputs/prof_revision_v0_3_1_analysis_20261126/seed42 --num_envs 64 --episodes 4 --seed 42 --wrench-diagnostics --headless
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --task Inspire-Sweep-Prof-Revision-v0_3_1 --checkpoint logs/TEMP/2026-11-26/inspire_sweep_prof_revision_v0_3_1/2026-11-25_14-35-42/model_15550.pt --output-dir outputs/prof_revision_v0_3_1_analysis_20261126/seed43 --num_envs 64 --episodes 4 --seed 43 --wrench-diagnostics --headless
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --task Inspire-Sweep-Prof-Revision-v0_3_1 --checkpoint logs/TEMP/2026-11-26/inspire_sweep_prof_revision_v0_3_1/2026-11-25_14-35-42/model_15550.pt --output-dir outputs/prof_revision_v0_3_1_analysis_20261126/reference_seed42 --num_envs 64 --episodes 4 --steps 20 --seed 42 --reference --headless
```

각 seed64환경의 처음4개 완료 episode를 사용해256+256=512건이다. 조기 실패 포함, 뒤의 추가/부분 episode 제외, 원본 reference20step은 분모에 넣지 않았다. 총254,165policy transition·5,083.30환경초다. 수집 loop/저장 시간은219.98/218.93초(앱 시작 제외)이며 각2,000벡터 tick이다.

방향은 초기 `atan2(dirY,-dirX)`로 로봇 반대 −X를0°로 두어 ±30°·±150° 경계로4구역을 나눈다. 각도 전체 원래 분포를 유지했으므로 구역 폭과 표본 수는 다르다. 별도30°×12구간도 집계했다. CI는 같은 seed/env의4회 반복을 cluster로 묶은 bootstrap5,000회이며 단순 Wilson 구간도 원시 집계에 보존했다.

## 최종 결과·의도 검토

| 방향 | 성공 | 최종 성공률 | 최초 목표 진입 | 진입했으나 최종 실패 |
| --- | ---: | ---: | ---: | ---: |
| 로봇 반대 −X | 78/93 | 83.87% | 92 | 14 |
| +Y 측면 | 119/163 | 73.01% | 157 | 38 |
| 로봇 쪽 +X | 46/90 | 51.11% | 77 | 31 |
| −Y 측면 | 91/166 | 54.82% | 165 | 74 |
| 전체 | 334/512 | 65.23% | 491 | 157 |

전체 성공 cluster95%60.55–69.92%, seed42=176/256·seed43=158/256이다. 성공은 timeout에서 추적 가시 OBB 중심 XY≤3cm이고 물리 실패 제외이며, 물체 root를 목표점으로 바꾸어 재정의하지 않았다.

최종 오차 중앙값23.80mm·P9049.93mm. −Y 측면은 목표 방향 평균+25.80mm로 지나친 쪽의 오차가 크며, 로봇 쪽은 순이동 각도 오차18.28°와 미진입13건도 있어 원인을 한 가지로 묶지 않았다. 전체 순이동 각도 오차는8.12°(순변위≥5mm508건), 순간 이동 접촉합력 오차66.68°다. 초기1초 합력 오차18.47°·남은30–60mm 구간86.54°로 시점/거리 차이가 커, 순간 힘 오차를 전체 이동 각도나 정책 의도로 대체하지 않았다.

목표 밖 이동 중 접촉96.29%, 전체 유효 step 접촉74.03%. 최초 접촉→최초 목표 진입(미진입이면 종료) 접촉률은 유효511episode 평균95.95%·최장 접촉 공백 P950.14초다. 전체 대기·접근을 포함하는 지표와 이동 중 지표를 구분했다.

양의 기여 예산+14.833·음의 기여−2.355·순보상+12.477. Formation+6.853(양의 예산46.20%)·Sweep+6.734(45.40%)이며, Formation22.26%는 실제 타겟 접촉이 없는 step에서 지급됐다. Sweep99.71%는 첫2초에 집중됐다. seed43/env41/episode1은 반경 진입 후 최종41.00mm로 실패해도 순보상+13.773·지속 Formation을 받았다. 이는 보상 식과 최종 성공이 완전히 같은 목적을 평가하지 않는 사례이며, 학습 인과나 의도적 우회라고 단정하지 않았다.

손가락 근접+양방향 정렬(진단 기준5mm·30°) 동시 충족은 엄지0%, 검지35.35%, 중지28.97%, 약지10.79%, 소지5.95%였다. 실제 body 접촉은 중지에서 가장 잦았지만 Formation 기여는 약지가 가장 컸다. distal pad의 가시 OBB gap, 손가락 전체 collider 접촉, 손 관절 각도를 구분했다. 순수 자세 보상에 접촉 gate를 임의로 추가하거나 계수를 바꾸지 않았다.

장애물 있는446건 중 최대 변위≥1cm31건·≥5cm8건,≥1cm 이동을 포함한 성공8건이었다. 최대 변위91.64mm·평균 episode 비용−0.139. 이는 이전 v0_3/7650 결과와 다른 checkpoint·학습 예산이므로 향상 인과를 주장하지 않았다.16개 각 항의 역할·발동 규모·한계는 최종 보고서에서 모두 판정했다.

## 검증·재현 산출물

- Formation raw 독립 오차≤2.3842e−6·실제 step Formation 오차≤1.31e−8, 장애물 step 비용 오차≤7.14e−9, 전체 보상 합 오차≤1.79e−7. Reach·Sweep 증분·힘 정렬도 독립 대조, 성공/TCP 재판정 불일치0.
- 원본 reference와 instrumented seed42 첫20step의 reward·done·joint/object 위치·모든 observation 최대 차이0. 전체512episode 원본 재생 검사가 아니라 prefix 동등성이다. [hook_parity.json](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/hook_parity.json).
- 두 실행 모두7개 Manager의 학습 params/현재 cfg 일치, 각326개 활성 source hash·checkpoint SHA256 재대조 일치. raw terminal에서 방향·성공을 별도 재집계,512개 unique episode·최종 거리 오차0·양/음 예산 합100%·손가락 기여 합 일치. [독립 validation](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/validation.json).
- 실제 PNG에서 최종 분포의 공통 축·성공 경계·direction performance·16항 방향 timeline·손가락/장애물 heatmap·실제 목표 이탈 사례를 확인했다. 성공률 CI와 숫자의 겹침을 수정해 재생성했다.
- 원시 자료·metadata·source snapshot·설정·PNG/SVG·CSV/JSON은 [출력 폴더](../../../../outputs/prof_revision_v0_3_1_analysis_20261126/direction_summary.json)에 있다. 분석 스크립트2개는 Sim 의존성 없이 이 원시 자료에서 재생성한다.

```powershell
python src/inspire_sweep_baseline/scripts/report_prof_revision_play.py --root outputs/prof_revision_v0_3_1_analysis_20261126 --runs seed42 seed43
python src/inspire_sweep_baseline/scripts/analyze_prof_revision_directions.py --root outputs/prof_revision_v0_3_1_analysis_20261126 --runs seed42 seed43
python src/inspire_sweep_baseline/scripts/report_prof_revision_directions.py --root outputs/prof_revision_v0_3_1_analysis_20261126 --output example/Contact-Rich-Manipulation-Context/02_implementation/experiments/2026-11-26_prof_revision_v0_3_1_play_analysis.md
python outputs/prof_revision_v0_3_1_analysis_20261126/validate_analysis.py
```

위치·보상 일치와 센서의 물리적 충실도는 구분했다. 이동 접촉합력 norm 최대1,645N와 raw/pure wrist force 최대73.63/82.98N은 서로 다른 물리량·표본 조건이므로 최대값 차이만으로 원인을 확정하지 않는다. 앞선 F/T 문제의 해결·실물 전이·다른 checkpoint·방향의 순수 인과 효과·부모 대비 개선·장기 재학습은 미검증이다.

완료 검사: 변경/신규 Python3개 `py_compile` 통과. 변경 Markdown5개 수식 검사 통과, external 파일 포함 링크 검사 오류0(외부33·내부251), workspace/문서 저장소 `git diff --check` 통과. Git LF→CRLF 안내는 whitespace 오류가 아니다. 독립 `validation.json`은 passed이며, 위 수집/센서/일반화 범위의 제한을 유지한다.
