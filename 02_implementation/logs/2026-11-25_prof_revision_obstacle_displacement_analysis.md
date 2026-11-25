# Prof Revision 3개 checkpoint 장애물 변위 비용 계측 기록

[최종 분석 보고서](../experiments/2026-11-25_prof_revision_obstacle_displacement_analysis.md) · [계통·학습 상태](../environments/PROF_REVISION_FAMILY.md)

## 요청·범위·시작 상태

사용자는 앞서 확인한 v0_1/v0_2/v0_3 체크포인트를 실제 Play하고, 학습 로그와 함께 장애물 이동량·변위 비용·전체 보상 대비 부담을 분석해 현재 비용이 의도보다 너그러운지 판단하도록 요청했다. 환경 수정·보상 계수 변경·재학습 요청은 아니다.

작업 시작 workspace HEAD는 `faed7d7ec2003c7445be80f68bd1a04136f69b24`, 문서 저장소 HEAD는 `36bf0bb5abde92460b669c0a898a831d1c8f5a75`였다. 기존 `IsaacLab`의 untracked 상태를 보존했다. `logs/rsl_rl` 정리·이동·삭제는 하지 않았다.

| 환경 | 원본 run (`logs/TEMP/2026-11-25/` 아래) | 평가 모델 |
| --- | --- | --- |
| v0_1 | `inspire_sweep_prof_revision_v0_1/2026-11-24_18-45-33` | `model_13850.pt` |
| v0_2 | `inspire_sweep_prof_revision_v0_2/2026-11-24_23-02-02` | `model_15200.pt` |
| v0_3 | `inspire_sweep_prof_revision_v0_3/2026-11-24_23-02-44` | `model_7650.pt` |

## 변경 전후·영향

| 대상 | 이전 | 이후·의도 |
| --- | --- | --- |
| `scripts/analyze_obstacle_displacement.py` | 없음 | 기존 terminal-inclusive trace와 TensorBoard 추출값에서 장애물·episode별 변위/비용, 학습 곡선, 고정 경로 민감도, PNG·CSV·JSON 생성 |
| `scripts/report_obstacle_displacement.py` | 없음 | 검토한 집계에서 저장소 형식의 최종 Markdown 보고서 재생성 |
| 기존 `collect_prof_revision_play.py` | 기존 계측기 | 파일 변경 없이 세 checkpoint에 재사용 |
| 환경·MDP·runtime·자산·PPO | 현재 v0_1/v0_2/v0_3 | 변경 없음. Hard/v0_3_1도 변경 없음 |
| 원본 학습 자료 | 모델·TensorBoard·params | 읽기만 수행. checkpoint 해시 재검산 일치, event 파일 해시 보관 |
| 문서 | 기존 계통·v0_3 분석 | 이번 실험 보고서·개발 로그 추가, 현재 인계와 계통 문서에 결과 링크 추가 |

분석 산출물은 [로컬 출력 폴더](../../../../outputs/prof_revision_obstacle_analysis_20261125/summary.json)에 저장했다. 보상·성공 정의를 바꾸거나 사용자 학습 상태 기록을 덮어쓰지 않았다.

## 실제 실행·cohort

