# Prof Revision v0_3_2 구현·검증

2026-11-26 KST. 사용자 요청: [최신 개발명세](../../01_plan/environments/2026-11-26_PROF_REVISION_V0_3_2_SPEC.md)를 구현하는 새 상속 환경을 추가한다. 제안되어 있던 이름 `Inspire-Sweep-Prof-Revision-v0_3_2`를 적용했다. 부모는 `v0_3_1`이며 부모 환경을 직접 수정하는 작업이 아니다.

## 기준과 사용자 작업 보존

코드 HEAD `4bff6449f2cbc8b7ee09abbe2a1956c86e2a060a`, 문서 HEAD `e35db19a646c0bbfe33de499f49f8ac4195a3b9f`. 시작 시 기존 보고 스크립트 변경·방향 분석 스크립트·`docs/plan/PLAN22.md`·IsaacLab 및 문서 저장소의 사용자 변경이 있었다. 이 변경들을 보존한다. 변경 전 역할별7개 소스와 해시는 [before](../../../../outputs/prof_revision_v0_3_2_validation/before)에 저장했다. `logs/rsl_rl`은 사용하지 않는다.

## 최종 변경 계약

| 항목 | 부모 v0_3_1 | 새 v0_3_2 |
| --- | --- | --- |
| EnvCfg | `ProfRevisionV0_3_1EnvCfg` | 직접 자식 `ProfRevisionV0_3_2EnvCfg` |
| Runtime | `ProfRevisionEnv` | 직접 자식 `ProfRevisionV0_3_2Env` |
| State | `ProfRevisionState` | 직접 자식 `ProfRevisionPrecisionState` |
| 진행 | 원래 거리 개선×접촉 인정×힘 정렬, weight100 | 가중 거리H 개선×접촉 인정×현재 유효 접촉×유효성×B, weight100 |
| 이탈 | 원래 거리 증가, weight−20 | 같은H 증가, weight−40; 접촉·힘 gate 없음 |
| Reach | signed 거리 증분, weight4.9 | 동일 함수·params, weight9.8 |
| Formation | 손가락별 거리×양방향cos² 합, weight0.245 | 동일 함수·mode·params, weight0.1715 |
| 장애물 변위 | 활성 비타겟 reset 대비3D 제곱변위 합, weight−150 | 동일 함수·raw cap0.04m², weight−300 |
| 추가 scalar | 없음 | force inner0.03m·outer0.06m, precision radius0.06m·중심 배수2 |
| PPO | v0_3_1 | 직접 자식, experiment name만 `inspire_sweep_prof_revision_v0_3_2` |

성공은10초 timeout에서 추적 가시 OBB 중심의 XY 거리<=3cm·동시 실패 제외다. 부모의 TCP `wrist_3_link` 선속도>=4m/s 종료,16개 보상과 순서, 빈 curriculum,108D policy·176D obstacles·12D action, 센서·초기 관측·손가락 자세·자산·원통 타겟·목표6–12cm·장애물0–6개·배치·reset·physics·전체PPO는 보존한다. Hard 분포·새 속도 비용·정지 보상·성공 bonus는 도입하지 않는다.

## 수식·수명·telemetry

거리 `d`는 현재 추적 OBB 중심과 목표의 XY 거리다. `S(u)=3u²−2u³`에서u를[0,1]로 자르고, `alpha=S((d−0.03)/0.03)`, `B=1−alpha+alpha*A`를 적용한다. `A`는 기존 힘 정렬로 남는다.6cm 이상 기존 힘 영향,3cm 이하 힘 방향·1N gate 영향0이지만 접촉 조건은 유지된다.

`u=clip(d/0.06,0,1)`, `H(d)=d+0.06*(u−u³+u⁴/2)`이다. `H`의 미분은 중심2·3cm1.5·6cm1로 변한다. 부모 finish 이전 거리를 보존하고 부모 finish 이후 `ΔH=H(previous)−H(current)`를 계산한다. 새 reward callable은 정밀 증분을dt로 나눠 읽기만 하며 Manager의dt가 한 번 상쇄된다. 기존 `positive/retreat/alignment/Reach` buffer의 의미·결과는 그대로다.

공통 runtime에 기본 상태 factory와 기본 빈 telemetry hook만 추가했다. 부모 factory는 기존 `_state_type(count,device)`를 그대로 호출하고, 자식만 명세 계수를 전달한다. 마지막physics substep 후·보상/종료/자동reset 전에 한 번 갱신한다. 부분reset은 선택된행의 부모 이력·정밀cache만 지운다.

기존 `ProfRevision/sweep_progress_m`, `sweep_retreat_m`, `force_alignment`는 원래 값이다. `ProfRevisionPrecision/` 아래 `force_influence`, `distance_sensitivity`, `effective_alignment`, `weighted_distance_delta_m`, `precision_progress_m`, `precision_retreat_m`, 근거리/전환/원거리 비중과4개 scalar를 추가했다. terminal에서도 reset 전 집계값을 유지한다. step 경로에 새 센서·mesh query·CPU 복사·환경별Python loop는 없다.

최신+100/−40은 대칭이 아니므로 닫힌 왕복 무이익을 보장하지 않는다. 동일 가중 거리0.01m 왕복은 최대+0.6이다. 사용자 지시에 따른 비율이며 장기 정착 개선과 분리해서 검증한다. 장애물 raw cap은 이전254,165step에서 도달0·최대21%였으므로 명세대로 유지한다.

