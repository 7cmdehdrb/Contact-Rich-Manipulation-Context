# v0_3_3/model_8600 충격·장애물 이동 실제 Play 계측 기록

[분석·수치 제안](../experiments/2026-11-27_prof_revision_v0_3_3_impact_analysis.md)

## 요청과 시작 상태

사용자는 `logs/TEMP/2026-11-27/inspire_sweep_prof_revision_v0_3_3`의 체크포인트를 실제 Play하며 부드러운 접촉 허용·큰 순간 충격 억제·장애물 이동 최소화를 위한 임계값과 비용 수준에 대한 의견을 요청했다. 가장 큰 iteration인 `2026-11-26_21-31-25/model_8600.pt`를 선택했다. 환경 수정이나 재학습은 요청 범위에 포함하지 않았다.

workspace HEAD `26312351bce566527e805b2f71f2caf18bcd756f`, 문서 HEAD `9ed8eafc2bda9e1ca30035acbf1d962ba1ca581f`. 시작 시 기존 `IsaacLab` untracked 표시를 보존했다. 원본 checkpoint·params·학습 로그는 읽기만 수행했고 `logs/rsl_rl`에는 접근·정리·기록하지 않았다.

## 변경 전후와 영향

| 파일 | 변경 전 | 변경 후·의도 |
| --- | --- | --- |
| `scripts/collect_prof_revision_play.py` | 정책step·타겟 접촉 substep 계측 | 선택 옵션 `--impact-diagnostics` 추가; 객체별 손 접촉 normal vector/load,whole-hand load,raw/support/pure wrench를 매 물리step 복사 |
| `scripts/analyze_prof_revision_impact.py` | 없음 | terminal 포함 episode별 접촉·변위·비용,고정 궤적 민감도,CSV/JSON/PNG 생성 |
| 환경 패키지·PPO·보상 수치 | v0_3_3 | 변경 없음 |
| 문서 | 관련 기록 없음 | 실험 보고서·본 개발 로그·현재 인계 링크 추가 |

기존 collector 호출은 새 옵션을 주지 않으면 기존 실행 경로를 유지한다. source snapshot과 CLI를 실행 폴더에 저장했다. 계측은 기존 보상을 정확히 한 번 호출한 후 복사하고 terminal reset 전에 기록한다. 추가 wrench read는 기존 물리 sample을 읽으며 물리·관측·보상 설정을 변경하지 않는다.

## 실행

Python: `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`,RTX4070. 기본 sandbox 실행은 사용자 Sim 설정 저장 접근 오류와 자산 초기화 정체로 중단했다. 해당 작업이 시작한 프로세스만 종료하고 승인된 외부 실행으로 재시작했다. 실패 경로 `outputs/prof_revision_impact_20261127/seed42`는 평가 자료에서 제외했다.

작업 디렉터리는 workspace 루트다. 아래 `python`은 위 Isaac Lab 환경 Python이다.

```powershell
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --task Inspire-Sweep-Prof-Revision-v0_3_3 --checkpoint logs/TEMP/2026-11-27/inspire_sweep_prof_revision_v0_3_3/2026-11-26_21-31-25/model_8600.pt --output-dir outputs/prof_revision_impact_20261127/seed42_live --num_envs 64 --episodes 4 --seed 42 --headless --wrench-diagnostics --impact-diagnostics
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --task Inspire-Sweep-Prof-Revision-v0_3_3 --checkpoint logs/TEMP/2026-11-27/inspire_sweep_prof_revision_v0_3_3/2026-11-26_21-31-25/model_8600.pt --output-dir outputs/prof_revision_impact_20261127/seed43_live --num_envs 64 --episodes 4 --seed 43 --headless --wrench-diagnostics --impact-diagnostics
python src/inspire_sweep_baseline/scripts/analyze_prof_revision_impact.py --root outputs/prof_revision_impact_20261127
```

완료 episode512개,policy transition254,609개,physics sample509,218개다. 각 seed에서64개 환경을4회 재사용했으므로512개 독립 seed를 평가한 것은 아니다. headless로 실행했고 영상을 녹화하지 않았다.

## 최종 대조와 검증

