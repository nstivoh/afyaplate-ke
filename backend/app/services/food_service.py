import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.food import Food
from app.db.database import SessionLocal
from app.models.sql_models import SQLFood

logger = logging.getLogger(__name__)

class FoodService:
    def __init__(self):
        pass

    def search(self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 20) -> List[Food]:
        """
        Searches and filters the food data using SQLite.
        """
        db: Session = SessionLocal()
        try:
            sql_query = db.query(SQLFood)

            if category:
                sql_query = sql_query.filter(SQLFood.category == category)

            if query:
                search_term = f"%{query}%"
                sql_query = sql_query.filter(
                    or_(
                        SQLFood.display_name.ilike(search_term),
                        SQLFood.food_name_english.ilike(search_term),
                        SQLFood.food_name_swahili.ilike(search_term),
                        SQLFood.category.ilike(search_term)
                    )
                )

            # Limit results
            results = sql_query.limit(limit).all()
            
            # Convert SQLAlchemy models to Pydantic models
            return [Food.model_validate(record) for record in results]
        
        except Exception as e:
            logger.error(f"Error querying foods: {e}")
            return []
        finally:
            db.close()

    def get_all_categories(self) -> List[str]:
        """
        Returns a distinct list of all categories in the database.
        """
        db: Session = SessionLocal()
        try:
            # Query distinct categories where category is not null
            categories = db.query(SQLFood.category).filter(SQLFood.category.isnot(None)).distinct().all()
            # Extract the string values from the keyed tuple returned by SQLAlchemy
            return sorted([cat[0] for cat in categories if cat[0]])
        except Exception as e:
            logger.error(f"Error querying categories: {e}")
            return []
        finally:
            db.close()
