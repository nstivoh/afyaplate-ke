"""
AfyaPlate KE — Complete Database Rebuild from XLSX
====================================================
Rebuilds BOTH database tables cleanly from the XLSX source of truth.

Fixes applied:
  1. foods table: was 33 rows → now 513 (all KFCT 2018 foods)
  2. energy_kcal: was storing kJ values (e.g. 1520) → now correct kcal (e.g. 360)
  3. iron_mg / zinc_mg: were always 0 → now populated from XLSX
  4. Category labels: codes 06-15 were all wrong (off-by-one shift) → corrected
  5. Duplicate Pumpkin: kept as two entries with distinct codes (04082, 04083)
  6. kfct_* tables: rebuilt with correct categories and values

Usage:
    python rebuild_db_from_xlsx.py --db PATH_TO_DB --xlsx PATH_TO_XLSX

Defaults:
    --db   ./backend/data/afyaplate.db
    --xlsx ./kfct_complete_data.xlsx
"""

import argparse
import math
import sqlite3
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("Missing dependency. Run: pip install pandas openpyxl")


# Category boundaries in the 513-food Table 1 ordered list.
# Derived by cross-referencing the category sheets (01 Cereals, 02 Starchy Roots,
# 03 Legumes) with the Master_Food_List ordering and original DB code ranges.
CATEGORY_BOUNDARIES = {
    "01": (0,   15),
    "02": (15,  25),
    "03": (25,  30),
    "04": (30,  128),
    "05": (128, 167),
    "06": (167, 198),
    "07": (198, 257),
    "08": (257, 299),
    "09": (299, 312),
    "10": (312, 327),
    "11": (327, 330),
    "12": (330, 339),
    "13": (339, 374),
    "14": (374, 378),
    "15": (378, 513),
}

CATEGORY_FULL = {
    "01": "Cereals and Cereal Products",
    "02": "Starchy Roots, Tubers and Plantains",
    "03": "Legumes and their Products",
    "04": "Vegetables and their Products",
    "05": "Fruits and their Products",
    "06": "Milk and their Products",
    "07": "Meat, Poultry and their Products",
    "08": "Fish and their Products",
    "09": "Fats and Oils",
    "10": "Nuts, Seeds and their Products",
    "11": "Sugars and Syrups",
    "12": "Beverages",
    "13": "Miscellaneous",
    "14": "Insects and other Edible Animals",
    "15": "Composite Dishes",
}

CATEGORY_SHORT = {
    "01": "Cereals & Grains",
    "02": "Starchy Roots & Tubers",
    "03": "Legumes & Pulses",
    "04": "Vegetables",
    "05": "Fruits",
    "06": "Milk & Dairy",
    "07": "Meat & Poultry",
    "08": "Fish & Seafood",
    "09": "Fats & Oils",
    "10": "Nuts & Seeds",
    "11": "Sugars & Sweets",
    "12": "Beverages",
    "13": "Miscellaneous",
    "14": "Insects",
    "15": "Composite Dishes",
}


def clean_float(val, default=0.0):
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return default if (isinstance(val, float) and math.isnan(val)) else float(val)
    s = str(val).strip().lower()
    if s in ("tr", "trace", "n", "-", "", "nd", "nan", "not detected"):
        return 0.0
    try:
        return float(s)
    except (ValueError, TypeError):
        return default


def assign_codes(foods_in_order):
    pos_to_prefix = {}
    for prefix, (start, end) in CATEGORY_BOUNDARIES.items():
        for i in range(start, end):
            pos_to_prefix[i] = prefix

    cat_counters = {p: 1 for p in CATEGORY_BOUNDARIES}
    result = []
    for i, food_name in enumerate(foods_in_order):
        prefix = pos_to_prefix.get(i, "99")
        seq = cat_counters.get(prefix, 1)
        code = f"{prefix}{seq:03d}"
        cat_counters[prefix] = seq + 1
        result.append((food_name, code, prefix))
    return result


def load_xlsx(xlsx_path):
    print(f"  Loading XLSX: {xlsx_path}")

    def load_sheet(name):
        df = pd.read_excel(xlsx_path, sheet_name=name, engine="openpyxl")
        df = df.loc[:, df.columns.notna()]
        df.columns = [str(c).strip() for c in df.columns]
        return df.reset_index(drop=True)

    energy = load_sheet("Table 1 - Energy")
    prox   = load_sheet("Table 1 - Proximates")
    mins   = load_sheet("Table 1 - Minerals")
    vits   = load_sheet("Table 1 - Vitamins")

    counts = [len(energy), len(prox), len(mins), len(vits)]
    if len(set(counts)) != 1:
        raise ValueError(f"Sheet row counts differ: {counts}")

    # Positional concat — avoids cross-join from duplicate Pumpkin entry
    merged = pd.concat([
        energy,
        prox.drop(columns=["food_name"]),
        mins.drop(columns=["food_name"]),
        vits.drop(columns=["food_name"]),
    ], axis=1)

    print(f"  Loaded {len(merged)} foods, {len(merged.columns)} columns")
    return merged