- 두 run의 actions·observations·events·rewards·terminations·commands·curriculum이 학습 params와 일치했다. checkpoint SHA256 `fbf9930150501603bed7a47a82f9d4cbe3ae5cb9aa4142f1afb605de26a28282` 일치.
- 각 환경의 최초4완료episode·terminal 포함,step연속·초기 위치/mask 불변 검사 통과.
- 실제 raw 입력에서 비용 독립 재계산: 장애물 변위 최대1.88e−8,접촉·손목0,보상합3.58e−7 오차.
- [수식 검사](../../../../outputs/prof_revision_impact_20261127/formula_checks.json): 실제 AST 추출 callable과 독립 scalar 계산의 허용 경계·포화16개 사례,일정 크기 방향반전의 기존 비용0,최대 이탈 비용의 경로 합1.8 검증.
- seed42의 계측 없는 원래 Play20step과 reward·done·관절/물체 상태 동일,policy관측 최대차2.33e−10. [대조 결과](../../../../outputs/prof_revision_impact_20261127/reference_audit.json).
- 추가 substep 계측을 끈 `recheck43`1110step에서도 env14/episode2의policy step102에 타겟 normal301.24/842.90N(두 substep),정책시점 손목 힘9.87e−7N이 재현됐다. 다음step 첫substep은1,273.56N이었다. **장시간 궤적의 완전 동등성은 성립하지 않았다**: action 최대차4.314,물체위치 최대차22.86mm,보상 최대차0.6943. action의1e−6초과 차이는tick4,1e−2초과 차이는tick51부터다. 관측 읽기 시점·수치적 실행 차이와 증폭의 정확한 원인은 확정하지 않았다. 같은 궤적 재현이 아니라 기존 계측 경로에서도 큰 F/T누락이 나타나는 독립 재현으로 해석한다. [실제 차이와 재현값](../../../../outputs/prof_revision_impact_20261127/late_recheck.json).
- 계측 전후 환경 패키지의 source manifest 모든 파일 해시 일치. 변경은 계측/분석 스크립트와 문서에 한정된다. [해시 대조](../../../../outputs/prof_revision_impact_20261127/source_preservation.json).
- Python2개 `py_compile`,변경Markdown3개 수식 검사,외부링크 포함 링크 검사,workspace/문서 `git diff --check` 통과. overview·최대접촉·최대변위·타겟충격 PNG를 직접 열어 축·범례·누적 비용·사례 일치를 확인했다.

재현/계측 대조 명령:

```powershell
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --task Inspire-Sweep-Prof-Revision-v0_3_3 --checkpoint logs/TEMP/2026-11-27/inspire_sweep_prof_revision_v0_3_3/2026-11-26_21-31-25/model_8600.pt --output-dir outputs/prof_revision_impact_20261127/reference42 --num_envs 64 --episodes 1 --steps 20 --seed 42 --headless --reference
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --task Inspire-Sweep-Prof-Revision-v0_3_3 --checkpoint logs/TEMP/2026-11-27/inspire_sweep_prof_revision_v0_3_3/2026-11-26_21-31-25/model_8600.pt --output-dir outputs/prof_revision_impact_20261127/recheck43 --num_envs 64 --episodes 4 --steps 1110 --seed 43 --headless --wrench-diagnostics
```

## 결과와 미검증

과업 성공477/512. 장애물 존재452회 중1cm 이상 이동34회,그중17회 성공. 접촉 비용0step·손목 비용2step·변위cap0step. 현재 허용값이 대부분의 충격을 통과시키고,작고 짧은 이동 비용의 구조적 한계가 있다. 새 후보5N·5N·0.3Nm,손목 최대step0.2,장애물2mm초과 최대 이탈 증가100/m는 고정 궤적에서 재계산했다. 적용·재학습하지 않았다.

가장 중요한 한계는 큰 타겟 접촉과 raw incoming-joint wrench/F/T 불일치다. 일반 구간의 일치로 전체 충격 감지 신뢰도를 주장하지 않는다. 원인 확정·센서 수리·실물 물리 교정·장기학습 개선은 미검증이다. 기록된 샘플은10ms 구간의 PhysX출력이며 실제 연속시간 peak의 측정치가 아니다.
