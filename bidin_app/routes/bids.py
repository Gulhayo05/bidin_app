from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from schemas import BidCreate, BidResponse
from dependencies import get_db, get_current_user
from crud import create_bid, get_bid, update_bid, delete_bid, list_user_bids
from models import Bid, AutoPlate, User

router = APIRouter(prefix="/bids", tags=["bids"])

@router.get("/", response_model=List[BidResponse])
def list_user_bids_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bids = list_user_bids(db, current_user.id)
    return bids

@router.post("/", response_model=BidResponse)
def place_bid(
    bid: BidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if the plate exists and is active
    plate = db.query(AutoPlate).filter(AutoPlate.id == bid.plate_id).first()
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")
    if not plate.is_active or plate.deadline <= datetime.now():
        raise HTTPException(status_code=400, detail="Bidding is closed for this plate")

    highest_bid = (
        db.query(Bid.amount)
        .filter(Bid.plate_id == bid.plate_id)
        .order_by(Bid.amount.desc())
        .first()
    )
    if highest_bid and bid.amount <= highest_bid[0]:
        raise HTTPException(status_code=400, detail="Bid amount must exceed current highest bid")

    return create_bid(db, bid, current_user.id)

@router.get("/{bid_id}", response_model=BidResponse)
def get_bid_details(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = get_bid(db, bid_id)
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    if bid.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to view this bid")
    return bid

@router.put("/{bid_id}", response_model=BidResponse)
def update_bid_details(
    bid_id: int,
    bid: BidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_bid = get_bid(db, bid_id)
    if not db_bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    if db_bid.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this bid")

    plate = db.query(AutoPlate).filter(AutoPlate.id == db_bid.plate_id).first()
    if not plate.is_active or plate.deadline <= datetime.now():
        raise HTTPException(status_code=400, detail="Bidding is closed for this plate")

    highest_bid = (
        db.query(Bid.amount)
        .filter(Bid.plate_id == db_bid.plate_id)
        .order_by(Bid.amount.desc())
        .first()
    )
    if highest_bid and bid.amount <= highest_bid[0]:
        raise HTTPException(status_code=400, detail="Bid amount must exceed current highest bid")

    return update_bid(db, bid_id, bid)

@router.delete("/{bid_id}")
def delete_bid_details(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_bid = get_bid(db, bid_id)
    if not db_bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    if db_bid.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this bid")

    plate = db.query(AutoPlate).filter(AutoPlate.id == db_bid.plate_id).first()
    if not plate.is_active or plate.deadline <= datetime.now():
        raise HTTPException(status_code=400, detail="Bidding is closed for this plate")

    delete_bid(db, bid_id)
    return {"message": "Bid deleted successfully"}