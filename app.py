import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF

# --- CONFIGURATION ---
API_URL = "https://career-pivot-api.onrender.com/analyze" # Your Production Backend

st.set_page_config(page_title="Vantage Digital | CareerPivot", layout="wide")

# --- ADVANCED PDF GENERATOR ---
def create_pro_pdf(data, profile_inputs):
    class PDF(FPDF):
        def header(self):
            # 1. Dark Blue Brand Banner
            self.set_fill_color(26, 35, 126) # Deep Navy Blue
            self.rect(0, 0, 210, 40, 'F')
            
            # 2. Title Text (White)
            self.set_y(10)
            self.set_font('Arial', 'B', 24)
            self.set_text_color(255, 255, 255)
            self.cell(0, 10, 'VANTAGE DIGITAL', 0, 1, 'C')
            
            # 3. Subtitle
            self.set_font('Arial', 'I', 12)
            self.cell(0, 10, 'Career Transition Strategic Report', 0, 1, 'C')
            self.ln(20)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Vantage Digital Strategy • Page {self.page_no()}', 0, 0, 'C')

        def section_title(self, label):
            self.set_font('Arial', 'B', 14)
            self.set_fill_color(240, 240, 240) # Light Grey
            self.set_text_color(0, 0, 0)
            self.cell(0, 10, f"  {label}", 0, 1, 'L', fill=True)
            self.ln(4)

        def financial_row(self, label, value):
            self.set_font('Arial', '', 11)
            self.cell(100, 8, label, 1) # Border=1 for grid look
            self.set_font('Arial', 'B', 11)
            self.cell(0, 8, value, 1, 1) # '1' at end means new line

    pdf = PDF()
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)

    # --- SECTION 1: EXECUTIVE SUMMARY ---
    pdf.section_title("1. Executive Summary")
    pdf.set_font('Arial', '', 11)
    
    # Target Role Context
    pdf.multi_cell(0, 6, f"Strategic analysis for the transition to: {profile_inputs['role']}.\n"
                         f"Timeline: {profile_inputs['timeline']} months | Risk Profile: {profile_inputs['risk']}")
    pdf.ln(5)

    # --- SECTION 2: FINANCIAL HEALTH ---
    pdf.section_title("2. Financial Reality")
    
    # Creating a Grid Table
    pdf.financial_row("Monthly Burn Rate (Lean)", f"${data['monthly_burn_rate']:,.0f}")
    pdf.financial_row("Current Runway", f"{data['total_runway_months']:.1f} Months")
    pdf.financial_row("Capital Gap (Deficit)", f"${data['capital_gap']:,.0f}")
    
    if data['capital_gap'] > 0:
        pdf.set_text_color(192, 57, 43) # Red for warning
        pdf.cell(0, 10, "  (!) WARNING: Capital deficit detected. Upskilling requires funding.", 0, 1)
        pdf.set_text_color(0, 0, 0) # Reset
    else:
        pdf.set_text_color(39, 174, 96) # Green for good
        pdf.cell(0, 10, "  (OK) You are fully funded for this transition.", 0, 1)
        pdf.set_text_color(0, 0, 0)

    pdf.ln(5)

    # --- SECTION 3: AI STRATEGY ---
    if 'strategy' in data:
        strategy = data['strategy']
        pdf.section_title(f"3. AI Strategy Verdict: {strategy['verdict']}")
        
        # Action Plan Box
        pdf.set_fill_color(255, 252, 230) # Light Yellow Background for tips
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, "Immediate Action Plan:", 0, 1, fill=True)
        pdf.set_font('Arial', '', 10)
        
        for action in strategy['action_plan']:
            safe_text = action.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 6, f"- {safe_text}", fill=True)
        
        pdf.ln(5)

        # Resources Box
        pdf.set_fill_color(232, 248, 245) # Light Green/Teal Background
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, "Recommended Resources:", 0, 1, fill=True)
        pdf.set_font('Arial', '', 10)
        
        for res in strategy['resources']:
            if isinstance(res, dict):
                name = res.get('name', '').encode('latin-1', 'replace').decode('latin-1')
                cost = res.get('cost', '').encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 6, f"- {name} ({cost})", fill=True)
            else:
                safe_res = str(res).encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 6, f"- {safe_res}", fill=True)

    return pdf.output(dest='S').encode('latin-1')

# --- MAIN UI ---
st.title("🚀 CareerPivot")
st.caption("Powered by Vantage Digital")

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
    with st.spinner("Analyzing strategy..."):
        
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
                
                # --- DISPLAY FINANCIALS ---
                st.markdown("### 📊 Financial Snapshot")
                col1, col2, col3 = st.columns(3)
                col1.metric("Monthly Burn", f"${data['monthly_burn_rate']:,.0f}")
                col2.metric("Runway", f"{data['total_runway_months']:.1f} Months")
                col3.metric("Gap", f"${data['capital_gap']:,.0f}", 
                            delta_color="inverse" if data['capital_gap'] > 0 else "normal")
                st.divider()

                # --- DISPLAY AI STRATEGY ---
                if 'strategy' in data:
                    strategy = data['strategy']
                    st.subheader(f"🤖 Verdict: {strategy['verdict']}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.info("### 🛑 Action Plan")
                        for action in strategy['action_plan']:
                            st.write(f"• {action}")
                    
                    with c2:
                        st.success("### 📚 Resources")
                        for res in strategy['resources']:
                            if isinstance(res, dict):
                                st.write(f"**{res.get('name')}**")
                                st.caption(f"Cost: {res.get('cost')}")
                            else:
                                st.write(f"• {res}")

                # --- GENERATE PRO PDF ---
                st.divider()
                
                # Package inputs for the PDF header context
                user_context = {
                    "role": target_role,
                    "timeline": months,
                    "risk": risk
                }
                
                pdf_bytes = create_pro_pdf(data, user_context)
                
                st.download_button(
                    label="📄 Download Official Strategy Report (PDF)",
                    data=pdf_bytes,
                    file_name="Vantage_Digital_Report.pdf",
                    mime="application/pdf"
                )

                # --- CHART ---
                st.subheader("📉 Burn Down Chart")
                months_range = list(range(13))
                start_bal = total_savings - float(bootcamp_cost)
                burn = data['monthly_burn_rate']
                balances = [start_bal - (burn * m) for m in months_range]
                st.line_chart(pd.DataFrame(balances, columns=["Projected Savings"]))

            else:
                st.error(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"Connection Error: {e}")
