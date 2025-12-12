import streamlit as st
import pandas as pd
import requests

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000/analyze" 

st.set_page_config(page_title="CareerPivot AI", layout="wide")
st.title("🚀 CareerPivot: AI-Powered Escape Planner")

# --- SIDEBAR INPUTS ---
st.sidebar.header("1. Your Finances")
cash = st.sidebar.number_input("Cash Savings ($)", value=20000)
brokerage = st.sidebar.number_input("Liquid Investments ($)", value=10000)
spouse_income = st.sidebar.number_input("Spouse/Side Income (Monthly Net)", value=2000)

st.sidebar.header("2. Your Expenses")
fixed = st.sidebar.number_input("Fixed Bills", value=2500)
variable = st.sidebar.number_input("Essentials", value=600)
fun_money = st.sidebar.number_input("Discretionary", value=500)

st.sidebar.header("3. The Transition")
target_role = st.sidebar.text_input("Target Role", value="Full Stack Developer")
months = st.sidebar.slider("Job Hunt Duration", 3, 12, 6)
bootcamp_cost = st.sidebar.number_input("Education Cost", value=5000)
risk = st.sidebar.selectbox("Risk Tolerance", ["low", "medium", "high"], index=1)

# --- THE "CALL API" BUTTON ---
if st.button("Generate My Escape Plan"):
    with st.spinner("Crunching numbers & consulting AI..."):
        
        # 1. PRE-CALCULATE DATA
        total_savings = float(cash) + float(brokerage)
        total_expenses = float(fixed) + float(variable) + float(fun_money)
        annual_spouse_income = float(spouse_income) * 12
        
        # 2. CONSTRUCT PAYLOAD
        payload = {
            "current_salary": annual_spouse_income,
            "monthly_expenses": total_expenses,
            "current_savings": total_savings,
            "transition_months": int(months),
            "emergency_fund_months": 3
        }

        # 3. CALL THE BACKEND
        try:
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # --- SECTION 1: THE FINANCIALS ---
                st.markdown("### 📊 The Financial Reality")
                col1, col2, col3 = st.columns(3)
                col1.metric("Monthly Burn Rate", f"${data['monthly_burn_rate']:,.0f}")
                col2.metric("Runway", f"{data['total_runway_months']:.1f} Months")
                col3.metric("Capital Gap", f"${data['capital_gap']:,.0f}", 
                            delta_color="inverse" if data['capital_gap'] > 0 else "normal")

                st.divider()

                # --- SECTION 2: THE AI STRATEGY ---
                if 'strategy' in data:
                    strategy = data['strategy']
                    
                    st.subheader(f"🤖 AI Verdict: {strategy['verdict']}")
                    
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.info("### 🛑 Immediate Action Plan")
                        for action in strategy['action_plan']:
                            st.write(f"• {action}")
                    
                    with c2:
                        st.success("### 📚 Recommended Resources")
                        for res in strategy['resources']:
                            if isinstance(res, dict):
                                st.write(f"**{res.get('name')}**")
                                st.caption(f"Cost: {res.get('cost')}")
                            else:
                                st.write(f"• {res}")
                
                # --- SECTION 3: VISUALIZATION ---
                st.divider()
                st.subheader("📉 Burn Down Chart")
                
                # Simple projection logic for the chart
                months_range = list(range(13))
                start_bal = total_savings - float(bootcamp_cost)
                burn = data['monthly_burn_rate']
                balances = [start_bal - (burn * m) for m in months_range]
                
                st.line_chart(pd.DataFrame(balances, columns=["Projected Savings"]))

            else:
                st.error(f"Backend Error ({response.status_code})")
                st.write(response.json())

        except requests.exceptions.ConnectionError:
            st.error("🚨 Backend is offline! Is uvicorn running?")
        except Exception as e:
            st.error(f"An error occurred: {e}")
