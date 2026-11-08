# Relative-v3 Hand Configuration 이미지

## 요청과 범위

`WRENCH_REFACTOR_RELATIVE_V3_TASK_ID`의 실제 Hand 에셋으로 `[0,0]`, `[0,1]`, `[1,0]`, `[1,1]` 네 자세를 같은 카메라에서 촬영한다. 환경 수정이 아닌 시각 자료 생성이다. 환경·Manager·관절 목표·에셋·학습 로그는 변경하지 않았다.

- 코드 기준: `2b88fe8c9de734b9649a9fcf64493a039bc6b92c`.
- 문서 기준: `0221e1dc4431648f5a1f726adaea7aba2b663a77`.
- 시작 시 루트 작업트리에 기존 `IsaacLab` submodule 변경 표시가 있었고 문서 저장소에는 기존 `2026-11-08_research_presentation.md` 미추적 파일이 있었다. 모두 보존했다.

## 실제 구성과 생성 방법

등록 ID는 `Inspire-Wrench-Refactor-Relative-v3`, 설정은 `WrenchRefactorRelativeV3EnvCfg`다. `parse_env_cfg`로 해당 task의 최종 `scene.robot`을 읽고 그 설정의 실제 spawner로 로봇만 생성했다. 선반·물체·정책은 생성하지 않았다.

사용 에셋은 `assets/data/wrench_right_hand/ur5e_inspire_right.usda`이며 로컬 `ur5e_inspire_usd/ur5e_inspire.usd`를 참조한다. 오른손 기하와 spawner 재질 및 Axia80 조립은 그대로 사용했다. 팔 바디는 촬영에서만 숨겼다. 기하·색상을 생성형 이미지로 대체하지 않았다.

`hand_joint_targets`의 첫 채널은 엄지 굽힘을 포함한 굽힘 11관절의 열림 정도, 두 번째는 엄지 첫 대립 관절의 열림 정도다. `0`은 closed target, `1`은 open target이다. 실제 함수로 만든 12관절 목표값을 `write_joint_state_to_sim`에 기록하고 `sim.forward()`로 FK와 렌더 상태를 갱신했다. 따라서 접촉·중력·구동기 수렴 뒤의 동적 상태가 아니라 정확한 목표 자세다.

## 카메라와 시각 확인

초기 촬영은 손 방향을 월드 축으로 추측해 손끝이 잘렸다. 최종 촬영은 초기 Arm 관절 적용 뒤 실제 손바닥·검지·소지 바디 위치로 손의 길이·너비·법선 축을 구했다. 엄지 쪽으로 기울어진 손바닥 사선 구도를 고정해 네 상태를 촬영했다. 카메라 위치·회전·초점거리60mm·해상도1600×1600·조명은 네 장에서 같다. 실제 카메라 수치는 metadata에 저장했다.

개별 원본에 다른 크롭이나 확대를 적용하지 않았다. 비교 그림은 네 장 모두 동일한 `(400,200,1360,1480)` 크롭으로 배치했으며 상태 라벨만 추가했다. 네 상태의 엄지 대립·굽힘 차이, 손끝 잘림 없음, 동일 손목 위치·배율을 이미지로 확인했다.

## 산출물과 재현

Workspace의 `outputs/hand_configuration_relative_v3/`에 저장했다.

- `hand_00.png`, `hand_01.png`, `hand_10.png`, `hand_11.png`: 개별 원본1600×1600.
- `hand_configuration_2x2.png`: 라벨 포함 비교 그림2000×3020.
- `hand_configuration_preview.png`: 비교 그림 미리보기.
- `render_metadata.json`: 12관절 값, 최대 목표 오차, 역투영한 Hand Configuration, 카메라, 에셋·이미지 SHA-256.
- `render_hand.py`, `compose.py`: 생성·합성 스크립트.
- `hand_configuration_relative_v3.zip`: 비교 그림·원본4개·metadata·스크립트 묶음.

Workspace 루트 PowerShell에서 실행한다.

```powershell
& C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe outputs/hand_configuration_relative_v3/render_hand.py --headless
python outputs/hand_configuration_relative_v3/compose.py
```

## 검증과 미검증

Isaac Sim5.1 / Isaac Lab / D3D12 / RTX4070에서 실제 렌더링했다. 최종 실행은 `root_physx_view.get_dof_positions()`로 PhysX 관절 상태를 직접 읽었다. 네 상태 모두 PhysX 관절과 목표의 최대 절대 오차0rad, `hand_configuration`과 같은 역투영 수식으로 복원한 두 채널의 오차는1e-6 미만이다. PNG4개의 저장과 비교 그림 전체를 시각 확인했다. Markdown 수식·문서 링크 검사와 `git diff --check`를 통과했다.

첫 두 촬영의 구도는 폐기했다. 세 번째 촬영에서 최종 구도를 확정하고 네 번째 촬영은 같은 구도에서 PhysX 직접 readback 검증을 추가해 원본을 갱신했다. Isaac Sim은 `COMPLETE`와 PNG·metadata 저장 후 종료 대기에서 프로세스가 남아 해당 촬영 프로세스만 종료했다. 다른 실행이나 학습 프로세스는 종료하지 않았다.

환경 코드·에셋·등록·학습 설정의 작업 전후 변경은 없다. 새 파일은 산출물 디렉토리와 이 개발 로그뿐이다. PPO 학습, 물체 접촉 상태의 실현 가능성, actuator 수렴 및 실물 자세는 검증 범위가 아니다.
