# 2026-11-05 패키지 환경 계열별 요약 문서

## 요청·의도

사용자가 `src/inspire_sweep_baseline/inspire_sweep_baseline`의 환경 전체를 다시 떠올릴 수 있도록 workspace `docs` 아래 새 폴더에 계열별 문서 N개와 통합 안내 1개를 요청했다. 베이스 환경의 관측·환경 구성·보상·터미네이션·커리큘럼, 직접 부모 및 파생 시 변경점을 간결하게 정리하는 작업이다. 사용자의 명시적 목적지에 따라 본문은 [docs/environments](../../../../docs/environments/README.md)에 두고 이 저장소에는 개발 기록만 남긴다.

## 변경 전후

- 전: `docs`에는 시스템/도구 안내만 있고 이 패키지 전체 환경의 계열별 요약과 등록 색인이 없었다.
- 후: `docs/environments`에 계열 13개 문서와 통합 안내 1개를 생성하고 `docs/README.md`에 진입 링크를 추가했다. 전체 75개 등록 ID와 75개 EnvCfg를 포함한다.
- 계열: Sweep, Omni, Renewal, Contact Sweep, Clutter, Fusion, Holding, Holding OSC, ObjectRandom, Final, GoalAccuracy, Revision, Wrench.
- 기준: 2026-11-05 작업트리의 실제 `__init__.py`, EnvCfg, Scene/MDP 설정, 필요한 실행 함수, runtime 및 PPO 관측 라우팅. 과거 백업이나 이전 패키지의 설명을 기준으로 삼지 않았다.
- 범위: 기본 환경의 핵심 구성을 요약하고 파생 환경은 직접 부모 대비 차이를 표로 기술한다. 전체 ID·클래스·직접 부모 색인은 실제 등록문과 AST에서 추출했다.

## 대조 중 확인한 주의점

- 개발 흐름과 EnvCfg 상속을 구분했다. Final/Revision/Wrench는 각각 직접 `ManagerBasedRLEnvCfg` 상속이고 OSC/ObjectRandom 버전들은 이전 번호를 순차 상속하지 않는다.
- 원시 관측과 장애물 인코딩 이후 MLP 입력, 물리 물체 수와 관측 슬롯 수를 구분했다. Critic의 현재 장애물은 Revision/Wrench에서 별도 입력된다.
- Omni-v1의 실제 Arm 종료 속도는 docstring의 3rad/s가 아니라 1.5rad/s다. GoalAccuracy-v0_1 Reaching은 현재 코드의 10cm로 기록했다.
- ObjectRandom/Final의 Gray 경계 조정 0.15는 미터가 아니라 비율 15%다. OBB 기반 Accuracy-v0_2_1의 60→69mm, Revision/Wrench 65mm와 분리했다.
- 목표 점유/정지 성공, timeout truncation/조기 terminated, 이벤트 보너스/지속 보상을 구분했다. Accuracy-v0_2 보너스의 strict 2cm 경계와 성공 분류의 inclusive 경계도 기록했다.
- Wrench-v0_2의 count 최대 10, 5회 불인정 초기화, 최대 0.29/step을 현재 함수와 대조했다.

## 영향·보존

환경 코드, 자산, 학습 설정, 테스트 및 `logs/rsl_rl`은 수정하지 않았다. 작업 중 생성한 검사/작성 보조 파일은 `/tmp`에만 두었다. 기존 사용자 변경인 `tests/test_wrench_v0_2.py`와 문서 submodule의 부모 저장소 대비 HEAD 차이를 보존했다. 문서 submodule HEAD는 `6273d45cd1d1f20749d3d7742c8c496b33a40b75`이며 commit/checkout/stage는 하지 않았다.

## 최종 대조·검증

- 등록 코드만 경량 Gym stub으로 실행하여 75개 등록을 수집했다. Isaac 환경을 실행한 검사가 아니다.
- 정적 검사: 75개 ID의 누락/중복 없음, 모든 EnvCfg와 직접 부모의 AST 일치, 등록 runtime/PPO 클래스 존재 확인, 13개 계열 모두 필수 다섯 구성 항목 확인.
- 활성 패키지 Python 소스 217개의 SHA-256을 문서 작성 전후 대조하여 변경 없음 확인.
- Markdown 수식 검사, 새 문서 및 `docs/README.md`의 외부 경로 포함 링크 검사 통과. 초안의 Omni 관측 링크 1건은 실제 상속 파일 `observations/sweep.py`로 수정했다.
- 개발 로그 포함 수식 검사 16개 파일 통과. 요청 문서 링크 검사 15개 파일 오류 0건, 개발 로그 포함 문서 저장소 전체 링크 검사 472개 파일 오류 0건. 양 저장소 `git diff --check`와 새 파일 공백 검사 통과.
- 미검증: Markdown의 GUI 렌더링, Isaac import/초기화/reset/rollout, GPU·PPO·장기 성능. 실행 코드 변경 없는 문서 작업이므로 학습은 실행하지 않았다.

## 유지보수

향후 환경 추가/수정 시 해당 계열 요약과 통합 색인을 함께 갱신한다. 이 문서는 상세 구현 계약을 대체하지 않으며, 기준일 이후에는 실제 코드를 우선한다.
