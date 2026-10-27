# Final v1 3000·9500 보상 재생 진단

[개발 로그 목록](README.md) · [Final 환경 계약](../environments/FINAL_V1_V2_ENVIRONMENTS.md) · [분석 실행기](../../../../src/inspire_sweep_baseline/scripts/diagnose_final_v1_play_rewards.py)

2026-10-27 사용자 요청: `logs/TEMP/2026-10-26_17-11-27`의 3000 및 최신 iteration 정책을 각각 play하여 `object_penalty`와 `goal_hold`의 내부 변화, 합산·중첩 항과 커리큘럼의 영향을 확인한다. 원본 run과 체크포인트는 읽기 전용으로 취급한다.

## 확보한 입력과 실행 제약

해당 run에는 `model_3000.pt`와 최신 `model_9500.pt`가 모두 있으며 checkpoint 내부 `iter`는 각각3000·9500이다. `rg --files` 기본 검색은 `.pt` 무시 규칙 때문에 누락했으며 `rg --files -uuu`와 실제 디렉터리 목록으로 확인했다. 두 파일은 각각 약1.5MB다. TensorBoard scalar의 마지막 step은9503이다.

기본 실행 격리 안에서는 `nvidia-smi -L`이 exit9 (`couldn't communicate with the NVIDIA driver`)였고 `/dev/nvidia*` 장치가 보이지 않았다. 이후 호스트 PCI와 드라이버를 확인했으며, 격리 밖의 `nvidia-smi -L`은 RTX 3090을 정상 표시했다. 따라서 앞선 제한은 호스트 GPU 부재가 아니라 실행 격리의 장치 접근 제한이다. `env_isaaclab` Python으로 headless CPU 1환경 생성·reset·step을 시도했을 때는 `No CUDA devices found`와 `Unable to create PxCudaContextManager!`가 출력됐고, `PROBE: creating environment` 이후 reset 메시지에 도달하지 못했다. 실행은60초 상한 이후 종료했으므로 물리 play 성공으로 기록하지 않는다. 원시 출력은 `/tmp/final_v1_cpu_smoke.log`에 있다. 진단 실행기 역시 CPU에서 `Creating Isaac-Inspire-Final-v1...`까지 확인했으나35초 상한으로 종료했으며 물리 episode·분해 결과는 생성되지 않았다. 원시 출력은 `/tmp/final_v1_diagnostic_cpu_attempt.log`다.

기존 TensorBoard event의 2900–2999와9404–9503 구간에서는 `object_penalty`가−3.30→−11.34, `goal_hold`가11.64→4.48(10초 환산 평균)로 변했다. 이는 각각 전체 하락의45.6%,40.6%이며 합계86.2%다. **이는 Manager 항 수준의 산술 기여**다. event에는 병합된 `object_penalty`의 기울기·장애물 변위·물체 가속도 세 비용이나 goal의 step별 거리·속도가 없으므로 내부 인과 비중을 추정하지 않는다.

## 재생 분석기

[실행기](../../../../src/inspire_sweep_baseline/scripts/diagnose_final_v1_play_rewards.py)는 기존 Final v1 보상 함수와 설정을 변경하지 않는다. `play.py`처럼 체크포인트를 로드하되 `exported/policy.onnx`를 덮어쓰지 않고 결과를 `outputs/final_v1_play_diagnostics`에 둔다. 보상 계산 순간을 관찰하여 reset 이전 상태를 수집한다.

- `object_penalty`의 내부 비용을 타깃 기울기·장애물 기울기·활성 장애물 변위·물체 가속도로 나눈다. 네 항의 합이 원래 `object_penalty` 및 전체 RewardManager 보상과 매 step·episode에서 일치하는지 검사한다.
- `goal_hold`의 유효 상태·XY 거리·3D 속도·반경 내 체류율·거리/속도 지수 인자·중심 배율과 보상값을 기록한다. 이 항은 반경 진입 조건과 거리·속도·중심 인자의 **곱**이므로, 인자별 보상 금액을 단순 합산하지 않는다. **동일한 물체 상태**에 3000·9500 iteration의 반경/속도 공식을 각각 평가하여 수식 변경의 직접 효과를 분리한다.
- 모든 RewardManager 항과 종료 항도 기록한다. `hand_reaching`·`hand_contact` 등 goal 반경을 함께 읽는 항의 변화와 보상 합산을 확인할 수 있다.
- 같은 seed로 정책3000·9500 × 커리큘럼3000·9500의 2×2 조건을 별도 process에서 실행한다. 같은 정책의 stage 차이와 같은 stage의 정책 차이를 분리하되, 장애물 개수가 달라지면 동일 seed라도 물리 장면이 완전히 같다고 간주하지 않는다.

GPU와 선반 USD에 접근 가능한 workspace 루트에서 다음 네 명령을 실행한다. `--episodes 32`는 조건별 완료 episode 수다.

```bash
for policy_iter in 3000 9500; do
  for curriculum_iter in 3000 9500; do
    ./IsaacLab/isaaclab.sh -p src/inspire_sweep_baseline/scripts/diagnose_final_v1_play_rewards.py \
      --checkpoint "logs/TEMP/2026-10-26_17-11-27/model_${policy_iter}.pt" \
      --curriculum-iteration "$curriculum_iter" \
      --num-envs 16 --episodes 32 --seed 42 --headless --device cuda:0
  done
done
```

출력은 조건별 episode CSV와 평균·커리큘럼 설정 JSON이다. 실행기는 원본 checkpoint·event·학습 로그를 수정하지 않는다. 실제 GPU play 출력이 확보되기 전에는 어느 내부 항이 몇 %를 설명하는지, 정착 보상 하락 중 물리 상태 변화와 공식 변경의 비중을 결론내릴 수 없다.

## 확인한 명령과 남은 검증

`env_isaaclab` Python의 `--help`는 exit0, `python -m py_compile`과 `git diff --check`는 통과했다. 실제 reward observer 연결·episode CSV·2×2 비교는 이 호스트에서 검증하지 못했다. GPU 실행에서는 첫 조건을1환경·1episode로 먼저 실행해 원래 보상과 세부 항의 reconciliation assertion이 통과하는지 확인한 뒤 나머지 조건을 실행한다. 출력의 episode별 원시 보상 합계와 TensorBoard의 10초 환산 평균은 집계 단위가 다르므로 직접 비교할 때 길이 보정이 필요하다. 원본 log의 정리·이동·삭제, `logs/rsl_rl` 수정, 새 학습은 수행하지 않았다.
