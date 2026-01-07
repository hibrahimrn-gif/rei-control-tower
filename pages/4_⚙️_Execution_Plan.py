"""
REI Nationwide LLC - Execution Plan Page
Weekly scoreboard, staffing calculator, and bottleneck alerts
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.calculations import ScenarioInputs, run_full_calculation
from components.visualizations import create_staffing_chart

st.set_page_config(page_title="Execution Plan | REI Control Tower", page_icon="⚙️", layout="wide")

# Custom CSS for alerts
st.markdown("""
<style>
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
    .scoreboard-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #2d4a6f;
    }
    .scoreboard-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4ade80;
    }
    .scoreboard-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_inputs' not in st.session_state:
    st.session_state.current_inputs = ScenarioInputs()

st.title("⚙️ Execution Plan")
st.markdown("Operational control tower - weekly targets, staffing, and bottleneck detection")

# Sidebar for staffing capacity inputs
with st.sidebar:
    st.header("👥 Staffing Capacities")
    st.caption("Adjust to match your team's actual capacity")
    
    st.subheader("Closers")
    closer_leads = st.number_input(
        "Leads/Week per Closer",
        min_value=30, max_value=150,
        value=int(st.session_state.current_inputs.closer_lead_capacity),
        step=5,
        help="How many new leads can one closer handle per week"
    )
    
    closer_contracts = st.number_input(
        "Contracts/Week per Closer",
        min_value=1.0, max_value=10.0,
        value=st.session_state.current_inputs.closer_contract_capacity,
        step=0.5,
        help="How many contracts can one closer sign per week"
    )
    
    st.subheader("Underwriting")
    offer_ratio = st.number_input(
        "Offers per Contract",
        min_value=1.0, max_value=10.0,
        value=st.session_state.current_inputs.offer_to_contract_ratio,
        step=0.5,
        help="How many offers needed per signed contract"
    )
    
    uw_capacity = st.number_input(
        "Underwrites/Week per UW",
        min_value=10, max_value=80,
        value=int(st.session_state.current_inputs.underwriter_capacity),
        step=5
    )
    
    st.subheader("Project Management")
    rehab_days = st.number_input(
        "Avg Rehab Cycle (days)",
        min_value=14, max_value=120,
        value=st.session_state.current_inputs.rehab_cycle_days,
        step=7
    )
    
    pm_capacity = st.number_input(
        "Active Rehabs per PM",
        min_value=3, max_value=20,
        value=int(st.session_state.current_inputs.pm_capacity),
        step=1
    )
    
    st.subheader("Transaction & Dispo")
    tc_capacity = st.number_input(
        "Contracts/Week per TC",
        min_value=4, max_value=20,
        value=int(st.session_state.current_inputs.tc_capacity),
        step=1
    )
    
    dispo_capacity = st.number_input(
        "Wholesale/Week per Dispo",
        min_value=2, max_value=15,
        value=int(st.session_state.current_inputs.dispo_capacity),
        step=1
    )
    
    dscr_capacity = st.number_input(
        "Refis/Week per DSCR Coord",
        min_value=2, max_value=15,
        value=int(st.session_state.current_inputs.dscr_capacity),
        step=1
    )
    
    st.subheader("Membership Sales")
    close_rate = st.slider(
        "Held Call Close Rate",
        min_value=0.10, max_value=0.50,
        value=st.session_state.current_inputs.membership_close_rate,
        step=0.05,
        format="%.0f%%"
    )
    
    show_rate = st.slider(
        "Booked Call Show Rate",
        min_value=0.40, max_value=0.90,
        value=st.session_state.current_inputs.membership_show_rate,
        step=0.05,
        format="%.0f%%"
    )

# Update session state
st.session_state.current_inputs.closer_lead_capacity = float(closer_leads)
st.session_state.current_inputs.closer_contract_capacity = closer_contracts
st.session_state.current_inputs.offer_to_contract_ratio = offer_ratio
st.session_state.current_inputs.underwriter_capacity = float(uw_capacity)
st.session_state.current_inputs.rehab_cycle_days = rehab_days
st.session_state.current_inputs.pm_capacity = float(pm_capacity)
st.session_state.current_inputs.tc_capacity = float(tc_capacity)
st.session_state.current_inputs.dispo_capacity = float(dispo_capacity)
st.session_state.current_inputs.dscr_capacity = float(dscr_capacity)
st.session_state.current_inputs.membership_close_rate = close_rate
st.session_state.current_inputs.membership_show_rate = show_rate

