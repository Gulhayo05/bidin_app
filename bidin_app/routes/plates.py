from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from schemas import AutoPlateCreate, AutoPlateResponse, AutoPlateDetailResponse
from dependencies import get_db, get_current_user
from crud import create_plate, get_plate, update_plate, delete_plate, list_plates
from models import AutoPlate, Bid, User

router = APIRouter(prefix="/plates", tags=["plates"])

def get_highest_bid(db: Session, plate_id: int) -> Optional[float]:
    highest_bid = (
        db.query(Bid.amount)
        .filter(Bid.plate_id == plate_id)
        .order_by(Bid.amount.desc())
        .first()
    )
    return highest_bid[0] if highest_bid else None

@router.get("/", response_model=List[AutoPlateResponse])
def list_plates_endpoint(
    ordering: Optional[str] = Query(None, description="Sort by 'deadline' (asc/desc)"),
    plate_number__contains: Optional[str] = Query(None, description="Filter by plate number containing"),
    db: Session = Depends(get_db),
):
    query = db.query(AutoPlate).filter(AutoPlate.is_active == True)

    if plate_number__contains:
        query = query.filter(AutoPlate.plate_number.contains(plate_number__contains))

    if ordering == "deadline":
        query = query.order_by(AutoPlate.deadline.asc())
    elif ordering == "-deadline":
        query = query.order_by(AutoPlate.deadline.desc())

    plates = query.all()
    response = []
    for plate in plates:
        response.append({
            "id": plate.id,
            "plate_number": plate.plate_number,
            "description": plate.description,
            "deadline": plate.deadline,
            "is_active": plate.is_active,  
            "created_by_id": plate.created_by_id,  
        })
    return response


@router.post("/", response_model=AutoPlateResponse)
def create_plate_endpoint(
    plate: AutoPlateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Only admins can create plates")
    return create_plate(db, plate, current_user.id)

@router.get("/{plate_id}", response_model=AutoPlateDetailResponse)
def get_plate_details(plate_id: int, db: Session = Depends(get_db)):
    plate = get_plate(db, plate_id)
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")
    
    bids = (
        db.query(Bid)
        .filter(Bid.plate_id == plate_id)
        .order_by(Bid.created_at.asc())
        .all()
    )
    bid_details = [
        {"amount": bid.amount, "user": bid.user_id, "created_at": bid.created_at}
        for bid in bids
    ]
    return {
        "id": plate.id,
        "plate_number": plate.plate_number,
        "description": plate.description,
        "deadline": plate.deadline,
        "is_active": plate.is_active,
        "bids": bid_details,
    }

@router.put("/{plate_id}", response_model=AutoPlateResponse)
def update_plate_endpoint(
    plate_id: int,
    plate: AutoPlateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Only admins can update plates")
    return update_plate(db, plate_id, plate)

@router.delete("/{plate_id}")
def delete_plate_endpoint(
    plate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Only admins can delete plates")
    delete_plate(db, plate_id)
    return {"message": "Plate deleted successfully"}