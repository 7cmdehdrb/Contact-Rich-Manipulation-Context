# 초기 부분 관측 OBB 티켓 구현

## 요청과 기준

사용자는 `implement` 스킬로 앞서 제시한 T1–T5를 순차 구현하도록 요청했다. 기준은 [개발 명세](../../01_plan/environments/2026-11-16_observed_obb_visualization_spec.md)와 대화의 티켓 분할이다. 새 요구사항이나 학습 연결을 추가하지 않는다.

코드 비교 기준은 workspace `2b855bcd46b80a4d5088cc723fae6bf8b1d88c43`이다. 문서 저장소 시작 HEAD는 `e40d6250c7cf58b1567b5a08afda6bb11461fd9a`다. 기존 사용자 변경·미추적 문서·학습 로그는 보존한다.

## 변경 전후와 영향

기존에는 별도 부분 관측 검토 패키지가 없었다. workspace의 `src/observed_obb`에 계산 인터페이스, 비충돌 USD 선 표시, 스냅샷 생명주기, Simple 장면 어댑터와 실행기를 추가했다. 기존 baseline·scene_randomization 소스는 변경하지 않았다. 학습 환경·관측 term·새 task ID·보상·제어는 추가하지 않는다.

| 티켓 | 구현 내용 | 현재 검증 범위 |
| --- | --- | --- |
| T1 | 새 패키지, 완전 가시 Box → 독립 ID/OBB, USD BasisCurves 표시 | 계산 테스트와 실제 CPU USD 장면 확인. 화면 렌더 미검증 |
| T2 | 축 정렬 부분 가림, 높이 무관 가림, 분리 조각, 폭·비율 필터 | 해석적 경계·분리·가림 유지 테스트 통과 |
| T3 | 회전 박스 경계 교차, 바닥면 절단, 최소 면적 직사각형 | 회전 절단·앞뒤 순서 전환·원본 yaw와 다른 피팅·좌표 변환 테스트 통과 |
| T4 | 참고 표시 토글, 고정 스냅샷, 새 배치·재관측 | 실제 CPU USD 표시와 생명주기 확인. 라이브 카메라·버튼 미검증 |
| T5 | Simple 자산 roster/스케일/배치 재사용, 정지 장면 연결, 비용 기록 | 기존 CircleResetLayout CPU 실행 확인. 실제 자산 로딩·렌더 통합 미검증 |

T1의 완전 가시, T2의 한쪽 가림, T3의 최소 면적 피팅 및 앞뒤 순서 전환은 각각 실패 테스트를 확인한 뒤 구현했다. 테스트 경계는 승인된 `observe` 입력·출력이다. 표시 검증은 실제 USD 장면에서 별도로 수행했다.

## 구현 결정

- 입력 Box는 원본 root가 아닌 기하 중심을 사용한다. Simple 스포너의 이미 스케일된 bounds에서 중심 오프셋을 구하고 yaw를 적용한 뒤 root 위치와 합친다. 스케일을 중복 적용하지 않는다.
- Simple의 SceneCfg·스포너와 CircleResetLayout 및 초기 배치 파라미터를 재사용한다. 17개 고정 자산 풀 중 타겟과 활성 장애물만 관측 입력으로 전달한다. 미사용 후보는 표시하지 않는다.
- 고정 정면은 선반 +X에서 -X 방향이다. 회전 박스의 투영 꼭짓점과 경계 교차점으로 구간을 나누고 가장 앞 경계를 선택한다. 중심 거리 정렬이나 기존 원형 가시성 bool을 관측 형상으로 쓰지 않는다.
- 같은 물체의 인접한 가시 구간만 연결한다. 떨어진 조각은 독립 ID를 받는다. 타겟/장애물 역할과 원본 대응은 출력하지 않는다.
- 각 조각에서 `max(0.02, 0.20 × 원본 전체 폭)`를 비교한 뒤 통과한 조각만 절단·피팅한다. 경계 비교에는 부동소수점 뺄셈의 수 ULP 보정만 사용하며 물리적 폭 허용치를 추가하지 않는다. 경계 ±1nm 사례를 확인했다.
- 최소 면적 직사각형은 절단된 볼록 다각형의 변 방향 후보를 비교한다. 실제 높이와 전체 깊이를 유지한다. 이미지·점군·원본 mesh 절단은 없다.
- 관측과 참고 표시는 물리 스키마 없는 BasisCurves다. 원본 장면의 rigid-body dynamics도 비활성화하며 실행기는 physics step을 호출하지 않는다.
- 같은 입력의 기하와 스냅샷은 결정적이다. ID의 의미는 스냅샷 내부 독립성에 한정하며 시간에 따른 추적을 추가하지 않는다.

