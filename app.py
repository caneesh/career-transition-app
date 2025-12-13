import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# --- CONFIGURATION ---
API_URL = "https://career-pivot-api.onrender.com/analyze"

st.set_page_config(
    page_title="CareerPivot AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Main title styling */
    h1 {
        background: linear-gradient(120deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        padding: 1rem 0;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }

    /* Info boxes */
    div[data-baseweb="notification"] {
        border-radius: 0.75rem;
        border-left: 4px solid #6366f1;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(120deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4);
    }

    /* Dividers */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #6366f1, transparent);
    }

    /* Cards */
    div.element-container {
        transition: transform 0.2s ease;
    }

    /* Input fields */
    input {
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 CareerPivot: AI-Powered Escape Planner")
st.markdown("### Plan your career transition with confidence and clarity")
st.markdown("---")

# --- SIDEBAR INPUTS ---
st.sidebar.markdown("## 💰 Your Finances")
st.sidebar.markdown("---")
cash = st.sidebar.number_input("💵 Cash Savings ($)", value=20000, help="Your liquid cash available")
brokerage = st.sidebar.number_input("📈 Liquid Investments ($)", value=10000, help="Easily accessible investments")
spouse_income = st.sidebar.number_input("💼 Spouse/Side Income (Monthly Net)", value=2000, help="Regular income during transition")

st.sidebar.markdown("## 💳 Your Expenses")
st.sidebar.markdown("---")
fixed = st.sidebar.number_input("🏠 Fixed Bills ($)", value=2500, help="Rent, utilities, insurance, etc.")
variable = st.sidebar.number_input("🛒 Essentials ($)", value=600, help="Food, gas, necessities")
fun_money = st.sidebar.number_input("🎯 Discretionary ($)", value=500, help="Entertainment, dining out, etc.")

st.sidebar.markdown("## 🎯 The Transition")
st.sidebar.markdown("---")
target_role = st.sidebar.text_input("🚀 Target Role", value="Full Stack Developer", help="Your dream job title")
months = st.sidebar.slider("⏱️ Job Hunt Duration (months)", 3, 12, 6, help="Expected time to land the role")
bootcamp_cost = st.sidebar.number_input("📚 Education Cost ($)", value=5000, help="Bootcamp, courses, certifications")
risk = st.sidebar.selectbox("⚡ Risk Tolerance", ["low", "medium", "high"], index=1, help="How aggressive can you be?")

# --- THE "CALL API" BUTTON ---
st.markdown("")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Generate My Escape Plan", use_container_width=True):
        with st.spinner("✨ Crunching numbers & consulting AI..."):

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
                    st.markdown("## 📊 The Financial Reality")
                    st.markdown("")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown('<div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 1.5rem; border-radius: 1rem; border: 1px solid #475569;">', unsafe_allow_html=True)
                        st.metric("💸 Monthly Burn Rate", f"${data['monthly_burn_rate']:,.0f}")
                        st.markdown('</div>', unsafe_allow_html=True)

                    with col2:
                        st.markdown('<div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 1.5rem; border-radius: 1rem; border: 1px solid #475569;">', unsafe_allow_html=True)
                        st.metric("⏳ Runway", f"{data['total_runway_months']:.1f} Months")
                        st.markdown('</div>', unsafe_allow_html=True)

                    with col3:
                        st.markdown('<div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 1.5rem; border-radius: 1rem; border: 1px solid #475569;">', unsafe_allow_html=True)
                        st.metric("💰 Capital Gap", f"${data['capital_gap']:,.0f}",
                                delta_color="inverse" if data['capital_gap'] > 0 else "normal")
                        st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown("")
                    st.divider()

                    # --- SECTION 2: THE AI STRATEGY ---
                    if 'strategy' in data:
                        strategy = data['strategy']

                        st.markdown(f"## 🤖 AI Verdict: {strategy['verdict']}")
                        st.markdown("")

                        c1, c2 = st.columns(2)

                        with c1:
                            st.markdown('<div style="background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); padding: 1.5rem; border-radius: 1rem; border: 1px solid #3b82f6;">', unsafe_allow_html=True)
                            st.markdown("### 🎯 Immediate Action Plan")
                            for action in strategy['action_plan']:
                                st.markdown(f"✓ {action}")
                            st.markdown('</div>', unsafe_allow_html=True)

                        with c2:
                            st.markdown('<div style="background: linear-gradient(135deg, #064e3b 0%, #059669 100%); padding: 1.5rem; border-radius: 1rem; border: 1px solid #10b981;">', unsafe_allow_html=True)
                            st.markdown("### 📚 Recommended Resources")
                            for res in strategy['resources']:
                                if isinstance(res, dict):
                                    st.markdown(f"**{res.get('name')}**")
                                    st.caption(f"Cost: {res.get('cost')}")
                                else:
                                    st.markdown(f"• {res}")
                            st.markdown('</div>', unsafe_allow_html=True)

                    # --- SECTION 3: VISUALIZATION ---
                    st.markdown("")
                    st.divider()
                    st.markdown("## 📉 Financial Runway Projection")
                    st.markdown("")

                    # Simple projection logic for the chart
                    months_range = list(range(13))
                    start_bal = total_savings - float(bootcamp_cost)
                    burn = data['monthly_burn_rate']
                    balances = [start_bal - (burn * m) for m in months_range]

                    # Create a beautiful Plotly chart
                    fig = go.Figure()

                    # Add the main savings line
                    fig.add_trace(go.Scatter(
                        x=months_range,
                        y=balances,
                        mode='lines+markers',
                        name='Projected Savings',
                        line=dict(
                            color='#6366f1',
                            width=3,
                            shape='spline'
                        ),
                        marker=dict(
                            size=8,
                            color='#8b5cf6',
                            line=dict(color='#a78bfa', width=2)
                        ),
                        fill='tozeroy',
                        fillcolor='rgba(99, 102, 241, 0.1)'
                    ))

                    # Add zero line (danger zone)
                    fig.add_hline(
                        y=0,
                        line_dash="dash",
                        line_color="#ef4444",
                        annotation_text="Danger Zone",
                        annotation_position="right"
                    )

                    # Add planned job start marker if applicable
                    if months <= 12:
                        fig.add_vline(
                            x=months,
                            line_dash="dash",
                            line_color="#10b981",
                            annotation_text=f"Target Job Start (Month {months})",
                            annotation_position="top"
                        )

                    # Update layout for dark theme
                    fig.update_layout(
                        template="plotly_dark",
                        plot_bgcolor='rgba(15, 23, 42, 0.8)',
                        paper_bgcolor='rgba(15, 23, 42, 0.8)',
                        font=dict(
                            family="sans-serif",
                            size=12,
                            color="#f1f5f9"
                        ),
                        xaxis=dict(
                            title="Months from Now",
                            gridcolor='rgba(71, 85, 105, 0.3)',
                            showgrid=True
                        ),
                        yaxis=dict(
                            title="Savings Balance ($)",
                            gridcolor='rgba(71, 85, 105, 0.3)',
                            showgrid=True
                        ),
                        hovermode='x unified',
                        margin=dict(l=20, r=20, t=40, b=20),
                        height=450
                    )

                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.error(f"Backend Error ({response.status_code})")
                    st.write(response.json())

            except requests.exceptions.ConnectionError:
                st.error("🚨 Backend is offline! Is uvicorn running?")
            except Exception as e:
                st.error(f"An error occurred: {e}")
