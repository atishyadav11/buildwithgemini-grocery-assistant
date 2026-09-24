# app/tools/firestore_tools.py
"""Firestore tool definitions for the Grocery Assistant agent."""

from google.cloud import firestore

# CRITICAL: Hardcode GCP Project ID as a string so it works both locally and on Agent Platform
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-01-8566d63f79b1"


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded GCP project ID."""
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def search_products(query: str = "", category: str = "", dietary_tag: str = "") -> str:
    """Search for grocery products in the Firestore database.

    Args:
        query: Optional search keyword to match product name or description (case-insensitive).
        category: Optional category filter (e.g. Produce, Dairy, Bakery, Pantry, Dairy Alternatives).
        dietary_tag: Optional dietary filter (e.g. organic, vegan, gluten-free, dairy-free).

    Returns:
        Formatted string listing matching products with ID, name, price, category, and stock status.
    """
    db = get_firestore_client()
    docs = db.collection("grocery_products").stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        
        # Category filter
        if category and data.get("category", "").lower() != category.lower():
            continue
            
        # Dietary tag filter
        if dietary_tag and dietary_tag.lower() not in [t.lower() for t in data.get("dietary_tags", [])]:
            continue
            
        # Query keyword filter
        if query:
            q_lower = query.lower()
            name_match = q_lower in data.get("name", "").lower()
            desc_match = q_lower in data.get("description", "").lower()
            if not (name_match or desc_match):
                continue
                
        results.append(data)
        
    if not results:
        return "No grocery products matched your criteria."
        
    output = [f"Found {len(results)} product(s):"]
    for p in results:
        stock_str = "In Stock" if p.get("in_stock", True) else "Out of Stock"
        tags_str = ", ".join(p.get("dietary_tags", []))
        output.append(
            f"- [{p['id']}] {p['name']} (${p['price']:.2f} / {p['unit']}) - {p['category']} | {stock_str} | Tags: [{tags_str}]"
        )
    return "\n".join(output)


def get_product_details(product_id: str) -> str:
    """Get full details for a specific grocery product by its ID.

    Args:
        product_id: The unique product identifier (e.g. 'prod-001').

    Returns:
        Formatted string containing all details of the specified product.
    """
    db = get_firestore_client()
    doc_ref = db.collection("grocery_products").document(product_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        return f"Product with ID '{product_id}' was not found in database."
        
    p = doc.to_dict()
    tags_str = ", ".join(p.get("dietary_tags", []))
    stock_str = "In Stock" if p.get("in_stock", True) else "Out of Stock"
    
    return (
        f"Product Details for [{doc.id}]:\n"
        f"Name: {p.get('name')}\n"
        f"Category: {p.get('category')}\n"
        f"Price: ${p.get('price'):.2f} / {p.get('unit')}\n"
        f"Stock Status: {stock_str}\n"
        f"Dietary Tags: {tags_str}\n"
        f"Description: {p.get('description', 'N/A')}"
    )


def add_or_update_product(
    product_id: str,
    name: str,
    category: str,
    price: float,
    unit: str,
    dietary_tags: list[str] | str,
    in_stock: bool = True,
    description: str = "",
) -> str:
    """Add a new product or update an existing product in the Firestore catalog.

    Args:
        product_id: Unique product ID (e.g., 'prod-007').
        name: Name of the product (e.g., 'Organic Bananas').
        category: Product category (e.g., 'Produce').
        price: Price per unit (e.g., 1.49).
        unit: Unit of measure (e.g., 'bunch').
        dietary_tags: List or comma-separated string of dietary tags (e.g. ['organic', 'vegan']).
        in_stock: Whether the item is currently in stock.
        description: Brief product description.

    Returns:
        Status message confirming the addition or update.
    """
    db = get_firestore_client()
    
    if isinstance(dietary_tags, str):
        dietary_tags = [t.strip() for t in dietary_tags.split(",") if t.strip()]
        
    product_data = {
        "id": product_id,
        "name": name,
        "category": category,
        "price": float(price),
        "unit": unit,
        "dietary_tags": dietary_tags,
        "in_stock": in_stock,
        "description": description,
    }
    
    doc_ref = db.collection("grocery_products").document(product_id)
    doc_ref.set(product_data)
    
    return f"Successfully saved product '{name}' ({product_id}) to Firestore!"


def manage_shopping_cart(action: str, product_id: str = "", quantity: int = 1) -> str:
    """Manage items in the user's active shopping cart in Firestore.

    Args:
        action: Cart operation: 'add', 'remove', 'view', or 'clear'.
        product_id: Product ID to add or remove (e.g. 'prod-001').
        quantity: Quantity of the product (default: 1).

    Returns:
        Formatted status message showing cart contents and total price.
    """
    db = get_firestore_client()
    cart_ref = db.collection("shopping_carts").document("active_cart")
    doc = cart_ref.get()

    cart_data = doc.to_dict() if doc.exists else {"items": {}}
    items = cart_data.get("items", {})

    action_clean = action.lower().strip()

    if action_clean == "clear":
        cart_ref.set({"items": {}})
        return "Shopping cart has been cleared."

    if action_clean == "view":
        if not items:
            return "Your shopping cart is currently empty."
        lines = ["🛒 Current Shopping Cart:"]
        total = 0.0
        for item_id, item_info in items.items():
            item_total = item_info.get("price", 0.0) * item_info.get("quantity", 1)
            total += item_total
            lines.append(
                f"- [{item_id}] {item_info.get('name')} x{item_info.get('quantity')} @ ${item_info.get('price', 0.0):.2f} = ${item_total:.2f}"
            )
        lines.append(f"Grand Total: ${total:.2f}")
        return "\n".join(lines)

    if action_clean == "add":
        if not product_id:
            return "Please provide a valid product_id to add to cart."
        prod_doc = db.collection("grocery_products").document(product_id.strip()).get()
        if not prod_doc.exists:
            return f"Product '{product_id}' not found in grocery catalog."
        prod_info = prod_doc.to_dict()

        curr_qty = items.get(product_id, {}).get("quantity", 0)
        new_qty = curr_qty + quantity
        items[product_id] = {
            "name": prod_info.get("name"),
            "price": prod_info.get("price", 0.0),
            "unit": prod_info.get("unit"),
            "quantity": new_qty,
        }
        cart_ref.set({"items": items})
        return f"Added {quantity}x '{prod_info.get('name')}' to cart. Total quantity in cart: {new_qty}."

    if action_clean == "remove":
        if not product_id or product_id not in items:
            return f"Product '{product_id}' is not currently in your cart."
        prod_name = items[product_id].get("name", product_id)
        del items[product_id]
        cart_ref.set({"items": items})
        return f"Removed '{prod_name}' from cart."

    return f"Unknown action '{action}'. Supported actions: 'add', 'remove', 'view', 'clear'."

