# Collection 병목 진단과 구성 보존 최적화

## 요청·기준

사용자는2048환경에서 collection이5–10초 걸리는 문제를 진단하고, 환경 구성·의미를 바꾸지 않는 개선만 허용했다. 다른 장비의 측정치를 이 장비와 직접 비교하지 않는다. 작업 시작 당시 Relative-IK의 확정 범위·보상·관측과 기존 미커밋 변경을 보존했다.

기존 `logs/rsl_rl/inspire_wrench_refactor_relative_v2_5/2026-11-08_18-24-32`의 TensorBoard 마지막5개 collection은6.79–6.98초, learning은0.318–0.348초였다. 학습 로그와 체크포인트는 읽기만 했다. 모든 신규 실행·체크포인트·프로파일은 workspace `outputs/collection_profile`에 저장했다.

## 재현·측정 방법

RTX4070에서 실제 `scripts/train.py`와 기존 CurriculumOnPolicyRunner/NumericalPPO를 실행했다. Task는 Relative-IK-v0, num_envs2048, seed42, iteration4개, 기존36-step horizon, headless다. 관측·보상·센서·물리·시각화 설정은 그대로다. 진단 wrapper `outputs/collection_profile/profile_train.py`는 실제 learn 호출만 cProfile로 계측하고 종료 전에 저장한다. 환경 step·reset뿐 아니라 정책 추론·PPO update·logging의 함수 호출도 수집한다. 이 wrapper는 학습 구현을 복제하지 않고 train.py를 runpy로 호출한다.

초기4환경 측정에서도 워밍업 후 collection2.34–2.38초가 남았다.2048환경 원본에서는8.76–9.27초가 재현되어 작은 배치의 고정 호출 비용도 조사했다. 가설은 reset/IK·배치의 작은 CUDA 연산, 센서·관측, 물리·OSC, 정책 처리 순으로 실제 프로파일과 대조했다.

각 실행의 `learn.prof`와 `functions.csv`는 모든 계측 함수의 호출 수·자체 시간·하위 호출 포함 시간을 보관한다. CPU cProfile 시간은 GPU 대기 시간을 해당 호출에 포함할 수 있으므로 순수 CUDA kernel 시간으로 해석하지 않는다. 아래 포함 시간 항목은 중첩되므로 단순 합산하지 않는다.

## Relative-IK-v0 비교 결과

| 측정 | 변경 전 | 변경 후 |
| --- | --- | --- |
| collection, 워밍업 제외3회 평균 | 8.951초 | 7.310초 |
| collection, 개별3회 | 8.825 / 8.759 / 9.268초 | 7.189 / 6.965 / 7.775초 |
| reset 전체,36step당 포함 시간 | 4.763초 | 2.914초 |
| IK reset event,36step당 포함 시간 | 2.487초 | 1.333초 |
| IK solve,36step당 포함 시간 | 1.988초 | 0.838초 |
| scene reset,36step당 포함 시간 | 1.815초 | 1.123초 |
| 장애물 search,36step당 포함 시간 | 1.509초 | 0.816초 |
| PhysX fetch_results,36step당 | 1.727초 | 1.865초 |
| 관측 manager,36step당 | 0.606초 | 0.620초 |
| Arm action apply,36step당 | 0.463초 | 0.466초 |
| IK 박스 갱신,36step당 | 0.274초 | 0.273초 |

collection 평균 약18.3% 개선. warm-up 제외와 함수 프로파일의 전체4회 집계 기준이 다름에 주의한다.4iteration 중144step에서141번 부분 reset이 발생했다. 최적화 실행의 reset 배치는 평균4.49개, 최대10개였으며137회가8개 이하였다. 따라서 전체환경2048개와 실제 reset 연산 배치 크기는 전혀 다르다.

## 학습된 Relative-v2_5 추가 비교

동일한 기존 `model_450.pt`, seed42,2048환경으로 iteration450–453을 양쪽에서 실행했다. 원본 비교는 진단 wrapper의 `COLLECTION_REFERENCE=1`로 CPU fast path만 끈다. 동일 solver·search의 CUDA 원본 경로이며 환경 설정은 변경하지 않는다.

| 측정 | CUDA 원본 경로 | 최적화 |
| --- | --- | --- |
| collection, 워밍업 제외3회 | 7.788 / 7.340 / 8.156초 | 7.817 / 7.228 / 6.785초 |
| collection 평균 | 7.761초 | 7.277초 |
| reset 전체,36step당 | 2.559초 | 2.041초 |
| 장애물 search,36step당 | 1.625초 | 1.027초 |
| PhysX fetch_results,36step당 | 2.074초 | 2.131초 |
| 관측 manager,36step당 | 1.330초 | 1.311초 |
| Arm action apply,36step당 | 0.532초 | 0.540초 |

