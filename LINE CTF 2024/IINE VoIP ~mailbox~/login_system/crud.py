import os

from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, name: str):
    return db.query(models.Users).filter(models.Users.name == name).first()

def get_all_user(db: Session):
    return db.query(models.Users).all()

def create_user(db: Session, user: schemas.UserCreate):
    # Create secure password
    password = os.urandom(16).hex()
    db_user = models.Users(name=user.name, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user