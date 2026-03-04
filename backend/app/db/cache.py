import redis.asyncio as redis
import csv
import re
import logging
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

KJ_TO_KCAL = 4.184
FOOD_CODE_PATTERN = re.compile(r'^(\d{5})\s+(.+)')
TRAILING_MULTIPLIER = re.compile(r'\s+1\.00$')


def clean_food_name(raw: str) -> str:
    match = FOOD_CODE_PATTERN.match(raw.strip())
    if not match:
        return raw.strip()
    name = match.group(2).strip()
    name = TRAILING_MULTIPLIER.sub('', name)
    name = name.rstrip(',').strip()
    if name:
        name = name[0].upper() + name[1:]
    return name


async def load_food_data_to_redis():
    """
    Parses the KFCT CSV data and loads clean food items into Redis as hashes.
    Filters out junk rows, strips food codes from names, converts kJ→kcal.
    """
    await redis_client.flushdb()
    logger.info("Flushed Redis DB. Starting to load food data...")

    from pathlib import Path
    DATA_DIR = Path(__file__).resolve().parents[2] / "data"
    csv_path = DATA_DIR / "kfct_clean.csv"

    try:
        with open(csv_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            pipeline = redis_client.pipeline()
            count = 0
            seen_codes = set()

            for row in reader:
                raw_code = row.get('food_code', '').strip()

                # Only process rows with a proper 5-digit food code
                if not FOOD_CODE_PATTERN.match(raw_code):
                    continue

                match = FOOD_CODE_PATTERN.match(raw_code)
                food_code = match.group(1)

                # Skip duplicates
                if food_code in seen_codes:
                    continue
                seen_codes.add(food_code)

                food_name = clean_food_name(raw_code)
                if not food_name or food_name == food_code:
                    continue

                # Convert kJ to kcal
                try:
                    energy_kj = float(row.get('energy_kcal', '0') or '0')
                except (ValueError, TypeError):
                    energy_kj = 0.0
                energy_kcal = round(energy_kj / KJ_TO_KCAL, 1)

                # Skip zero-energy items
                if energy_kcal < 1:
                    continue

                # Sanity check: filter out entries with misaligned CSV columns
                try:
                    protein_g = float(row.get('protein_g', '0') or '0')
                    fat_g = float(row.get('fat_g', '0') or '0')
                    carbs_g = float(row.get('carbs_g', '0') or '0')
                except (ValueError, TypeError):
                    protein_g = fat_g = carbs_g = 0.0

                total_macros = protein_g + fat_g + carbs_g
                if protein_g > 100 or fat_g > 100 or carbs_g > 100 or total_macros > 120:
                    continue
                if energy_kcal < 15 and total_macros > 20:
                    continue

                # Filter foods with all-zero macros
                if protein_g == 0 and fat_g == 0 and carbs_g == 0:
                    continue

                food_data = {
                    "name": food_name,
                    "category": row.get('category', 'Other'),
                    "energy_kcal": str(energy_kcal),
                    "protein_g": row.get('protein_g', '0'),
                    "fat_g": row.get('fat_g', '0'),
                    "carbs_g": row.get('carbs_g', '0'),
                    "fibre_g": row.get('fibre_g', '0'),
                    "calcium_mg": row.get('calcium_mg', '0')
                }

                pipeline.hset(f"food:{food_code}", mapping=food_data)
                count += 1

            await pipeline.execute()
            logger.info(f"Successfully loaded {count} clean food items into Redis.")

    except FileNotFoundError:
        logger.error(f"{csv_path} not found. Cannot load food data.")
    except Exception as e:
        logger.error(f"An error occurred while loading food data: {e}")

async def get_redis():
    """Dependency to get a Redis connection."""
    return redis_client

async def on_shutdown():
    """Closes the Redis connection pool."""
    await redis_client.close()
