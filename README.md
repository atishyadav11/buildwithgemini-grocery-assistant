# Grocery Assistant

An intelligent conversational grocery and meal-planning AI agent built with the **Google Agent Development Kit (ADK)**, **Gemini 2.5 Flash**, **Vertex AI**, and **Agent-to-User Interface (A2UI)**.

The Grocery Assistant enables users to search product catalog items, manage persistent shopping carts, search real recipes, locate nearby supermarkets, track personal dietary restrictions, and dynamically generate product/dish images and video previews.

---

## 🌟 Core Capabilities & Tools

All features below are implemented and active in `app/` and `app/tools/`:

* **Product Inventory Search & Management** (`app/tools/firestore_tools.py`)
  * Search products by name or category and inspect inventory status.
  * Add new products or update existing item details in Cloud Firestore.

* **Shopping Cart Management** (`app/tools/firestore_tools.py`)
  * Add, remove, view, and clear shopping cart items with persistent quantity tracking backed by Cloud Firestore.

* **Recipe Discovery** (`app/tools/api_tools.py`)
  * Search real-world recipes filtered by keywords, cuisine, or dietary restrictions via the Spoonacular API.

* **Location & Geocoding** (`app/tools/maps_tools.py`)
  * Geocode street addresses into coordinates using the Google Maps Geocoding API.
  * Search for nearby grocery stores, markets, or supermarkets using the Google Maps Places API.

* **AI Image Generation** (`app/tools/image_tools.py`)
  * Generate high-quality product and dish photos using `gemini-3.1-flash-lite-image` in Vertex AI (`global` location).
  * Automatically saves generated images as ADK Artifacts and uploads them to Google Cloud Storage to serve public HTTPS URLs.

* **AI Video Generation** (`app/tools/video_tools.py`)
  * Generate short video previews for grocery items or recipes using Google's Omni model (`gemini-omni-flash-preview`) in Vertex AI (`global` location) via the Interactions API.
  * Saves video outputs as ADK Artifacts and uploads video bytes to Google Cloud Storage for public HTTPS streaming.

* **Durable Memory & Allergy Tracking** (`app/agent.py`)
  * Automatically records user allergies, dietary restrictions, and personal food preferences across sessions using ADK Memory Bank callbacks.

* **Secure Code Execution** (`app/agent.py`)
  * Safely executes calculations and data processing using an isolated Agent Engine sandbox (`AgentEngineSandboxCodeExecutor`).

* **Structured Dynamic UI (A2UI v0.8)** (`app/a2ui_utils.py`)
  * Dynamically generates structured visual components (Cards, Columns, Text, Images) for rich response rendering in the client interface.

---

## ☁️ Google Cloud Services Integrated

The codebase directly integrates with the following Google Cloud services:

* **Google Cloud Agent Platform / Agent Engine**: Hosted ADK agent runtime and sandbox execution environment.
* **Google Cloud Firestore**: NoSQL document store backing product inventory (`products`) and user shopping carts (`carts`).
* **Google Cloud Storage (GCS)**: Bucket storage hosting generated product images and video previews.
* **Vertex AI / Gemini Models**:
  * `gemini-2.5-flash` for agent reasoning, dialogue orchestration, and tool selection.
  * `gemini-3.1-flash-lite-image` for AI image generation.
  * `gemini-omni-flash-preview` for AI video generation via the Interactions API.
* **Google Maps Platform**: Google Maps Geocoding API and Places API.
* **Google Cloud Run**: Serverless container platform hosting the FastAPI web frontend.

---

## 📁 Project Structure

```
grocery-assistant/
├── app/                        # Core ADK Agent code
│   ├── agent.py                # Agent configuration, tools, and A2UI instruction
│   ├── a2ui_utils.py           # A2UI callback and surface rendering helpers
│   ├── fast_api_app.py         # Agent FastAPI application entrypoint
│   └── tools/                  # Custom tool modules
│       ├── api_tools.py        # Spoonacular Recipe Search API
│       ├── firestore_tools.py  # Firestore Products and Carts CRUD
│       ├── image_tools.py      # Vertex AI Image Generation & GCS upload
│       ├── maps_tools.py       # Google Maps Geocoding & Places API
│       └── video_tools.py      # Vertex AI Omni Video Generation & GCS upload
├── frontend/                   # Web Interface
│   ├── main.py                 # FastAPI proxy server connecting UI to Agent Engine
│   └── static/
│       └── index.html          # Single-page chat interface with A2UI renderer
├── deployment_metadata.json    # Agent Engine deployment metadata
├── agents-cli-manifest.yaml    # Agents CLI configuration
├── seed_database.py            # Firestore database seeding script
├── pyproject.toml              # Python project dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Setup & Local Execution

### Prerequisites

Ensure you have installed:
* **Python 3.11+**
* **uv** (Python package manager): `pip install uv`
* **Google Cloud SDK (`gcloud`)**: Authenticated with `gcloud auth application-default login`

### 1. Installation

Install all project dependencies using `agents-cli` or `uv`:

```bash
uv sync
```

### 2. Seeding Firestore Database

Populate the Firestore database with sample grocery products:

```bash
python seed_database.py
```

### 3. Local Agent Testing via Playground

To test the agent locally using the ADK Playground:

```bash
agents-cli playground
```

### 4. Running the Web Frontend Locally

To run the custom FastAPI frontend locally:

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set the required environment variables:
   ```bash
   export AGENT_ENGINE_RESOURCE_NAME="<your-agent-engine-resource-name>"
   export AGENT_DIRECTORY="app"
   ```

4. Start the server on port 8080:
   ```bash
   python main.py
   ```

---

## 🌐 Cloud Run Deployment

To deploy the frontend to Google Cloud Run:

```bash
cd frontend
gcloud run deploy grocery-assistant-frontend \
  --source . \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars="AGENT_ENGINE_RESOURCE_NAME=$AGENT_ENGINE_RESOURCE_NAME,AGENT_DIRECTORY=app"
```

Grant the Cloud Run service account access to invoke Agent Engine:

```bash
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:<SERVICE_ACCOUNT_EMAIL>" \
  --role="roles/aiplatform.user"
```