Python은 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`, RTX4070·Isaac Sim5.1.0이었다. 세 앱을 순차 실행했고 각64환경·seed42·최초4개 완료 episode, 각256건·총768건을 사용했다. 조기 종료도 포함하고 뒤에 생긴 추가·부분 episode는 제외했다. 정책은 deterministic inference, 원래 observation noise는 유지했다. 총347,749개 유효 policy transition·6,954.98환경초이며 terminal step은 자동 reset 전에 계측했다.

```powershell
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --checkpoint logs/TEMP/2026-11-25/inspire_sweep_prof_revision_v0_1/2026-11-24_18-45-33/model_13850.pt --output-dir outputs/prof_revision_obstacle_analysis_20261125/v0_1_seed42 --num_envs 64 --episodes 4 --seed 42 --headless
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --checkpoint logs/TEMP/2026-11-25/inspire_sweep_prof_revision_v0_2/2026-11-24_23-02-02/model_15200.pt --output-dir outputs/prof_revision_obstacle_analysis_20261125/v0_2_seed42 --num_envs 64 --episodes 4 --seed 42 --headless
python src/inspire_sweep_baseline/scripts/collect_prof_revision_play.py --checkpoint logs/TEMP/2026-11-25/inspire_sweep_prof_revision_v0_3/2026-11-24_23-02-44/model_7650.pt --output-dir outputs/prof_revision_obstacle_analysis_20261125/v0_3_seed42 --num_envs 64 --episodes 4 --seed 42 --headless
```

수집 loop·저장 시간은 각각383.68/393.50/466.42초(앱 기동 제외), 각각2,000policy tick이었다. Omniverse 자산·사용자 Sim/Warp 캐시 접근을 위해 승인된 외부 실행을 사용했다. 평가 GPU 메모리 조건 때문에 found/lost aggregate pair capacity만2^25→2^21로 설정했다. 물리·제어·보상 계수는 그대로다. 각 실행 폴더에 metadata·설정·초기 상태·소스 snapshot·checkpoint SHA256가 있다.

TensorBoard는 checkpoint iteration까지 잘라 최근1,000개 logged iteration을 집계했다. `Episode_Reward/*`가 episode 누적항/고정 최대10초임을 RewardManager에서 확인해×10 환산했다. 로그 표는 iteration별 평균을 동일 가중했고, 모든 실제 episode 수를 재가중한 평균이라고 해석하지 않는다.

## 정량 결과·최종 대조

| 환경 | 장애물 있는 episode | 최대 변위≥1cm | 전체256건 평균 변위 비용 | 평균 양의 보상 | 비용/양의 보상 |
| --- | ---: | ---: | ---: | ---: | ---: |
| v0_1 | 222 | 1 | −0.000988 | +4.244 | 0.0233% |
| v0_2 | 220 | 41 | −0.245368 | +4.737 | 5.1802% |
| v0_3 | 224 | 25 | −0.236750 | +7.607 | 3.1121% |

v0_3의1cm 이상 이동25건 중13건이 성공이었다. 이 집단 비용/양의 보상 합계 비율41.13%와 episode별 비율 중앙값6.91%를 구분했다.1cm 이상·5cm 미만20건은 평균 비용−0.452/+6.070(7.45%)·11성공,5cm 이상5건은−10.189/+4.887(208.50%)·2성공이었다. 큰 지속 이탈에는 이미 큰 비용이 있으나 작은·짧은·늦은 이탈에는 약하다는 판단이다.

v0_2의 env6/episode1은4.80cm 이동·비용−3.049에도 순보상+3.126·성공이었다. env29/episode1은1cm 초과 후0.02초 만에 Joint 속도 실패 종료되어 최대1.41cm 이동에도 비용−0.00148이었다. v0_1의 최대2.61cm 사례는0.70초에 물체 낙하/기울기로 종료되었으며 Joint 종료라고 귀속하지 않았다. 조기 실패 사례는 다른 비용으로 순보상이 음수이므로 행동 전체가 이득이라고 단정하지 않았다.

현재 비용은 활성 비타겟의 초기 위치 대비3D 제곱거리 합×−150×0.02초다. cap0.04는 m²이고 한 물체20cm에서 포화하며, 새768episode의 cap 도달은0step이었다. `obstacle_contact` 비용도 새 Play에서0step이었으나 학습 로그에서는 작게 비영이었다. 손–장애물 합력50N 문턱의 제한을 설명하고 비용0을 충돌0이라고 해석하지 않았다.

기존 v0_3 seed43의256episode를 별도 보조 자료로 재분석했다. 장애물 있는225건 중≥1cm28건·전체 평균 비용−0.749로, 새 seed42의−0.237보다 크다. 드문 큰 사건의 크기와 지속시간에 평균이 민감하다. 세 모델 주 비교 표에는 seed42만 사용했다.

권고는 지속 변위 비용 유지와 최대 이탈 증가분에 대한 즉시 비용 보완이다. 허용오차·계수·성공 guardrail은 예시 민감도이며 확정/적용하지 않았다. weight×2/5/10과 peak 증가 비용의 표는 같은 경로에서의 재계산으로, 재학습 결과나 정책 개선의 인과 예측이 아니다.

## 검증·한계

- 실제 초기 위치·현재 위치·활성 mask에서 비용을 독립 재계산, 최대 step 오차6.23e−9 이하. 실제 함수를 AST로 추출해 타겟 제외·비활성 NaN 제외·3D·다중 물체 합산·cap 경계8사례 통과. [수식 검사](../../../../outputs/prof_revision_obstacle_analysis_20261125/formula_check.json).
- 세 모델 모두 학습 params와 현재 Play 설정의7개 Manager(actions·observations·events·rewards·terminations·commands·curriculum)가 일치하고 checkpoint SHA256 재검산 일치. [입력 검사](../../../../outputs/prof_revision_obstacle_analysis_20261125/final_input_validation.json).
- 첫 reset 장면은 세 모델에서 joint/object/mask/goal 동일. 이후 episode는 행동·종료·reset 소비가 달라 짝지어진 반사실이라고 취급하지 않는다. 새 v0_3와 기존 seed42 첫20step audit는 모든 필드 최대 차이0이며 전체 trajectory 동일성을 주장하지 않는다.
- 완료·step 연속성·초기 위치/mask episode 내 불변·유한 위치·보상 합 검증. 그림은 학습 곡선·cohort timeline·상수 변위 수식·개별 사례를 실제 PNG로 열어 확인했다.
- primary는 seed42의64환경 재사용4회이고 v0_3만 seed43 보조가 있다. 전체 초기 상태 일반화, 다른 checkpoint, 재학습, 실물 전이, 충격 가해 링크·충격량·50Hz 관측 사이 순간 회전은 미검증이다. 앞선 F/T 물리적 충실도 문제도 이번 위치 비용 대조로 해결되었다고 보지 않는다.

완료 검사: 신규 분석 Python2개 `py_compile` 통과. 변경 Markdown4개 수식 검사 통과, 링크 검사 오류0(외부 파일 링크32·내부 링크229), workspace/문서 저장소 `git diff --check` 통과. 표의 연속 행과 그림의 범례·축·사례도 확인했다. Git의 LF→CRLF 안내는 whitespace 오류가 아니다.
