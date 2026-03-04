import os
import sys
from pathlib import Path

# Add project root to sys.path so we can import from app
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

import pandas as pd
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.sql_models import (
    KFCTFood, KFCTEnergy, KFCTProximates, 
    KFCTMinerals, KFCTVitamins
)

DATA_DIR = project_root / "data" / "kfct"

def get_category_from_code(code: str) -> str:
    """Infer category from the first two digits of the code."""
    categories = {
        "01": "Cereals and Cereal Products",
        "02": "Starchy Roots, Tubers and Plantains",
        "03": "Legumes and their Products",
        "04": "Vegetables and their Products",
        "05": "Fruits and their Products",
        "06": "Sugars and Syrups",
        "07": "Meat, Poultry and their Products",
        "08": "Eggs and their Products",
        "09": "Fish and their Products",
        "10": "Milk and their Products",
        "11": "Fats and Oils",
        "12": "Beverages",
        "13": "Miscellaneous",
    }
    prefix = str(code).zfill(5)[:2]
    return categories.get(prefix, "Unknown")

def clean_float(val):
    if pd.isna(val) or val == 'Tr' or val == 'N' or val == '-' or val == '' or val == '[]' or val == '(':
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def import_data():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Reading CSVs...")
        energy_df = pd.read_csv(DATA_DIR / "kfct complete data - Table 1 - Energy.csv")
        prox_df = pd.read_csv(DATA_DIR / "kfct complete data - Table 1 - Proximates.csv")
        min_df = pd.read_csv(DATA_DIR / "kfct complete data - Table 1 - Minerals.csv")
        vit_df = pd.read_csv(DATA_DIR / "kfct complete data - Table 1 - Vitamins.csv")
        
        # Merge all base tables on code
        print("Merging data...")
        df = energy_df.merge(prox_df, on="code", how="outer", suffixes=("", "_prox"))
        df = df.merge(min_df, on="code", how="outer", suffixes=("", "_min"))
        df = df.merge(vit_df, on="code", how="outer", suffixes=("", "_vit"))
        
        # We might have duplicate food_name columns, let's just use the first one
        food_name_col = "food_name" if "food_name" in df.columns else "food_name_x"
        if food_name_col not in df.columns:
             # Just find the first column that looks like food_name
             names = [c for c in df.columns if "food_name" in c]
             if names:
                 food_name_col = names[0]
        
        print(f"Total foods to import: {len(df)}")
        
        # Clear existing data
        print("Clearing existing KFCT data...")
        db.query(KFCTEnergy).delete()
        db.query(KFCTProximates).delete()
        db.query(KFCTMinerals).delete()
        db.query(KFCTVitamins).delete()
        db.query(KFCTFood).delete()
        db.commit()

        print("Importing foods...")
        count = 0
        for _, row in df.iterrows():
            code_str = str(row['code']).zfill(5)
            
            food = KFCTFood(
                code=code_str,
                food_name=row[food_name_col],
                category=get_category_from_code(code_str),
                edible_conversion_factor=clean_float(row.get('edible_conversion_factor', 1.0))
            )
            db.add(food)
            db.flush() # Get the auto-incremented ID
            
            energy = KFCTEnergy(
                food_id=food.id,
                energy_kj=clean_float(row.get('energy_kj', 0.0)),
                energy_kcal=clean_float(row.get('energy_kcal', 0.0))
            )
            db.add(energy)
            
            prox = KFCTProximates(
                food_id=food.id,
                water_g=clean_float(row.get('water_g', 0.0)),
                protein_g=clean_float(row.get('protein_g', 0.0)),
                fat_g=clean_float(row.get('fat_g', 0.0)),
                carbohydrate_available_g=clean_float(row.get('carbohydrate_available_g', 0.0)),
                fibre_g=clean_float(row.get('fibre_g', 0.0)),
                ash_g=clean_float(row.get('ash_g', 0.0))
            )
            db.add(prox)
            
            mins = KFCTMinerals(
                food_id=food.id,
                ca_mg=clean_float(row.get('ca_mg', 0.0)),
                fe_mg=clean_float(row.get('fe_mg', 0.0)),
                mg_mg=clean_float(row.get('mg_mg', 0.0)),
                p_mg=clean_float(row.get('p_mg', 0.0)),
                k_mg=clean_float(row.get('k_mg', 0.0)),
                na_mg=clean_float(row.get('na_mg', 0.0)),
                zn_mg=clean_float(row.get('zn_mg', 0.0)),
                se_mcg=clean_float(row.get('se_mcg', 0.0))
            )
            db.add(mins)
            
            vits = KFCTVitamins(
                food_id=food.id,
                vit_a_rae_mcg=clean_float(row.get('vit_a_rae_mcg', 0.0)),
                vit_a_re_mcg=clean_float(row.get('vit_a_re_mcg', 0.0)),
                retinol_mcg=clean_float(row.get('retinol_mcg', 0.0)),
                b_carotene_equivalent_mcg=clean_float(row.get('b_carotene_equivalent_mcg', 0.0)),
                thiamin_mg=clean_float(row.get('thiamin_mg', 0.0)),
                riboflavin_mg=clean_float(row.get('riboflavin_mg', 0.0)),
                niacin_mg=clean_float(row.get('niacin_mg', 0.0)),
                folate_eq_mcg=clean_float(row.get('folate_eq_mcg', 0.0)),
                food_folate_mcg=clean_float(row.get('food_folate_mcg', 0.0)),
                vit_b12_mcg=clean_float(row.get('vit_b12_mcg', 0.0)),
                vit_c_mg=clean_float(row.get('vit_c_mg', 0.0))
            )
            db.add(vits)
            
            count += 1
            if count % 100 == 0:
                db.commit()
                print(f"Imported {count} foods...")
                
        db.commit()
        print(f"Success! Imported {count} total foods.")
        
    except Exception as e:
        print(f"Error during import: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_data()
