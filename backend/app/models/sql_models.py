from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base
# Import subscription model so it is registered with Base.metadata
from app.models.subscription import SQLSubscription  # noqa: F401


class SQLFood(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    food_code = Column(String, index=True)
    food_name_english = Column(String, nullable=True)
    food_name_swahili = Column(String, nullable=True)
    category = Column(String, index=True, nullable=True)
    display_name = Column(String, index=True)
    energy_kcal = Column(Float, default=0.0)
    protein_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fibre_g = Column(Float, default=0.0)
    calcium_mg = Column(Float, default=0.0)
    iron_mg = Column(Float, default=0.0)
    zinc_mg = Column(Float, default=0.0)

# -------------------------------------------------------------
# Unused Relational Structure (KFCTFood) removed to unify schemas.
# -------------------------------------------------------------


class SQLClient(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    health_goal = Column(String, nullable=True)
    target_calories = Column(Integer, nullable=True)
    protein_grams = Column(Integer, nullable=True)
    fat_grams = Column(Integer, nullable=True)
    carb_grams = Column(Integer, nullable=True)
    dietary_restrictions = Column(String, nullable=True) # Stored as comma separated string
