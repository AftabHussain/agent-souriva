from souriva.agent import Action, AgentResult
from souriva.alignment import GroundedAnswer
from souriva.config import Settings
from souriva.tracking import log_agent_run, log_evaluation


def test_tracking_is_noop_when_disabled(tmp_path):
    settings = Settings(data_dir=tmp_path, mlflow_enabled=False)
    result = AgentResult(
        GroundedAnswer("I do not have enough evidence to answer.", (), True),
        (),
        (Action.RETRIEVE, Action.ABSTAIN),
    )

    assert log_agent_run("Unknown?", result, 1.5, settings) is None
    assert log_evaluation({"latency_ms": 1.5}, [], settings) is None

