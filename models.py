from pydantic import BaseModel, Field
from typing import Literal, Optional

class SREObservation(BaseModel):
    active_alert: Optional[str] = Field(description="The current PagerDuty alert.")
    cluster_health: Literal["green", "yellow", "red"] = Field(description="Overall health.")
    last_command_output: str = Field(description="Terminal output from the previous command.")
    active_pods: int = Field(description="Number of currently running inference pods.")
    gpu_utilization_pct: float = Field(description="Average GPU utilization.")

class SREAction(BaseModel):
    command: Literal[
        "get_metrics", 
        "read_pod_logs", 
        "scale_replicas", 
        "restart_pod", 
        "rollback_deployment",
        "resolve_incident"
    ]
    target_pod: Optional[str] = Field(None, description="Required for read_pod_logs and restart_pod.")
    replica_count: Optional[int] = Field(None, description="Required for scale_replicas.")

class SREState(BaseModel):
    task_id: str
    step_count: int
    resolved: bool