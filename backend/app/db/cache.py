import redis.asyncio as redis
import csv
import asyncio
import os
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

async def load_food_data_to_redis():
    """
    Parses the KFCT CSV data and loads it into Redis as hashes.
    Each food item is stored with a key like "food:01001" and contains
    the food name and all its nutritional values.
    """
    await redis_client.flushdb()
    logger.info("Flushed Redis DB. Starting to load food data...")

    # Construct absolute path to the CSV file
    from pathlib import Path
    DATA_DIR = Path(__file__).resolve().parents[2] / "data"
    csv_path = DATA_DIR / "kfct_clean.csv"

    try:
        with open(csv_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row

            pipeline = redis_client.pipeline()
            count = 0
            for row in reader:
                # Basic data validation
                if len(row) < 8 or not row[0] or not row[2].replace('.', '', 1).isdigit():
                    continue

                food_code_raw = row[0]
                food_code_parts = food_code_raw.split(" ")
                food_code = food_code_parts[0]
                food_name = " ".join(food_code_parts[1:]).split(",")[0].strip()

                if not food_name:
                    continue

                food_data = {
                    "name": food_name,
                    "category": row[1],
                    "energy_kcal": row[2],
                    "protein_g": row[3],
                    "fat_g": row[4],
                    "carbs_g": row[5],
                    "fibre_g": row[6],
                    "calcium_mg": row[7]
                }

                # Add to pipeline to execute in a batch
                pipeline.hset(f"food:{food_code}", mapping=food_data)
                count += 1

            await pipeline.execute()
            logger.info(f"Successfully loaded {count} food items into Redis.")

    except FileNotFoundError:
        logger.error(f"{csv_path} not found. Cannot load food data.")
    except Exception as e:
        logger.error(f"An error occurred while loading food data: {e}")

async def get_redis():
    """
    Dependency to get a Redis connection.
    """
    return redis_client

async def on_shutdown():
    """
    Closes the Redis connection pool.
    """
    await redis_client.close()
