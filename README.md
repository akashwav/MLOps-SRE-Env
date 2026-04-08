---
title: MLOps SRE Env
emoji: 📟
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
tags:
  - openenv
---

# MLOps-SRE-Env

A real-world OpenEnv simulator where an AI agent acts as a Site Reliability Engineer (SRE) to diagnose and resolve AI model endpoint failures.

## Motivation (Real-World Utility)
As AI engineers deploy more models to production, the bottleneck is infrastructure maintenance. This environment evaluates if frontier LLMs can safely navigate Kubernetes-style logic, query logs, and resolve incidents (like CUDA OOMs or bad configs) without taking destructive actions.

## Tasks & Progression
1. **Easy:** High Latency (Action: Check metrics, scale GPUs).
2. **Medium:** Bad Config (Action: Read logs, rollback deployment).
3. **Hard:** The CUDA Trap (Action: Isolate the single crashed pod from the logs and surgically restart it. Standard LLMs will fail by restarting the whole cluster).

## Setup
1. Build and run the server locally: `docker build -t mlops-env -f server/Dockerfile . && docker run -p 7860:7860 mlops-env`
2. Run baseline: `export OPENAI_API_KEY="your-key" && python baseline.py`