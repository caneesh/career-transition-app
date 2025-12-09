from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import FinancialProfile, TransitionPlan
from app.logic import FinancialBridge

app = FastAPI(
    title="Career Transition Calculator API",
    description="Financial analysis API for career transitions",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Career Transition Calculator API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze financial profile for career transition",
            "/health": "GET - Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "career-transition-api"}


@app.post("/analyze", response_model=TransitionPlan)
async def analyze_transition(profile: FinancialProfile) -> TransitionPlan:
    """
    Analyze financial profile and generate transition plan.

    Args:
        profile: FinancialProfile containing user's financial information

    Returns:
        TransitionPlan with calculations and recommendations

    Raises:
        HTTPException: If validation or calculation fails
    """
    try:
        # Create financial bridge calculator
        bridge = FinancialBridge(profile)

        # Perform analysis
        plan = bridge.analyze()

        return plan

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
