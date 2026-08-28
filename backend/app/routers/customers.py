from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.customer import CustomerResponse, CustomerTimelineResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/api/customers", tags=["Customers"])

@router.get("", response_model=List[CustomerResponse])
def get_customers(
    status: Optional[str] = None,
    high_risk_only: bool = False,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Exposes customer list with entry time, exit time, current status, and total stay duration."""
    return CustomerService.get_customers(db, status=status, high_risk_only=high_risk_only, limit=limit)

@router.get("/{id}", response_model=CustomerResponse)
def get_customer_by_id(id: int, db: Session = Depends(get_db)):
    """Returns details for a specific customer."""
    customer = CustomerService.get_customer_by_id(db, id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/{id}/timeline", response_model=CustomerTimelineResponse)
def get_customer_timeline(id: int, db: Session = Depends(get_db)):
    """Returns chronologically ordered timeline of events for a customer."""
    timeline = CustomerService.get_customer_timeline(db, id)
    if not timeline:
        raise HTTPException(status_code=404, detail="Customer timeline not found")
    return timeline
