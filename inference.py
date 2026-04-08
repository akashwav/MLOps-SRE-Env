import os
import json
from openai import OpenAI
from client import MLOpsClient
from models import SREAction

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are an SRE AI Agent. Fix the system. 
You must output valid JSON matching this schema:
{"command": "get_metrics|read_pod_logs|scale_replicas|restart_pod|rollback_deployment|resolve_incident", "target_pod": "str", "replica_count": 0}"""

def get_action(obs_dict: dict) -> SREAction:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"State: {json.dumps(obs_dict)}"}
        ]
    )
    return SREAction(**json.loads(response.choices[0].message.content))

def run_task(task_id: str):
    print(f"\n=== Running {task_id} ===")
    env = MLOpsClient()
    result = env.reset(task_id)
    total_reward = 0.0

    for step in range(1, 10):
        action = get_action(result.observation.model_dump())
        print(f"Step {step} | Action: {action.command}")
        
        result = env.step(action)
        total_reward += result.reward
        
        if result.done:
            break
            
    print(f"Final Score: {total_reward:.2f}")

if __name__ == "__main__":
    # Ensure the server is running (e.g. via Docker) before executing this
    run_task("task-1-easy-latency")
    run_task("task-2-medium-config")
    run_task("task-3-hard-oom")