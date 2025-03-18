from sqlalchemy.orm import Session
from models import User, AutoPlate, Bid
from schemas import UserCreate, AutoPlateCreate, BidCreate
from dependencies import get_password_hash

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_staff=user.is_staff,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_plate(db: Session, plate: AutoPlateCreate, user_id: int):
    db_plate = AutoPlate(**plate.dict(), created_by_id=user_id)
    db.add(db_plate)
    db.commit()
    db.refresh(db_plate)
    return db_plate

def get_plate(db: Session, plate_id: int):
    return db.query(AutoPlate).filter(AutoPlate.id == plate_id).first()

def update_plate(db: Session, plate_id: int, plate: AutoPlateCreate):
    db_plate = db.query(AutoPlate).filter(AutoPlate.id == plate_id).first()
    if not db_plate:
        return None
    for key, value in plate.dict().items():
        setattr(db_plate, key, value)
    db.commit()
    db.refresh(db_plate)
    return db_plate

def delete_plate(db: Session, plate_id: int):
    db_plate = db.query(AutoPlate).filter(AutoPlate.id == plate_id).first()
    if not db_plate:
        return None
    db.delete(db_plate)
    db.commit()
    return db_plate

def list_plates(db: Session):
    return db.query(AutoPlate).all()

def create_bid(db: Session, bid: BidCreate, user_id: int):
    db_bid = Bid(**bid.dict(), user_id=user_id)
    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)
    return db_bid

def get_bid(db: Session, bid_id: int):
    return db.query(Bid).filter(Bid.id == bid_id).first()

def update_bid(db: Session, bid_id: int, bid: BidCreate):
    db_bid = db.query(Bid).filter(Bid.id == bid_id).first()
    if not db_bid:
        return None
    for key, value in bid.dict().items():
        setattr(db_bid, key, value)
    db.commit()
    db.refresh(db_bid)
    return db_bid

def delete_bid(db: Session, bid_id: int):
    db_bid = db.query(Bid).filter(Bid.id == bid_id).first()
    if not db_bid:
        return None
    db.delete(db_bid)
    db.commit()
    return db_bid

def list_user_bids(db: Session, user_id: int):
    return db.query(Bid).filter(Bid.user_id == user_id).all()