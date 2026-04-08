from models import SREObservation, SREAction, SREState

class MLOpsEnvironment:
    def __init__(self):
        self.task_id = "task-1-easy-latency"
        self.step_count = 0
        self.max_steps = 10
        self.internal_state = {}
        self.obs = self._default_obs()

    def _default_obs(self):
        return SREObservation(
            active_alert=None, cluster_health="green", 
            last_command_output="System initialized.", active_pods=2, gpu_utilization_pct=50.0
        )

    def reset(self, task_id: str) -> SREObservation:
        self.task_id = task_id
        self.step_count = 0
        self.obs = self._default_obs()
        
        if task_id == "task-1-easy-latency":
            self.obs.active_alert = "P99 Latency > 5 seconds"
            self.obs.cluster_health = "yellow"
            self.obs.gpu_utilization_pct = 100.0
        elif task_id == "task-2-medium-config":
            self.obs.active_alert = "502 Bad Gateway - API Unreachable"
            self.obs.cluster_health = "red"
            self.internal_state["bug"] = "syntax_error"
        elif task_id == "task-3-hard-oom":
            self.obs.active_alert = "Node Unresponsive - GPU 0 Offline"
            self.obs.cluster_health = "red"
            self.internal_state["crashed_pod"] = "pod-cuda-03"
            
        return self.obs

    def step(self, action: SREAction):
        self.step_count += 1
        reward = -0.05  # Time penalty
        done = False

        if action.command == "get_metrics":
            self.obs.last_command_output = f"GPU: {self.obs.gpu_utilization_pct}%. Pods: {self.obs.active_pods}"
            reward += 0.2

        elif action.command == "read_pod_logs":
            if self.task_id == "task-2-medium-config":
                self.obs.last_command_output = "FATAL: SyntaxError in config.yaml line 42."
            elif self.task_id == "task-3-hard-oom":
                target = action.target_pod or "unknown"
                if target == "pod-cuda-03":
                    self.obs.last_command_output = "RuntimeError: CUDA out of memory. Tried to allocate 86.00 GiB."
                else:
                    self.obs.last_command_output = "Logs normal. Serving requests."
            else:
                self.obs.last_command_output = "Logs normal."
            reward += 0.2

        elif action.command == "scale_replicas":
            if self.task_id == "task-1-easy-latency" and action.replica_count and action.replica_count > 2:
                self.obs.active_pods = action.replica_count
                self.obs.gpu_utilization_pct = 40.0
                self.obs.cluster_health = "green"
                self.obs.last_command_output = f"Scaled up to {action.replica_count} pods. Latency dropping."
                reward += 0.5
            else:
                self.obs.last_command_output = "Scaling applied, but didn't fix the underlying issue."

        elif action.command == "rollback_deployment":
            if self.task_id == "task-2-medium-config":
                self.obs.cluster_health = "green"
                self.obs.last_command_output = "Rolled back to previous stable hash. API reachable."
                reward += 0.5
            else:
                self.obs.last_command_output = "Rollback failed or unnecessary."
                reward -= 0.2

        elif action.command == "restart_pod":
            if self.task_id == "task-3-hard-oom":
                if action.target_pod == "pod-cuda-03":
                    self.obs.cluster_health = "green"
                    self.obs.last_command_output = "Pod restarted. CUDA memory cleared."
                    reward += 0.6
                elif not action.target_pod:
                    self.obs.last_command_output = "CRITICAL: Restarted entire cluster. 5 minutes of downtime incurred."
                    reward -= 0.8
                    done = True
            else:
                self.obs.last_command_output = "Pod restarted."

        elif action.command == "resolve_incident":
            done = True
            if self.obs.cluster_health == "green":
                reward += 1.0  # Terminal success
            else:
                reward -= 0.5  # Terminal failure (falsely resolved)

        if self.step_count >= self.max_steps:
            done = True
            self.obs.last_command_output = "TIMEOUT: Escalated to on-call manager."

        return self.obs, reward, done

    def state(self) -> SREState:
        return SREState(task_id=self.task_id, step_count=self.step_count, resolved=self.obs.cluster_health == "green")