import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dataclasses import dataclass
from typing import Dict

# --- 1. CORE LOGIC (Embedded for Portability) ---
@dataclass
class FinancialProfile:
    cash_savings: float
    brokerage_taxable: float
    spouse_net_income: float
    passive_income: float
    fixed_expenses: float
    variable_expenses: float
    discretionary_expenses: float
    risk_tolerance: str

@dataclass
class TransitionPlan:
    target_role: str
    upskilling_cost: float
    estimated_months: int
    health_insurance_gap: float

class CareerPivotCalculator:
    RISK_MULTIPLIERS = {'low': 1.5, 'medium': 1.25, 'high': 1.1}

    def __init__(self, profile: FinancialProfile, plan: TransitionPlan):
        self.profile = profile
        self.plan = plan

    def calculate_burn_rates(self) -> Dict[str, float]:
        monthly_income = self.profile.spouse_net_income + self.profile.passive_income
        total_outflow_comfort = (self.profile.fixed_expenses + 
                               self.profile.variable_expenses + 
                               self.profile.discretionary_expenses)
        burn_comfort = total_outflow_comfort - monthly_income
        
        total_outflow_lean = (self.profile.fixed_expenses + 
                            self.profile.variable_expenses)
        burn_lean = total_outflow_lean - monthly_income

        return {"comfort": max(0, burn_comfort), "lean": max(0, burn_lean)}

    def run_simulation(self) -> Dict:
        burn_rates = self.calculate_burn_rates()
        liquid_assets = self.profile.cash_savings + self.profile.brokerage_taxable
        
        # Base Transition Cost
        base_cost_lean = (
            (burn_rates['lean'] * self.plan.estimated_months) + 
            self.plan.upskilling_cost + 
            (self.plan.health_insurance_gap * self.plan.estimated_months)
        )

        multiplier = self.RISK_MULTIPLIERS.get(self.profile.risk_tolerance, 1.25)
        required_capital = base_cost_lean * multiplier
        gap = required_capital - liquid_assets
        
        # Runway Calculation
        runway_months = liquid_assets / burn_rates['lean'] if burn_rates['lean'] > 0 else 999

        return {
            "metrics": {
                "burn_lean": burn_rates['lean'],
                "required_capital": required_capital,
                "current_assets": liquid_assets,
                "gap": gap,
                "runway": runway_months
            },
            "burn_data": burn_rates # Passing this specifically for the chart
        }

# --- 2. THE STREAMLIT UI ---
st.set_page_config(page_title="CareerPivot Calculator", layout="wide")

st.title("🚀 CareerPivot: The 'Can I Quit?' Calculator")
st.markdown("### Calculate your financial runway before you hand in your resignation.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("1. Your Finances")
cash = st.sidebar.number_input("Cash Savings ($)", value=20000, step=1000)
brokerage = st.sidebar.number_input("Liquid Investments ($)", value=10000, step=1000)
spouse_income = st.sidebar.number_input("Spouse/Side Income (Monthly Net)", value=2000, step=100)

st.sidebar.header("2. Your Expenses (Monthly)")
fixed = st.sidebar.number_input("Fixed Bills (Rent, Debt, Ins.)", value=2500, step=100)
variable = st.sidebar.number_input("Essentials (Food, Transport)", value=600, step=100)
fun_money = st.sidebar.number_input("Discretionary (Fun, Dining)", value=500, step=100)

st.sidebar.header("3. The Transition Plan")
months = st.sidebar.slider("Estimated Job Hunt Duration (Months)", 3, 12, 6)
bootcamp_cost = st.sidebar.number_input("Education Cost (One-time)", value=5000, step=500)
risk = st.sidebar.selectbox("Risk Tolerance", ["low", "medium", "high"], index=1)

# --- RUN CALCULATION ---
profile = FinancialProfile(cash, brokerage, spouse_income, 0, fixed, variable, fun_money, risk)
plan = TransitionPlan("Target Role", bootcamp_cost, months, 400)
engine = CareerPivotCalculator(profile, plan)
results = engine.run_simulation()
metrics = results['metrics']

# --- MAIN DISPLAY ---
col1, col2, col3 = st.columns(3)
col1.metric("Lean Monthly Burn", f"${metrics['burn_lean']:,.0f}", 
            help="Expenses minus Spouse Income. This is what you lose every month.")
col2.metric("Runway (Survival Mode)", f"{metrics['runway']:.1f} Months", 
            delta_color="normal" if metrics['runway'] > months else "inverse")
col3.metric("Capital Gap", f"${metrics['gap']:,.0f}", 
            delta_color="inverse" if metrics['gap'] > 0 else "normal",
            help="Positive means you need MORE money. Negative means you are safe.")

st.divider()

# --- THE BURN DOWN CHART ---
st.subheader("📉 Your Financial Trajectory")

# Generate data points for the chart
months_range = list(range(0, 19)) # Show 18 months out
balance_history = []
current_balance = metrics['current_assets'] - bootcamp_cost # Pay tuition day 1

for m in months_range:
    if m == 0:
        balance_history.append(current_balance)
    else:
        # Subtract monthly burn
        current_balance -= metrics['burn_lean']
        balance_history.append(current_balance)

# Create Plotly Chart
fig = go.Figure()

# 1. The Money Line
fig.add_trace(go.Scatter(x=months_range, y=balance_history, mode='lines+markers', 
                         name='Bank Balance', line=dict(color='#00CC96', width=4)))

# 2. The Danger Zone (Zero Line)
fig.add_hline(y=0, line_dash="dot", line_color="red", annotation_text="Broke")

# 3. The "Got Hired" Milestone Vertical Line
fig.add_vline(x=months, line_dash="dash", line_color="white", annotation_text="Planned Hire Date")

# Layout
fig.update_layout(
    title="Projected Savings Balance (Lean Mode)",
    xaxis_title="Months from Quitting",
    yaxis_title="Liquid Assets ($)",
    template="plotly_dark",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# --- THE UPSELL (SMOKE TEST) ---
st.info(f"💡 Analysis: You are planning for a **{months}-month** transition. Your money runs out in **{metrics['runway']:.1f} months**.")
# Replace the old st.button logic with this:
st.markdown("### 🚀 Ready to escape?")
url = "https://forms.google.com/your-form-id-here" # Replace with your real Google Form link

if metrics['gap'] > 0:
    st.link_button("👉 Apply for a Custom Bridge Plan (Beta)", url)
else:
    st.link_button("👉 Get My Career Pivot Roadmap (Beta)", url)

# if metrics['gap'] > 0:
#     st.error(f"🚨 GAP DETECTED: You are short by ${metrics['gap']:,.0f}.")
#     st.markdown("""
#     ### Don't Panic. You just need a better plan.
#     We can build a custom roadmap to bridge this gap by:
#     1. Finding freelance work using your *current* skills.
#     2. Accelerating your learning path to {months - 2} months.
#     3. Negotiating a signing bonus.
#     """)
#     st.button("👉 Get My Personalized Escape Plan ($29)")
# else:
#     st.success("✅ YOU ARE SAFE: You have the capital to quit.")
#     st.markdown("Now the only risk is **wasting time** on the wrong skills.")
#     st.button("👉 Get My Optimized Curriculum ($29)")
