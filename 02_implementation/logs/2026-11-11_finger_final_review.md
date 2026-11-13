# Finger 네 환경 최종 코드 리뷰

[환경 계약](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md) · [개발 로그](README.md)

## 요청과 범위

2026-11-11 사용자 요청: Finger-v0, Finger-v0-Wrench, Finger-v0-Test, Finger-v1에 의도한 변경만 반영됐는지 최종 검토한다. 최신 대화의 정정을 명세로 삼았다. 코드 수정은 하지 않았다.

검토 시점 HEAD는 `1ab6e579cf1c4f4152954b1c6fb0120a99729eb5`, 직전 기준은 `65bb0a395c3b48338ddcef21ed5e27d48d46cf35`이다. 해당 변경뿐 아니라 현재 등록, 부모 전체 구성, Action/Observation/Reward/Termination/Curriculum, runtime, PPO, native OSC 경로를 함께 대조했다. Standards와 Spec을 별도로 검토했다.

## 최종 대조

| 환경 | 제어·Last Action | 팔 속도 종료 | 팔 속도 비용 |
| --- | --- | --- | --- |
| Finger-v0 | 기존 pose OSC, 추가 raw arm clip 없음, Last Action tanh | 기존 4→2 커리큘럼 | −0.03 |
| Finger-v0-Test | v0와 동일 | 1.0rad/s 고정, 해당 커리큘럼 없음 | −0.03 |
| Finger-v0-Wrench | 센서 프레임 wrench OSC, arm/hand raw clip, Last Action은 clip된 raw | 1.0rad/s 고정, 해당 커리큘럼 없음 | −0.03 |
| Finger-v1 | pose OSC, 기존 scale 이전 raw arm/hand clip, Last Action은 clip된 raw | 1.0rad/s 고정, 해당 커리큘럼 없음 | −0.03 |

세 파생 환경은 Finger-v0를 직접 상속한다. 모든 환경의 손 제어는 6개 drive joint이다. v0/Test도 실제 손 목표는 URDF 범위로 제한하지만 추가 raw ActionManager 클리핑은 하지 않는다. Wrench의 센서 제어 프레임 변경은 기존 EEF 관측·보상 프레임을 변경하지 않는다.

모든 환경에서 PPO 샘플과 likelihood는 원본 Gaussian을 사용한다. v1만 앞서 승인된 축별 초기 평균·표준편차 설정을 사용한다. Wrench의 action term 내부 clip은 ActionManager 원본을 바꾸지 않아 Action 변화 비용은 원본 기준이다. v1은 runtime에서 out-of-place clip 후 ActionManager에 전달하므로 비용도 clip값 기준이다. 이 차이는 기존 승인된 계약이며 이번 리뷰에서 변경하지 않았다.

전체 환경 Action 변화 비용 상한 삭제도 반영됐다. 가중치와 입력 선택, 다른 비용 및 실제 제어 제한은 유지한다. 초기화·부분 reset·부모 객체 격리·등록을 포함해 확인한 범위에서 명세 불일치나 요청 밖 변경을 발견하지 못했다. 문서화된 코드 규칙 위반과 조치가 필요한 설계 결함도 발견하지 못했다.

## 실행 검증과 한계

- `test_sweep_simple_finger.py`, `test_sweep_simple_finger_versions.py`, `test_sweep_simple_finger_wrench.py`: 35 passed.
- `test_bounded_ppo_failure.py`: 11 passed. 과거 변환 분포 실패 재현과 일반 Gaussian PPO 경로 회귀를 포함한다.
- 총 46개 관련 CPU 테스트 통과. 일부 EnvCfg 통합 테스트의 Action leaf는 doubles이며 별도의 실제 역할 구성·native OSC 계산 테스트로 보완한다.
- GPU/PhysX 환경 생성·play·학습 rollout은 실행하지 않았다. 센서 프레임 물리 거동과 장시간 학습 안정성을 검증 완료로 해석하지 않는다.
- 이번 검토는 전체 테스트 스위트를 재실행하지 않았다. 이전 전체 실행에서 확인된 무관한 Final shelf termination fixture 및 runtime whitelist 테스트 실패를 해결했다고 주장하지 않는다.

결과: Standards 0건, Spec 0건. 실행 코드 변경 없음. 이 기록과 로그 색인만 추가했다.
