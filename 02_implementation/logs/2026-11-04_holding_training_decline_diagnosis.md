# Holding 학습 성공 지표 하락: backup 및 TEMP 분석

## 요청·범위·전후

사용자는 Holding 계열의 4000 iteration 이후 성공률 하락과 보상/페널티 적응의 관계를 검토하도록 요청했다. 최초 지정 `logs/backup`에는 해당 장기 하락 실행이 없었으며, 사용자 후속 지정 `logs/TEMP`에서 두 관련 장기 실행을 찾았다. 실행 코드와 원본 로그를 변경하지 않고 읽기 전용 분석을 수행했다. 재학습·정책 수정은 요청 범위에 포함하지 않았다.

Workspace 기준 commit `ba1aa88bf462c5263531379b0a67248ad2439552`. 기존 문서 작업과 사용자 untracked 로그 분류 파일을 보존했다. 분석 스크립트·CSV·JSON은 workspace `outputs/holding_backup_diagnosis/`에 추가했다.

## 원본과 재현

- OSC-v2: `logs/TEMP/inspire_contact_sweep_clutter_fusion_holding_osc_v2/2026-10-24_02-46-06`, step1900~21669. 저장 commit `e3fe8e33f0757254ef7b44fc296c9fcb0d5bdd01`.
- ObjectRandom-v2: `logs/TEMP/inspire_contact_sweep_clutter_fusion_holding_osc_object_random_v2/2026-10-25_01-26-24`, step0~11145. 저장 commit `b6910a6c1b480eafcace5cead5695b2dcd657869`.
- ObjectRandom-v3: step0~11999이나 success termination/tag가 없으므로 성공률 비교에서 제외.
- 나머지 TEMP Holding 4개 실행은 최대2448 iteration으로 해당 하락 구간 미포함. 전체 TEMP Holding 이벤트7개.
- backup의 OSC-v2 `2026-10-24_02-43-09`는 별도 실행이며 위 TEMP 실행과 합치지 않는다. backup에는 별도 ObjectRandom-Test-v0 단기 실행도 있다.

```bash
python outputs/holding_backup_diagnosis/analyze_temp.py
python outputs/holding_backup_diagnosis/summarize_temp.py
```

스크립트는 TensorBoard scalar 전체를 reservoir 축소 없이 추출하며 시간축 `/time` 중복 태그는 제외한다. `temp_results/summary.json`에는 입력 SHA256, 범위, 태그별 개수·중복·비유한값·누락과250-step 구간평균이 있다. `full_windows1000.json`은 완전한1000-iteration 구간만 평균한다. CSV는 iteration 단위 원시 scalar다. 기존 backup 분석의 동일 폴더 `summary.json`과 TEMP 하위 파일을 구분한다.

첫 TEMP 추출 시 success 없는 v3 출력에서 KeyError, 재개 구간의 빈 bin 출력에서 TypeError가 발생했다. 출력 처리와 시작 bin을 수정한 뒤 전체7개 추출을 완료했다. 분석 대상 장기2개는 중복 step·누락 step·비유한 scalar가 없다. 단기2개 실행의 Loss/value에 각1개 비유한값이 있으며 주 분석에는 포함하지 않았다.

## 정의·비교 제한

성공률 표기는 TensorBoard `Episode_Termination/success`의 iteration별 기록을 구간 산술평균한 값이다. 독립 고정 난이도 평가 성공률이나 원시 episode 건수로 재집계한 비율이 아니다. 로컬 Isaac Lab TerminationManager는 환경별 마지막 종료 상태 평균을 기록하며 runner 집계도 적용되므로 이를 독립 Bernoulli 표본으로 해석하거나 신뢰구간을 만들지 않았다.

`Episode_Reward/*`는 weight와 dt가 적용된 episode 누적값을 최대 episode 길이10초로 나눈 scalar다. 실제 episode 길이로 나눈 보상률과 다르다. `Train/mean_reward`는 별도 집계창을 사용하므로 항별 합×10과 정확히 같을 필요가 없다. 접촉 보상 증가는 종료 지연에 따른 누적시간 증가를 포함한다.

실행별 저장 env.yaml과 실제 Curriculum 태그를 대조했다. 주요 보상·성공 함수는 저장 commit의 `git show`로 확인했다. 코드에는 목표 반경 축소와 장애물 증가, ObjectRandom-v2의 누적3초 Hold 지급 상한, 속도≤0.01m/s·연속3초 성공 조건이 있다. 원시 거리·속도 궤적, 접촉 대상별 분해, 물체 비용의 기울기/변위 분해, 고정 반경 재평가 결과는 없다.

## 관측 결과

