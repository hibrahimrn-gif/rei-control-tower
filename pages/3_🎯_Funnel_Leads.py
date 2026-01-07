"""
REI Nationwide LLC - Funnel & Lead Requirements Page
Work backwards from outcomes to lead volume
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.calculations import ScenarioInputs, run_full_calculation
from components.visualizations import (
    create_funnel_chart, create_pipeline_split_chart, create_weekly_targets_chart
)

st.set_page_config(page_title="Funnel & Leads | REI Control Tower", page_icon="🎯", layout="wide")

# Initialize session state
if 'current_inputs' not in st.session_state:
    st.session_state.current_inputs = ScenarioInputs()

st.title("🎯 Funnel & Lead Requirements")
st.markdown("Working backwards from target outcomes to required lead volume")

# Sidebar for funnel-specific inputs
with st.sidebar:
    st.header("⚙️ Funnel Parameters")
    
    st.subheader("Pipeline Split")
    st.caption("Must sum to 100%")
    
    internal_split = st.slider(
        "Internal Retain %",
        min_value=0.0, max_value=0.60,
        value=st.session_state.current_inputs.internal_split,
        step=0.05,
        format="%.0f%%"
    )
    
    wholesale_split = st.slider(
        "Wholesale %",
        min_value=0.0, max_value=0.60,
        value=st.session_state.current_inputs.wholesale_split,
        step=0.05,
        format="%.0f%%"
    )
    
    retail_split = st.slider(
        "Retail Listing %",
        min_value=0.0, max_value=0.40,
        value=st.session_state.current_inputs.retail_split,
        step=0.05,
        format="%.0f%%"
    )
    
    fallout = st.slider(
        "Fallout/Nurture %",
        min_value=0.05, max_value=0.40,
        value=st.session_state.current_inputs.fallout_rate,
        step=0.05,
        format="%.0f%%"
    )
    
    total_split = internal_split + wholesale_split + retail_split + fallout
    if abs(total_split - 1.0) > 0.01:
        st.error(f"⚠️ Splits sum to {total_split*100:.0f}% (must be 100%)")
    else:
        st.success(f"✅ Splits sum to 100%")
    
    st.markdown("---")
    
    st.subheader("Marketing")
    
    weekly_spend = st.number_input(
        "Weekly Ad Spend ($)",
        min_value=1000, max_value=100000,
        value=int(st.session_state.current_inputs.weekly_ad_spend),
        step=1000
    )
    
    cpl = st.number_input(
        "Cost Per Lead ($)",
        min_value=20, max_value=300,
        value=int(st.session_state.current_inputs.cpl),
        step=5
    )
    
    st.markdown("---")
    
    st.subheader("Target Override")
    st.caption("Override volume targets from Pro Forma")
    
    use_override = st.checkbox("Use custom targets", value=False)
    
    if use_override:
        wholesale_override = st.number_input(
            "Wholesale Deals/Year",
            min_value=0, max_value=1000,
            value=st.session_state.current_inputs.wholesale_volume
        )
        internal_override = st.number_input(
            "Retained Doors/Year",
            min_value=0, max_value=1000,
            value=st.session_state.current_inputs.retained_doors
        )
        retail_override = st.number_input(
            "Retail Listings/Year",
            min_value=0, max_value=500,
            value=st.session_state.current_inputs.retail_listings
        )
    else:
        wholesale_override = st.session_state.current_inputs.wholesale_volume
        internal_override = st.session_state.current_inputs.retained_doors
        retail_override = st.session_state.current_inputs.retail_listings

# Update session state
st.session_state.current_inputs.internal_split = internal_split
st.session_state.current_inputs.wholesale_split = wholesale_split
st.session_state.current_inputs.retail_split = retail_split
st.session_state.current_inputs.fallout_rate = fallout
st.session_state.current_inputs.weekly_ad_spend = float(weekly_spend)
st.session_state.current_inputs.cpl = float(cpl)

if use_override:
    st.session_state.current_inputs.wholesale_volume = wholesale_override
    st.session_state.current_inputs.retained_doors = internal_override
    st.session_state.current_inputs.retail_listings = retail_override

# Calculate outputs
inputs = st.session_state.current_inputs
outputs = run_full_calculation(inputs)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📊 Reverse-Engineered Lead Requirements")
    
    # Key metrics in a highlighted box
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
                padding: 1.5rem; border-radius: 12px; border: 1px solid #3b82f6;">
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric(
            "Monetized Outcomes",
            f"{outputs.funnel.monetized_outcomes:,}/year",
            help="Wholesale + Internal + Retail"
        )
    
    with m2:
        st.metric(
            "Contracts Needed",
            f"{outputs.funnel.contracts_needed_annual:.0f}/year",
            delta=f"{outputs.funnel.contracts_per_week:.1f}/week"
        )
    
    with m3:
        st.metric(
            "Leads Needed",
            f"{outputs.funnel.leads_per_year:,.0f}/year",
            delta=f"{outputs.funnel.leads_per_week:.0f}/week"
        )
    
    with m4:
        st.metric(
            "Conversion Required",
            f"{outputs.funnel.lead_to_contract_rate*100:.1f}%",
            help="Lead → Contract rate"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Funnel visualization
    st.markdown("### 🔄 Weekly Pipeline Funnel")
    
    funnel_fig = create_funnel_chart(
        leads=outputs.funnel.leads_per_week,
        contracts=outputs.funnel.contracts_per_week,
        internal=outputs.funnel.internal_per_week,
        wholesale=outputs.funnel.wholesale_per_week,
        retail=outputs.funnel.retail_per_week,
        fallout=outputs.funnel.fallout_per_week
    )
    st.plotly_chart(funnel_fig, use_container_width=True)
    
    # Calculation breakdown
    st.markdown("### 📐 Calculation Breakdown")
    
    calc_df = pd.DataFrame({
        'Step': [
            '1. Target Outcomes (Annual)',
            '2. Fallout Rate',
            '3. Contracts Needed',
            '4. Contracts/Week',
            '5. Weekly Ad Spend',
            '6. CPL',
            '7. Leads/Week',
            '8. Leads/Year',
            '9. Lead→Contract Rate',
            '10. Leads per Contract'
        ],
        'Calculation': [
            f"WS({inputs.wholesale_volume}) + INT({inputs.retained_doors}) + RET({inputs.retail_listings})",
            f"{inputs.fallout_rate*100:.0f}%",
            f"{outputs.funnel.monetized_outcomes} / (1 - {inputs.fallout_rate:.2f})",
            f"{outputs.funnel.contracts_needed_annual:.0f} / 52",
            f"${inputs.weekly_ad_spend:,.0f}",
            f"${inputs.cpl:.0f}",
            f"${inputs.weekly_ad_spend:,.0f} / ${inputs.cpl:.0f}",
            f"{outputs.funnel.leads_per_week:.0f} × 52",
            f"{outputs.funnel.contracts_needed_annual:.0f} / {outputs.funnel.leads_per_year:,.0f}",
            f"{outputs.funnel.leads_per_year:,.0f} / {outputs.funnel.contracts_needed_annual:.0f}"
        ],
        'Result': [
            f"{outputs.funnel.monetized_outcomes:,}",
            f"{inputs.fallout_rate*100:.0f}%",
            f"{outputs.funnel.contracts_needed_annual:.0f}",
            f"{outputs.funnel.contracts_per_week:.2f}",
            f"${inputs.weekly_ad_spend:,.0f}",
            f"${inputs.cpl:.0f}",
            f"{outputs.funnel.leads_per_week:.0f}",
            f"{outputs.funnel.leads_per_year:,.0f}",
            f"{outputs.funnel.lead_to_contract_rate*100:.2f}%",
            f"{outputs.funnel.leads_per_contract:.2f}"
        ]
    })
    
    st.dataframe(calc_df, hide_index=True, use_container_width=True)

with col2:
    st.markdown("### 🥧 Pipeline Split")
    
    split_fig = create_pipeline_split_chart(
        internal=internal_split,
        wholesale=wholesale_split,
        retail=retail_split,
        fallout=fallout
    )
    st.plotly_chart(split_fig, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 📋 Weekly Targets")
    
    targets_data = pd.DataFrame({
        'Chute': ['Internal Retain', 'Wholesale', 'Retail Listing', 'Fallout/Nurture', 'Memberships'],
        'Weekly': [
            f"{outputs.funnel.internal_per_week:.1f}",
            f"{outputs.funnel.wholesale_per_week:.1f}",
            f"{outputs.funnel.retail_per_week:.1f}",
            f"{outputs.funnel.fallout_per_week:.1f}",
            f"{outputs.funnel.membership_per_week:.1f}"
        ],
        'Annual': [
            f"{inputs.retained_doors}",
            f"{inputs.wholesale_volume}",
            f"{inputs.retail_listings}",
            f"{int(outputs.funnel.fallout_per_week * 52)}",
            f"{inputs.memberships_sold}"
        ]
    })
    
    st.dataframe(targets_data, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 💡 Key Insights")
    
    # Conversion assessment
    if outputs.funnel.lead_to_contract_rate > 0.08:
        st.error(f"""
        🔴 **Aggressive Conversion Target**  
        {outputs.funnel.lead_to_contract_rate*100:.1f}% is above 8% - challenging to sustain.
        
        Options:
        - Increase weekly spend
        - Lower deal targets
        - Improve lead quality
        """)
    elif outputs.funnel.lead_to_contract_rate > 0.06:
        st.warning(f"""
        🟡 **Ambitious Conversion Target**  
        {outputs.funnel.lead_to_contract_rate*100:.1f}% requires strong performance.
        
        Monitor closely and build buffer.
        """)
    else:
        st.success(f"""
        🟢 **Healthy Conversion Target**  
        {outputs.funnel.lead_to_contract_rate*100:.1f}% is achievable with good lead quality.
        """)
    
    # Leads per contract
    st.info(f"""
    📊 **Leads per Contract: {outputs.funnel.leads_per_contract:.1f}**
    
    This means you need ~{int(outputs.funnel.leads_per_contract)} leads 
    for every signed contract.
    """)
    
    # Marketing efficiency
    annual_spend = inputs.weekly_ad_spend * 52
    cost_per_contract = annual_spend / outputs.funnel.contracts_needed_annual if outputs.funnel.contracts_needed_annual > 0 else 0
    
    st.info(f"""
    💰 **Cost per Contract: ${cost_per_contract:,.0f}**
    
    Annual marketing: ${annual_spend/1e6:.2f}M  
    Contracts needed: {outputs.funnel.contracts_needed_annual:.0f}
    """)

# Bottom section - weekly scoreboard preview
st.markdown("---")
st.markdown("### 📊 Weekly Scoreboard Preview")

score_cols = st.columns(6)

with score_cols[0]:
    st.metric("Leads", f"{outputs.funnel.leads_per_week:.0f}")
with score_cols[1]:
    st.metric("Contracts", f"{outputs.funnel.contracts_per_week:.1f}")
with score_cols[2]:
    st.metric("Internal", f"{outputs.funnel.internal_per_week:.1f}")
with score_cols[3]:
    st.metric("Wholesale", f"{outputs.funnel.wholesale_per_week:.1f}")
with score_cols[4]:
    st.metric("Retail", f"{outputs.funnel.retail_per_week:.1f}")
with score_cols[5]:
    st.metric("Memberships", f"{outputs.funnel.membership_per_week:.1f}")

st.caption("→ See Execution Plan page for full scoreboard with staffing")
