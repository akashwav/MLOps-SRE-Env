from fastapi import FastAPI
from pydantic import BaseModel
import gradio as gr
from models import SREObservation, SREAction, SREState
from server.environment import MLOpsEnvironment

app = FastAPI()
env = MLOpsEnvironment()

# --- 1. The OpenEnv API Routes (For the Auto-Grader) ---
class ResetRequest(BaseModel):
    task_id: str

@app.post("/reset", response_model=SREObservation)
async def reset(req: ResetRequest):
    return env.reset(req.task_id)

@app.post("/step")
async def step(action: SREAction):
    obs, reward, done = env.step(action)
    return {"observation": obs.model_dump(), "reward": reward, "done": done}

@app.get("/state", response_model=SREState)
async def state():
    return env.state()

# --- 2. The Gradio UI (For the Human Judges) ---
def ui_reset(task):
    obs = env.reset(task)
    return f"Loaded {task}\nHealth: {obs.cluster_health.upper()}", obs.last_command_output

def ui_step(command, target, replicas):
    # Map UI inputs to our strict Pydantic model
    action = SREAction(
        command=command, 
        target_pod=target if target else None, 
        replica_count=int(replicas) if replicas else None
    )
    obs, reward, done = env.step(action)
    
    status = f"Health: {obs.cluster_health.upper()} | Pods: {obs.active_pods} | GPU: {obs.gpu_utilization_pct}%\nReward: {reward} | Done: {done}"
    return status, obs.last_command_output

with gr.Blocks(theme=gr.themes.Monochrome()) as dashboard:
    gr.Markdown("# 📟 MLOps SRE Incident Response Terminal")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1. Select Incident")
            task_dropdown = gr.Dropdown(
                choices=["task-1-easy-latency", "task-2-medium-config", "task-3-hard-oom"], 
                value="task-1-easy-latency", label="Alert"
            )
            reset_btn = gr.Button("Acknowledge Alert (Reset Env)")
            system_status = gr.Textbox(label="Cluster Status", lines=2)
            
        with gr.Column(scale=2):
            gr.Markdown("### 2. SRE Toolkit")
            with gr.Row():
                cmd_dropdown = gr.Dropdown(
                    choices=["get_metrics", "read_pod_logs", "scale_replicas", "restart_pod", "rollback_deployment", "resolve_incident"],
                    label="Command"
                )
                target_input = gr.Textbox(label="Target Pod (Optional)")
                replica_input = gr.Number(label="Replicas (Optional)", precision=0)
            
            execute_btn = gr.Button("Execute Command", variant="primary")
            terminal_out = gr.Textbox(label="Terminal Output", lines=5)

    reset_btn.click(ui_reset, inputs=[task_dropdown], outputs=[system_status, terminal_out])
    execute_btn.click(ui_step, inputs=[cmd_dropdown, target_input, replica_input], outputs=[system_status, terminal_out])

# Mount Gradio onto the FastAPI app
app = gr.mount_gradio_app(app, dashboard, path="/")