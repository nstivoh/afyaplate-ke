from pydantic import BaseModel
from typing import Optional

class ClientBase(BaseModel):
    name: str
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    health_goal: Optional[str] = None
    target_calories: Optional[int] = None
    protein_grams: Optional[int] = None
    fat_grams: Optional[int] = None
    carb_grams: Optional[int] = None
    dietary_restrictions: Optional[str] = None # Comma separated string for simplicity

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int

    class Config:
        from_attributes = True
