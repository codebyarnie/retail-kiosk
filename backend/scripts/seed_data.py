"""Seed database with sample data for development and testing."""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings
from app.models import Category, Product, ProductCategory


# Sample categories
CATEGORIES = [
    {
        "name": "Screws & Fasteners",
        "slug": "screws-fasteners",
        "description": "All types of screws, bolts, and fastening hardware",
        "display_order": 1,
        "children": [
            {"name": "Wood Screws", "slug": "wood-screws", "description": "Screws designed for wood applications"},
            {"name": "Deck Screws", "slug": "deck-screws", "description": "Outdoor screws for decking projects"},
            {"name": "Drywall Screws", "slug": "drywall-screws", "description": "Screws for drywall installation"},
            {"name": "Machine Screws", "slug": "machine-screws", "description": "Precision screws for machinery"},
        ]
    },
    {
        "name": "Power Tools",
        "slug": "power-tools",
        "description": "Electric and battery-powered tools",
        "display_order": 2,
        "children": [
            {"name": "Drills", "slug": "drills", "description": "Corded and cordless drills"},
            {"name": "Impact Drivers", "slug": "impact-drivers", "description": "High-torque fastening tools"},
            {"name": "Sanders", "slug": "sanders", "description": "Power sanding tools"},
        ]
    },
    {
        "name": "Building Materials",
        "slug": "building-materials",
        "description": "Lumber, drywall, and construction materials",
        "display_order": 3,
        "children": [
            {"name": "Lumber", "slug": "lumber", "description": "Wood boards and beams"},
            {"name": "Drywall", "slug": "drywall", "description": "Wall and ceiling panels"},
        ]
    },
]

