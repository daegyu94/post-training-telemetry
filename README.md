# Post-Training Telemetry

분산 학습 실행의 상태와 성능을 관측하는 collector, metric SDK, dashboard와 분석 도구입니다.
먼저 host·GPU·통신·저장소와 학습 지표에서 이상이 발생한 시간·node·rank를 찾고, 원인 분석이 필요할 때만 해당 구간의 짧은 trace를 수집합니다.
Synthetic demo는 dashboard 동작을 보여 주기 위한 예시이며 실제 LLM 학습 결과와 구분합니다.

이 저장소는 workload launcher를 포함하지 않습니다.
[`post-training-lab`](https://github.com/daegyu94/post-training-lab)은 이 저장소를 `third_party/post-training-telemetry` submodule로 참조합니다.

## Layout

| 경로 | 내용 |
| --- | --- |
| `post_training_telemetry/metrics/` | framework를 import하지 않는 application metric SDK와 textfile 변환 |
| `post_training_telemetry/adapters/` | Hugging Face Trainer 등 framework adapter |
| `post_training_telemetry/` | GPU·host resource sampler, topology·live demo, stack 검증, `show_run`, run summary |
| `scripts/` | tool 설치, `node`·`storage`·`server` role 실행, profile·NCCL baseline |
| `examples/dashboards/` | Grafana dashboard와 Docker Compose 예시 |
| `config/` | Metrics Contract |

사용하는 쪽은 저장소 루트를 `PYTHONPATH`에 추가합니다.

```bash
export PYTHONPATH="/path/to/post-training-telemetry${PYTHONPATH:+:$PYTHONPATH}"
```

## Start Here

분산 실행을 관측하려면 먼저 [분산 실행 모니터링](docs/monitoring.md)에서 collector와 dashboard 설정 방법을 확인합니다.
이상이 발견되면 [실행 분석](docs/analysis.md)에 따라 run history를 확인하고, 필요한 구간의 selected-rank trace를 수집하거나 hardware baseline과 비교합니다.
지표를 추가하거나 해석할 때는 [Metrics Contract](docs/metrics.md)에 정의된 이름·단위·측정 범위를 따릅니다.
Training이나 agentic RL application에 metric을 연결할 때는 [Application Metrics Guide](docs/application-metrics.md)를 따릅니다.

| 목적 | 문서 |
| --- | --- |
| application에 metric emitter나 Trainer callback 연결 | [Application Metrics Guide](docs/application-metrics.md) |
| node collector, monitoring server, dashboard, SSD health, application metrics | [분산 실행 모니터링](docs/monitoring.md) |
| 과거 실행 요약, selected-rank PyTorch trace, NCCL baseline | [실행 분석](docs/analysis.md) |
| metric 이름·단위·scope, label, workflow phase | [Metrics Contract](docs/metrics.md) |

## Local Validation

GPU workload를 실행하기 전에 기본 도구 상태와 테스트를 로컬 환경에서 확인합니다.
다음 명령은 저장소 루트에서 실행합니다.
`setup.sh`는 `.venv`와 pytest만 준비하며 CUDA PyTorch, NCCL Tests, Python package는 설치하지 않습니다.

```bash
bash scripts/setup.sh
. .venv/bin/activate
bash scripts/check_tools.sh
python -m pytest -q
for f in scripts/*.sh; do bash -n "$f"; done
```

미설치 도구 표시는 해당 기능을 아직 사용할 수 없다는 뜻이며 다른 로컬 검사는 계속 실행할 수 있습니다.

## Migrating from `observability/`

`post-training-lab/observability`에서 분리하면서 다음 이름이 바뀌었습니다.
`training_*` application metric 이름은 그대로입니다.

| 이전 | 현재 |
| --- | --- |
| `scripts/run_observability.sh` | `scripts/run_telemetry.sh` |
| `scripts/install_observability_tools.sh` | `scripts/install_telemetry_tools.sh` |
| `scripts/validate_observability.sh` | `scripts/validate_stack.sh` |
| `observatory_metrics` | `post_training_telemetry.metrics` |
| `profiling_lab` | `post_training_telemetry` |
| `profiling_lab.telemetry` | `post_training_telemetry.gpu_sampler` |
| `profiling_lab.observability` | `post_training_telemetry.stack` |
| `resource_sampler.py`, `run_summary.py` (저장소 루트) | `post_training_telemetry.resource_sampler`, `post_training_telemetry.run_summary` |
| `OBSERVATORY_RUN_ID`, `OBSERVATORY_METRICS_DIR`, `OBSERVATORY_METRICS_INTERVAL` | `TELEMETRY_RUN_ID`, `TELEMETRY_METRICS_DIR`, `TELEMETRY_METRICS_INTERVAL` |
| `<output>/observatory-metrics/`, textfile `observatory.prom` | `<output>/telemetry-metrics/`, `application.prom` |
| Prometheus metric `profiling_gpu_*`, `profiling_topology_*` | `telemetry_gpu_*`, `telemetry_topology_*` |
| `examples/observability/` | `examples/dashboards/` |
| `OBSERVABILITY_TARGETS`, `OBSERVABILITY_LOG_ROOTS` | `TELEMETRY_TARGETS`, `TELEMETRY_LOG_ROOTS` |
| 기본 `TOOLS_DIR` `~/.local/share/observability-tools` | `TOOLS_DIR` 필수 지정 |
| Prometheus job `observability` | `telemetry` |
| Grafana uid `observability-{overview,prometheus,loki}` | `telemetry-{overview,prometheus,loki}` |

기존 tool 설치를 다시 내려받지 않으려면 `TOOLS_DIR`에 이전 경로를 지정합니다.
Prometheus job과 Grafana uid가 바뀌었으므로 이전 monitoring state의 TSDB·dashboard와 새 시계열은 이어지지 않습니다.