## 실행한 검증

workspace 루트에서 Isaac Lab conda Python으로 실행했다.

```bash
PYTHONPATH=src/observed_obb:src/inspire_sweep_baseline /home/min/miniconda3/envs/env_isaaclab/bin/python -m pytest src/observed_obb/tests src/inspire_sweep_baseline/tests/test_fast_reset.py src/inspire_sweep_baseline/tests/test_sweep_simple.py -q
```

결과: **54 passed, 2 skipped**. 새 계산 테스트 22개와 기존 배치·Simple 회귀 검사다. GPU 동작을 증명하는 결과는 아니다.

```bash
/usr/bin/python3 -m mypy --check-untyped-defs --follow-imports=skip --ignore-missing-imports --cache-dir=/tmp/observed-obb-mypy-skip src/observed_obb/observed_obb src/observed_obb/scripts/show.py
```

결과: **7개 소스 파일 오류 없음**. 외부 Isaac/ USD API 타입은 누락 import 허용 범위이며 런타임 검증을 대신하지 않는다. `--follow-imports=silent` 실행도 같은 파일들에서 통과했다.

Isaac Sim에 포함된 USD 24.5 Python 라이브러리를 CPU에서 로드해 실제 `Usd.Stage.CreateInMemory()`에서 표시를 생성했다. 선 24개 점, CollisionAPI/RigidBodyAPI 부재, 토글 중 스냅샷 동일성, 재관측 동일 결과, 새 배치 결과 변경을 확인했다. Kit 렌더러나 UI 버튼을 실행한 검증은 아니다.

기존 CircleResetLayout을 CPU에서 직접 호출하고, 해석 가능한 동일 크기 bounds로 만든 100개 장면을 관측했다. 물리 물체 수 1–7개를 모두 포함했다. 준비 약 14.7ms, 관측 계산 중앙값 약 1.49ms·p95 약 4.29ms였다. **실제 Simple 자산의 성능 측정이 아닌 합성 기하 fixture 결과**다. 실행기는 실제 환경에서 startup·관측·USD 표시 갱신을 별도 출력하도록 구성했으며 시간 한도를 수락 조건으로 추가하지 않았다.

`git diff --quiet HEAD -- src/inspire_sweep_baseline src/scene_randomization`으로 기존 소스 변경 없음을 확인했다.

## 미완료 검증과 실행 장애

```bash
/home/min/miniconda3/envs/env_isaaclab/bin/python -u src/observed_obb/scripts/show.py --headless --device cpu --frames 2 --validate
```

Isaac Sim 초기화에서 `No device could be created`, `no CUDA-capable device is detected`, `Unable to create PxCudaContextManager`가 발생했다. `nvidia-smi`도 드라이버에 연결하지 못했고 `/dev/nvidia*`가 없었다. 프로세스 종료 코드 0은 검증 통과가 아니다. `[ObservedOBB] Live validation passed`가 출력되지 않았다. 실행 로그는 `/tmp/observed-obb-viewer.log`에 있다.

남은 항목은 GPU·원본 자산 접근이 가능한 환경에서 실제 Simple 장면 로딩, 표시 렌더, 카메라 이동·버튼 조작, 원본 기하와 표시의 라이브 대조, 실제 startup·표시 비용 확인이다. 현재 상태를 전체 구현·검증 완료로 표시하지 않는다. 목표를 축소하지 않고 이 항목들을 완료 조건으로 유지한다.

## 리뷰와 문서 검사

`code-review` 스킬에 따라 두 독립 에이전트가 새 소스·설정·안내 파일 10개의 작업트리를 검토했다. 리뷰 diff에는 pytest의 무시된 캐시 README도 포함됐지만 제출 변경에는 포함되지 않는다. 사용자 후속 지시로 커밋은 하지 않으므로 커밋 간 diff 대신 각 새 파일과 빈 파일의 diff를 사용했다.

- Standards: 지적 0건. 새 패키지 분리·기존 구조 보존·검증 상태 구분을 확인했다.
- Spec: 확인된 결함 0건. 실제 Simple 코드와 기하·배치·스냅샷 계약을 대조했다. GPU 검증 미완료는 그대로 유지한다.
- 루트의 새 장면에 Z-up·미터 단위를 명시해 Kit 기본 설정에 의존하지 않도록 했다.
- 문서 수식 검사 1개 통과, 문서 링크 검사 595개 Markdown·오류 0건, 새 파일 whitespace와 Python compileall을 확인했다.

`implement`의 커밋 단계는 자동 승인 검토에서 거절되었으며, 확인 질문에 사용자가 **“커밋 없이 변경만 유지”**로 답했다. 이 최신 지시를 따라 커밋·원격 게시를 수행하지 않았다. 기존 문서 서브모듈 HEAD와 사용자 변경도 보존했다.

