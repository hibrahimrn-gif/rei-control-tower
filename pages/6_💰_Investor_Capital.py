"""
REI Nationwide LLC - Investor Capital & ROI Tracking
Tracks capital injections, quarterly compounding returns, and investor ROI
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict

st.set_page_config(page_title="Investor Capital", page_icon="💰", layout="wide")

# ============================================================================
# INVESTOR DATA STRUCTURES
# ============================================================================

@dataclass
class Investor:
    name: str
    initial_capital: float
    quarterly_rate: float  # e.g., 0.30 for 30%
    start_date: str
    capital_type: str  # "investment" or "runway"
    notes: str = ""

@dataclass 
class CapitalProjection:
    quarter: int
    quarter_label: str
    beginning_balance: float
    quarterly_return: float
    ending_balance: float
    cumulative_return: float
    roi_percent: float

# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def calculate_quarterly_projections(
    initial_capital: float,
    quarterly_rate: float,
    num_quarters: int = 8,
    start_quarter: str = "Q1 2026"
) -> List[CapitalProjection]:
    """Calculate quarterly compounding projections"""
    projections = []
    balance = initial_capital
    cumulative_return = 0
    
    # Parse start quarter
    q_num = int(start_quarter[1])
    year = int(start_quarter.split()[1])
    
    for i in range(num_quarters):
        # Calculate current quarter label
        current_q = ((q_num - 1 + i) % 4) + 1
        current_year = year + ((q_num - 1 + i) // 4)
        quarter_label = f"Q{current_q} {current_year}"
        
        beginning_balance = balance
        quarterly_return = balance * quarterly_rate
        ending_balance = balance + quarterly_return
        cumulative_return += quarterly_return
        roi_percent = (cumulative_return / initial_capital) * 100
        
        projections.append(CapitalProjection(
            quarter=i + 1,
            quarter_label=quarter_label,
            beginning_balance=beginning_balance,
            quarterly_return=quarterly_return,
            ending_balance=ending_balance,
            cumulative_return=cumulative_return,
            roi_percent=roi_percent
        ))
        
        balance = ending_balance
    
    return projections

def calculate_runway_burn(
    runway_capital: float,
    monthly_burn: float,
    num_months: int = 12
) -> pd.DataFrame:
    """Calculate runway burn schedule"""
    data = []
    balance = runway_capital
    
    for month in range(1, num_months + 1):
        if balance > 0:
            burn = min(monthly_burn, balance)
            balance -= burn
            data.append({
                "Month": month,
                "Beginning Balance": balance + burn,
                "Monthly Burn": burn,
                "Ending Balance": balance
            })
        else:
            data.append({
                "Month": month,
                "Beginning Balance": 0,
                "Monthly Burn": 0,
                "Ending Balance": 0
            })
    
    return pd.DataFrame(data)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'investors' not in st.session_state:
    st.session_state.investors = {
        "M Capitals": {
            "initial_capital": 3_500_000,
            "quarterly_rate": 0.30,
            "capital_type": "investment",
            "start_date": "Q1 2026",
            "notes": "Primary equity partner - 30% quarterly compound (100%+ annual target)"
        },
        "Clear Capital - Investment": {
            "initial_capital": 1_200_000,
            "quarterly_rate": 0.30,
            "capital_type": "investment",
            "start_date": "Q1 2026",
            "notes": "Strategic partner investment tranche"
        },
        "Clear Capital - Runway": {
            "initial_capital": 800_000,
            "quarterly_rate": 0.0,
            "capital_type": "runway",
            "start_date": "Q1 2026",
            "notes": "Operating runway allocation - non-compounding"
        }
    }

if 'monthly_runway_burn' not in st.session_state:
    st.session_state.monthly_runway_burn = 133_333  # ~$800K / 6 months

# ============================================================================
# PAGE HEADER
# ============================================================================

st.title("💰 Investor Capital & ROI Tracking")
st.markdown("---")

# ============================================================================
# SIDEBAR - CAPITAL INPUTS
# ============================================================================

with st.sidebar:
    st.header("⚙️ Capital Configuration")
    
    st.subheader("M Capitals")
    m_cap_initial = st.number_input(
        "Initial Capital ($)",
        value=st.session_state.investors["M Capitals"]["initial_capital"],
        step=100_000,
        key="m_cap_initial"
    )
    m_cap_rate = st.slider(
        "Quarterly Rate (%)",
        min_value=10,
        max_value=50,
        value=int(st.session_state.investors["M Capitals"]["quarterly_rate"] * 100),
        key="m_cap_rate"
    )
    
    st.subheader("Clear Capital - Investment")
    clear_inv_initial = st.number_input(
        "Investment Capital ($)",
        value=st.session_state.investors["Clear Capital - Investment"]["initial_capital"],
        step=100_000,
        key="clear_inv_initial"
    )
    clear_inv_rate = st.slider(
        "Quarterly Rate (%)",
        min_value=10,
        max_value=50,
        value=int(st.session_state.investors["Clear Capital - Investment"]["quarterly_rate"] * 100),
        key="clear_inv_rate"
    )
    
    st.subheader("Clear Capital - Runway")
    clear_runway = st.number_input(
        "Runway Capital ($)",
        value=st.session_state.investors["Clear Capital - Runway"]["initial_capital"],
        step=100_000,
        key="clear_runway"
    )
    monthly_burn = st.number_input(
        "Monthly Burn Rate ($)",
        value=st.session_state.monthly_runway_burn,
        step=10_000,
        key="monthly_burn"
    )
    
    st.subheader("Projection Settings")
    num_quarters = st.slider("Quarters to Project", 4, 16, 8)
    start_quarter = st.selectbox(
        "Start Quarter",
        ["Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026"],
        index=0
    )

# Update session state
st.session_state.investors["M Capitals"]["initial_capital"] = m_cap_initial
st.session_state.investors["M Capitals"]["quarterly_rate"] = m_cap_rate / 100
st.session_state.investors["Clear Capital - Investment"]["initial_capital"] = clear_inv_initial
st.session_state.investors["Clear Capital - Investment"]["quarterly_rate"] = clear_inv_rate / 100
st.session_state.investors["Clear Capital - Runway"]["initial_capital"] = clear_runway
st.session_state.monthly_runway_burn = monthly_burn

# ============================================================================
# SUMMARY KPIs
# ============================================================================

total_investment = m_cap_initial + clear_inv_initial
total_capital = total_investment + clear_runway

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Capital Injected",
        f"${total_capital:,.0f}",
        delta=None
    )

with col2:
    st.metric(
        "Investment Capital",
        f"${total_investment:,.0f}",
        delta="Compounds quarterly"
    )

with col3:
    st.metric(
        "Runway Capital",
        f"${clear_runway:,.0f}",
        delta=f"{clear_runway / monthly_burn:.1f} months runway"
    )

with col4:
    # Calculate Year 1 total obligation
    m_cap_y1 = m_cap_initial * ((1 + m_cap_rate/100) ** 4)
    clear_inv_y1 = clear_inv_initial * ((1 + clear_inv_rate/100) ** 4)
    y1_total_obligation = m_cap_y1 + clear_inv_y1
    st.metric(
        "Year 1 Total Obligation",
        f"${y1_total_obligation:,.0f}",
        delta=f"+${y1_total_obligation - total_investment:,.0f} returns"
    )

st.markdown("---")

# ============================================================================
# INVESTOR PROJECTIONS
# ============================================================================

st.header("📈 Quarterly Compounding Projections")

tab1, tab2, tab3 = st.tabs(["M Capitals", "Clear Capital", "Combined View"])

# M Capitals Tab
with tab1:
    m_cap_projections = calculate_quarterly_projections(
        initial_capital=m_cap_initial,
        quarterly_rate=m_cap_rate / 100,
        num_quarters=num_quarters,
        start_quarter=start_quarter
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Projection table
        m_cap_df = pd.DataFrame([
            {
                "Quarter": p.quarter_label,
                "Beginning Balance": f"${p.beginning_balance:,.0f}",
                "Quarterly Return (30%)": f"${p.quarterly_return:,.0f}",
                "Ending Balance": f"${p.ending_balance:,.0f}",
                "Cumulative Return": f"${p.cumulative_return:,.0f}",
                "ROI %": f"{p.roi_percent:.1f}%"
            }
            for p in m_cap_projections
        ])
        st.dataframe(m_cap_df, use_container_width=True, hide_index=True)
    
    with col2:
        # Key metrics
        final_proj = m_cap_projections[-1]
        y1_proj = m_cap_projections[3] if len(m_cap_projections) >= 4 else final_proj
        
        st.markdown("### 📊 M Capitals Summary")
        st.markdown(f"""
        **Initial Investment:** ${m_cap_initial:,.0f}
        
        **Year 1 (Q4) Balance:** ${y1_proj.ending_balance:,.0f}
        
        **Year 1 Return:** ${y1_proj.cumulative_return:,.0f}
        
        **Year 1 ROI:** {y1_proj.roi_percent:.1f}%
        
        **Final Balance ({final_proj.quarter_label}):** ${final_proj.ending_balance:,.0f}
        
        **Total Return:** ${final_proj.cumulative_return:,.0f}
        
        **Total ROI:** {final_proj.roi_percent:.1f}%
        """)
    
    # Growth chart
    fig_m = go.Figure()
    fig_m.add_trace(go.Scatter(
        x=[p.quarter_label for p in m_cap_projections],
        y=[p.ending_balance for p in m_cap_projections],
        mode='lines+markers',
        name='Balance',
        line=dict(color='#00D4AA', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 170, 0.2)'
    ))
    fig_m.update_layout(
        title="M Capitals - Balance Growth",
        xaxis_title="Quarter",
        yaxis_title="Balance ($)",
        template="plotly_dark",
        height=350,
        yaxis_tickformat='$,.0f'
    )
    st.plotly_chart(fig_m, use_container_width=True)

# Clear Capital Tab
with tab2:
    clear_inv_projections = calculate_quarterly_projections(
        initial_capital=clear_inv_initial,
        quarterly_rate=clear_inv_rate / 100,
        num_quarters=num_quarters,
        start_quarter=start_quarter
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Investment Tranche (Compounding)")
        clear_inv_df = pd.DataFrame([
            {
                "Quarter": p.quarter_label,
                "Beginning Balance": f"${p.beginning_balance:,.0f}",
                "Quarterly Return (30%)": f"${p.quarterly_return:,.0f}",
                "Ending Balance": f"${p.ending_balance:,.0f}",
                "Cumulative Return": f"${p.cumulative_return:,.0f}",
                "ROI %": f"{p.roi_percent:.1f}%"
            }
            for p in clear_inv_projections
        ])
        st.dataframe(clear_inv_df, use_container_width=True, hide_index=True)
        
        st.subheader("Runway Tranche (Burn Schedule)")
        runway_df = calculate_runway_burn(clear_runway, monthly_burn, 12)
        runway_df_display = runway_df.copy()
        runway_df_display["Beginning Balance"] = runway_df_display["Beginning Balance"].apply(lambda x: f"${x:,.0f}")
        runway_df_display["Monthly Burn"] = runway_df_display["Monthly Burn"].apply(lambda x: f"${x:,.0f}")
        runway_df_display["Ending Balance"] = runway_df_display["Ending Balance"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(runway_df_display, use_container_width=True, hide_index=True)
    
    with col2:
        final_clear = clear_inv_projections[-1]
        y1_clear = clear_inv_projections[3] if len(clear_inv_projections) >= 4 else final_clear
        
        st.markdown("### 📊 Clear Capital Summary")
        st.markdown(f"""
        **Investment Tranche:** ${clear_inv_initial:,.0f}
        
        **Runway Tranche:** ${clear_runway:,.0f}
        
        **Total from Clear:** ${clear_inv_initial + clear_runway:,.0f}
        
        ---
        
        **Year 1 Investment Balance:** ${y1_clear.ending_balance:,.0f}
        
        **Year 1 Investment Return:** ${y1_clear.cumulative_return:,.0f}
        
        **Year 1 Investment ROI:** {y1_clear.roi_percent:.1f}%
        
        ---
        
        **Runway Duration:** {clear_runway / monthly_burn:.1f} months
        
        **Monthly Burn:** ${monthly_burn:,.0f}
        """)

# Combined View Tab
with tab3:
    st.subheader("Total Investor Obligations by Quarter")
    
    # Combine projections
    combined_data = []
    for i in range(num_quarters):
        m_proj = m_cap_projections[i]
        c_proj = clear_inv_projections[i]
        
        combined_data.append({
            "Quarter": m_proj.quarter_label,
            "M Capitals Balance": m_proj.ending_balance,
            "Clear Capital Balance": c_proj.ending_balance,
            "Total Obligation": m_proj.ending_balance + c_proj.ending_balance,
            "M Capitals Return": m_proj.cumulative_return,
            "Clear Capital Return": c_proj.cumulative_return,
            "Total Returns Owed": m_proj.cumulative_return + c_proj.cumulative_return
        })
    
    combined_df = pd.DataFrame(combined_data)
    
    # Display formatted table
    display_df = combined_df.copy()
    for col in display_df.columns:
        if col != "Quarter":
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Stacked area chart
    fig_combined = go.Figure()
    fig_combined.add_trace(go.Scatter(
        x=combined_df["Quarter"],
        y=combined_df["M Capitals Balance"],
        mode='lines',
        name='M Capitals',
        stackgroup='one',
        line=dict(color='#00D4AA'),
        fillcolor='rgba(0, 212, 170, 0.6)'
    ))
    fig_combined.add_trace(go.Scatter(
        x=combined_df["Quarter"],
        y=combined_df["Clear Capital Balance"],
        mode='lines',
        name='Clear Capital',
        stackgroup='one',
        line=dict(color='#FF6B6B'),
        fillcolor='rgba(255, 107, 107, 0.6)'
    ))
    fig_combined.update_layout(
        title="Total Investor Obligations Over Time",
        xaxis_title="Quarter",
        yaxis_title="Total Obligation ($)",
        template="plotly_dark",
        height=400,
        yaxis_tickformat='$,.0f',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_combined, use_container_width=True)
    
    # Annual summary
    st.subheader("📅 Annual Summary")
    
    col1, col2, col3 = st.columns(3)
    
    y1_total = combined_df.iloc[3]["Total Obligation"] if len(combined_df) >= 4 else combined_df.iloc[-1]["Total Obligation"]
    y2_total = combined_df.iloc[7]["Total Obligation"] if len(combined_df) >= 8 else combined_df.iloc[-1]["Total Obligation"]
    
    with col1:
        st.markdown("### Year 1 (End of Q4 2026)")
        st.markdown(f"""
        - **M Capitals Obligation:** ${m_cap_projections[3].ending_balance if len(m_cap_projections) >= 4 else 0:,.0f}
        - **Clear Capital Obligation:** ${clear_inv_projections[3].ending_balance if len(clear_inv_projections) >= 4 else 0:,.0f}
        - **Total Obligation:** ${y1_total:,.0f}
        - **Total Returns Owed:** ${combined_df.iloc[3]["Total Returns Owed"] if len(combined_df) >= 4 else 0:,.0f}
        """)
    
    with col2:
        st.markdown("### Year 2 (End of Q4 2027)")
        if len(combined_df) >= 8:
            st.markdown(f"""
            - **M Capitals Obligation:** ${m_cap_projections[7].ending_balance:,.0f}
            - **Clear Capital Obligation:** ${clear_inv_projections[7].ending_balance:,.0f}
            - **Total Obligation:** ${y2_total:,.0f}
            - **Total Returns Owed:** ${combined_df.iloc[7]["Total Returns Owed"]:,.0f}
            """)
        else:
            st.markdown("*Extend projection to 8+ quarters to see Year 2*")
    
    with col3:
        st.markdown("### 📊 Key Metrics")
        total_initial = m_cap_initial + clear_inv_initial
        st.markdown(f"""
        - **Total Initial Investment:** ${total_initial:,.0f}
        - **Quarterly Compound Rate:** {m_cap_rate}%
        - **Effective Annual Rate:** {((1 + m_cap_rate/100)**4 - 1) * 100:.1f}%
        - **Runway Capital:** ${clear_runway:,.0f}
        - **Runway Duration:** {clear_runway / monthly_burn:.1f} months
        """)

# ============================================================================
# NOI vs OBLIGATIONS CHECK
# ============================================================================

st.markdown("---")
st.header("⚠️ NOI vs Investor Obligations")

# Get NOI from main scenario if available
if 'scenario_inputs' in st.session_state:
    from components.calculations import run_full_calculation, ScenarioInputs
    inputs = ScenarioInputs.from_dict(st.session_state.scenario_inputs)
    results = run_full_calculation(inputs)
    projected_noi = results['comp'].noi
else:
    projected_noi = 13_434_200  # Default from 2026 base plan

y1_returns_owed = (m_cap_projections[3].cumulative_return + clear_inv_projections[3].cumulative_return) if len(m_cap_projections) >= 4 else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Projected Annual NOI",
        f"${projected_noi:,.0f}"
    )

with col2:
    st.metric(
        "Year 1 Returns Owed",
        f"${y1_returns_owed:,.0f}"
    )

with col3:
    coverage_ratio = projected_noi / y1_returns_owed if y1_returns_owed > 0 else 0
    surplus = projected_noi - y1_returns_owed
    st.metric(
        "Coverage Ratio",
        f"{coverage_ratio:.2f}x",
        delta=f"${surplus:,.0f} surplus" if surplus > 0 else f"${surplus:,.0f} shortfall"
    )

if coverage_ratio >= 1.5:
    st.success(f"✅ **Strong Coverage:** NOI covers investor obligations {coverage_ratio:.2f}x with ${surplus:,.0f} surplus for operations and growth.")
elif coverage_ratio >= 1.0:
    st.warning(f"⚠️ **Adequate Coverage:** NOI covers obligations but with thin margin. Consider increasing deal volume or reducing investor obligations.")
else:
    st.error(f"🚨 **Coverage Gap:** Projected NOI does not cover investor obligations. Shortfall of ${abs(surplus):,.0f}. Review deal targets or capital structure.")

# ============================================================================
# EXPORT SECTION
# ============================================================================

st.markdown("---")
st.header("📤 Export Capital Schedule")

col1, col2 = st.columns(2)

with col1:
    # Export M Capitals
    m_export_df = pd.DataFrame([
        {
            "Quarter": p.quarter_label,
            "Beginning Balance": p.beginning_balance,
            "Quarterly Return": p.quarterly_return,
            "Ending Balance": p.ending_balance,
            "Cumulative Return": p.cumulative_return,
            "ROI %": p.roi_percent
        }
        for p in m_cap_projections
    ])
    m_csv = m_export_df.to_csv(index=False)
    st.download_button(
        label="📥 Download M Capitals Schedule",
        data=m_csv,
        file_name="m_capitals_schedule.csv",
        mime="text/csv"
    )

with col2:
    # Export Combined
    combined_export_df = combined_df.copy()
    combined_csv = combined_export_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Combined Schedule",
        data=combined_csv,
        file_name="combined_investor_schedule.csv",
        mime="text/csv"
    )
