"""
REI Nationwide LLC - Overview Page
Executive snapshot with KPIs and high-level funnel
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.calculations import ScenarioInputs, run_full_calculation
from components.visualizations import (
    create_funnel_chart, create_revenue_breakdown_chart,
    create_weekly_targets_chart, format_currency
)

st.set_page_config(page_title="Overview | REI Control Tower", page_icon="📊", layout="wide")

# Initialize session state if needed
if 'current_inputs' not in st.session_state:
    st.session_state.current_inputs = ScenarioInputs()

# Custom CSS
st.markdown("""
<style>
    .kpi-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid #2d4a6f;
        margin-bottom: 1rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4ade80;
        margin: 0;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        text-transform: uppercase;
    }
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
</style>
""", unsafe_allow_html=True)

def render_kpi(value: str, label: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value">{value}</p>
        <p class="kpi-label">{label}</p>
        <p style="font-size: 0.75rem; color: #64748b; margin-top: 0.3rem;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


st.title("📊 Executive Overview")
st.markdown(f"**Scenario:** {st.session_state.current_inputs.name}")

# Calculate outputs
inputs = st.session_state.current_inputs
outputs = run_full_calculation(inputs)

# Top KPIs
st.markdown("---")
st.markdown("### 🎯 Key Performance Indicators")

cols = st.columns(6)

with cols[0]:
    render_kpi(
        f"${outputs.revenue.gross_revenue/1e6:.1f}M",
        "Gross Revenue",
        "Annual"
    )

with cols[1]:
    render_kpi(
        f"${outputs.comp.noi/1e6:.1f}M",
        "NOI",
        f"{outputs.comp.noi/outputs.revenue.gross_revenue*100:.0f}% margin"
    )

with cols[2]:
    render_kpi(
        f"${outputs.comp.hamza_total_comp/1e6:.2f}M",
        "CEO Comp",
        "Draw + Salary"
    )

with cols[3]:
    render_kpi(
        f"{outputs.funnel.contracts_per_week:.1f}",
        "Contracts/Week",
        f"{outputs.funnel.contracts_needed_annual:.0f}/year"
    )

with cols[4]:
    render_kpi(
        f"{outputs.funnel.leads_per_week:.0f}",
        "Leads/Week",
        f"@ ${inputs.cpl:.0f} CPL"
    )

with cols[5]:
    render_kpi(
        f"{outputs.funnel.lead_to_contract_rate*100:.1f}%",
        "Conversion",
        "Lead → Contract"
    )

st.markdown("---")

# Main content area
col_main, col_side = st.columns([3, 1])

with col_main:
    tab1, tab2, tab3 = st.tabs(["📈 Pipeline Funnel", "💰 Revenue Mix", "🎯 Weekly Targets"])
    
    with tab1:
        funnel_fig = create_funnel_chart(
            leads=outputs.funnel.leads_per_week,
            contracts=outputs.funnel.contracts_per_week,
            internal=outputs.funnel.internal_per_week,
            wholesale=outputs.funnel.wholesale_per_week,
            retail=outputs.funnel.retail_per_week,
            fallout=outputs.funnel.fallout_per_week
        )
        st.plotly_chart(funnel_fig, use_container_width=True)
        
        st.markdown("##### Funnel Metrics")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Leads/Contract", f"{outputs.funnel.leads_per_contract:.1f}")
        with m2:
            st.metric("Outcomes/Year", f"{outputs.funnel.monetized_outcomes:,}")
        with m3:
            st.metric("Fallout Rate", f"{inputs.fallout_rate*100:.0f}%")
        with m4:
            st.metric("Annual Spend", f"${inputs.weekly_ad_spend * 52 / 1e6:.2f}M")
    
    with tab2:
        rev_fig = create_revenue_breakdown_chart(
            wholesale=outputs.revenue.wholesale_revenue,
            internal=outputs.revenue.internal_revenue,
            membership=outputs.revenue.membership_revenue,
            listing=outputs.revenue.listing_revenue,
            prop_mgmt=outputs.revenue.property_mgmt_revenue
        )
        st.plotly_chart(rev_fig, use_container_width=True)
        
        # Revenue details
        st.markdown("##### Revenue Breakdown")
        import pandas as pd
        rev_df = pd.DataFrame({
            'Source': ['Wholesale Fees', 'Internal Acquisitions', 'Memberships', 'Listings', 'Property Mgmt'],
            'Annual': [
                f"${outputs.revenue.wholesale_revenue:,.0f}",
                f"${outputs.revenue.internal_revenue:,.0f}",
                f"${outputs.revenue.membership_revenue:,.0f}",
                f"${outputs.revenue.listing_revenue:,.0f}",
                f"${outputs.revenue.property_mgmt_revenue:,.0f}"
            ],
            '% of Total': [
                f"{outputs.revenue.wholesale_revenue/outputs.revenue.gross_revenue*100:.1f}%",
                f"{outputs.revenue.internal_revenue/outputs.revenue.gross_revenue*100:.1f}%",
                f"{outputs.revenue.membership_revenue/outputs.revenue.gross_revenue*100:.1f}%",
                f"{outputs.revenue.listing_revenue/outputs.revenue.gross_revenue*100:.1f}%",
                f"{outputs.revenue.property_mgmt_revenue/outputs.revenue.gross_revenue*100:.1f}%"
            ]
        })
        st.dataframe(rev_df, hide_index=True, use_container_width=True)
    
    with tab3:
        targets_fig = create_weekly_targets_chart(
            internal=outputs.funnel.internal_per_week,
            wholesale=outputs.funnel.wholesale_per_week,
            retail=outputs.funnel.retail_per_week,
            fallout=outputs.funnel.fallout_per_week,
            membership=outputs.funnel.membership_per_week
        )
        st.plotly_chart(targets_fig, use_container_width=True)
        
        # Weekly targets table
        st.markdown("##### Weekly Production Targets")
        targets_df = pd.DataFrame({
            'Metric': ['Internal Retains', 'Wholesale', 'Retail Listings', 'Memberships', 'Fallout'],
            'Weekly': [
                f"{outputs.funnel.internal_per_week:.1f}",
                f"{outputs.funnel.wholesale_per_week:.1f}",
                f"{outputs.funnel.retail_per_week:.1f}",
                f"{outputs.funnel.membership_per_week:.1f}",
                f"{outputs.funnel.fallout_per_week:.1f}"
            ],
            'Annual': [
                f"{inputs.retained_doors}",
                f"{inputs.wholesale_volume}",
                f"{inputs.retail_listings}",
                f"{inputs.memberships_sold}",
                f"{int(outputs.funnel.fallout_per_week * 52)}"
            ]
        })
        st.dataframe(targets_df, hide_index=True, use_container_width=True)

with col_side:
    st.markdown("### ⚠️ Alerts")
    
    if outputs.alerts:
        for alert in outputs.alerts:
            severity_class = 'alert-critical' if alert.severity == 'critical' else 'alert-warning'
            icon = '🔴' if alert.severity == 'critical' else '🟡'
            
            st.markdown(f"""
            <div class="{severity_class}">
                <strong>{icon} {alert.category}</strong><br>
                <span style="font-size: 0.85rem;">{alert.message}</span><br>
                <em style="color: #94a3b8; font-size: 0.8rem;">{alert.recommendation}</em>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ All systems nominal")
    
    st.markdown("---")
    
    st.markdown("### 👥 Quick Staff View")
    
    staff_data = [
        ("Closers", outputs.staffing.closers_needed),
        ("Underwriters", outputs.staffing.underwriters_needed),
        ("PMs", outputs.staffing.pms_needed),
        ("TCs", outputs.staffing.tcs_needed),
        ("Dispo", outputs.staffing.dispo_needed),
        ("DSCR Coord", outputs.staffing.dscr_coordinators_needed),
    ]
    
    for role, need in staff_data:
        headcount = max(1, int(need + 0.99))
        st.markdown(f"**{role}:** {headcount} ({need:.1f} calc)")
    
    st.markdown("---")
    
    st.markdown("### 💼 Comp Summary")
    st.markdown(f"**Hamza Draw:** ${outputs.comp.hamza_draw:,.0f}")
    st.markdown(f"**Hamza Salary:** ${outputs.comp.hamza_salary:,.0f}")
    st.markdown(f"**Total CEO:** ${outputs.comp.hamza_total_comp:,.0f}")
    st.markdown(f"**Clearroute:** ${outputs.comp.clearroute_dividend:,.0f}")
