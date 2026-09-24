# app/tools/api_tools.py
"""Public API function tools for the Grocery Assistant agent."""

import json
import os
import urllib.parse
import urllib.request


def search_recipes(query: str) -> str:
    """Search for real recipe suggestions by main ingredient or dish name using TheMealDB public API.

    Args:
        query: Main ingredient or meal keyword (e.g. 'apple', 'chicken', 'salmon', 'pasta').

    Returns:
        Formatted summary of real matching recipes with category, main ingredients, instructions, and thumbnail image.
    """
    api_key = os.getenv("MEALDB_API_KEY", "1")  # Default to free public tier "1"
    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={encoded_query}"

    req = urllib.request.Request(url, headers={"User-Agent": "GroceryAssistant/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        return f"Failed to fetch recipes: {str(e)}"

    meals = data.get("meals")
    if not meals:
        return f"No recipes found for '{query}'."

    results = []
    for m in meals[:3]:  # Limit to top 3 matching recipes
        name = m.get("strMeal")
        category = m.get("strCategory")
        area = m.get("strArea", "International")
        thumb = m.get("strMealThumb")

        # Collect non-empty ingredients
        ingredients = []
        for i in range(1, 21):
            ing = m.get(f"strIngredient{i}")
            meas = m.get(f"strMeasure{i}")
            if ing and ing.strip():
                meas_str = f" ({meas.strip()})" if meas and meas.strip() else ""
                ingredients.append(f"{ing.strip()}{meas_str}")

        instructions = m.get("strInstructions", "")
        short_instructions = (
            instructions[:180].replace("\r\n", " ") + "..."
            if len(instructions) > 180
            else instructions.replace("\r\n", " ")
        )

        results.append(
            f"🍳 {name} ({category} | {area})\n"
            f"   - Ingredients: {', '.join(ingredients[:8])}\n"
            f"   - Quick Instructions: {short_instructions}\n"
            f"   - Image: {thumb}"
        )

    return "\n\n".join(results)
