import os
import json
import anthropic
from app.models import FinancialProfileInput, CareerGoalInput, AIRecommendation

# Initialize the Client
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

class CareerAI:
    @staticmethod
    def analyze_path(profile: FinancialProfileInput, goal: CareerGoalInput) -> AIRecommendation:
        
        # 1. Construct the Context (The Prompt)
        system_prompt = (
            "You are CareerPivot-AI, a strategic career advisor. "
            "Your goal is to create a realistic transition plan based STRICTLY on the user's "
            "financial constraints. Do not recommend expensive bootcamps if they are broke."
        )

        user_message = f"""
        ANALYZE THIS USER:
        - Current Role: {goal.target_role} (Target)
        - Cash Savings: ${profile.cash_savings}
        - Monthly Burn: ${profile.fixed_expenses + profile.variable_expenses}
        - Transition Budget: ${goal.upskilling_cost}
        - Time Limit: {goal.estimated_months} months
        
        TASK:
        1. Determine if this transition is 'High Risk', 'Medium Risk', or 'Low Risk'.
        2. Suggest 3 concrete actions they must take in Month 1.
        3. Recommend 2 specific learning resources that fit their ${goal.upskilling_cost} budget.
        
        OUTPUT FORMAT:
        Return ONLY valid JSON matching this structure:
        {{
            "verdict": "Low Risk",
            "suggested_actions": ["Action 1", "Action 2", "Action 3"],
            "learning_resources": [
                {{"name": "Course Name", "cost": 0, "platform": "Provider"}}
            ]
        }}
        """

        # 2. Call Claude 3.5 Sonnet
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # 3. Parse the JSON Response
        # Claude sometimes adds text before/after JSON, so we extract the clean block
        raw_text = message.content[0].text
        try:
            # Simple cleanup to ensure we just get the JSON object
            json_str = raw_text.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            
            data = json.loads(json_str)
            
            return AIRecommendation(
                verdict=data["verdict"],
                suggested_actions=data["suggested_actions"],
                learning_resources=data["learning_resources"]
            )
        except Exception as e:
            # Fallback if AI hallucinates the format
            return AIRecommendation(
                verdict="Error parsing AI response",
                suggested_actions=["Manual review required"],
                learning_resources=[]
            )