## 검사와 실행

CPU 수식·접촉·dt·부분reset 검사와 부모 회귀를 실행했다. 실제 명령은 아래와 같다. 상세 결과는 후속 완료 기록에 추가한다.

```powershell
python -m pytest src/inspire_sweep_baseline/tests/test_prof_revision_precision.py src/inspire_sweep_baseline/tests/test_prof_revision.py src/inspire_sweep_baseline/tests/test_prof_revision_hard.py -q --basetemp outputs/prof_revision_v0_3_2_validation/pytest_tmp
python src/inspire_sweep_baseline/scripts/check_prof_revision_precision.py --headless --num-envs 16 --steps 100 --checkpoint logs/TEMP/2026-11-26/inspire_sweep_prof_revision_v0_3_1/2026-11-25_14-35-42/model_15550.pt
```

[CPU 결과](../../../../outputs/prof_revision_v0_3_2_validation/pytest.log). 검증 출력을 `outputs/prof_revision_v0_3_2_validation`에 격리하며 부모checkpoint는 동작/보상 wiring 확인용이다. 부모critic이 새 reward를 학습했다는 의미가 아니다. 새 환경의 장기 성공률·정밀 정착·장애물 억제 개선은 새 학습과 별도 평가가 필요하다.

일반 학습 명령:

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3_2 --num_envs 2048 --headless
```

## 완료 검증 결과

- CPU60개 통과.0/3/6cm 및 양옆 경계,독립 수치적분·H미분·분할합,힘 정/반대/저하중,접촉 이력·현재 접촉·invalid,첫step·정지·목표 통과/복귀·부분reset,세dt·callable 호출 순서,기존Formation/Reach/종료/PPO gradient/export 및Hard 회귀를 포함한다. ONNX deprecated 경고·기존pytest cache 쓰기 경고만 있으며 검사는 통과했다.
- [전체 계약 대조](../../../../outputs/prof_revision_v0_3_2_validation/contract.json): 변경 전 소스와 기존8개 EnvCfg·모든 기존PPO의 전체to_dict 일치. 자식은4개 scalar와5개 reward의 명시된 callable/weight 차이만 허용한 뒤 전체to_dict 일치. 모든 기존 클래스·함수AST와Gym 등록 보존; 공통runtime만 명세의factory/빈telemetry hook 두 확장을 허용했다.
- [실제16환경 검사](../../../../outputs/prof_revision_v0_3_2_validation/smoke.json): 부모model15550으로100step+강제timeout1step,양의 진행466행·이탈663행. live OBB 거리에서 독립 수식으로H·B·gate·실제5개term 기여·전체dt를 매step 재계산했다. 기존raw progress/retreat도 보존됐다. 부분reset의미선택행 전체state/cache 불변,16개 terminal transition 보상·자동reset 전telemetry 보존을 통과했다. 이것은새정책의성공률평가가아니다.
- [16환경PPO1회](../../../../outputs/prof_revision_v0_3_2_validation/ppo_smoke/training_status.json): rollout36step·PPO1update 완료. value loss0.1653·surrogate loss−0.0549·entropy17.0193,출력reward와loss finite. [checkpoint 검사](../../../../outputs/prof_revision_v0_3_2_validation/ppo_checkpoint_check.json)에서132개tensor 모두finite. 검증 학습만 실행했고2048환경 장기학습은 시작하지 않았다.

```powershell
python src/inspire_sweep_baseline/scripts/train.py --task Inspire-Sweep-Prof-Revision-v0_3_2 --num_envs 16 --headless --max_iterations 1 --resilient-attempt-dir outputs/prof_revision_v0_3_2_validation/ppo_smoke --resilient-target-iterations 1
python src/inspire_sweep_baseline/scripts/check_prof_revision.py --task Inspire-Sweep-Prof-Revision-v0_3_1 --headless --num-envs 4 --output outputs/prof_revision_v0_3_2_validation/parent_smoke.json
```

실행 중 확인한 문제와 처리: 첫sandbox 실행은Isaac Sim 사용자설정 쓰기 오류 후초기화가완료되지않아로컬cache 쓰기를허용한실행으로재시도했다. 초기checker는RSL wrapper가자체reset한이전snapshot을비교하여실패했다. wrapper초기화이후snapshot을저장하도록checker기준점을수정했고실제환경로직은바꾸지않았다. 또한검증예외traceback을app.close전에출력하도록보완했다. 최종성공은exit code만으로판단하지않고성공marker·smoke.json의완료를확인했다.

미검증:2048환경 처리시간·장기학습 안정성·방향별 새정책 성공률·진입후재이탈 감소·최종거리 개선·장애물 억제 효과. 이전의힘센서물리충실도문제는이번보상변경으로해결됐다고주장하지않는다.

최종 완료: [부모v0_3_1 live 회귀](../../../../outputs/prof_revision_v0_3_2_validation/parent_smoke.json)도4환경12step·부분reset·자동timeout·고정Actor snapshot·OBB 추적·Formation 독립 계산·TCP 경계/동시 성공 제외·JIT export까지 통과했다. 변경Python9개py_compile,Markdown7개수식 검사,문서6개상대/외부링크 검사(오류0·외부18·내부473),루트/문서저장소git diff --check 통과. LF/CRLF 안내는내용오류가아니다. 환경 계약·계통·활성 안내·README·명세 상태·인계를 함께 갱신했다. 별도 commit·원격전송은 수행하지 않았다.
