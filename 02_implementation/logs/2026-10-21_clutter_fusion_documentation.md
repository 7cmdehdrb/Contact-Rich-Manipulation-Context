# Clutter Fusion 독립 환경 설명서 작성

[개발 로그](README.md) · [설명서](../environments/CONTACT_SWEEP_CLUTTER_FUSION_ENVIRONMENT.md)

## 요청과 작업 범위

2026-10-21 사용자 요청에 따라 Fusion 환경을 Scene, Observation, Action, Reward, Termination, Curriculum 여섯 영역으로 설명하는 문서를 작성했다. 다른 환경과의 비교·상속 이력은 본문에서 다루지 않았다. Scene은 구현 클래스 설명 대신 구성 목적과 과제 조건을 설명한다.

Workspace 기준 commit은 `0e314e91686e8a7b10a8b081d97e776c86cc1479`, 문서 submodule은 `a953e0a880d881f375b665892b382c0d924dfeeb`이며 기존 수정·미추적 파일을 보존했다. 이번 작업은 문서만 수정했다.

## 확인한 내용

- 실제 Scene·MDP 함수·PPO와 Isaac Lab Action 설정을 읽어 관측의 단위·Frame·저장 시점·노이즈를 확인했다.
- Policy 55D와 obstacles 40D, Critic 전용 현재 타겟 3D, 16D 장애물 인코더를 구분했다.
- Raw Gaussian Action에는 유한 상한이 없고 Arm은 기본각 +0.5a, Hand 처리 후 값만 [0,1]이라는 사실을 명시했다.
- 15개 reward를 설계 목적 순서로 설명하고 거리 진전·초당 rate·step·일회성 보상을 구분했다.
- 물체 밑면 원점, 낮은 무게중심, 접촉 상대 미구분, 선반 속도 기준의 단위 혼합, `hand_velocity`가 실제로 Arm 검사라는 점을 확인했다.
- Reward 수치는 명시적 상태/시간의 계산 예시이며 실제 학습 비중이나 확정된 보상 배분 목표가 아님을 명시했다.

## 검증

Python 표준 `math`로 문서의 양의 보상 예시, tilt, 지수 속도 및 F/T 중간점 비용을 재계산했다. 예시 양의 보상은 14+4.5+11.2+11.2+3=43.9이고 항별 비중은 31.89/10.25/25.51/25.51/6.83%다. Tilt 10°·30°의 물체당 초당 비용은 약 0.345875·8.646884, F/T 정규화 초과량 0.5의 가중 비용 크기는 초당 0.01824255다.

문서 submodule에서 실행하는 검증 명령:

```bash
python 00_guidelines/scripts/check_markdown_math.py 02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_ENVIRONMENT.md 02_implementation/README.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-21_clutter_fusion_documentation.md ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external 02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_ENVIRONMENT.md 02_implementation/README.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/README.md 02_implementation/logs/2026-10-21_clutter_fusion_documentation.md ../../src/inspire_sweep_baseline/README.md
git diff --check
```

수식 검사 6개 파일 통과, 링크 검사 오류 0개(내부 191·외부 workspace 참조 73), Workspace 및 문서 submodule의 `git diff --check` 모두 통과했다. 코드 변경이 없어 simulator·학습·코드 테스트를 다시 실행하지 않았다. 새 성능 측정·실물 검증·학습 후 실제 보상 비중 분석은 이번 작업 범위가 아니다.

## 접촉 보상 설정 및 문서 검증

사용자 요청에 따라 Fusion의 `contact_any`와 `contact_count` 가중치를 각각 0.4로 설정했다. GPU probe의 기대값과 환경 설명서·활성 환경 안내·패키지 README를 일치시켰다. 설명서에는 현재 설정만 기술하며, 7초 최대 접촉 보상 합계는 5.6, 양의 보상 예시 합계는 27.1이다. 해당 예시의 비중과 F/T 예산도 재계산했다.

실행한 코드 검증:

```bash
env -u PYTHONPATH -u ROS_PACKAGE_PATH -u AMENT_PREFIX_PATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /home/ssu/miniconda3/envs/jd_isaaclab/bin/python -B -m pytest -q -p no:cacheprovider src/inspire_sweep_baseline/tests/test_clutter_fusion_rewards.py src/inspire_sweep_baseline/tests/test_clutter_v1_rewards.py src/inspire_sweep_baseline/tests/test_clutter_fusion_safety_rewards.py
```

Python AST로 실제 CFG의 두 weight가 0.4인지 확인하고, 문서 예시 합계 27.1을 산술 검증했다. Simulator와 학습은 다시 실행하지 않았으며 실제 학습 후 보상 비중은 미검증이다.

결과: 관련 보상 테스트 **41 passed (1.13s)**. 아래 문서 검사도 통과했다(수식 4개 파일, 링크 오류 0개·내부 93·외부 73). Workspace 및 문서 submodule에서 `git diff --check`가 통과했다.

```bash
python 00_guidelines/scripts/check_markdown_math.py 02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_ENVIRONMENT.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/2026-10-21_clutter_fusion_documentation.md ../../src/inspire_sweep_baseline/README.md
python 00_guidelines/scripts/check_document_links.py --check-external 02_implementation/environments/CONTACT_SWEEP_CLUTTER_FUSION_ENVIRONMENT.md 02_implementation/08_ACTIVE_ENVIRONMENTS.md 02_implementation/logs/2026-10-21_clutter_fusion_documentation.md ../../src/inspire_sweep_baseline/README.md
```
