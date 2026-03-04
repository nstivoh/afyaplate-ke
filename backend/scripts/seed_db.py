import csv
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.sql_models import SQLFood, SQLClient

def safe_float(val: str, default: float = 0.0) -> float:
    try:
        return float(val) if val.strip() else default
    except (ValueError, TypeError):
        return default

def init_db():
    Base.metadata.create_all(bind=engine)

def seed_foods(db: Session):
    if db.query(SQLFood).first():
        print("Database already seeded with foods. Skipping.")
        return

    data_path = Path(__file__).resolve().parents[1] / "data" / "kfct_clean.csv"
    if not data_path.exists():
        data_path = Path(__file__).resolve().parents[2] / "data" / "kfct_clean.csv" # Fallback if executed differently
        
    if not data_path.exists():
        print(f"Error: kfct_clean.csv not found at {data_path}")
        return

    print("Seeding foods from CSV...")
    
    foods_to_insert = []
    with open(data_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            food_code = row.get('food_code', '').strip()
            if not food_code:
                continue

            food_name_en = row.get('food_name_english', '').strip()
            food_name_sw = row.get('food_name_swahili', '').strip()
            display_name = food_name_en or food_name_sw or food_code or "Unknown Food"
            
            food = SQLFood(
                food_code=food_code,
                food_name_english=row.get('food_name_english', '').strip(),
                food_name_swahili=row.get('food_name_swahili', '').strip(),
                category=row.get('category', '').strip(),
                display_name=display_name,
                energy_kcal=safe_float(row.get('energy_kcal')),
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
    print(f"Successfully seeded {len(foods_to_insert)} foods.")

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
