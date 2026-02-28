# backend/app/services/food_service.py
import pandas as pd
from rapidfuzz import process, fuzz
from pathlib import Path
from typing import List, Optional

from app.models.food import Food

class FoodService:
    _instance = None
    _food_df = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FoodService, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        """Loads and prepares the food data from the CSV."""
        if self._food_df is None:
            data_path = Path(__file__).resolve().parents[3] / "data" / "kfct_clean.csv"
            try:
                df = pd.read_csv(data_path)
                # Prepare a display name
                df['display_name'] = df['food_name_english'].fillna('') + " (" + df['food_name_swahili'].fillna('') + ")"
                self._food_df = df
            except FileNotFoundError:
                # In a real app, you'd have more robust error handling or logging
                print(f"Error: Food data file not found at {data_path}")
                self._food_df = pd.DataFrame()

    def search(self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 20) -> List[Food]:
        """
        Searches and filters the food data.
        """
        if self._food_df.empty:
            return []

        df = self._food_df.copy()

        if category:
            df = df[df['category'].str.lower() == category.lower()]

        if query:
            searchable_series = df['display_name'].fillna('')
            extracted_matches = process.extract(query, searchable_series, scorer=fuzz.WRatio, limit=limit*2)
            
            matched_indices = [index for _, _, index in extracted_matches if _ > 70]
            df = df.loc[matched_indices]

        # Limit results and convert to Pydantic models
        results = df.head(limit).to_dict(orient='records')
        return [Food(**record) for record in results]

    def get_all_categories(self) -> List[str]:
        if self._food_df.empty:
            return []
        return sorted(self._food_df['category'].unique().tolist())
