# 2026-11-10 Sweep Simple 독립 계열 구성

[환경 계약](../environments/SWEEP_SIMPLE_ENVIRONMENTS.md) · [현재 환경 안내](../08_ACTIVE_ENVIRONMENTS.md)

## 요청·의도와 기준

사용자는 누적된 Relative-IK 테스트 상속을 끊고 독립 Simple-v0를 만들도록 요청했다. 기준은 **현재 v0_2_2_4**이며, Prof-v0는 v0_2_2_5 보상, Simple-v1는 v0_2_2_6 Reach, Prof-v1는 Prof-v0에서 Reach만 교체한다. 기능 개선이나 튜닝은 요청 범위가 아니다. 완료 조건에는 기존 환경과의 코드리뷰가 포함된다.

작업 시작 root HEAD는 `0cfd188637092f5f64691352400484ce67a44285`다. 기존 문서 submodule 포인터 변경과 사용자 untracked 문서를 보존했다. `logs/rsl_rl`은 읽거나 수정하지 않았다.

## 변경 전후와 영향

이전 구성은 v0_2-Test부터 Fast와 v0_2_2_3을 거쳐 v0_2_2_4/5/6로 이어졌다. 새 구성은 `ManagerBasedRLEnvCfg → SweepSimpleEnvCfg`와 사용자 지정 자식 세 개다. 런타임은 `ManagerBasedRLEnv → SweepSimpleEnv`로 독립했다. 과거 환경·런타임·Manager Cfg·PPO 파일은 수정하지 않았다.

새 파일은 기존 역할별 디렉토리 안에 `sweep_simple.py` 계열로 추가했다. 환경 구성은 `envs/sweep_simple_envs.py`, PPO는 `agent/sweep_simple_ppo_cfg.py`다. 새 task 네 개만 패키지 등록 파일에 추가했다. 기존 공통 train/play 스폰 시각화 처리가 적용되므로 스크립트 변경은 없다.

독립 구성 선언에는 기존 최종 값을 명시적으로 복제했다. 공유 연산 함수·모델·자산 스포너는 재사용한다. 기존 환경으로부터 Cfg 또는 runtime을 상속하는 우회 wrapper는 없다. 기존 클래스와 새 클래스의 설정 객체도 서로 공유하지 않는다.

## 최종 대조 방법

`tests/test_sweep_simple.py`에서 다음을 비교한다.

1. 기존 v0_2_2_4/5/6와 대응 새 환경의 전체 `to_dict()`를 키 순서까지 재귀 대조. 공식 Isaac Lab `configclass`와 manager term 사용. Env/Scene base와 simulator 자산 leaf는 CPU 대역이며, actions는 별도 AST 전체 대조로 검증한다.
2. Prof-v1는 Prof-v0의 전체 설정 중 Reach 하나만 v0_2_2_6와 동일하게 교체되는지 확인. 네 EnvCfg의 직접 부모 확인.
3. Manager term 이름·순서·함수 객체 identity·params·weight·커리큘럼 일정 비교. 기존 환경과 새 인스턴스의 mutable 설정 격리 확인.
4. Scene/Actions/Observations/Commands의 live 정의를 클래스 이름 정규화 후 AST 전체 대조. 자산 roster·센서 구성·제어 설정·관측 계산/노이즈 보존.
5. PPO 전체 설정 비교. experiment_name만 제외하며 공유 네트워크 클래스 경로와 optimizer·rollout 값 유지.
6. 기존 상속 런타임과 독립 런타임을 같은 CPU 대역 Manager base 위에서 실행. 초기 버퍼·reset reseeding·step·부분 reset·최근 에피소드 ring eviction·hand action reset·통계 로그 비교. 변경 없는 메서드와 ring 구현은 AST도 일치.
7. 등록 문자열 네 개와 과거 Cfg/runtime 상속 및 import 부재 확인. 계산 함수 재사용은 허용한다.

## 실행한 검증

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH \
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  /home/min/miniconda3/envs/env_isaaclab/bin/python -B -m pytest \
  src/inspire_sweep_baseline/tests/test_sweep_simple.py \
  src/inspire_sweep_baseline/tests/test_wrench_refactor_relative_ik_test.py \
  src/inspire_sweep_baseline/tests/test_fast_reset.py -q -p no:cacheprovider
```

**71 passed, 2 skipped**, 10.71초. 새 동등성 검사15개와 기존 보상·접촉·Reach·Fast reset 회귀를 함께 통과했다. skip은 opt-in 대규모 기하 stress와 Isaac Sim native library path가 필요한 실제 USD IK 검사다. 이번 분리에서 이 두 검사를 새로 실행하지 않았다.

초기 PPO 대조 테스트의 대역 타입에 `inspect.signature` 가능한 생성자가 없어 테스트가 실패했고, 기존 fixture 방식의 명시적 생성자로 수정 후 위 최종 검사를 통과했다. 생산 코드에서 발견한 설정 차이는 없었다.

`nvidia-smi`는 NVIDIA 드라이버와 통신하지 못했다. 실제 Isaac Sim import/PhysX reset-step·GPU rollout·play 렌더·기존 체크포인트 로드·학습 결과·Collection Time 동등성은 **미검증**이다. CPU 설정/연산 대조 결과를 물리 실행 검증으로 해석하지 않는다.

## 코드리뷰

요청에 따라 `code-review` 스킬의 Standards/Spec 두 축을 별도 리뷰 에이전트로 검토했다. 기준은 작업 시작 HEAD와 이번 사용자 요청이며, 미커밋 작업의 추가 파일까지 포함한 diff를 사용했다.

- **Standards: 0건.** 역할별 구조, 독립 구성 선언, 기존 코드 보존, 변경 기록과 검증 범위가 개발 지침에 부합했다. 별도 수정이 필요한 기준 스멜도 발견하지 못했다.
- **Spec: 0건.** 네 환경의 대응 관계·직접 상속·보상 차이와 기존 전체 구성 보존을 확인했다. Spec 리뷰어가 새 동등성 테스트15개를 독립 실행해 통과를 확인했다.

검토 결론은 소스 및 CPU 검사 범위에서 의도한 동등성을 확인했다는 것이다. GPU/PhysX와 실제 성능은 위 미검증 범위를 유지한다.

새 Python 파일12개의 구문 compile, root 및 문서 저장소 `git diff --check`, 변경 Markdown4개 수식 검사, 문서 링크 검사(errors0)를 통과했다. 기존 추적 Python 소스 중 변경은 Gym 등록을 추가한 패키지 `__init__.py` 한 파일뿐이며, 과거 환경 정의·연산 파일은 그대로다.
