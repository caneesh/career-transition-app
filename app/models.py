from pydantic import BaseModel, Field
from typing import Optional


class FinancialProfile(BaseModel):
    """Financial profile for career transition analysis"""
    current_salary: float = Field(..., description="Current annual salary", gt=0)
    monthly_expenses: float = Field(..., description="Monthly living expenses", gt=0)
    current_savings: float = Field(..., description="Current savings amount", ge=0)
    transition_months: int = Field(..., description="Expected months for transition", gt=0)
    new_salary: Optional[float] = Field(None, description="Expected new salary (if known)", gt=0)
    emergency_fund_months: int = Field(3, description="Desired months of emergency fund", gt=0)


class TransitionPlan(BaseModel):
    """Career transition financial plan results"""
    monthly_burn_rate: float = Field(..., description="Monthly spending rate during transition")
    total_runway_months: float = Field(..., description="Months of financial runway available")
    capital_gap: float = Field(..., description="Additional capital needed (negative if surplus)")
    emergency_fund_needed: float = Field(..., description="Emergency fund amount needed")
    total_capital_needed: float = Field(..., description="Total capital required for safe transition")
    is_financially_ready: bool = Field(..., description="Whether financially ready for transition")
    recommendations: list[str] = Field(..., description="Financial recommendations")
