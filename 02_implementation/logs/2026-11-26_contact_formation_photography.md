# Contact Formation 캡처 전용 정적 환경

2026-11-26 KST. 사용자 요청: Prof Revision v0_3_2의 Contact Formation 의도를 설명할 손가락 지문면 방향·OBB 근접·감싸쥐기 직전 장면을 `src`에 추가한다. 물리 정합성은 요구하지 않으며 사용자가 직접 캡처한다.

## 기준과 변경 경계

코드 HEAD `cf70cd4bea328b8e2121d896c49bc87e05f14ce8`. 시작 시 IsaacLab 서브모듈에 기존 변경이 있었으며 보존했다. 문서 서브모듈은 작업 시작 시 깨끗했다. `logs/rsl_rl`은 읽거나 수정하지 않았다.

추가 실행 파일은 [photograph_contact_formation.py](../../../../src/inspire_sweep_baseline/scripts/photograph_contact_formation.py)다. `ProfRevisionV0_3_2EnvCfg`를 읽어 실제 로봇 spawner와 Formation 거리 scale을 재사용한다. 학습 Env를 상속한 Gym 과업이 아니라 사진용 standalone 정적 장면이다. 사용자 요청은 시각화이므로 Manager·정책·reset·학습 루프를 실행하지 않는다.

| 항목 | 기존 v0_3_2 | 사진 환경 |
| --- | --- | --- |
| 로봇 | UR5e–Axia80–RH56E2 오른손 | 동일 spawner; 화면에는 손·Axia80만 표시 |
| 물체 | 무작위 크기 원통·장애물 | 반경3cm·높이8cm 파란 원통 하나 |
| 자세 | 정책·물리 제어 | USD 관절 frame FK·12개 손 관절 독립 최적화·고정 |
| 거리 | OBB까지 손가락별 거리 | 같은 OBB 거리 정의, 기본7mm 근접 목표 |
| 방향 | 양방향 cos² | 사진 구성은 지문면 +Z가 중심을 향하도록 signed 방향 사용 |
| Scene | 선반·장애물·센서 | 스튜디오 바닥·조명·카메라·선택적 OBB/normal 선 |
| Manager·PPO·종료·커리큘럼 | 기존 계약 유지 | 생성·실행 없음; physics step 0 |

기존 Gym 등록·EnvCfg·runtime·보상·관측·행동·사건·종료·커리큘럼·PPO 소스는 수정하지 않는다. 손가락 coupling·충돌·정역학의 정확성은 사진용 요구 범위 밖이다. Formation 수식의 앞뒤 대칭성을 변경한 것이 아니라 사진 자세에만 더 엄격한 방향을 적용했다.

## 실행

Workspace 루트에서 Isaac Lab Python으로 실행한다. 체크포인트는 필요 없다.

```powershell
python src/inspire_sweep_baseline/scripts/photograph_contact_formation.py
```

뷰포트에서 orbit/pan/zoom 후 사용자가 캡처한다. 패널에서 사선·반대쪽·정면·위쪽 카메라와 OBB/지문면 방향 표시를 선택한다. 초록 선은 지문면 +Z의 방향선이며 화살촉은 없다. `--gap-mm 7`은 최적화 목표 간격으로, 정확한 다섯 손가락 동일 간격을 보장하지 않는다. 실제 간격과 signed cosine은 metadata에 남는다.

```powershell
python src/inspire_sweep_baseline/scripts/photograph_contact_formation.py --headless --preview-only --width 800 --height 600
```

기본 산출물은 `outputs/contact_formation_photography/preview.png`, `metadata.json`, `contact_formation_scene.usdc`다. USD의 rigid body·joint·articulation은 비활성화되어 고정 자세를 보존한다. GUI의 가이드 토글은 실행 중 보기에 적용한다.

## 검증

구현 후 Python AST와 `git diff --check`를 검사했다. Isaac Sim headless 미리보기 검증 결과는 아래 후속 기록에 남긴다. 학습·물리 정합성·정책 성능은 검증 대상이 아니다.

### 실제 렌더링 검증

로컬 `C:/Users/3cmde/miniconda3/envs/env_isaaclab/python.exe`로 위 headless 명령을 실행하여800×600 PNG·metadata·정적 USD를 생성하고 PNG를 직접 확인했다. 첫 배치는 물체를 손등 쪽에 두어 과도한 말림이 발생했다. 실제 authored joint frame FK로 열린 손가락 지문면 방향을 확인하고 물체를 손바닥 쪽으로 옮겼으며, distal 관절 상한을1.6rad로 제한했다. 기존 환경의 자산·관절 제한 자체를 변경하지 않고 사진 전용 최적화 범위만 제한했다.

최종 손 자세의 OBB 간격은 엄지·검지·중지·약지·소지 순서로6.77/2.63/5.13/4.84/6.27mm다. 지문면 +Z와 물체 중심 방향의 signed cosine은0.540/0.767/0.904/0.911/0.800으로 모두 양수다. 원본 `distance_angle_formation`으로 계산한 raw Formation은2.88143이다. 따라서 두 면 대칭인 원래 리워드와 별개로 실제 지문면이 중심 쪽을 향하는지 확인했다. 손가락 전체 mesh 관통·충돌과 실제 grasp 성공은 확인하지 않았다.

