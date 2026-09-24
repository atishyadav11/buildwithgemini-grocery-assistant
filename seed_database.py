# seed_database.py
"""Seed script for initializing the Firestore grocery_products collection."""

from google.cloud import firestore

# CRITICAL: Hardcode GCP Project ID as a string so it works both locally and on Agent Platform
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-01-8566d63f79b1"

PRODUCTS_DATA = [
    {
        "id": "prod-001",
        "name": "Organic Gala Apples",
        "category": "Produce",
        "price": 2.99,
        "unit": "lb",
        "in_stock": True,
        "dietary_tags": ["organic", "vegan", "gluten-free"],
        "description": "Crisp and sweet organic gala apples sourced from Washington state orchards.",
    },
    {
        "id": "prod-002",
        "name": "Unsweetened Almond Milk",
        "category": "Dairy Alternatives",
        "price": 3.49,
        "unit": "carton (64 oz)",
        "in_stock": True,
        "dietary_tags": ["vegan", "gluten-free", "dairy-free"],
        "description": "Smooth plant-based milk with zero added sugar.",
    },
    {
        "id": "prod-003",
        "name": "Artisan Sourdough Bread",
        "category": "Bakery",
        "price": 4.99,
        "unit": "loaf",
        "in_stock": True,
        "dietary_tags": ["vegan"],
        "description": "Traditional naturally fermented sourdough loaf with a crispy crust.",
    },
    {
        "id": "prod-004",
        "name": "Organic Hass Avocados",
        "category": "Produce",
        "price": 1.99,
        "unit": "each",
        "in_stock": True,
        "dietary_tags": ["organic", "vegan", "gluten-free"],
        "description": "Creamy, perfectly ripe organic avocados.",
    },
    {
        "id": "prod-005",
        "name": "Organic Tricolor Quinoa",
        "category": "Pantry",
        "price": 5.29,
        "unit": "16 oz bag",
        "in_stock": True,
        "dietary_tags": ["organic", "vegan", "gluten-free"],
        "description": "Nutrient-dense ancient grain blend high in protein.",
    },
    {
        "id": "prod-006",
        "name": "Plain Greek Yogurt",
        "category": "Dairy",
        "price": 4.29,
        "unit": "32 oz tub",
        "in_stock": True,
        "dietary_tags": ["gluten-free", "vegetarian"],
        "description": "Rich and creamy whole-milk Greek yogurt packed with protein.",
    },
]


def seed_products():
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    collection_ref = db.collection("grocery_products")
    print(f"Seeding Firestore collection 'grocery_products' in project '{FIRESTORE_PROJECT_ID}'...")

    for item in PRODUCTS_DATA:
        doc_ref = collection_ref.document(item["id"])
        doc_ref.set(item)
        print(f"  ✓ Added/Updated item: {item['name']} ({item['id']})")

    print("Firestore seeding complete!")


if __name__ == "__main__":
    seed_products()
