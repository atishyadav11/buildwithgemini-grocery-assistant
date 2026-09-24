# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

load_dotenv()


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """Converts temperature between Celsius, Fahrenheit, and Kelvin.

    Args:
        value: The numerical temperature value.
        from_unit: Source unit ('C', 'F', or 'K').
        to_unit: Target unit ('C', 'F', or 'K').

    Returns:
        Converted temperature formatted as a string.
    """
    f_u, t_u = from_unit.upper().strip(), to_unit.upper().strip()
    # Convert to Celsius first
    if f_u in ("C", "CELSIUS"):
        c_val = value
    elif f_u in ("F", "FAHRENHEIT"):
        c_val = (value - 32) * 5 / 9
    elif f_u in ("K", "KELVIN"):
        c_val = value - 273.15
    else:
        return f"Unknown source unit '{from_unit}'."

    # Convert Celsius to target
    if t_u in ("C", "CELSIUS"):
        result = c_val
    elif t_u in ("F", "FAHRENHEIT"):
        result = c_val * 9 / 5 + 32
    elif t_u in ("K", "KELVIN"):
        result = c_val + 273.15
    else:
        return f"Unknown target unit '{to_unit}'."

    return f"{value} °{f_u[0]} is equal to {result:.2f} °{t_u[0]}"


import json
from pathlib import Path

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from app.a2ui_utils import a2ui_callback
from app.tools import (
    add_or_update_product,
    find_nearby_places,
    generate_item_image,
    generate_item_video,
    geocode_address,
    get_product_details,
    manage_shopping_cart,
    search_products,
    search_recipes,
)


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback executed after each agent turn to store durable memories into Memory Bank."""
    await callback_context.add_session_to_memory()
    return None


# Build A2UI System Prompt using A2uiSchemaManager (version 0.8) and BasicCatalog
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are the Smart Grocery Assistant agent. You help shoppers search products, "
        "find real recipes, generate product/dish images and short video previews, manage shopping carts, geocode locations, "
        "locate nearby grocery stores, and perform calculations or data processing safely using Python code execution.\n\n"
        "CRITICAL MANDATE - USER ALLERGIES & DIETARY RESTRICTIONS:\n"
        "1. You MUST remember, track, and record ALL user allergies (e.g. peanuts, tree nuts, gluten, dairy/lactose, shellfish, eggs, soy, etc.), intolerances, and dietary preferences across sessions.\n"
        "2. Whenever a user mentions an allergy or dietary restriction, explicitly acknowledge it and ensure it is saved in memory.\n"
        "3. Before recommending any grocery products or recipes, review all remembered user allergies to warn the user about allergens or suggest safe alternative products."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


# Load Agent Engine sandbox code executor from deployment_metadata.json
code_executor = None
metadata_file = Path(__file__).resolve().parent.parent / "deployment_metadata.json"

if metadata_file.exists():
    try:
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        agent_engine_id = metadata.get("remote_agent_runtime_id")
        if agent_engine_id:
            code_executor = AgentEngineSandboxCodeExecutor(
                sandbox_resource_name="projects/474836361338/locations/us-east1/reasoningEngines/1578786547300302848/sandboxEnvironments/8086208530343362560",
                agent_engine_resource_name=agent_engine_id,
            )
    except Exception:
        pass

if not code_executor:
    code_executor = AgentEngineSandboxCodeExecutor(
        sandbox_resource_name="projects/474836361338/locations/us-east1/reasoningEngines/1578786547300302848/sandboxEnvironments/8086208530343362560"
    )


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=a2ui_instruction,
    tools=[
        get_weather,
        get_current_time,
        convert_temperature,
        search_products,
        get_product_details,
        add_or_update_product,
        manage_shopping_cart,
        search_recipes,
        geocode_address,
        find_nearby_places,
        generate_item_image,
        generate_item_video,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