이번 짧은 실행의 collection 평균 차이는약6.2%다. 실행별 변동과 학습 trajectory 차이가 있으므로 보장 개선율로 표현하지 않는다. 원본은143회 reset/평균6.54개, 최적화는141회/평균6.65개였다. 부동소수점 차이와 PhysX 비결정성으로 이후 학습 trajectory가 비트 단위로 일치하지 않을 수 있으며 이 비교를 동일 trajectory 재생이라고 부르지 않는다. 두 실행의 전체 EnvCfg/PPO YAML도 log_dir을 제외하고 동일했다. 실제 접촉이 많은 정책에서는 촉각·물리 비용이 커지며, IK 없는 계열에서는 IK 최적화의 이득이 없다.

함수별 전체 결과: [IK 원본](../../../../outputs/collection_profile/baseline2048/functions.csv), [IK 최적화](../../../../outputs/collection_profile/optimized2048/functions.csv), [학습된 v2_5 원본](../../../../outputs/collection_profile/trained_reference2048/functions.csv), [학습된 v2_5 최적화](../../../../outputs/collection_profile/trained_optimized2048/functions.csv). 같은 폴더의 learn.prof는 caller/callee 분석용 원본이다.

## 적용한 변경

1. `mdp/common/wrench_refactor_ik.py`: CUDA IK 배치128개 이하만 동일한 DLS 계산을 캐시한 CPU chain에서 수행한다. USD joint frame·seed·관절 한계·반복 상한80·damping·step cap·수렴 오차는 그대로다. 입출력 전송을 포함한 실험에서1–128개 배치의 CPU 계산은 약28–40ms, CUDA는약56–83ms였다. 큰 배치는 기존 CUDA 경로를 사용한다. CPU chain은 첫 사용 시 실제 chain tensor를 복사하며 임의 로봇 치수를 사용하지 않는다.
2. `mdp/common/bbox_scene_layout.py`, `wrench_refactor_layout.py`: Refactor reset의 장애물 search는 배치8개 이하만 CPU로 실행한다. 난수는 원래 CUDA generator에서 원래 호출 순서·shape로 모두 생성하고 전달한다. 후보64·restart4·pass2·zone 규칙·margin·실패 재시도·tie 선택은 보존한다. 일반 layout 호출자는 기본 비활성이라 영향이 없다. 원본 RNG 최종 state와 active/actual/complete/zone 결과의 일치를 검증했다.

장애물 search의32/64개 CPU 후보는 각각약91/119ms로 GPU약44/46ms보다 느려 채택하지 않았다.8개 이하는약17–35ms로 GPU약45–47ms보다 빨랐다. Scripted IK prototype도 비교했으나 작은 추가 이득을 위해 별도 solver 구현을 유지하는 방식은 채택하지 않았다. prototype들은 `outputs/collection_profile/prototypes`에 진단 전용으로 보관한다.

## 계약 대조·검증

변경 전후 실제 train.py가 저장한 전체 `env.yaml`, `agent.yaml`은 출력용 log_dir을 제외하고 동일했다. 환경 수·dt·decimation·36step horizon·reset 조건/시점·장애물 개수·자산·접촉 센서·보상 계수·관측 noise·목표/IK 위치 분포·박스·PPO 설정을 바꾸지 않았다. CUDA generator state도 보존한다.

CPU/CUDA의 부동소수점 연산 차이는 존재한다. IK 관절각 차이는 비교 배치에서약1.1e-5rad 이하, layout 좌표 차이는약3e-8m였다. 비트 단위의 전체 trajectory 동일성을 주장하지 않으며, 같은 알고리즘·난수·배치 판정과 기존 수렴 오차 내 동등성을 검증했다.

`test_wrench_refactor.py`, `test_wrench_refactor_ik.py`, `test_bbox_scene_layout.py`:119개 통과(CUDA 비교 포함). 공유 layout 영향 범위를 확인하는 `test_final_obb_layout.py`, `test_revision_layout.py`도9개 통과했다. 총128개다. 회귀 테스트는 실제 CPU 전송 경로의 IK 해·수렴/도달 불가능 판정, batch1/8/9의 layout RNG state·선택 결과·좌표를 비교한다. 기존 FK/Jacobian·보상·전체 상속 설정·독립 polygon collision 검사도 포함한다. 임시 `[DEBUG-collection]` 코드 alias는 제거했고 production runner와 train.py에는 변경이 없다.

## 유지한 비용과 한계

물리 step, OSC, 접촉점 기반 촉각, 보상·실패 판정, 매 episode의 새로운 장애물 배치와 시각화는 사용자 환경의 구성이다.1–2초를 목표로 이 항목들을 제거하거나 물리 빈도·환경 수·후보 수·센서 수·reset 빈도를 줄이지 않았다. 예시 환경과의 차이를 단순 GPU 성능만으로 설명할 수 없다. 본 수치는 단일 장비의 짧은 계측 실행이며 Blackwell 장비나 장기 학습 처리량을 검증한 결과가 아니다.
