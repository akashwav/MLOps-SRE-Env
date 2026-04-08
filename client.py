from typing import Dict, Any
from core.http_env_client import HTTPEnvClient, StepResult
from models import SREAction, SREObservation, SREState

class MLOpsClient(HTTPEnvClient[SREAction, SREObservation]):
    def __init__(self, base_url: str = "http://localhost:7860"):
        super().__init__(base_url=base_url)

    def _step_payload(self, action: SREAction) -> dict:
        return action.model_dump()

    def _parse_result(self, payload: dict) -> StepResult[SREObservation]:
        return StepResult(
            observation=SREObservation(**payload["observation"]),
            reward=payload["reward"],
            done=payload["done"]
        )
        
    def reset(self, task_id: str = "task-1-easy-latency") -> StepResult[SREObservation]:
        import requests
        resp = requests.post(f"{self.base_url}/reset", json={"task_id": task_id})
        obs = SREObservation(**resp.json())
        return StepResult(observation=obs, reward=0.0, done=False)

    def state(self) -> SREState:
        import requests
        resp = requests.get(f"{self.base_url}/state")
        return SREState(**resp.json())