## 후속 요청: 무제한 실행과 부분 가림 배치

사용자는 재생 시간을 영구적으로 변경하고 가려짐이 발생할 수 있도록 배치를 일부 조정하라고 요청했다. 초기 명세의 배치 분포 보존보다 이 후속 지시를 우선한다. 변경 범위는 새 검토 패키지다.

- 변경 전: 기본 실행 시간은 무제한이지만 앞서 안내한 `--frames 30` 명령은 30프레임 후 종료했다. 변경 후: 프레임 제한 옵션과 종료 조건을 제거했다. `--validate` 후에도 사용자가 닫을 때까지 유지한다. 현재 명령은 `python src/observed_obb/scripts/show.py --validate --seed 0`이다.
- 변경 전: 기존 배치의 무조건 표본이라 타겟만 있거나 가림이 없는 장면도 표시했다. 변경 후: 기존 CircleResetLayout 후보 중 적어도 두 물체의 선반 Y 투영이 2cm 이상 일부 겹치고, 겹침 바깥에 최소 폭·비율을 만족할 여유가 있는 후보를 선택한다. 초기 배치와 New placement에 동일하게 적용한다. 다른 물체가 추가로 가릴 수 있으므로 최종 관측 조각 수를 강제하지 않는다.
- 새 `placement.py`는 후보 선택만 담당한다. 실제 위치를 이동시키거나 충돌 여유·자산·학습 샘플러를 수정하지 않는다. 후보 선택에는 투영 범위만 사용하며 OBB 피팅을 중복 수행하지 않는다. 최대 256회 안에 후보가 없으면 오류로 알린다.
- CPU에서 기존 CircleResetLayout에 합성 8cm 정사각형 bounds를 넣어 시드 0–49를 확인했다. 50개 장면 모두 관측 결과에 잘린 OBB가 포함됐다. 이는 실제 자산 렌더 결과가 아니다. 분리 조각의 OBB는 서로 겹칠 수 있어 OBB 면적 합의 감소를 가림 검증 기준으로 사용하지 않았다.
- 기존 관측 테스트 22개 통과, 변경된 8개 소스 파일 mypy 통과. 기존 baseline·scene_randomization 소스 변경 없음. GPU 드라이버 부재로 실제 뷰어 검증은 여전히 미완료이며, 커밋하지 않는다.

## 후속 문서화: 최종 환경 통합 인계

사용자의 별도 정리 요청에 따라 [통합 인계](../environments/OBSERVED_OBB_INTEGRATION.md)를 작성하고 현재 인계 진입점에서 연결했다. 현재 코드의 입력·출력·좌표·가림·필터·스냅샷 계약, 후속 무제한 실행·배치 선택 변경, 검증 근거와 미검증 범위를 정리했다. 대상 환경 ID와 정책 입력 형식은 미확정으로 남겼으며 새 요구사항을 확정하거나 실행 코드를 수정하지 않았다. 뷰어 수명과 학습 episode, 검토용 조건부 배치와 학습 배치 분포를 구분한다. 기존 문서·사용자 변경을 보존하고 커밋하지 않는다.

문서 검증: 변경 Markdown 3개 수식 검사 통과, 전체 596개 Markdown 링크 오류 0건, 새 인계의 workspace 소스 링크 8개 포함 외부 경로 검사 오류 0건, diff 및 새 인계 whitespace 검사 통과. 문서만 변경했으므로 코드 테스트·GPU 실행은 재수행하지 않았다.

## 후속 문서화: 관측 방법의 독립 설명

사용자는 다른 코드나 자료를 참조하지 않아도 타인·에이전트가 관측 구성을 이해할 수 있는 문서를 요청했다. [초기 부분 관측 OBB의 구성 방법](../environments/INITIAL_PARTIAL_OBSERVATION_OBB_METHOD.md)을 별도로 작성했다. 문서 안에는 외부 링크·코드 경로·참고문헌을 넣지 않았다. 입력과 좌표, 기하 근사 가정, 정면 구간별 가림, 조각 분리, 2cm·20% 필터, 최소 면적 피팅, 숫자 예시, 출력·수명·한계를 자체 설명한다. 통합 인계에서 이 독립 설명을 찾을 수 있도록 연결했다. 기존 코드와 관측 규칙은 변경하지 않았으며 커밋하지 않는다.

검증: 변경 문서 3개 수식 검사 통과, 전체 597개 Markdown 링크 오류 0건, 독립 설명의 외부 링크·코드 경로 부재 및 whitespace 확인. 문서만 변경했으므로 코드·GPU 검증은 재실행하지 않았다.
