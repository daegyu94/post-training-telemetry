import pytest

from post_training_telemetry import gpu_sampler


@pytest.mark.parametrize("value", ["[N/A]", "Not Supported", "nan", ""])
def test_unavailable_is_null(value):
    assert gpu_sampler.optional_number(value) is None


def test_zero_is_still_a_measurement():
    assert gpu_sampler.optional_number("0") == 0


def test_device_and_process_memory_are_independent(monkeypatch):
    def fake_query(kind, fields):
        if kind == "gpu":
            return [["0", "0", "5", "45", "208", "[N/A]", "[N/A]"]]
        return [["GPU-example", "123", "python", "412"]]

    monkeypatch.setattr(gpu_sampler, "query", fake_query)
    value = gpu_sampler.snapshot()
    assert value["gpus"][0]["memory.used"] is None
    assert value["compute_processes"][0]["used_gpu_memory_mib"] == 412
