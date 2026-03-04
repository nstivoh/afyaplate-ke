from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base

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
# New Relational Structure for KFCT Data
# -------------------------------------------------------------
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class KFCTFood(Base):
    __tablename__ = "kfct_foods"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True)
    food_name = Column(String, index=True)
    category = Column(String, index=True)
    edible_conversion_factor = Column(Float, default=1.0)
    
    # Relationships to nutrient tables
    energy = relationship("KFCTEnergy", back_populates="food", uselist=False, cascade="all, delete-orphan")
    proximates = relationship("KFCTProximates", back_populates="food", uselist=False, cascade="all, delete-orphan")
    minerals = relationship("KFCTMinerals", back_populates="food", uselist=False, cascade="all, delete-orphan")
    vitamins = relationship("KFCTVitamins", back_populates="food", uselist=False, cascade="all, delete-orphan")

class KFCTEnergy(Base):
    __tablename__ = "kfct_energy"
    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("kfct_foods.id", ondelete="CASCADE"), unique=True)
    energy_kj = Column(Float, default=0.0)
    energy_kcal = Column(Float, default=0.0)
    
    food = relationship("KFCTFood", back_populates="energy")

class KFCTProximates(Base):
    __tablename__ = "kfct_proximates"
    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("kfct_foods.id", ondelete="CASCADE"), unique=True)
    water_g = Column(Float, default=0.0)
    protein_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    carbohydrate_available_g = Column(Float, default=0.0)
    fibre_g = Column(Float, default=0.0)
    ash_g = Column(Float, default=0.0)
    
    food = relationship("KFCTFood", back_populates="proximates")

class KFCTMinerals(Base):
    __tablename__ = "kfct_minerals"
    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("kfct_foods.id", ondelete="CASCADE"), unique=True)
    ca_mg = Column(Float, default=0.0)
    fe_mg = Column(Float, default=0.0)
    mg_mg = Column(Float, default=0.0)
    p_mg = Column(Float, default=0.0)
    k_mg = Column(Float, default=0.0)
    na_mg = Column(Float, default=0.0)
    zn_mg = Column(Float, default=0.0)
    se_mcg = Column(Float, default=0.0)
    
    food = relationship("KFCTFood", back_populates="minerals")

class KFCTVitamins(Base):
    __tablename__ = "kfct_vitamins"
    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("kfct_foods.id", ondelete="CASCADE"), unique=True)
    vit_a_rae_mcg = Column(Float, default=0.0)
    vit_a_re_mcg = Column(Float, default=0.0)
    retinol_mcg = Column(Float, default=0.0)
    b_carotene_equivalent_mcg = Column(Float, default=0.0)
    thiamin_mg = Column(Float, default=0.0)
    riboflavin_mg = Column(Float, default=0.0)
    niacin_mg = Column(Float, default=0.0)
    folate_eq_mcg = Column(Float, default=0.0)
    food_folate_mcg = Column(Float, default=0.0)
    vit_b12_mcg = Column(Float, default=0.0)
    vit_c_mg = Column(Float, default=0.0)
    
    food = relationship("KFCTFood", back_populates="vitamins")


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