| 실행 / 구간 | 성공 지표 | timeout | Train mean reward |
| --- | ---: | ---: | ---: |
| OSC-v2 3000~3999 | 41.80% | 57.43% | 32.45 |
| OSC-v2 4000~4999 | 40.03% | 58.58% | 30.20 |
| OSC-v2 8000~8999 | 24.85% | 72.73% | 28.95 |
| OSC-v2 10000~10999 | 17.56% | 80.48% | 27.70 |
| OSC-v2 20000~20999 | 4.94% | 92.70% | 25.42 |
| Random-v2 4000~4999 | 33.78% | 58.89% | 18.53 |
| Random-v2 8000~8999 | 18.81% | 70.91% | 11.75 |
| Random-v2 10000~10999 | 11.84% | 79.85% | 15.08 |

OSC-v2 3000대→20000대의 Episode_Reward 값:

| 항목 | 이전 | 이후 | 해석 |
| --- | ---: | ---: | --- |
| goal_hold | 1.19340 | .18006 | 큰 감소; 목표 반경/속도scale도 강화되어 행동 퇴행만의 증거는 아님 |
| goal_distance | 1.31480 | 1.35365 | 최단 거리 개선량은 유지; 종단 정착을 뜻하지 않음 |
| hand_contact | 1.05372 | 1.30381 | 증가; 전체 손 접촉 OR 목표 점유, episode 연장 영향 포함 |
| arm_action_rate | −.20734 | −.12315 | 비용 감소 |
| hand_action_rate | −.12498 | −.07641 | 비용 감소 |
| shelf_collision | −.10870 | −.06541 | 비용 감소 |
| object | −.25353 | −.38016 | 전체 기간에는 악화; 물체 비용 회피를 전체 원인으로 단정하지 않음 |
| object_acceleration | −.000143 | −.003358 | 다른 주요 비용에 비해 작음 |
| obstacle_contact | −.00000860 | −.000453 | 작음 |
| wrench_change | −.000000190 | −.00000889 | 극히 작음 |

OSC-v2 13000대→19000대는 reward26.13→26.22로 유지되나 성공12.83→5.40%. goal_hold 변화−.23152를 object 비용 개선+.11665, hand_contact+.06921, hand_action_rate+.01954 등으로 상쇄한다. 반경은 이 동안에도 축소된다.

Random-v2 8000대→10000대는 reward11.75→15.08, 성공18.81→11.84%. reward 항별 변화 합+.32809의 주요 성분은 object+.32102, hand_contact+.10433, goal_hold−.08038, arm_action_rate−.01927, EEF speed−.01045다. 즉 총보상 회복의 산술적 주성분은 물체 비용 개선이며 정착 개선이 아니다. 낙하 지표9.92→7.07%로 개선되나 timeout70.91→79.85%로 증가한다. object는 합산 비용이므로 기울기와 장애물 변위 중 무엇에 적응했는지는 분해 불가.

## 해석·가설 우선순위

1. 확인된 난이도/지표 변화: 5000부터 성공·Hold 공통 반경2cm→10000의1cm→20000의0.5cm로 축소. 6000 이후 Hold 속도scale도.05→.02. 장애물 개수도 증가한다. 4000 자체가 모든 실행의 단일 보상 전환점은 아니다. Random-v2는4000대 성공이3000대보다 높고5000 이후 하락이 뚜렷하다.
2. 강한 보상 불일치 근거: 전체 손 접촉 보상은 타겟 정착을 요구하지 않으며, 최단거리 개선 보상은 재이탈을 되돌려 차감하지 않는다. 비용 감소와 접촉 누적 유지가 Hold 감소를 상쇄하는 구간이 실제로 존재한다. 이는 산술적 분해이며 정책의 의식적 회피 행동이나 인과를 입증하지 않는다.
3. Random-v2의 추가 구조: 속도가 성공 기준을 넘거나 목표를 드나들어도 양의 Hold 지급이면 누적3초 예산을 소진한다. 성공은 연속3초 저속 유지이므로 목표에 다시 정착할 때 유인이 줄 가능성이 있다. 예산 소진 로그가 없어 실제 빈도 미확인.
4. 낮은 우선순위: wrench/가속도/장애물 접촉 비용을 주원인으로 보는 설명. 평균 지급 크기가 작아 현재 기록의 주 설명으로 뒷받침되지 않는다. 희소한 큰 비용의 gradient 영향까지 배제한 것은 아니다.

다음 인과 검증은 같은 checkpoint의 고정2cm·1cm·0.5cm/고정장애물 평가, terminal 거리·속도·최장 연속 정착시간 기록, contact 대상과 object 비용 분해, 한 항씩 바꾸는 대조 실험이다. 실행하지 않았으며 사용자 승인 요청을 위한 조건으로 삼지 않았다.

## 검증 범위

전체7개 파일 추출 완료, 장기2개 범위·중복·비유한값 확인, 저장설정/커리큘럼/과거 함수 대조, 보상 변화 합계 산술검증을 수행했다. 문서 수식·상대 링크·diff 공백 검사는 별도로 실행했다. 학습 로그 이동·정리, 환경 수정, 체크포인트 재생·재학습, 인과 대조 실험은 수행하지 않았다.
