"""
Credit System API Routes
========================
Endpoints for credit checking, balance, and package management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import User, CreditPackage
from ..schemas import (
    CreditCheckRequest,
    CreditCheckResponse,
    CreditBreakdownResponse,
    UserCreditsResponse,
    CreditPackageResponse,
    CreditPackagesListResponse,
)
from ..services.credit_system import (
    calculate_credits,
    get_generation_type_inference_type,
    get_credit_breakdown,
    InferenceType,
    CREDIT_PACKAGES,
)


router = APIRouter(prefix="/api/credits", tags=["credits"])


# Temporary mock user ID for development (will be replaced with auth)
TEMP_USER_ID = 1


def get_or_create_temp_user(db: Session) -> User:
    """Get or create a temporary user for development."""
    user = db.query(User).filter(User.id == TEMP_USER_ID).first()
    if not user:
        user = User(
            id=TEMP_USER_ID,
            email="demo@videlo.ai",
            credits_balance=100,  # Give demo user some credits
            total_credits_purchased=100,
            total_credits_used=0,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("/check", response_model=CreditCheckResponse)
async def check_credits(
    request: CreditCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check if user has enough credits for a generation.
    Returns credit requirement and user balance.
    """
    # Get user
    user = get_or_create_temp_user(db)
    
    # Calculate credits
    inference_type = get_generation_type_inference_type(request.generation_type)
    
    credits = calculate_credits(
        inference_type=inference_type,
        model=request.model,
        width=request.width,
        height=request.height,
        frames=request.frames,
        text_length=request.text_length,
        duration=request.duration,
    )
    
    # Get breakdown for display
    breakdown = get_credit_breakdown(
        inference_type=inference_type,
        model=request.model,
        width=request.width,
        height=request.height,
        frames=request.frames,
        text_length=request.text_length,
        duration=request.duration,
    )
    
    return CreditCheckResponse(
        credits_required=credits,
        user_balance=user.credits_balance,
        sufficient=user.credits_balance >= credits,
        breakdown=CreditBreakdownResponse(**breakdown)
    )


@router.get("/balance", response_model=UserCreditsResponse)
async def get_credits_balance(db: Session = Depends(get_db)):
    """
    Get current user's credit balance.
    """
    user = get_or_create_temp_user(db)
    
    return UserCreditsResponse(
        credits_balance=user.credits_balance,
        total_credits_purchased=user.total_credits_purchased,
        total_credits_used=user.total_credits_used,
    )


@router.get("/packages", response_model=CreditPackagesListResponse)
async def get_credit_packages(db: Session = Depends(get_db)):
    """
    Get available credit packages for purchase.
    """
    # Check if packages exist in DB, if not seed them
    db_packages = db.query(CreditPackage).filter(CreditPackage.is_active == True).all()
    
    if not db_packages:
        # Seed default packages
        for pkg in CREDIT_PACKAGES:
            db_pkg = CreditPackage(
                name=pkg["name"],
                credits=pkg["credits"],
                price_cents=pkg["price_cents"],
                bonus_percent=pkg["bonus_percent"],
                is_active=True,
            )
            db.add(db_pkg)
        db.commit()
        db_packages = db.query(CreditPackage).filter(CreditPackage.is_active == True).all()
    
    packages = []
    for pkg in db_packages:
        price_dollars = pkg.price_cents / 100
        packages.append(CreditPackageResponse(
            id=pkg.id,
            name=pkg.name,
            credits=pkg.credits,
            price_cents=pkg.price_cents,
            bonus_percent=pkg.bonus_percent,
            price_display=f"${price_dollars:.2f}",
        ))
    
    return CreditPackagesListResponse(packages=packages)


@router.post("/add-demo")
async def add_demo_credits(db: Session = Depends(get_db)):
    """
    Add demo credits for testing (development only).
    """
    user = get_or_create_temp_user(db)
    user.credits_balance += 100
    user.total_credits_purchased += 100
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "new_balance": user.credits_balance,
        "message": "Added 100 demo credits"
    }
