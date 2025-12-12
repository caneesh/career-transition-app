from pydantic import BaseModel, Field
from typing import Optional, List

# --- NEW: AI Advice Structure ---
class LearningResource(BaseModel):
    name: str
    cost: str
    url: Optional[str] = None

class AIStrategy(BaseModel):
    verdict: str = Field(..., description="Risk assessment: Low, Medium, High")
    action_plan: List[str] = Field(..., description="Immediate steps to take")
    resources: List[LearningResource] = Field(..., description="Recommended courses/books")

# --- EXISTING: Financial Models (Kept valid) ---
class FinancialProfile(BaseModel):
    current_salary: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., gt=0)
    current_savings: float = Field(..., ge=0)
    transition_months: int = Field(..., gt=0)
    new_salary: Optional[float] = Field(None)
    emergency_fund_months: int = Field(3)

class TransitionPlan(BaseModel):
    # Financials
    monthly_burn_rate: float
    total_runway_months: float
    capital_gap: float
    is_financially_ready: bool
    
    # The New "Brain" Section
    strategy: AIStrategy  # <--- This is the new part!