# Sample products
PRODUCTS = [
    # Screws
    {
        "sku": "SCREW-DECK-SS-10x3",
        "name": "Stainless Steel Deck Screw #10 x 3\"",
        "description": "Premium stainless steel deck screws, designed for outdoor use. Corrosion-resistant, perfect for treated lumber and composite decking. Star drive head for superior grip.",
        "short_description": "SS deck screw, corrosion-resistant, #10 x 3\"",
        "price": 24.99,
        "attributes": {"material": "stainless steel", "size": "#10 x 3\"", "drive": "star", "coating": "none"},
        "specifications": {"quantity": "100 pack", "weight": "2.5 lbs"},
        "categories": ["deck-screws"],
        "is_featured": True,
    },
    {
        "sku": "SCREW-WOOD-ZINC-8x2",
        "name": "Zinc-Coated Wood Screw #8 x 2\"",
        "description": "General purpose wood screws with zinc coating for indoor use. Phillips head, sharp point for easy starting.",
        "short_description": "Zinc wood screw, #8 x 2\", indoor use",
        "price": 12.99,
        "attributes": {"material": "steel", "size": "#8 x 2\"", "drive": "phillips", "coating": "zinc"},
        "specifications": {"quantity": "200 pack", "weight": "1.5 lbs"},
        "categories": ["wood-screws"],
        "is_featured": False,
    },
    {
        "sku": "SCREW-DRY-PHOS-6x1.25",
        "name": "Phosphate Drywall Screw #6 x 1-1/4\"",
        "description": "Fine thread drywall screws with phosphate coating. Bugle head design reduces paper tear. Ideal for hanging drywall on wood studs.",
        "short_description": "Drywall screw, fine thread, #6 x 1-1/4\"",
        "price": 8.99,
        "attributes": {"material": "steel", "size": "#6 x 1-1/4\"", "drive": "phillips", "coating": "phosphate", "thread": "fine"},
        "specifications": {"quantity": "500 pack", "weight": "2 lbs"},
        "categories": ["drywall-screws"],
        "is_featured": True,
    },
    # Power Tools
    {
        "sku": "DRILL-CORD-20V-DEWALT",
        "name": "DeWalt 20V MAX Cordless Drill Driver",
        "description": "Professional-grade cordless drill with 20V MAX battery system. Two-speed transmission (0-450/0-1500 RPM). Compact and lightweight design for tight spaces. Includes battery and charger.",
        "short_description": "DeWalt 20V cordless drill, 2-speed, battery included",
        "price": 149.99,
        "attributes": {"brand": "DeWalt", "voltage": "20V", "type": "cordless", "speeds": 2},
        "specifications": {"rpm_low": "0-450", "rpm_high": "0-1500", "chuck": "1/2\"", "weight": "3.5 lbs"},
        "categories": ["drills"],
        "is_featured": True,
    },
    {
        "sku": "IMPACT-CORD-20V-DEWALT",
        "name": "DeWalt 20V MAX Impact Driver",
        "description": "High-torque impact driver for driving long screws and large fasteners. 1825 in-lbs of torque. Compatible with 20V MAX batteries. Compact design fits in tight spaces.",
        "short_description": "DeWalt 20V impact driver, 1825 in-lbs torque",
        "price": 129.99,
        "attributes": {"brand": "DeWalt", "voltage": "20V", "type": "cordless", "torque": "1825 in-lbs"},
        "specifications": {"rpm": "0-2800", "impacts_per_min": "0-3200", "weight": "2.0 lbs"},
        "categories": ["impact-drivers"],
        "is_featured": True,
    },
    {
        "sku": "SANDER-ORB-5IN-MAKITA",
        "name": "Makita 5\" Random Orbit Sander",
        "description": "Variable speed random orbit sander with dust collection. Ergonomic palm grip design. 3.0 amp motor with variable speed dial. Perfect for finishing work.",
        "short_description": "Makita 5\" random orbit sander, variable speed",
        "price": 89.99,
        "attributes": {"brand": "Makita", "size": "5\"", "type": "random orbit", "power": "corded"},
        "specifications": {"amps": "3.0", "speed_range": "4000-12000 OPM", "weight": "2.9 lbs"},
        "categories": ["sanders"],
        "is_featured": False,
    },
    # Building Materials
    {
        "sku": "LUMBER-2X4-8FT-SPF",
        "name": "2x4 SPF Stud 8ft",
        "description": "Kiln-dried SPF (Spruce-Pine-Fir) dimensional lumber. Ideal for framing, general construction, and DIY projects. Straight and true for accurate building.",
        "short_description": "2x4 SPF stud lumber, 8 foot length",
        "price": 5.99,
        "attributes": {"species": "SPF", "dimensions": "2x4", "length": "8ft", "grade": "construction"},
        "specifications": {"actual_size": "1.5\" x 3.5\"", "treatment": "kiln-dried"},
        "categories": ["lumber"],
        "is_featured": False,
    },
    {
        "sku": "DRYWALL-0.5-4X8",
        "name": "1/2\" Drywall Panel 4x8",
        "description": "Standard 1/2\" thick drywall panel for interior walls and ceilings. Fire-resistant gypsum core with paper facing. Easy to cut and install.",
        "short_description": "1/2\" drywall sheet, 4ft x 8ft",
        "price": 14.99,
        "attributes": {"thickness": "1/2\"", "size": "4x8", "type": "standard"},
        "specifications": {"weight": "54 lbs", "fire_rating": "class A"},
        "categories": ["drywall"],
        "is_featured": False,
    },
]


async def seed_database():
    """Seed the database with sample data."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if data already exists
        result = await session.execute(select(Product).limit(1))
        if result.scalar_one_or_none():
            print("Database already has data. Skipping seed.")
            return

        print("Seeding categories...")
        category_map = {}  # slug -> category

        for cat_data in CATEGORIES:
            children = cat_data.pop("children", [])

            # Create parent category
            parent = Category(**cat_data, is_active=True)
            session.add(parent)
            await session.flush()
            category_map[parent.slug] = parent
            print(f"  Created category: {parent.name}")

            # Create child categories
            for child_data in children:
                child = Category(**child_data, parent_id=parent.id, is_active=True, display_order=0)
                session.add(child)
                await session.flush()
                category_map[child.slug] = child
                print(f"    Created subcategory: {child.name}")

        print("\nSeeding products...")
        for prod_data in PRODUCTS:
            categories = prod_data.pop("categories", [])

            # Create product
            product = Product(**prod_data, is_active=True)
            session.add(product)
            await session.flush()
            print(f"  Created product: {product.name}")

            # Add category associations
            for cat_slug in categories:
                if cat_slug in category_map:
                    assoc = ProductCategory(
                        product_id=product.id,
                        category_id=category_map[cat_slug].id
                    )
                    session.add(assoc)

        await session.commit()
        print("\nSeed completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
