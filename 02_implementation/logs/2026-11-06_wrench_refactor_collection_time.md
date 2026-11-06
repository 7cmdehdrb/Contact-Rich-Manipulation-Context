# Refactor v3 Collection Time 증가 조사

2026-11-06. 사용자 관찰: v3는 v2에서 제어만 바뀌었는데 Collection Time이 약2배로 증가했다. 이번 작업은 원인 조사와 측정이며 환경·학습 코드 변경을 요청받은 것은 아니다. diagnosing-bugs 절차에 따라 기존 로그의 신호를 확인하고 동일 장비 A/B 측정으로 제어 비용을 분리했다.

## 기존 학습 로그의 관찰

`logs/TEMP/wr2`의 v2 `2026-11-06_01-41-15`와 v3 `2026-11-06_01-42-12`를 읽었다. TensorBoard EventAccumulator로 Perf/collection_time, Perf/learning_time, Train/mean_episode_length를 추출했다. iteration1000–3999의각3000개샘플 중앙값은 다음과 같다.

| 항목 | v2 | v3 | v3/v2 |
| --- | ---: | ---: | ---: |
| Collection time | 4.0515초 | 7.3079초 | 1.804배 |
| Learning time | 0.1667초 | 0.3477초 | 2.086배 |
| Mean episode length | 107.55step | 106.49step | 약0.99배 |

v2 이벤트 호스트는 `ssu-System-Product-Name`, v3는 `min-System-Product-Name`다. 저장된자산/log경로도 `/home/ssu/Desktop/Contact-Rich-Manipulation`과 `/home/min/7cmdehdrb/grad`로다르다. 동일 장비 비교가 아니다. 상대 장비GPU모델/당시GPU부하/드라이버/코드세부버전은이로그만으로확정하지않는다. Learning time도약2배인것은 OSC 제어단독원인설명과맞지않으며실행환경교란을의심하게한다.

BaseLoader로저장된env.yaml전체를비교하면차이는오른손USD절대경로, log_dir, actions.arm_action.class_type뿐이다. agent.yaml차이는experiment_name뿐이다. 환경수2048, rollout36step,dt0.01,decimation2는같다. 절대경로가다르므로두USD내용까지동일하다고검증한것은아니다.

현재추가된OSC/페널티/종료print는cfg type이WrenchRefactorV3TestEnvCfg일때만실행되며일반v3에는활성화되지않는다. 기존학습이벤트도이번진단print추가전에생성됐다.

## 가설과 검사

1. 다른장비/부하가전체학습속도차이를만든다: 동일장비측정시큰차이가사라질것으로예측.
2. v3의EEF변환/Jacobian/velocity추가연산이주원인이다: 동일물리상태에서실제action코드만측정해도큰차이가나야함.
3. 제어가바뀌어접촉/reset비용이증가했다: 제어단독측정과전체rollout측정의차이및reset수를기록해구분.

프로덕션코드에새계측을추가하지않고 `outputs/wrench_refactor_collection_diagnosis/benchmark.py`에독립harness를작성했다. 앱초기화비용은측정에서제외한다. RTX3090·동일프로세스·2048환경에서하나의v3환경을생성하고action객체의class를v2기본클래스/v3클래스로전환한다. cfg·로봇·physics scene·joint/dynamics buffers는같다. v2전환시task frame을None으로되돌리고v3는기존로직으로EEF frame을설정한다. 종료후원래class를복구하고별도프로세스를닫는다.

고정물리상태의제어측정은36회process_actions+각2회apply_actions이며, ABBA순서를3회반복했다. GPU동기화로wall time을측정했다. 전체rollout은매조건seed42reset·8step워밍업후36step을측정하고ABBA순서로반복했다. 동일zero Arm action·Hand openness1이며정책추론/PPO업데이트는포함하지않는다. 전체rollout에서는제어에따라물리궤적/reset이달라질수있으므로reset수와비용도기록했다.

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH /home/min/miniconda3/envs/env_isaaclab/bin/python outputs/wrench_refactor_collection_diagnosis/benchmark.py --num_envs 2048 --headless --device cuda:0 > outputs/wrench_refactor_collection_diagnosis/benchmark.log 2>&1
```

## 측정 결과

| 36step 구간 중앙값 | v2 | v3 | v3/v2 |
| --- | ---: | ---: | ---: |
| 고정상태의제어코드만 | 0.35935초 | 0.29665초 | 0.826배 |
| 물리/관측/보상/reset포함rollout | 3.78346초 | 3.77696초 | 0.998배 |

제어코드단독에서는v3가약17.4%빨랐고, 전체rollout에서는차이가약0.2%였다. v2의두rollout은reset대상2048/2046개, reset호출1/2회, reset wall0.136/0.222초를기록했다. v3의두rollout에서는reset이없었다. 조건별episode궤적이동일하다고주장하지않는다. 동일상태제어측정은물리step을하지않으므로입력상태를공유한비교다.

동일장비에서제어변경만으로Collection이약2배증가한다는현상은재현되지않았다. 기존로그의장비/부하차이가유력한설명이나상대장비상태를확인하지않았으므로정확한원인을확정하지않는다. zero-action의4개36step블록결과이며학습된정책의장시간접촉궤적·다른GPU환경까지일반화하지않는다. 현재코드는기존학습이후목표범위등의사용자변경을포함하므로과거실행을완전히재현한것도아니다.

## 산출물·보존·검증

- `outputs/wrench_refactor_collection_diagnosis/historical_summary.json`: 기존이벤트관찰(표시자릿수4자리).
- `saved_env_diff.json`, `saved_agent_diff.json`: 저장된설정의전체차이.
- `benchmark.py`, `benchmark.log`, `benchmark_result.json`: 실행가능한harness·실제측정·원시반복별결과.
- 종료코드0, 제어단독12블록/전체4블록·2048환경확인, 전체rollout비율<1.5검사통과.
- 기존환경·PPO·제어·보상·출력코드는수정하지않았다. logs/TEMP·logs/rsl_rl과체크포인트도읽기만했다. 독립문서저장소및사용자작업트리를보존했다.

이조사에서제어성능회귀가재현되지않았으므로임의최적화/설정수정/학습은수행하지않았다. 신규프로덕션debug로그가없으며harness는outputs의진단폴더에명시적으로보관한다.
