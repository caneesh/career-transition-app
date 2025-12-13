import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF  # <--- NEW LIBRARY

# --- CONFIGURATION ---
# API_URL = "http://127.0.0.1:8000/analyze" 
API_URL = "https://career-pivot-api.onrender.com/analyze" # Production URL

st.set_page_config(page_title="CareerPivot AI", layout="wide")
st.title("🚀 CareerPivot: AI-Powered Escape Planner")

# --- PDF GENERATOR FUNCTION ---
def create_pdf(data):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'CareerPivot Escape Plan', 0, 1, 'C')
            self.ln(10)

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # 1. Financial Snapshot
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. The Financial Reality", 0, 1)
    pdf.set_font("Arial", size=12)
    
    pdf.cell(0, 10, f"Monthly Burn: ${data['monthly_burn_rate']:,.0f}", 0, 1)
    pdf.cell(0, 10, f"Runway: {data['total_runway_months']:.1f} Months", 0, 1)
    pdf.cell(0, 10, f"Capital Gap: ${data['capital_gap']:,.0f}", 0, 1)
    pdf.ln(5)

    # 2. AI Strategy
    if 'strategy' in data:
        strategy = data['strategy']
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"2. AI Verdict: {strategy['verdict']}", 0, 1)
        pdf.ln(5)

        # Actions
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Immediate Actions:", 0, 1)
        pdf.set_font("Arial", size=11)
        for action in strategy['action_plan']:
            # Clean text to avoid unicode errors in standard FPDF
            safe_text = action.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 8, f"- {safe_text}")
        pdf.ln(5)

        # Resources
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Recommended Resources:", 0, 1)
        pdf.set_font("Arial", size=11)
        for res in strategy['resources']:
            if isinstance(res, dict):
                name = res.get('name', '').encode('latin-1', 'replace').decode('latin-1')
                cost = res.get('cost', '').encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 8, f"- {name} ({cost})")
            else:
                safe_res = str(res).encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 8, f"- {safe_res}")

    return pdf.output(dest='S').encode('latin-1')

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
                
                # --- SECTION 3: DOWNLOAD PDF ---
                st.divider()
                pdf_bytes = create_pdf(data)
                st.download_button(
                    label="📄 Download My Escape Plan (PDF)",
                    data=pdf_bytes,
                    file_name="career_pivot_plan.pdf",
                    mime="application/pdf"
                )

                # --- SECTION 4: VISUALIZATION ---
                st.subheader("📉 Burn Down Chart")
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
