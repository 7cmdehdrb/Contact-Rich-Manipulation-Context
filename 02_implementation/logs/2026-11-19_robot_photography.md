# UR5e–Axia80–RH56E2 연결부 촬영 환경

## 요청과 기준

최신 Sweep Only/Finger 환경의 환경 구축 방식만 가져와 연결부 클로즈업 이미지와
사용자가 직접 사진을 찍는 비학습 환경을 만든다. 기존 학습 환경 직접 수정이 아니라
동일 로봇 factory를 재사용하는 standalone 촬영 실행기를 추가했다.

- Workspace 기준 HEAD: `37aea6365192e919176fe46245be73a4fe7126df`.
- 문서 저장소 기준 HEAD: `1de3604e4a10709635e722f80e94de45c112f044`.
- 시작 시 상위 저장소는 IsaacLab의 기존 작업트리 변경 표시만 있었고 문서 저장소는 깨끗했다.
- 기준 코드: `assets/scenes/stabilize_sweep.py::_robot`, `assets/scenes/sweep_simple.py::_robot`.
- 새 실행기: [photograph_robot.py](../../../../src/inspire_sweep_baseline/scripts/photograph_robot.py).
- 실행·촬영 사용법: [패키지 README](../../../../src/inspire_sweep_baseline/README.md#로봇-연결부-촬영--학습-없음).

## 의도와 변경 전후

기존 `_robot()`을 호출하여 오른손 RH56E2 overlay, RevisionRobotSpawnerCfg,
UR5e–Axia80–손의 두 fixed joint와 source root/joint pose를 재사용한다.
Axia80은 반지름0.041m·높이0.0254m의 기존 실린더다.

| 항목 | 기존 학습 환경 | 새 촬영 실행기 |
| --- | --- | --- |
| 로봇 자산·조립 | 오른손 USD + 기존 spawner | 동일 factory 직접 호출, 원본 변경 없음 |
| Scene | 선반·물체·센서·마커 등 | 로봇·조명·충돌 없는 단색 배경·카메라 |
| 자세 | task reset/IK/정책 | source 기본 관절 자세로 초기화 후 고정 |
| 물리 | task 주기로 계속 실행 | 중력0에서 초기화1스텝, 이후 render만 실행 |
| Gym·runtime·Manager·PPO | 각 task 계약 | 새 task 등록·RL env·checkpoint·정책 없음 |
| 촬영 | 기존 play/record 용도 | 5개 preset PNG + 자유 뷰포트 캡처 + 정적 USD |

관절 상태의 GPU PhysX 결과가 첫 스텝 후 USD에 자동 반영되지 않는 경우를 확인했다.
따라서 `body_link_state_w`로 계산된 월드 자세를 USD에 명시적으로 반영한 후 bounds와
카메라를 계산한다. 같은 자세를 flatten한 촬영 USD에도 저장한다. 초기 probe의
원본 USD 자세 기준 프레이밍은 최종 결과로 사용하지 않는다.

근위부 팔 링크는 클로즈업에서 숨기고 전체 구도에서 다시 표시한다. 분리 구도는
추가로 forearm/wrist1도 숨긴다. 메시나 물리 연결의 삭제가 아닌 촬영 시각화 설정이다.
`mount_detail`은 센서와 양쪽 체결부를 확대하므로 손가락 끝이 잘린다.

촬영 USD는 모든 rigid body/joint를 비활성화해 수동 재생으로 자세가 무너지는 것을
막는다. 원본 자산의 물성이나 기존 환경의 gravity는 수정하지 않는다.

## 실행과 산출물

RTX4070·Isaac Sim5.1·Isaac Lab의 `env_isaaclab` Python을 사용했다. Windows에서는
기존 `cli_args.apply_renderer_compatibility`의 D3D12 설정을 재사용한다.

```powershell
conda activate env_isaaclab
python src/inspire_sweep_baseline/scripts/photograph_robot.py --headless --capture-only
python src/inspire_sweep_baseline/scripts/photograph_robot.py
```

산출물 위치는 `outputs/robot_photography`다. 파일명과 수동 촬영법은 패키지 README를
기준으로 한다. 원본 자산·joint 값·camera eye/target·해상도는 `metadata.json`에 저장한다.
수동 캡처는 기본 preset과 구분한 고유 타임스탬프 파일에 저장한다.

## 검증과 최종 대조

초기 probe에서4개 PNG의 실제 렌더를 확인했고 조명·프레이밍·자세 동기화를 수정했다.
1920×1440 최종 출력은5개 구도다. PNG 생성 시 해상도·RGB 형식과 빈 영상 여부를 검사한다.
정적 USD를 다시 열어 Axia80 월드 위치가 캡처 기준과1µm 허용오차 이내인지,
활성 rigid body가 남지 않았는지를 실행기 자체에서 검사한다.

초기 capture-only 실행은 PNG·USD 저장 이후 Replicator 종료 대기에서 멈췄다.
동기 PNG 저장이 완료된 후에는 `app.close(wait_for_replicator=False)`를 사용하도록
수정했으나 Windows camera/PhysX 정리 단계도 대기하므로, 최종적으로 문서화된
`app.close(wait_for_replicator=False, skip_cleanup=True)`의 즉시 종료 경로를 사용한다.
해당 초기 probe 프로세스만 명령행·PID로 확인하여 종료했다. PNG·JSON·USD는
모두 동기 저장 완료 후 종료한다.

### 후속 검증

- 최종 종료 경로로 `--headless --capture-only --width640 --height480 --warmup-frames8`
  조건의5개 구도·USD 재열기 검사를 완료하고 프로세스 exit code0을 확인했다.
  실제 인자는 각 옵션과 수치 사이에 공백을 둔 CLI 형식이다.
- GUI 최종 실행은 기본1920×1440의5개 preset PNG를 생성했고, metadata의
  `static_scene_reopen_verified=true`, 실제 joint와 target의 최대 차이0rad를 확인했다.
- GUI에서 Mount Detail 전환과 Save current viewport PNG 클릭으로 실제 수동 PNG
  생성을 확인했다. 초기 GUI의 수동 이미지는 기본 viewport 해상도1280×720이어서,
  최종 GUI에는 viewport 해상도를 CLI와 동일한1920×1440으로 명시했다.
- `PinholeCameraCfg(lock_camera=False)`로 기본 카메라 잠금을 해제했다. 카메라는
  `/World/PhotoCamera`를 사용하며 촬영 패널을 Property 영역에 지연 docking한다.
  렌즈·카메라·패널이 적용된 실제 GUI 화면을 확인했다.
- `python -m py_compile src/inspire_sweep_baseline/scripts/photograph_robot.py` 통과.
- 변경된4개 Markdown의 수식 검사 통과. 문서 저장소의 변경3개 파일 상대 링크 검사
  0오류(내부316·외부3). 상위/문서 저장소 `git diff --check` 통과.
- 패키지 README 전체 링크 검사에서 기존 GoalAccuracy-v0_2 문서 누락1건을 확인했다.
  이번에 추가한46줄 이외의 링크·내용은 수정하지 않았으며 해당 기존 오류는 유지했다.

기존 task의 등록·EnvCfg·SceneCfg·runtime·Command·Event/reset·Observation·Action·
Reward·Termination·Curriculum·PPO 파일은 변경하지 않았다. 새로운 실행기와 패키지
사용법·이 문서만 추가/갱신하며 IsaacLab과 기존 사용자 변경, `logs/rsl_rl`은 보존한다.
학습 성능·정책 행동·실물 물성·실물 사진 유사성은 이 작업의 검증 대상이 아니다.
