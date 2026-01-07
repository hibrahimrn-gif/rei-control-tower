"""
REI Nationwide LLC - Dynamic View Control Tower
Main application entry point

Run with: streamlit run app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add components to path
sys.path.insert(0, str(Path(__file__).parent))

from components.calculations import ScenarioInputs, run_full_calculation
from components.utils import create_default_scenario

# Page configuration
st.set_page_config(
    page_title="REI Nationwide Control Tower",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme professional look
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid #2d4a6f;
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #4ade80;
        margin: 0;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Alert cards */
    .alert-critical {
        background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%);
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #78350f 0%, #451a03 100%);
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3b82f6;
    }
    
    /* Metric highlights */
    .metric-positive {
        color: #4ade80 !important;
    }
    
    .metric-negative {
        color: #ef4444 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Table styling */
    .dataframe {
        font-size: 0.85rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state with defaults"""
    if 'current_inputs' not in st.session_state:
        st.session_state.current_inputs = ScenarioInputs()
    
    if 'saved_scenarios' not in st.session_state:
        st.session_state.saved_scenarios = []
    
    if 'comparison_scenarios' not in st.session_state:
        st.session_state.comparison_scenarios = []


def render_kpi_card(value: str, label: str, delta: str = None):
    """Render a styled KPI card"""
    delta_html = f'<p style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.3rem;">{delta}</p>' if delta else ''
    
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value">{value}</p>
        <p class="kpi-label">{label}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main app function - renders the home/overview page"""
    init_session_state()
    
    # Header
    st.title("🏠 REI Nationwide Control Tower")
    st.markdown("*Dynamic View Dashboard - 2026 Planning & Execution*")
    
    # Compute current scenario
    inputs = st.session_state.current_inputs
    outputs = run_full_calculation(inputs)
    
    # Top KPI Row
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        gross_rev = outputs.revenue.gross_revenue
        render_kpi_card(
            f"${gross_rev/1e6:.1f}M",
            "Gross Revenue",
            "Annual Target"
        )
    
    with col2:
        noi = outputs.comp.noi
        render_kpi_card(
            f"${noi/1e6:.1f}M",
            "Net Operating Income",
            f"{noi/gross_rev*100:.0f}% margin"
        )
    
    with col3:
        render_kpi_card(
            f"${outputs.comp.hamza_total_comp/1e6:.2f}M",
            "CEO Total Comp",
            "Draw + Salary"
        )
    
    with col4:
        render_kpi_card(
            f"{outputs.funnel.contracts_per_week:.1f}",
            "Contracts/Week",
            "Target velocity"
        )
    
    with col5:
        render_kpi_card(
            f"{outputs.funnel.leads_per_week:.0f}",
            "Leads/Week",
            f"@ ${inputs.cpl:.0f} CPL"
        )
    
    st.markdown("---")
    
    # Two-column layout for charts and alerts
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### 📊 Pipeline Funnel")
        
        from components.visualizations import create_funnel_chart
        
        funnel_fig = create_funnel_chart(
            leads=outputs.funnel.leads_per_week,
            contracts=outputs.funnel.contracts_per_week,
            internal=outputs.funnel.internal_per_week,
            wholesale=outputs.funnel.wholesale_per_week,
            retail=outputs.funnel.retail_per_week,
            fallout=outputs.funnel.fallout_per_week
        )
        st.plotly_chart(funnel_fig, use_container_width=True)
        
        # Key Metrics Table
        st.markdown("### 🎯 Key Conversion Metrics")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.metric(
                "Lead → Contract Rate",
                f"{outputs.funnel.lead_to_contract_rate*100:.1f}%",
                help="Target: 4-6%"
            )
        
        with col_m2:
            st.metric(
                "Leads per Contract",
                f"{outputs.funnel.leads_per_contract:.1f}",
                help="Lower is better"
            )
        
        with col_m3:
            st.metric(
                "Monetized Outcomes/Year",
                f"{outputs.funnel.monetized_outcomes:,}",
                help="Deals that exit to a chute"
            )
    
    with col_right:
        st.markdown("### ⚠️ Bottleneck Alerts")
        
        if outputs.alerts:
            for alert in outputs.alerts:
                severity_class = 'alert-critical' if alert.severity == 'critical' else 'alert-warning'
                icon = '🔴' if alert.severity == 'critical' else '🟡'
                
                st.markdown(f"""
                <div class="{severity_class}">
                    <strong>{icon} {alert.category}</strong><br>
                    {alert.message}<br>
                    <em style="color: #94a3b8;">{alert.recommendation}</em>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No bottlenecks detected - all systems nominal")
        
        st.markdown("---")
        
        # Quick staffing summary
        st.markdown("### 👥 Staffing Summary")
        
        staffing_data = {
            "Role": ["Closers", "Underwriters", "PMs", "TCs", "Dispo", "DSCR"],
            "Need": [
                f"{outputs.staffing.closers_needed:.1f}",
                f"{outputs.staffing.underwriters_needed:.1f}",
                f"{outputs.staffing.pms_needed:.1f}",
                f"{outputs.staffing.tcs_needed:.1f}",
                f"{outputs.staffing.dispo_needed:.1f}",
                f"{outputs.staffing.dscr_coordinators_needed:.1f}"
            ],
            "HC": [
                max(1, int(outputs.staffing.closers_needed + 0.99)),
                max(1, int(outputs.staffing.underwriters_needed + 0.99)),
                max(1, int(outputs.staffing.pms_needed + 0.99)),
                max(1, int(outputs.staffing.tcs_needed + 0.99)),
                max(1, int(outputs.staffing.dispo_needed + 0.99)),
                max(1, int(outputs.staffing.dscr_coordinators_needed + 0.99))
            ]
        }
        
        import pandas as pd
        st.dataframe(pd.DataFrame(staffing_data), hide_index=True, use_container_width=True)
    
    # Bottom section - scenario info
    st.markdown("---")
    st.markdown(f"**Current Scenario:** {inputs.name} | Navigate to other pages in the sidebar →")


if __name__ == "__main__":
    main()