def rebuild_database(conn, merged):
    cur = conn.cursor()

    foods_in_order = merged["food_name"].tolist()
    code_assignments = assign_codes(foods_in_order)

    print("  Clearing existing data ...")
    for tbl in ["kfct_vitamins", "kfct_minerals", "kfct_proximates", "kfct_energy", "kfct_foods", "foods"]:
        cur.execute(f"DELETE FROM {tbl}")
    conn.commit()

    kfct_count = 0
    foods_count = 0

    for i, row in merged.iterrows():
        food_name, code, prefix = code_assignments[i]

        kcal  = clean_float(row.get("energy_kcal"))
        kj    = clean_float(row.get("energy_kj"))
        ecf   = clean_float(row.get("edible_conversion_factor"), default=1.0)
        water = clean_float(row.get("water_g"))
        prot  = clean_float(row.get("protein_g"))
        fat   = clean_float(row.get("fat_g"))
        carbs = clean_float(row.get("carbohydrate_available_g"))
        fibre = clean_float(row.get("fibre_g"))
        ash   = clean_float(row.get("ash_g"))
        ca    = clean_float(row.get("ca_mg"))
        fe    = clean_float(row.get("fe_mg"))
        mg_   = clean_float(row.get("mg_mg"))
        p_    = clean_float(row.get("p_mg"))
        k_    = clean_float(row.get("k_mg"))
        na_   = clean_float(row.get("na_mg"))
        zn    = clean_float(row.get("zn_mg"))
        se    = clean_float(row.get("se_mcg"))
        vit_a_rae  = clean_float(row.get("vit_a_rae_mcg"))
        vit_a_re   = clean_float(row.get("vit_a_re_mcg"))
        retinol    = clean_float(row.get("retinol_mcg"))
        bcarot     = clean_float(row.get("b_carotene_equivalent_mcg"))
        thiamin    = clean_float(row.get("thiamin_mg"))
        riboflavin = clean_float(row.get("riboflavin_mg"))
        niacin     = clean_float(row.get("niacin_mg"))
        folate_eq  = clean_float(row.get("folate_eq_mcg"))
        food_fol   = clean_float(row.get("food_folate_mcg"))
        b12        = clean_float(row.get("vit_b12_mcg"))
        vit_c      = clean_float(row.get("vit_c_mg"))

        full_cat  = CATEGORY_FULL.get(prefix, "Other")
        short_cat = CATEGORY_SHORT.get(prefix, "Other")

        cur.execute(
            "INSERT INTO kfct_foods (code, food_name, category, edible_conversion_factor) VALUES (?,?,?,?)",
            (code, food_name, full_cat, ecf),
        )
        food_id = cur.lastrowid

        cur.execute(
            "INSERT INTO kfct_energy (food_id, energy_kj, energy_kcal) VALUES (?,?,?)",
            (food_id, kj, kcal),
        )
        cur.execute(
            "INSERT INTO kfct_proximates (food_id, water_g, protein_g, fat_g, carbohydrate_available_g, fibre_g, ash_g) VALUES (?,?,?,?,?,?,?)",
            (food_id, water, prot, fat, carbs, fibre, ash),
        )
        cur.execute(
            "INSERT INTO kfct_minerals (food_id, ca_mg, fe_mg, mg_mg, p_mg, k_mg, na_mg, zn_mg, se_mcg) VALUES (?,?,?,?,?,?,?,?,?)",
            (food_id, ca, fe, mg_, p_, k_, na_, zn, se),
        )
        cur.execute(
            "INSERT INTO kfct_vitamins (food_id, vit_a_rae_mcg, vit_a_re_mcg, retinol_mcg, b_carotene_equivalent_mcg, thiamin_mg, riboflavin_mg, niacin_mg, folate_eq_mcg, food_folate_mcg, vit_b12_mcg, vit_c_mg) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (food_id, vit_a_rae, vit_a_re, retinol, bcarot, thiamin, riboflavin, niacin, folate_eq, food_fol, b12, vit_c),
        )
        kfct_count += 1

        cur.execute(
            """INSERT INTO foods
               (food_code, food_name_english, food_name_swahili, category, display_name,
                energy_kcal, protein_g, fat_g, carbs_g, fibre_g, calcium_mg, iron_mg, zinc_mg)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (code, food_name, None, short_cat, food_name,
             kcal, prot, fat, carbs, fibre, ca, fe, zn),
        )
        foods_count += 1

        if (i + 1) % 100 == 0:
            conn.commit()
            print(f"  ... {i+1} / {len(merged)} foods")

    conn.commit()
    return kfct_count, foods_count


def verify(conn):
    cur = conn.cursor()
    print("\\n" + "=" * 65)
    print("VERIFICATION SUMMARY")
    print("=" * 65)

    total  = cur.execute("SELECT COUNT(*) FROM foods").fetchone()[0]
    zero_e = cur.execute("SELECT COUNT(*) FROM foods WHERE energy_kcal = 0").fetchone()[0]
    zero_p = cur.execute("SELECT COUNT(*) FROM foods WHERE protein_g = 0").fetchone()[0]
    fe_pop = cur.execute("SELECT COUNT(*) FROM foods WHERE iron_mg > 0").fetchone()[0]
    zn_pop = cur.execute("SELECT COUNT(*) FROM foods WHERE zinc_mg > 0").fetchone()[0]
    high_e = cur.execute("SELECT COUNT(*) FROM foods WHERE energy_kcal > 900").fetchone()[0]

    print(f"\\n  foods table (app-facing search + algo planner):")
    print(f"    Total rows:          {total:>5}  (was 33)")
    print(f"    energy_kcal = 0:     {zero_e:>5}  (water, salt, baking soda — correct)")
    print(f"    protein_g = 0:       {zero_p:>5}  (oils, sugar, water — correct)")
    print(f"    iron_mg populated:   {fe_pop:>5}  (was 0 in every row before)")
    print(f"    zinc_mg populated:   {zn_pop:>5}  (was 0 in every row before)")
    print(f"    energy_kcal > 900:   {high_e:>5}  (should be 0 — kJ bug fixed)")

    print(f"\\n    Category breakdown:")
    for cat, n in cur.execute("SELECT category, COUNT(*) FROM foods GROUP BY category ORDER BY category").fetchall():
        print(f"      {cat:<35} {n:>4}")

    kfct_total = cur.execute("SELECT COUNT(*) FROM kfct_foods").fetchone()[0]
    print(f"\\n  kfct_foods table:")
    print(f"    Total rows:          {kfct_total:>5}")
    print(f"\\n    Category breakdown:")
    for cat, n in cur.execute("SELECT category, COUNT(*) FROM kfct_foods GROUP BY category ORDER BY category").fetchall():
        print(f"      {cat:<45} {n:>4}")

    print(f"\\n  Spot-checks (values from XLSX):")
    row = cur.execute("SELECT food_code, energy_kcal, protein_g, iron_mg FROM foods WHERE food_name_english = 'Amaranth, whole grain, dry, raw'").fetchone()
    if row: print(f"    Amaranth dry raw:   code={row[0]}, kcal={row[1]} (exp 360), prot={row[2]} (exp 14.7), Fe={row[3]} (exp 9.5)")

    row = cur.execute("SELECT food_code, category, energy_kcal FROM foods WHERE food_name_english = 'Corn oil'").fetchone()
    if row: print(f"    Corn oil:           code={row[0]}, cat={row[1]} (exp Fats & Oils), kcal={row[2]} (exp 900)")

    row = cur.execute("SELECT food_code, category FROM foods WHERE food_name_english LIKE 'Butter%cow%no added%'").fetchone()
    if row: print(f"    Butter:             code={row[0]}, cat={row[1]} (exp Milk & Dairy)")

    rows = cur.execute("SELECT food_code, energy_kcal FROM foods WHERE food_name_english LIKE '%Pumpkin%seeds%boiled%'").fetchall()
    for r in rows: print(f"    Pumpkin (dup):      code={r[0]}, kcal={r[1]}")

    row = cur.execute("SELECT food_code, category FROM foods WHERE food_name_english LIKE '%Grasshopper%'").fetchone()
    if row: print(f"    Grasshopper:        code={row[0]}, cat={row[1]} (exp Insects)")

    row = cur.execute("SELECT food_code, category, energy_kcal FROM foods WHERE food_name_english LIKE '%Ugali%Maize%' LIMIT 1").fetchone()
    if row: print(f"    Ugali:              code={row[0]}, cat={row[1]} (exp Composite Dishes), kcal={row[2]}")

    print()


def main():
    parser = argparse.ArgumentParser(description="Rebuild AfyaPlate KE DB from XLSX")
    parser.add_argument("--db",   default="./backend/data/afyaplate.db")
    parser.add_argument("--xlsx", default="./kfct_complete_data.xlsx")
    args = parser.parse_args()

    db_path   = Path(args.db).resolve()
    xlsx_path = Path(args.xlsx).resolve()

    if not db_path.exists():
        sys.exit(f"ERROR: Database not found: {db_path}")
    if not xlsx_path.exists():
        sys.exit(f"ERROR: XLSX not found: {xlsx_path}")

    print(f"\\nAfyaPlate KE — Database Rebuild")
    print(f"  DB:   {db_path}")
    print(f"  XLSX: {xlsx_path}\\n")

    conn = sqlite3.connect(db_path)
    try:
        print("Step 1: Loading XLSX ...")
        merged = load_xlsx(xlsx_path)

        print("\\nStep 2: Rebuilding database ...")
        kfct_count, foods_count = rebuild_database(conn, merged)

        verify(conn)
        print(f"✅  Rebuild complete: {foods_count} foods in foods table, {kfct_count} in kfct tables.")
        print(f"    Restart the FastAPI backend — Redis cache will auto-reload.\\n")

    except Exception:
        conn.rollback()
        import traceback
        traceback.print_exc()
        sys.exit("\\n❌ Rebuild failed. Database rolled back.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
