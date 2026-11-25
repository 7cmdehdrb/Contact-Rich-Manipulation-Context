# Prof Revision v0_3 실제 Play 분석·계측 기록

[최종 실험 보고서](../experiments/2026-11-25_prof_revision_v0_3_play_analysis.md) · [환경 계약](../environments/PROF_REVISION_V0.md#prof-revision-v0_3)

## 요청과 변경 범위

사용자는 `Inspire-Sweep-Prof-Revision-v0_3`를 직접 Play하면서 각 보상 timeline, 접촉 유지, 힘 방향, 손가락 자세, 성공률 등 수집 가능한 동작을 분석하고 최종 보고서로 검증하도록 요청했다. 새 환경 생성·보상 수정·학습 요청은 아니다.

작업 시작 HEAD는 workspace `464b01570a8f73a2b1abf1a426f5eb70e5e30f68`, 문서 저장소 HEAD는 `809a2c7a4acf0ce639a87054d4fa5c632990c001`이다. 기존 IsaacLab submodule의 untracked 상태와 작업 중 나타난 `docs/plan/PLAN21.md`는 보존했다. 학습 checkpoint가 기록한 commit `c8df111ce9c59636b2386ad7971df423a2b2b506`과 현재 HEAD 사이 활성 패키지 코드 차이는0이다.

## 전후 차이와 영향

| 대상 | 이전 | 이후 / 의도 |
| --- | --- | --- |
| `scripts/collect_prof_revision_play.py` | 없음 | standalone read-only 정책 계측기. 원래 callable을 각각1회 호출하고 raw·rate·dt 적용 보상·물리·접촉·종료를 자동reset 전에 복사 |
| `scripts/report_prof_revision_play.py` | 없음 | NPZ에서 완료 cohort 집계, confidence interval,16항 timeline과 실제 사례 PNG/SVG·CSV·JSON 생성 |
| 환경/runtime/MDP/자산/PPO | 기존 v0_3 | 파일·함수·수치·상속 변경 없음 |
| 학습 로그·모델 | `logs/TEMP/.../model_7650.pt`와 원본 TensorBoard | 읽기만 수행, checkpoint SHA256 재검산 일치. `logs/rsl_rl` 접근·정리 없음 |
| 문서 | 기존 구현·단기 검증 설명 | 본 로그와 실험 보고서 추가, 환경 설명·인계에 결과 링크 추가 |

실행 시 병렬 수·seed·log_dir와 GPU found/lost aggregate pair capacity만 평가용으로 설정했다. capacity는2^25→2^21이며 원래 물리·제어·보상 수치는 보존했다. 본 분석 frame의 contact valid는 모두 True였다. 활성7개 Manager 구성은 학습 params/env.yaml과 BaseLoader로 비교해 전부 일치했다.

## 실제 실행

실행 Python은 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`, RTX4070, Isaac Sim5.1.0이다. Workspace root에서 실행했다.

```powershell
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --checkpoint logs/TEMP/2026-11-25/inspire_sweep_prof_revision_v0_3/2026-11-24_23-02-44/model_7650.pt --output-dir outputs/prof_revision_v0_3_analysis_20261125/seed42 --num_envs 64 --episodes 4 --seed 42 --headless
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --checkpoint logs/TEMP/2026-11-25/inspire_sweep_prof_revision_v0_3/2026-11-24_23-02-44/model_7650.pt --output-dir outputs/prof_revision_v0_3_analysis_20261125/seed43 --num_envs 64 --episodes 4 --seed 43 --headless
python src/inspire_sweep_baseline/scripts/report_prof_revision_play.py --root outputs/prof_revision_v0_3_analysis_20261125 --runs seed42 seed43 --training-run logs/TEMP/2026-11-25/inspire_sweep_prof_revision_v0_3/2026-11-24_23-02-44
```

각64환경의 첫4개 완료 에피소드만 집계하고 조기 물리 실패도 분모에 포함했다. 이후 추가reset과 부분 에피소드로 성공률을 높이거나 낮추지 않았다. 총512완료,250,526policy step·5,010.52환경초다. loop·저장 시간은 seed42=215.36s, seed43=215.05s이며 앱 기동 제외다.

원격 선반 기본 경로 `omniverse://192.168.0.13/.../speedrack_shape.usd`와 Isaac Sim 사용자 캐시 접근 때문에 sandbox 안의 첫 smoke는 자산 로딩 단계에서 대기했다. 해당 session을 중지하고 자동 승인된 외부 실행으로 동일 자산을 읽어 진행했다. 실패한 첫 smoke 폴더와 로그는 보존했고 본 표본에는 포함하지 않았다. 환경 코드나 자산 경로를 바꿔 대체하지 않았다.

추가 smoke는4환경20step의 original/reference와 instrumented 최종 버전을 비교했다. reward·done·joint_pos·object_pos·policy observation·obstacle observation의 최대 절대 차이는 모두0이었다. `hook_parity_final.json`에 기록했다.

## 추가 F/T 대조

seed43에 target-only collider별 normal force를 추가 복사했다. seed42에는 해당 필드가 없어 손가락별 실제 접촉 빈도·하중은 seed43의 미는 frame4,667개로만 계산했다. 거리·패드 방향 진단은 전체 두 seed의9,539개 미는 frame이다. 전용 palm pad collider와 손바닥/손등이 포함된 base hull을 구분했다.

드문 kN 접촉 하중과 거의0인 보정 F/T가 함께 나타나 원본과 같은 seed43·64환경·1,600step을 `--wrench-diagnostics`로 추가 재생했다. 이 실행은 본 성공률 분모에 추가하지 않았다. 전체 손 법선력, target normal, raw/support/pure wrench를 같은 최종 substep에서 대조했다.

```powershell
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --checkpoint logs/TEMP/2026-11-25/inspire_sweep_prof_revision_v0_3/2026-11-24_23-02-44/model_7650.pt --output-dir outputs/prof_revision_v0_3_analysis_20261125/wrench_focus --num_envs 64 --episodes 4 --steps 1600 --seed 43 --wrench-diagnostics --headless
```

추가 계측과 기존 seed43의 첫1,600step force·reward·action·target은 bitwise 동일했다.102,020개 유효 transition에서 최종 타겟 힘>100N인 frame73개,9개 에피소드가 확인됐고 그중62개는 보정 F/T<0.1N이었다. 최대 사례는 env35/episode3/step73에서 target total3367.56N, whole-hand normal3290.73N, raw/support 각9.7265N, pure6.96e−7N이다. 다른 법선 접촉의 단순 상쇄와2substep 평균의 차이만으로 설명되지 않았다. raw incoming-joint-wrench 경로·API/cache·물리 모델 중 정확한 원인은 미확정이다. 수정은 하지 않았다.

## 정량 결과와 최종 대조

- 성공389/512=75.9766%; cluster bootstrap95%72.27–79.49%. 구역3은35/89=39.33%.
- 이동 frame 접촉96.60%, 실제 미는 frame 힘30° 이내63.99%,90° 초과17.47%.
- Sweep 진행 보상99.86%가 초기2초 안에 발생. 목표에 진입한451회 중62회 최종 실패.
- 약지 중심 접촉·자세, 엄지·소지 기여 약함. v0_3 Formation은 거리 합이며 각도·실제 접촉을 강제하지 않는 계약과 구분했다.
- 물체 실패6회·선반 실패9회·TCP 실패0회. TCP 최대0.6561m/s라4m/s 실발동은 검증되지 않았다.
- 보상 합 오차≤4.77e−7, rate 오차≤5.97e−8, 독립 Sweep 증분 오차≤1.87e−9. 성공·TCP 재판정 불일치0.
- 학습의 성공 log·timeout-only 성공 log와 deterministic 전체 완료 성공률의 분모 차이, Episode_Reward 로그의10초 정규화를 명시했다.

환경·Manager·runtime·PPO는 작업 전후 변경0이다. 활성 Python 소스 manifest와 checkpoint hash를 두 수집 모두 끝에서 확인했고 독립 `validate_results.py`로 원시 종료 flag·최종 거리·보상 합·episode CSV까지 재검산했다. `validation.json` status는 passed다.

## 산출물·검증 범위

최종 보고서는 실험 문서에, 원시 NPZ·초기 물리 상태·실행 metadata·config YAML·현재 코드 snapshot·CSV·PNG/SVG·독립 audit script는 [로컬 분석 폴더](../../../../outputs/prof_revision_v0_3_analysis_20261125/summary.json)에 있다. 기존120초3시점 영상은 동일 checkpoint의 별도1환경 자료로만 인용하며64환경 표본과의1:1 대응을 주장하지 않았다.

시각 QA는 보상 timeline, 성공·접촉, 손가락, 힘 이상값, 개별 사례를 실제 PNG로 확인했다. Markdown의 수식·내부/외부 파일 링크·diff whitespace 검사를 수행하고 결과는 작업 완료 시 아래에 기록한다. 원격 USD revision 전체·PhysX solver state·실물 전이·다른 checkpoint·장기 수렴·F/T 불일치의 원인/수정은 검증하지 않았다.

완료 검사: 두 신규 Python 파일 py_compile 통과, 독립 원시 재검산 `validation.json` passed. 변경 Markdown4개의 math 검사 통과, external 파일까지 포함한 변경 문서 링크 오류0, 문서 저장소 전체682개 Markdown·CSV/XLSX 자료 링크 검사 오류0, workspace/문서 저장소 `git diff --check` 통과. Git의 LF→CRLF 안내는 whitespace 오류가 아니다. 보고서는 계산·출처·정해진 성공률에 대해 준비됐고, 센서의 물리적 충실도와 실물 전이에는 본문의 제한을 유지한다.
