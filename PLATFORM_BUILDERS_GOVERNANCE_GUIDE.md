# Platform Builders Track: How to Build, Scale, Govern and Optimize Enterprise Agents

This directory contains the complete guide for the **Platform Builders Track** on Google Cloud's Gemini Enterprise Agent Platform.

---

## 📚 Module Overview

| Module | Document | Description |
| :--- | :--- | :--- |
| **Overview & Core Architecture** | [README.md](docs/platform-builders-track/README.md) | Architectural principles, steering skill, and operational guardrails for enterprise agent governance. |
| **Module 0: See Everything** | [M0_See_Everything.md](docs/platform-builders-track/M0_See_Everything.md) | Estate discovery, cross-checking official Agent Registry vs live running workloads, and identifying shadow agents. |
| **Module 1: Take Action** | [M1_Take_Action.md](docs/platform-builders-track/M1_Take_Action.md) | Registering shadow agents, splitting shared logins (Service Accounts), right-sizing IAM permissions, and proving least privilege. |
| **Module 2: Control Connections** | [M2_Control_Connections.md](docs/platform-builders-track/M2_Control_Connections.md) | Inbound A2A caller authorization (Resource IAM) and fine-grained Outbound Egress Gateway policy governance with IAP & CEL filters. |
| **Module 3: Protect Content** | [M3_Protect_Content.md](docs/platform-builders-track/M3_Protect_Content.md) | Ingress content screening and safety guardrails powered by Google Model Armor. |
| **Module 4: Observe Trajectory** | [M4_Observe_Trajectory.md](docs/platform-builders-track/M4_Observe_Trajectory.md) | OpenTelemetry distributed tracing, GenAI semantic conventions, and message payload capture (`SPAN_AND_EVENT`). |
| **Module 5: Evaluate and Decide** | [M5_Evaluate_and_Decide.md](docs/platform-builders-track/M5_Evaluate_and_Decide.md) | GenAI evaluation service, offline batch evaluation, and quality flywheel metrics prior to production go-live. |

---

## 🛠️ Key Platform Controls & Building Blocks

1. **Agent Registry**: Centralized catalog of official agents and tools (`gcloud agent-registry agents list`).
2. **Agent Identity**: SPIFFE-based per-agent principals (`principal://...`) ensuring fine-grained, auditable service-to-service communication.
3. **Egress Gateway & Authz Policies**: Default-deny outbound proxy controlling MCP tool execution and external API calls via CEL expressions.
4. **Model Armor**: Perimeter content safety filter inspecting prompts and agent outputs for sensitive data and policy compliance.
5. **Evaluation Quality Flywheel**: Automated scoring datasets and LLM-as-a-judge evaluation prior to enterprise deployment.
