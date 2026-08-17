from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

from app.database.session import get_db
from app.services.auth_service import AuthService
from app.models.transaction import Transaction
from app.models.user import User
from app.config import settings
from app.routes.auth import oauth2_scheme

router = APIRouter(prefix="/transactions", tags=["transactions"])

class TransactionCreate(BaseModel):
    amount: float
    transaction_type: str  # deposit, withdrawal, transfer
    description: Optional[str] = None
    recipient_username: Optional[str] = None  # For transfers

class TransactionResponse(BaseModel):
    id: int
    amount: float
    transaction_type: str
    status: str
    description: Optional[str]
    reference: str
    created_at: datetime

@router.post("/create", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    # Get current user
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Validate transaction
    if transaction_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than zero"
        )
    
    # Process different transaction types
    if transaction_data.transaction_type == "deposit":
        # Simple deposit - update balance
        user.balance += transaction_data.amount
        
        transaction = Transaction(
            user_id=user.id,
            amount=transaction_data.amount,
            transaction_type="deposit",
            status="completed",
            description=transaction_data.description,
            reference=f"DEP-{uuid.uuid4().hex[:8].upper()}"
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    
    elif transaction_data.transaction_type == "withdrawal":
        # Check sufficient balance
        if user.balance < transaction_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        
        user.balance -= transaction_data.amount
        
        transaction = Transaction(
            user_id=user.id,
            amount=transaction_data.amount,
            transaction_type="withdrawal",
            status="completed",
            description=transaction_data.description,
            reference=f"WTH-{uuid.uuid4().hex[:8].upper()}"
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    
    elif transaction_data.transaction_type == "transfer":
        # Transfer to another user
        if not transaction_data.recipient_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recipient username required for transfers"
            )
        
        # Check sufficient balance
        if user.balance < transaction_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        
        # Find recipient
        recipient = db.query(User).filter(User.username == transaction_data.recipient_username).first()
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient not found"
            )
        
        # Process transfer (atomic operation)
        # In production, use database transactions for consistency
        user.balance -= transaction_data.amount
        recipient.balance += transaction_data.amount
        
        # Create sender transaction
        transaction = Transaction(
            user_id=user.id,
            amount=transaction_data.amount,
            transaction_type="transfer",
            status="completed",
            description=f"Transfer to {recipient.username}",
            reference=f"TRF-{uuid.uuid4().hex[:8].upper()}"
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction type"
        )

@router.get("/history")
async def get_transaction_history(
    limit: int = 10,
    offset: int = 0,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get user's transaction history"""
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user.id
    ).order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()
    
    return transactions