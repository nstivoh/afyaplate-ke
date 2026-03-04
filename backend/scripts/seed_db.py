import csv
import re
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.sql_models import SQLFood, SQLClient

KJ_TO_KCAL = 4.184

# Matches a real food entry: starts with 5-digit code
FOOD_CODE_PATTERN = re.compile(r'^(\d{5})\s+(.+)')

# Strips trailing " 1.00" multiplier and trailing commas
TRAILING_MULTIPLIER = re.compile(r'\s+1\.00$')


def safe_float(val, default: float = 0.0) -> float:
    try:
        if val is None:
            return default
        return float(val) if str(val).strip() else default
    except (ValueError, TypeError):
        return default


def clean_food_name(raw: str) -> str:
    """Strip food code prefix, trailing multipliers, and clean up the name."""
    match = FOOD_CODE_PATTERN.match(raw.strip())
    if not match:
        return raw.strip()
    name = match.group(2).strip()
    # Remove trailing "1.00" multiplier
    name = TRAILING_MULTIPLIER.sub('', name)
    # Remove trailing comma
    name = name.rstrip(',').strip()
    # Title-case the first letter
    if name:
        name = name[0].upper() + name[1:]
    return name


def extract_food_code(raw: str) -> str:
    match = FOOD_CODE_PATTERN.match(raw.strip())
    return match.group(1) if match else ""


def extract_category(food_code: str) -> str:
    """Map KFCT 2-digit prefix to human-readable category."""
    categories = {
        "01": "Cereals & Grains",
        "02": "Starchy Roots & Tubers",
        "03": "Legumes & Pulses",
        "04": "Nuts & Seeds",
        "05": "Vegetables",
        "06": "Fruits",
        "07": "Meat & Poultry",
        "08": "Fish & Seafood",
        "09": "Eggs",
        "10": "Milk & Dairy",
        "11": "Oils & Fats",
        "12": "Sugars & Sweets",
        "13": "Beverages",
        "14": "Spices & Condiments",
        "15": "Composite Dishes",
        "16": "Snacks & Street Foods",
        "17": "Baby Foods",
        "18": "Special Dietary",
    }
    prefix = food_code[:2] if food_code else ""
    return categories.get(prefix, "Other")


def init_db():
    Base.metadata.create_all(bind=engine)


def seed_foods(db: Session):
    """Seed foods from KFCT CSV with proper filtering and cleanup."""
    # Always re-seed to get clean data
    existing = db.query(SQLFood).count()
    if existing > 0:
        print(f"Clearing {existing} existing food entries...")
        db.query(SQLFood).delete()
        db.commit()

    data_path = Path(__file__).resolve().parents[1] / "data" / "kfct_clean.csv"
    if not data_path.exists():
        data_path = Path(__file__).resolve().parents[2] / "data" / "kfct_clean.csv"

    if not data_path.exists():
        print(f"Error: kfct_clean.csv not found at {data_path}")
        return

    print("Seeding foods from CSV (filtering junk rows, converting kJ→kcal)...")

    foods_to_insert = []
    seen_codes = set()

    with open(data_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_code = row.get('food_code', '').strip()

            # Only process rows with a proper 5-digit food code
            if not FOOD_CODE_PATTERN.match(raw_code):
                continue

            food_code = extract_food_code(raw_code)

            # Skip duplicates (some foods appear with and without "1.00")
            if food_code in seen_codes:
                continue
            seen_codes.add(food_code)

            display_name = clean_food_name(raw_code)
            if not display_name or display_name == food_code:
                continue

            # Convert energy from kJ to kcal
            energy_kj = safe_float(row.get('energy_kcal'))
            energy_kcal = round(energy_kj / KJ_TO_KCAL, 1)

            # Skip entries with 0 kcal (likely section headers disguised as foods)
            if energy_kcal < 1:
                continue

            protein_g = safe_float(row.get('protein_g'))
            fat_g = safe_float(row.get('fat_g'))
            carbs_g = safe_float(row.get('carbs_g'))

            # Sanity check: filter out entries with misaligned CSV columns
            # In reality, no food has > 100g of any single macro per 100g of food
            # and total macros (P+F+C) cannot exceed ~120g per 100g
            total_macros = protein_g + fat_g + carbs_g
            if protein_g > 100 or fat_g > 100 or carbs_g > 100 or total_macros > 120:
                continue

            # Filter suspiciously low-energy but high-macro foods (column misalignment)
            if energy_kcal < 15 and total_macros > 20:
                continue

            # Filter foods with all-zero macros (physically impossible to have calories with no macros)
            if protein_g == 0 and fat_g == 0 and carbs_g == 0:
                continue

            category = extract_category(food_code)

            food = SQLFood(
                food_code=food_code,
                food_name_english=display_name,
                food_name_swahili=None,
                category=category,
                display_name=display_name,
                energy_kcal=energy_kcal,
                protein_g=safe_float(row.get('protein_g')),
                fat_g=safe_float(row.get('fat_g')),
                carbs_g=safe_float(row.get('carbs_g')),
                fibre_g=safe_float(row.get('fibre_g')),
                calcium_mg=safe_float(row.get('calcium_mg')),
                iron_mg=safe_float(row.get('iron_mg')),
                zinc_mg=safe_float(row.get('zinc_mg'))
            )
            foods_to_insert.append(food)

    db.add_all(foods_to_insert)
    db.commit()
    print(f"Successfully seeded {len(foods_to_insert)} clean food items.")


def seed_clients(db: Session):
    if db.query(SQLClient).first():
        print("Database already seeded with clients. Skipping.")
        return

    print("Seeding sample clients...")
    clients = [
        SQLClient(
            name="Athi",
            age=25,
            weight_kg=70.5,
            health_goal="Muscle Gain",
            target_calories=2800,
            protein_grams=150,
            fat_grams=80,
            carb_grams=350,
            dietary_restrictions=""
        ),
        SQLClient(
            name="Wanjiku",
            age=32,
            weight_kg=65.0,
            health_goal="Weight Loss",
            target_calories=1800,
            protein_grams=120,
            fat_grams=60,
            carb_grams=180,
            dietary_restrictions="gluten-free"
        ),
        SQLClient(
            name="Ochieng",
            age=45,
            weight_kg=85.0,
            health_goal="Maintenance",
            target_calories=2400,
            protein_grams=140,
            fat_grams=70,
            carb_grams=280,
            dietary_restrictions="pescatarian"
        ),
        SQLClient(
            name="Neymar",
            age=28,
            weight_kg=60.0,
            health_goal="General Health",
            target_calories=2200,
            protein_grams=100,
            fat_grams=65,
            carb_grams=250,
            dietary_restrictions="vegetarian, gluten-free"
        )
    ]
    db.add_all(clients)
    db.commit()
    print(f"Successfully seeded {len(clients)} sample clients.")


def main():
    init_db()
    db = SessionLocal()
    try:
        seed_foods(db)
        seed_clients(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
