import os
import math
import anthropic
import json
from app.models import FinancialProfile, TransitionPlan, AIStrategy, LearningResource

# Initialize the Brain
# CRITICAL: Make sure you set your API Key in your terminal or .env file!
# export ANTHROPIC_API_KEY="sk-ant..."
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

class FinancialBridge:
    @staticmethod
    def calculate(profile: FinancialProfile) -> TransitionPlan:
        # --- 1. THE MATH (Deterministic) ---
        burn_rate = profile.monthly_expenses
        required_runway = burn_rate * profile.transition_months
        
        # Add safety buffer (Emergency Fund)
        emergency_buffer = burn_rate * profile.emergency_fund_months
        total_needed = required_runway + emergency_buffer
        
        gap = total_needed - profile.current_savings
        
        runway_months = 0
        if burn_rate > 0:
            runway_months = profile.current_savings / burn_rate

        is_ready = gap <= 0

        # --- 2. THE BRAIN (AI Strategy) ---
        
        # FIX 1: Hardcode the Key temporarily to rule out environment issues
        # (Delete this line later and go back to os.environ for security!)
        # Back to secure mode
        api_key = os.environ.get("ANTHROPIC_API_KEY") 
        
        # Re-initialize client with the direct key
        secure_client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""
        You are a career strategist. Analyze this user:
        - Savings: ${profile.current_savings}
        - Monthly Burn: ${burn_rate}
        - Runway: {runway_months:.1f} months
        - Goal: Transition in {profile.transition_months} months
        - Capital Gap: ${gap}
        
        Provide a JSON response with:
        1. 'verdict': (Low/Medium/High Risk)
        2. 'action_plan': 3 specific bullet points on how to bridge the gap or optimize study.
        3. 'resources': 2 specific, real learning resources (courses/books) that are low-cost.
        
        Return ONLY valid JSON matching this structure:
        {{
            "verdict": "string",
            "action_plan": ["string", "string"],
            "resources": [{{"name": "string", "cost": "string"}}]
        }}
        """

        try:
            message = secure_client.messages.create(
                # FIX: Switched to Claude 3 Haiku (Universally available)
                model="claude-3-haiku-20240307", 
                max_tokens=500,
                temperature=0,
                system="You are a helpful JSON-only financial assistant.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            
            # Parse AI Response
            ai_text = message.content[0].text
            # Clean up potential markdown code blocks
            if "```json" in ai_text:
                ai_text = ai_text.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_text:
                ai_text = ai_text.split("```")[1].split("```")[0].strip()
                
            ai_data = json.loads(ai_text)
            
            # Convert to Pydantic Models
            resources = [LearningResource(**r) for r in ai_data.get('resources', [])]
            strategy = AIStrategy(
                verdict=ai_data.get('verdict', "Unknown"),
                action_plan=ai_data.get('action_plan', ["Review finances"]),
                resources=resources
            )

        except Exception as e:
            print(f"AI Error: {e}")
            # Fallback if AI fails (so app doesn't crash)
            strategy = AIStrategy(
                verdict="AI Offline", 
                action_plan=["Check internet connection", "Verify API Key"], 
                resources=[]
            )

        # --- 3. MERGE AND RETURN ---
        return TransitionPlan(
            monthly_burn_rate=burn_rate,
            total_runway_months=runway_months,
            capital_gap=gap,
            is_financially_ready=is_ready,
            strategy=strategy
        )