# Calculate outputs
inputs = st.session_state.current_inputs
outputs = run_full_calculation(inputs)

# Main content
st.markdown("## 📊 Weekly Scoreboard")

def render_scoreboard_card(value: str, label: str):
    st.markdown(f"""
    <div class="scoreboard-card">
        <div class="scoreboard-value">{value}</div>
        <div class="scoreboard-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

# Top row - Lead & Contract metrics
cols = st.columns(8)

with cols[0]:
    render_scoreboard_card(f"{outputs.funnel.leads_per_week:.0f}", "Leads/Week")
with cols[1]:
    render_scoreboard_card(f"{outputs.funnel.contracts_per_week:.1f}", "Contracts/Week")
with cols[2]:
    render_scoreboard_card(f"{outputs.funnel.internal_per_week:.1f}", "Internal/Week")
with cols[3]:
    render_scoreboard_card(f"{outputs.funnel.wholesale_per_week:.1f}", "Wholesale/Week")
with cols[4]:
    render_scoreboard_card(f"{outputs.funnel.retail_per_week:.1f}", "Retail/Week")
with cols[5]:
    render_scoreboard_card(f"{outputs.funnel.fallout_per_week:.1f}", "Fallout/Week")
with cols[6]:
    render_scoreboard_card(f"{outputs.funnel.membership_per_week:.1f}", "Members/Week")
with cols[7]:
    render_scoreboard_card(f"{outputs.staffing.offers_per_week:.0f}", "Offers/Week")

st.markdown("---")

# Two column layout for staffing and alerts
col_staff, col_alerts = st.columns([2, 1])

with col_staff:
    st.markdown("## 👥 Staffing Calculator")
    
    # Staffing chart
    staff_fig = create_staffing_chart(
        closers=outputs.staffing.closers_needed,
        underwriters=outputs.staffing.underwriters_needed,
        pms=outputs.staffing.pms_needed,
        tcs=outputs.staffing.tcs_needed,
        dispo=outputs.staffing.dispo_needed,
        dscr=outputs.staffing.dscr_coordinators_needed
    )
    st.plotly_chart(staff_fig, use_container_width=True)
    
    # Detailed staffing table
    st.markdown("### 📋 Detailed Breakdown")
    
    staffing_df = pd.DataFrame({
        'Role': [
            'Closers',
            'Underwriters',
            'Project Managers',
            'Transaction Coordinators',
            'Dispo Team',
            'DSCR Coordinator'
        ],
        'Calculated Need': [
            f"{outputs.staffing.closers_needed:.2f}",
            f"{outputs.staffing.underwriters_needed:.2f}",
            f"{outputs.staffing.pms_needed:.2f}",
            f"{outputs.staffing.tcs_needed:.2f}",
            f"{outputs.staffing.dispo_needed:.2f}",
            f"{outputs.staffing.dscr_coordinators_needed:.2f}"
        ],
        'Recommended HC': [
            max(1, int(outputs.staffing.closers_needed + 0.99)),
            max(1, int(outputs.staffing.underwriters_needed + 0.99)),
            max(1, int(outputs.staffing.pms_needed + 0.99)),
            max(1, int(outputs.staffing.tcs_needed + 0.99)),
            max(1, int(outputs.staffing.dispo_needed + 0.99)),
            max(1, int(outputs.staffing.dscr_coordinators_needed + 0.99))
        ],
        'Driver': [
            f"Max of: {outputs.staffing.closers_by_leads:.1f} (leads) or {outputs.staffing.closers_by_contracts:.1f} (contracts)",
            f"{outputs.staffing.offers_per_week:.0f} offers/wk ÷ {inputs.underwriter_capacity:.0f} cap",
            f"{outputs.staffing.active_rehabs:.1f} active rehabs ÷ {inputs.pm_capacity:.0f} cap",
            f"{outputs.funnel.contracts_per_week:.1f} contracts/wk ÷ {inputs.tc_capacity:.0f} cap",
            f"{outputs.funnel.wholesale_per_week:.1f} wholesale/wk ÷ {inputs.dispo_capacity:.0f} cap",
            f"{outputs.funnel.internal_per_week:.1f} refis/wk ÷ {inputs.dscr_capacity:.0f} cap"
        ]
    })
    
    st.dataframe(staffing_df, hide_index=True, use_container_width=True)
    
    # Membership sales calls
    st.markdown("### 📞 Membership Sales Calls")
    
    call_cols = st.columns(4)
    with call_cols[0]:
        st.metric("Memberships/Week", f"{outputs.funnel.membership_per_week:.1f}")
    with call_cols[1]:
        st.metric("Held Calls Needed", f"{outputs.staffing.held_calls_needed:.1f}",
                  help=f"@ {inputs.membership_close_rate*100:.0f}% close rate")
    with call_cols[2]:
        st.metric("Booked Calls Needed", f"{outputs.staffing.booked_calls_needed:.1f}",
                  help=f"@ {inputs.membership_show_rate*100:.0f}% show rate")
    with call_cols[3]:
        daily_calls = outputs.staffing.booked_calls_needed / 5  # 5 day week
        st.metric("Booked/Day (5d)", f"{daily_calls:.1f}")

with col_alerts:
    st.markdown("## ⚠️ Bottleneck Alerts")
    
    if outputs.alerts:
        for alert in outputs.alerts:
            severity_class = 'alert-critical' if alert.severity == 'critical' else 'alert-warning'
            icon = '🔴' if alert.severity == 'critical' else '🟡'
            
            st.markdown(f"""
            <div class="{severity_class}">
                <strong>{icon} {alert.category}</strong><br>
                <span style="font-size: 0.9rem;">{alert.message}</span><br>
                <em style="color: #94a3b8; font-size: 0.85rem;">💡 {alert.recommendation}</em>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No bottlenecks detected")
        st.markdown("All capacity metrics are within target ranges.")
    
    st.markdown("---")
    
    # Quick capacity checks
    st.markdown("### 🔍 Capacity Checks")
    
    # Closer check
    closer_util = outputs.staffing.closers_needed / max(1, int(outputs.staffing.closers_needed + 0.99)) * 100
    if closer_util > 90:
        st.error(f"Closers at {closer_util:.0f}% capacity")
    elif closer_util > 75:
        st.warning(f"Closers at {closer_util:.0f}% capacity")
    else:
        st.success(f"Closers at {closer_util:.0f}% capacity")
    
    # UW check
    uw_hc = max(1, int(outputs.staffing.underwriters_needed + 0.99))
    uw_util = outputs.staffing.underwriters_needed / uw_hc * 100
    if uw_util > 90:
        st.error(f"Underwriting at {uw_util:.0f}% capacity")
    elif uw_util > 75:
        st.warning(f"Underwriting at {uw_util:.0f}% capacity")
    else:
        st.success(f"Underwriting at {uw_util:.0f}% capacity")
    
    # PM check
    pm_hc = max(1, int(outputs.staffing.pms_needed + 0.99))
    pm_util = outputs.staffing.pms_needed / pm_hc * 100
    if pm_util > 90:
        st.error(f"Project Mgmt at {pm_util:.0f}% capacity")
    elif pm_util > 75:
        st.warning(f"Project Mgmt at {pm_util:.0f}% capacity")
    else:
        st.success(f"Project Mgmt at {pm_util:.0f}% capacity")

st.markdown("---")

# Operating cadence section
st.markdown("## 📅 Operating Cadence (Recommended)")

cadence_cols = st.columns(3)

with cadence_cols[0]:
    st.markdown("""
    ### Daily
    - Lead assignment review
    - Hot contract check-in
    - Dispo status update
    """)

with cadence_cols[1]:
    st.markdown("""
    ### Weekly
    - **Monday:** Pipeline review
    - **Wednesday:** Contract velocity check
    - **Friday:** Scoreboard review + alerts
    """)

with cadence_cols[2]:
    st.markdown("""
    ### Monthly
    - P&L vs plan review
    - Conversion rate analysis
    - Staffing capacity assessment
    - CPL trend review
    """)

# Export section
st.markdown("---")
with st.expander("📥 Export Weekly Targets"):
    export_data = {
        'Metric': ['Leads/Week', 'Contracts/Week', 'Internal/Week', 'Wholesale/Week', 
                   'Retail/Week', 'Memberships/Week', 'Offers/Week'],
        'Target': [
            outputs.funnel.leads_per_week,
            outputs.funnel.contracts_per_week,
            outputs.funnel.internal_per_week,
            outputs.funnel.wholesale_per_week,
            outputs.funnel.retail_per_week,
            outputs.funnel.membership_per_week,
            outputs.staffing.offers_per_week
        ]
    }
    
    export_df = pd.DataFrame(export_data)
    
    csv = export_df.to_csv(index=False)
    st.download_button(
        label="Download Weekly Targets CSV",
        data=csv,
        file_name="rei_weekly_targets.csv",
        mime="text/csv"
    )
