---

title: MLOps-SRE-Env
emoji: 📟
colorFrom: blue
colorTo: green
sdk: docker
app_file: server/app.py
pinned: false
-------------

# MLOps SRE Environment

This project simulates an MLOps SRE incident response system with:

* FastAPI backend (environment simulation)
* Gradio UI (human interaction)
* AI agent (baseline automation)

## Run locally

```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload
```
