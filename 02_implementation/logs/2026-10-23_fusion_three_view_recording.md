# Fusion v1_0 세 카메라 동기화 녹화

[개발 로그](README.md)

독립 `src/inspire_sweep_baseline/scripts/record_three_views.py`를 추가했다. 기존 play·환경 등록·보상·종료는 변경하지 않는다. 환경1개, 기본 내부 시간60초·50Hz로 하이 앵글/선반 뒤 아이 레벨/내부 탑다운 세 render product를 같은 post-step 상태에서 저장한다. reset 발생 시 세 영상 모두 reset 후 장면을 기록하고 CSV에 경계를 남긴다. 영상시간0초는 시뮬레이션 첫 step(0.02초)에 대응한다.

출력은 `outputs/three_view_recordings/`의 새 폴더이며 MP4세 개·frames.csv·metadata.json을 생성한다. 중단·실패 시 complete로 표시하지 않는다. 현재 시점은 기본 선반 위치를 기준으로 고정된 world 좌표다. 카메라 영상은 정책 관측에 추가하지 않는다.

실행 안내는 [패키지 README](../../../../src/inspire_sweep_baseline/README.md#fusion-v1_0-동기화-3카메라-녹화)를 따른다. 검증: Python AST 구문 검사 통과. GPU 시험은 model_16400으로 `--headless --seconds 0.1 --width 320 --height 240` 실행. 전체60초 녹화는 이번 코드 추가에서 실행하지 않는다.

GPU 시험 결과: 정상 종료, metadata complete, 세 MP4 각각5프레임·50fps 확인. imageio로 첫 프레임을 디코딩하여 하이 앵글·로봇을 바라보는 뒤쪽 시점·물체 탑다운을 시각 확인했다. 시험 출력은 `outputs/three_view_recordings/smoke_20261023/`다. 전체60초 길이는 미실행이다.

## 시점 조정과 PNG 미리보기

사용자 검토용 `--preview-only`를 추가했다. 최소720×480, 기본960×720. Rear eye는(-1.22,0,1.16)에서 수평으로 로봇을 바라본다. High angle은(0,-0.95,1.95)에서(-0.78,0.03,1.08)을 바라본다. 베이스 방향은 월드+X다. Top down은 명시적 OpenGL 단위 쿼터니언으로 수직 방향을 유지하고 기존 화면 위가 왼쪽으로 향하도록 광학축−90° 회전을 적용한다. 수직 look-at의 up-axis 특이점 영향을 피한다.

GPU 미리보기 명령은 `record_three_views.py --headless --preview-only --output-dir outputs/three_view_recordings/preview_v3_20261023 --checkpoint <model_16400.pt>`이다. 전체 녹화는 사용자 시점 검토 이후에 실행한다.

검증 결과: preview_v3 metadata complete, PNG3개 모두960×720, MP4 없음. 탑다운 이미지를 열어 수직 시점·90° 방향 전환을 확인했다. Markdown 검사 통과.

## 16:9 광각 미리보기

후속 요청으로 기본1920×1080 및16:9 출력으로 변경했다. 탑다운은 고정 월드 yaw 대신 선반 실제 root quaternion에 정렬하며 카메라 optical -Z가 선반 평면을 수직으로 향한다. 이미지 가로는 선반-Y, 세로는+X로 대응한다. 매 기록 프레임 정렬을 갱신해 reset·물리 회전 후에도 유지한다. 광각 pinhole은 top7.5mm/rear12mm, 수평 aperture24mm이며 rear는 x=-1.60로 추가 후퇴했다. High angle의 pose·18mm 렌즈는 유지한다.

실행: 기존 model_16400에 `--headless --preview-only --output-dir outputs/three_view_recordings/preview_v5_20261023`. Python AST 검사 통과. 전체60초 녹화는 실행하지 않는다.

최종 검증: preview_v5 GPU 실행 정상 종료, metadata complete, PNG3개 각각1920×1080, MP4 없음. 미리보기에서 탑다운 작업면 전체와 이미지 축 평행 정렬, rear 작업 선반 양끝·기둥 포함을 확인했다. Markdown 검사와 git diff --check 통과.
