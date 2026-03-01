from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.sql_models import SQLClient
from app.schemas.client import Client

router = APIRouter()

@router.get("/", response_model=List[Client])
def get_all_clients(db: Session = Depends(get_db)):
    """
    Retrieve all sample clients from the database.
    """
    clients = db.query(SQLClient).all()
    return clients