렌더러는 설치 디렉토리의 user.config/material cache 및 NVIDIA OptiX cache 쓰기 권한 경고를 출력했지만 PNG·USD 생성은 완료됐다. 캐시나 설치 파일을 삭제·수정하지 않았다. 기존 전체 RL 소스에 tracked diff가 없음을 확인했다. 문서4개 수식 검사 통과, 내부446/외부3 링크 검사 오류0, 양쪽 저장소 `git diff --check` 통과.

최종 GUI 실행은 기본1600×1200에서 수행했다. 사선 기본 카메라를 손가락 쪽으로 돌려 전체 손·Axia80가 잘리지 않는 구도를 확인했다. `Interactive viewport and controls ready` 로그와 실행 중인 프로세스를 확인했으며 사용자의 캡처를 위해 창을 열어 두었다. 내보낸 USD를 다시 열어 dynamic rigid body가 없고 타겟 위치가 보존됨을 자동 검사했다. GUI 패널 생성은 통과했고 개별 버튼·체크박스의 실제 클릭은 미검증이다. 실행 로그는 `outputs/contact_formation_gui.log`, `outputs/contact_formation_gui_errors.log`다.

## 후속: 옆 접근과 먼 거리 추가

사용자 후속 요청: 옆에서 잡는 자세와 손이 더 떨어진 상태도 추가한다. 같은 사진 스크립트를 수정하며 기존 RL 소스·자산·설정·학습 로그는 보존한다.

사진 preset은 `top_near`, `top_far`, `side_near`, `side_far` 네 개다. Top은 기존 관절 최적화·방향·원통을 유지한다. Side는 원통이 서 있는 상태를 유지하면서 손바닥이 옆을 향하고 손목·손가락이 수평으로 뻗도록 손 frame을 회전한다. 회전된 원통 축에 맞춰 손가락 근접·signed 방향을 별도로 최적화한다. 각 Far는 같은 접근의 Near와 관절값·회전을 유지한 채 손바닥 반대 방향으로 기본6cm 평행이동한다. 물체·바닥·OBB는 움직이지 않으며 방향선은 손과 함께 이동한다. Far에서 손가락별 최종 OBB 간격이 정확히6cm인 것은 아니며 실제 값은 metadata에 기록한다.

GUI에 자세 선택 버튼4개를 추가했다. 시작 자세는 `--pose side_near`(기본값)로 선택하고, 추가 이격은 `--retreat-cm 6`(허용2–20cm)으로 조절한다. 기존 `--gap-mm`는 Near 최적화 목표 간격이다. PNG·USD를 각 preset 이름으로 저장하고 전체 측정치를 `presets.json`에 저장한다. 기존 `preview.png`, `metadata.json`, `contact_formation_scene.usdc`는 시작 시 선택한 preset을 나타낸다. GUI 자세 변경은 현재 뷰포트에 적용되고 디스크의 시작 preset 파일을 덮어쓰지 않는다.

```powershell
python src/inspire_sweep_baseline/scripts/photograph_contact_formation.py --pose side_near --retreat-cm 6
```

로컬 검증에서는 이전 산출물을 보존하기 위해 `--output-dir outputs/contact_formation_variants --width 1200 --height 900`을 추가했다. 이전 에이전트가 띄운 사진 프로세스는 PID·실행경로·시작시각을 대조한 뒤 종료하고 수정된 창으로 교체했다.

검증: 네 자세 PNG·USD·`presets.json` 생성과 GUI 패널 준비 로그를 확인했다. Side Near 간격은7.94/7.55/6.43/6.79/7.76mm, signed cosine 최솟값0.615다. 모든 자세에서5개 지문 방향 cosine이 양수다. Top Near 관절값·OBB 간격은 이전 metadata와 정확히 일치한다. 두 Far preset은 대응 Near와 관절값·회전이 같고 평행이동 길이가 정확히0.06m인 것을 독립 계산으로 확인했다. 초기 Top Far 미리보기에서 손목이 화면 위에 잘려 카메라 중심을3cm 높이고 거리를1.25배로 넓혔다. 이후 최종 렌더링을 다시 확인한다. 문서4개 수식 검사와 링크449개 검사, `git diff --check` 통과. RL 소스 변경 없음, 기존 물리·학습 미검증 범위 유지.

최종 재실행:1200×900 Top Far·Side Near PNG에서 손·물체가 화면 안에 들어오는 구도를 직접 확인했다. 네 preset 산출물 갱신·정적 USD 재열기 검사·`Interactive viewport and controls ready` 로그를 확인했다. 시작 자세 Side Near로 창을 열어 두었다. 카메라·GUI·이격 옵션 외에 기존 Top Near 수치 변경은 없다. 개별 GUI 버튼 실제 클릭은 미검증이며 각 버튼이 호출하는 `select_pose`는 네 산출물 생성 과정에서 모두 실행했다.
