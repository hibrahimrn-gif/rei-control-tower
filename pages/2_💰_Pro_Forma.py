"""
REI Nationwide LLC - Pro Forma Page
Full P&L with adjustable drivers
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.calculations import ScenarioInputs, run_full_calculation
from components.visualizations import (
    create_expense_breakdown_chart, create_proforma_waterfall, format_currency
)

st.set_page_config(page_title="Pro Forma | REI Control Tower", page_icon="💰", layout="wide")

# Initialize session state
if 'current_inputs' not in st.session_state:
    st.session_state.current_inputs = ScenarioInputs()

st.title("💰 Pro Forma P&L")
st.markdown("Adjust drivers in the sidebar to see real-time impact on financials")

# Sidebar inputs
with st.sidebar:
    st.header("📝 Revenue Drivers")
    
    # Volume inputs
    st.subheader("Deal Volume (Annual)")
    
    wholesale_vol = st.number_input(
        "Wholesale Deals",
        min_value=0, max_value=1000,
        value=st.session_state.current_inputs.wholesale_volume,
        step=10,
        help="Number of wholesale deals per year"
    )
    
    retained = st.number_input(
        "Retained Doors (Internal)",
        min_value=0, max_value=1000,
        value=st.session_state.current_inputs.retained_doors,
        step=10,
        help="Properties bought for rental portfolio"
    )
    
    memberships = st.number_input(
        "Memberships Sold",
        min_value=0, max_value=500,
        value=st.session_state.current_inputs.memberships_sold,
        step=10
    )
    
    listings = st.number_input(
        "Retail Listings",
        min_value=0, max_value=500,
        value=st.session_state.current_inputs.retail_listings,
        step=10
    )
    
    st.subheader("Avg Fee/Price")
    
    avg_wholesale = st.number_input(
        "Avg Wholesale Fee ($)",
        min_value=5000, max_value=100000,
        value=int(st.session_state.current_inputs.avg_wholesale_fee),
        step=1000
    )
    
    avg_internal = st.number_input(
        "Internal Acq Fee ($)",
        min_value=5000, max_value=100000,
        value=int(st.session_state.current_inputs.internal_acq_fee),
        step=1000
    )
    
    membership_price = st.number_input(
        "Membership Price ($)",
        min_value=1000, max_value=50000,
        value=int(st.session_state.current_inputs.membership_price),
        step=500
    )
    
    avg_retail = st.number_input(
        "Avg Retail Price ($)",
        min_value=50000, max_value=500000,
        value=int(st.session_state.current_inputs.avg_retail_price),
        step=10000
    )
    
    listing_rate = st.slider(
        "Listing Commission Rate",
        min_value=0.01, max_value=0.06,
        value=st.session_state.current_inputs.listing_commission_rate,
        step=0.005,
        format="%.1f%%"
    )
    
    prop_mgmt = st.number_input(
        "Property Mgmt Revenue ($)",
        min_value=0, max_value=2000000,
        value=int(st.session_state.current_inputs.property_mgmt_revenue),
        step=10000
    )
    
    st.markdown("---")
    st.header("💸 Commission Rates")
    
    pres_override = st.slider(
        "President Override",
        min_value=0.0, max_value=0.20,
        value=st.session_state.current_inputs.president_override_rate,
        step=0.01,
        format="%.0f%%"
    )
    
    acq_comm = st.slider(
        "Acquisition Commission",
        min_value=0.0, max_value=0.20,
        value=st.session_state.current_inputs.acq_commission_rate,
        step=0.01,
        format="%.0f%%"
    )
    
    dispo_comm = st.slider(
        "Dispo Commission",
        min_value=0.0, max_value=0.15,
        value=st.session_state.current_inputs.dispo_commission_rate,
        step=0.01,
        format="%.0f%%"
    )
    
    member_comm = st.slider(
        "Membership Commission",
        min_value=0.0, max_value=0.20,
        value=st.session_state.current_inputs.membership_commission_rate,
        step=0.01,
        format="%.0f%%"
    )
    
    st.markdown("---")
    st.header("📢 Marketing")
    
    weekly_spend = st.number_input(
        "Weekly Ad Spend ($)",
        min_value=0, max_value=100000,
        value=int(st.session_state.current_inputs.weekly_ad_spend),
        step=1000
    )
    
    cpl = st.number_input(
        "Cost Per Lead ($)",
        min_value=10, max_value=500,
        value=int(st.session_state.current_inputs.cpl),
        step=5
    )
    
    st.markdown("---")
    st.header("👔 Salaries")
    
    exec_sal = st.number_input(
        "Executive Salaries ($)",
        min_value=0, max_value=2000000,
        value=int(st.session_state.current_inputs.executive_salaries),
        step=10000,
        help="Hamza + Jacqui + Melissa"
    )
    
    staff_sal = st.number_input(
        "Staff Salaries ($)",
        min_value=0, max_value=2000000,
        value=int(st.session_state.current_inputs.staff_salaries),
        step=10000
    )
    
    hamza_sal = st.number_input(
        "Hamza Base Salary ($)",
        min_value=0, max_value=1000000,
        value=int(st.session_state.current_inputs.hamza_salary),
        step=10000
    )
    
    st.markdown("---")
    st.header("📊 Comp Structure")
    
    hamza_share = st.slider(
        "Hamza NOI Share",
        min_value=0.0, max_value=0.50,
        value=st.session_state.current_inputs.hamza_noi_share,
        step=0.01,
        format="%.0f%%"
    )
    
    cr_share = st.slider(
        "Clearroute NOI Share",
        min_value=0.0, max_value=0.50,
        value=st.session_state.current_inputs.clearroute_noi_share,
        step=0.01,
        format="%.0f%%"
    )

# Update session state with new inputs
st.session_state.current_inputs.wholesale_volume = wholesale_vol
st.session_state.current_inputs.retained_doors = retained
st.session_state.current_inputs.memberships_sold = memberships
st.session_state.current_inputs.retail_listings = listings
st.session_state.current_inputs.avg_wholesale_fee = float(avg_wholesale)
st.session_state.current_inputs.internal_acq_fee = float(avg_internal)
st.session_state.current_inputs.membership_price = float(membership_price)
st.session_state.current_inputs.avg_retail_price = float(avg_retail)
st.session_state.current_inputs.listing_commission_rate = listing_rate
st.session_state.current_inputs.property_mgmt_revenue = float(prop_mgmt)
st.session_state.current_inputs.president_override_rate = pres_override
st.session_state.current_inputs.acq_commission_rate = acq_comm
st.session_state.current_inputs.dispo_commission_rate = dispo_comm
st.session_state.current_inputs.membership_commission_rate = member_comm
st.session_state.current_inputs.weekly_ad_spend = float(weekly_spend)
st.session_state.current_inputs.cpl = float(cpl)
st.session_state.current_inputs.executive_salaries = float(exec_sal)
st.session_state.current_inputs.staff_salaries = float(staff_sal)
st.session_state.current_inputs.hamza_salary = float(hamza_sal)
st.session_state.current_inputs.hamza_noi_share = hamza_share
st.session_state.current_inputs.clearroute_noi_share = cr_share

# Calculate outputs
inputs = st.session_state.current_inputs
outputs = run_full_calculation(inputs)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📈 Revenue")
    
    rev_data = pd.DataFrame({
        'Line Item': [
            'Wholesale Fees',
            'Internal Acquisition Fees',
            'Membership Sales',
            'Listing Commissions',
            'Property Management',
            '**GROSS REVENUE**'
        ],
        'Annual': [
            f"${outputs.revenue.wholesale_revenue:,.0f}",
            f"${outputs.revenue.internal_revenue:,.0f}",
            f"${outputs.revenue.membership_revenue:,.0f}",
            f"${outputs.revenue.listing_revenue:,.0f}",
            f"${outputs.revenue.property_mgmt_revenue:,.0f}",
            f"**${outputs.revenue.gross_revenue:,.0f}**"
        ],
        'Formula': [
            f"{inputs.wholesale_volume} × ${inputs.avg_wholesale_fee:,.0f}",
            f"{inputs.retained_doors} × ${inputs.internal_acq_fee:,.0f}",
            f"{inputs.memberships_sold} × ${inputs.membership_price:,.0f}",
            f"{inputs.retail_listings} × ${inputs.avg_retail_price:,.0f} × {inputs.listing_commission_rate*100:.0f}%",
            "Fixed",
            ""
        ]
    })
    
    st.dataframe(rev_data, hide_index=True, use_container_width=True)
    
    st.markdown("### 💸 Expenses")
    
    exp_data = pd.DataFrame({
        'Line Item': [
            'President Override',
            'Acquisition Commissions',
            'Dispo Commissions',
            'Membership Commissions',
            'Marketing Spend',
            'Executive Salaries',
            'Staff Salaries',
            '**TOTAL EXPENSES**'
        ],
        'Annual': [
            f"${outputs.expenses.president_override:,.0f}",
            f"${outputs.expenses.acq_commissions:,.0f}",
            f"${outputs.expenses.dispo_commissions:,.0f}",
            f"${outputs.expenses.membership_commissions:,.0f}",
            f"${outputs.expenses.marketing_spend:,.0f}",
            f"${outputs.expenses.executive_salaries:,.0f}",
            f"${outputs.expenses.staff_salaries:,.0f}",
            f"**${outputs.expenses.total_expenses:,.0f}**"
        ],
        'Rate/Formula': [
            f"{inputs.president_override_rate*100:.0f}% of Gross Rev",
            f"{inputs.acq_commission_rate*100:.0f}% of WS+Internal Rev",
            f"{inputs.dispo_commission_rate*100:.0f}% of Wholesale Rev",
            f"{inputs.membership_commission_rate*100:.0f}% of Membership Rev",
            f"${inputs.weekly_ad_spend:,.0f}/wk × 52",
            "Fixed",
            "Fixed",
            ""
        ]
    })
    
    st.dataframe(exp_data, hide_index=True, use_container_width=True)

with col2:
    st.markdown("### 📊 P&L Summary")
    
    # Big metrics
    m1, m2 = st.columns(2)
    with m1:
        st.metric(
            "Gross Revenue",
            f"${outputs.revenue.gross_revenue/1e6:.2f}M"
        )
    with m2:
        st.metric(
            "Total Expenses",
            f"${outputs.expenses.total_expenses/1e6:.2f}M"
        )
    
    m3, m4 = st.columns(2)
    with m3:
        margin = outputs.comp.noi / outputs.revenue.gross_revenue * 100 if outputs.revenue.gross_revenue > 0 else 0
        st.metric(
            "Net Operating Income",
            f"${outputs.comp.noi/1e6:.2f}M",
            delta=f"{margin:.0f}% margin"
        )
    with m4:
        st.metric(
            "Expense Ratio",
            f"{outputs.expenses.total_expenses/outputs.revenue.gross_revenue*100:.0f}%"
        )
    
    st.markdown("---")
    
    # Expense breakdown chart
    exp_fig = create_expense_breakdown_chart(
        president=outputs.expenses.president_override,
        acq=outputs.expenses.acq_commissions,
        dispo=outputs.expenses.dispo_commissions,
        membership=outputs.expenses.membership_commissions,
        marketing=outputs.expenses.marketing_spend,
        exec_sal=outputs.expenses.executive_salaries,
        staff_sal=outputs.expenses.staff_salaries
    )
    st.plotly_chart(exp_fig, use_container_width=True)

st.markdown("---")

# Comp splits section
st.markdown("### 💼 Compensation & Profit Splits")

comp_cols = st.columns(4)

with comp_cols[0]:
    st.markdown("#### Hamza (CEO)")
    st.metric("NOI Draw (25%)", f"${outputs.comp.hamza_draw:,.0f}")
    st.metric("Base Salary", f"${outputs.comp.hamza_salary:,.0f}")
    st.metric("**Total Comp**", f"${outputs.comp.hamza_total_comp:,.0f}")

with comp_cols[1]:
    st.markdown("#### President (Jacqui)")
    st.metric("Override (10% GR)", f"${outputs.expenses.president_override:,.0f}")

with comp_cols[2]:
    st.markdown("#### Clearroute")
    st.metric("Dividend (20% NOI)", f"${outputs.comp.clearroute_dividend:,.0f}")

with comp_cols[3]:
    st.markdown("#### Remaining NOI")
    remaining = outputs.comp.noi - outputs.comp.hamza_draw - outputs.comp.clearroute_dividend
    st.metric("After Splits", f"${remaining:,.0f}")
    st.caption("Available for reinvestment")

# Waterfall chart
st.markdown("---")
st.markdown("### 📉 Revenue to NOI Waterfall")

waterfall_expenses = {
    'Pres Override': outputs.expenses.president_override,
    'Acq Comm': outputs.expenses.acq_commissions,
    'Dispo Comm': outputs.expenses.dispo_commissions,
    'Member Comm': outputs.expenses.membership_commissions,
    'Marketing': outputs.expenses.marketing_spend,
    'Exec Sal': outputs.expenses.executive_salaries,
    'Staff Sal': outputs.expenses.staff_salaries,
}

waterfall_fig = create_proforma_waterfall(
    revenue=outputs.revenue.gross_revenue,
    expenses_breakdown=waterfall_expenses,
    noi=outputs.comp.noi
)
st.plotly_chart(waterfall_fig, use_container_width=True)

# Validation check
st.markdown("---")
with st.expander("🔍 Validation Check"):
    target_rev = 21540000
    target_noi = 13434200
    target_ceo = 3838550
    
    st.markdown("**Comparing to 2026 Pro Forma targets:**")
    
    v1, v2, v3 = st.columns(3)
    with v1:
        diff_rev = outputs.revenue.gross_revenue - target_rev
        color = "green" if abs(diff_rev) < 100000 else "red"
        st.markdown(f"Gross Revenue: **${outputs.revenue.gross_revenue:,.0f}** (target: $21.54M)")
        st.markdown(f"Variance: :{color}[${diff_rev:+,.0f}]")
    
    with v2:
        diff_noi = outputs.comp.noi - target_noi
        color = "green" if abs(diff_noi) < 100000 else "red"
        st.markdown(f"NOI: **${outputs.comp.noi:,.0f}** (target: $13.43M)")
        st.markdown(f"Variance: :{color}[${diff_noi:+,.0f}]")
    
    with v3:
        diff_ceo = outputs.comp.hamza_total_comp - target_ceo
        color = "green" if abs(diff_ceo) < 50000 else "red"
        st.markdown(f"CEO Comp: **${outputs.comp.hamza_total_comp:,.0f}** (target: $3.84M)")
        st.markdown(f"Variance: :{color}[${diff_ceo:+,.0f}]")
