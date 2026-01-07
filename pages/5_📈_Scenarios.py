"""
REI Nationwide LLC - Scenarios & Sensitivity Page
Save/load scenarios, sensitivity analysis, comparison view, and export
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.calculations import (
    ScenarioInputs, run_full_calculation, scenario_to_export,
    generate_sensitivity_cpl, generate_sensitivity_fallout, 
    generate_sensitivity_conversion
)
from components.utils import (
    save_scenario, load_scenario, list_saved_scenarios, delete_scenario,
    create_default_scenario
)
from components.visualizations import create_scenario_comparison_chart

st.set_page_config(page_title="Scenarios | REI Control Tower", page_icon="📈", layout="wide")

# Initialize session state
if 'current_inputs' not in st.session_state:
    st.session_state.current_inputs = ScenarioInputs()

if 'comparison_scenarios' not in st.session_state:
    st.session_state.comparison_scenarios = []

st.title("📈 Scenarios & Sensitivity")
st.markdown("Save, compare scenarios and run sensitivity analysis")

# Calculate current outputs
inputs = st.session_state.current_inputs
outputs = run_full_calculation(inputs)

# Tabs for different functions
tab_save, tab_compare, tab_sensitivity, tab_export = st.tabs([
    "💾 Save/Load", "🔄 Compare", "📊 Sensitivity", "📥 Export"
])

# ========== SAVE/LOAD TAB ==========
with tab_save:
    col_save, col_load = st.columns(2)
    
    with col_save:
        st.markdown("### 💾 Save Current Scenario")
        
        scenario_name = st.text_input(
            "Scenario Name",
            value=st.session_state.current_inputs.name,
            help="Enter a descriptive name for this scenario"
        )
        
        if st.button("Save Scenario", type="primary"):
            st.session_state.current_inputs.name = scenario_name
            scenario_data = st.session_state.current_inputs.to_dict()
            filepath = save_scenario(scenario_data, scenario_name)
            st.success(f"✅ Saved: {scenario_name}")
            st.caption(f"File: {filepath}")
        
        st.markdown("---")
        
        # Quick save to comparison
        st.markdown("### ➕ Add to Comparison")
        
        if st.button("Add Current to Comparison"):
            comp_data = {
                'name': st.session_state.current_inputs.name,
                'inputs': st.session_state.current_inputs.to_dict(),
                'gross_revenue': outputs.revenue.gross_revenue,
                'noi': outputs.comp.noi,
                'contracts_per_week': outputs.funnel.contracts_per_week,
                'leads_per_week': outputs.funnel.leads_per_week
            }
            
            # Check if already exists
            existing_names = [s['name'] for s in st.session_state.comparison_scenarios]
            if comp_data['name'] in existing_names:
                st.warning("⚠️ Scenario with this name already in comparison")
            elif len(st.session_state.comparison_scenarios) >= 4:
                st.warning("⚠️ Maximum 4 scenarios for comparison")
            else:
                st.session_state.comparison_scenarios.append(comp_data)
                st.success(f"✅ Added '{comp_data['name']}' to comparison")
    
    with col_load:
        st.markdown("### 📂 Load Saved Scenario")
        
        saved = list_saved_scenarios()
        
        if saved:
            # Create selection options
            options = {f"{s['name']} ({s['modified'].strftime('%Y-%m-%d %H:%M')})": s 
                      for s in saved}
            
            selected_label = st.selectbox(
                "Select Scenario",
                options=list(options.keys())
            )
            
            if selected_label:
                selected = options[selected_label]
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("Load Scenario"):
                        loaded = load_scenario(selected['filepath'])
                        if loaded:
                            st.session_state.current_inputs = ScenarioInputs.from_dict(loaded)
                            st.success(f"✅ Loaded: {selected['name']}")
                            st.rerun()
                        else:
                            st.error("Failed to load scenario")
                
                with col_btn2:
                    if st.button("Delete Scenario", type="secondary"):
                        if delete_scenario(selected['filepath']):
                            st.success(f"🗑️ Deleted: {selected['name']}")
                            st.rerun()
                        else:
                            st.error("Failed to delete scenario")
        else:
            st.info("No saved scenarios yet. Save your first scenario above!")
        
        st.markdown("---")
        
        # Reset to defaults
        st.markdown("### 🔄 Reset to Defaults")
        
        if st.button("Load 2026 Base Plan"):
            default = create_default_scenario()
            st.session_state.current_inputs = ScenarioInputs.from_dict(default)
            st.success("✅ Reset to 2026 Base Plan defaults")
            st.rerun()

# ========== COMPARE TAB ==========
with tab_compare:
    st.markdown("### 🔄 Scenario Comparison")
    
    if len(st.session_state.comparison_scenarios) < 2:
        st.info("Add at least 2 scenarios to compare. Use 'Add to Comparison' on the Save/Load tab.")
        
        # Show what's currently in comparison
        if st.session_state.comparison_scenarios:
            st.markdown("**Currently in comparison:**")
            for s in st.session_state.comparison_scenarios:
                st.markdown(f"- {s['name']}")
    else:
        # Clear comparison button
        if st.button("Clear Comparison"):
            st.session_state.comparison_scenarios = []
            st.rerun()
        
        # Comparison chart
        comp_fig = create_scenario_comparison_chart(st.session_state.comparison_scenarios)
        if comp_fig:
            st.plotly_chart(comp_fig, use_container_width=True)
        
        # Comparison table
        st.markdown("### 📋 Detailed Comparison")
        
        comp_df_data = []
        for s in st.session_state.comparison_scenarios:
            comp_df_data.append({
                'Scenario': s['name'],
                'Gross Revenue': f"${s['gross_revenue']/1e6:.2f}M",
                'NOI': f"${s['noi']/1e6:.2f}M",
                'NOI Margin': f"{s['noi']/s['gross_revenue']*100:.0f}%" if s['gross_revenue'] > 0 else "N/A",
                'Contracts/Week': f"{s['contracts_per_week']:.1f}",
                'Leads/Week': f"{s['leads_per_week']:.0f}"
            })
        
        comp_df = pd.DataFrame(comp_df_data)
        st.dataframe(comp_df, hide_index=True, use_container_width=True)
        
        # Variance analysis
        if len(st.session_state.comparison_scenarios) >= 2:
            st.markdown("### 📊 Variance from First Scenario")
            
            base = st.session_state.comparison_scenarios[0]
            
            var_data = []
            for s in st.session_state.comparison_scenarios[1:]:
                var_data.append({
                    'Scenario': f"{s['name']} vs {base['name']}",
                    'Revenue Δ': f"${(s['gross_revenue'] - base['gross_revenue'])/1e6:+.2f}M",
                    'NOI Δ': f"${(s['noi'] - base['noi'])/1e6:+.2f}M",
                    'Contracts Δ': f"{s['contracts_per_week'] - base['contracts_per_week']:+.1f}",
                    'Leads Δ': f"{s['leads_per_week'] - base['leads_per_week']:+.0f}"
                })
            
            var_df = pd.DataFrame(var_data)
            st.dataframe(var_df, hide_index=True, use_container_width=True)

# ========== SENSITIVITY TAB ==========
with tab_sensitivity:
    st.markdown("### 📊 Sensitivity Analysis")
    st.markdown("How key metrics change when you adjust critical drivers")
    
    sens_tabs = st.tabs(["CPL Sensitivity", "Fallout Sensitivity", "Conversion Sensitivity"])
    
    with sens_tabs[0]:
        st.markdown("#### CPL Impact on Lead Volume & Required Conversion")
        
        cpl_values = st.multiselect(
            "CPL Values to Test ($)",
            options=[60, 80, 100, 120, 150, 180, 200, 250],
            default=[80, 100, 120, 150, 200]
        )
        
        if cpl_values:
            cpl_data = generate_sensitivity_cpl(inputs, sorted(cpl_values))
            cpl_df = pd.DataFrame(cpl_data)
            st.dataframe(cpl_df, hide_index=True, use_container_width=True)
            
            st.markdown("**Key Insight:** Higher CPL = fewer leads = higher required conversion rate")
    
    with sens_tabs[1]:
        st.markdown("#### Fallout Rate Impact on Required Contracts")
        
        fallout_values = st.multiselect(
            "Fallout Rates to Test (%)",
            options=[10, 15, 20, 25, 30, 35, 40],
            default=[10, 15, 20, 25, 30]
        )
        
        if fallout_values:
            fallout_data = generate_sensitivity_fallout(inputs, [v/100 for v in sorted(fallout_values)])
            fallout_df = pd.DataFrame(fallout_data)
            st.dataframe(fallout_df, hide_index=True, use_container_width=True)
            
            st.markdown("**Key Insight:** Higher fallout = more contracts needed = more leads required")
    
    with sens_tabs[2]:
        st.markdown("#### Required Leads/Spend at Different Conversion Rates")
        
        conv_values = st.multiselect(
            "Conversion Rates to Test (%)",
            options=[2, 3, 4, 5, 6, 7, 8, 10],
            default=[3, 4, 5, 6, 7, 8]
        )
        
        if conv_values:
            conv_data = generate_sensitivity_conversion(inputs, [v/100 for v in sorted(conv_values)])
            conv_df = pd.DataFrame(conv_data)
            st.dataframe(conv_df, hide_index=True, use_container_width=True)
            
            st.markdown("**Key Insight:** Lower conversion = more leads/spend required to hit targets")

# ========== EXPORT TAB ==========
with tab_export:
    st.markdown("### 📥 Export Data")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.markdown("#### Current Scenario")
        
        export_data = scenario_to_export(inputs, outputs)
        
        # CSV export
        csv_df = pd.DataFrame([export_data])
        csv = csv_df.to_csv(index=False)
        
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name=f"rei_scenario_{inputs.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # JSON export
        json_str = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label="📋 Download JSON",
            data=json_str,
            file_name=f"rei_scenario_{inputs.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
    
    with col_exp2:
        st.markdown("#### Full Inputs Export")
        
        full_inputs = inputs.to_dict()
        full_json = json.dumps(full_inputs, indent=2, default=str)
        
        st.download_button(
            label="📋 Download Full Inputs JSON",
            data=full_json,
            file_name=f"rei_full_inputs_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
        
        st.markdown("---")
        
        st.markdown("#### Load Inputs from JSON")
        
        uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
        
        if uploaded_file is not None:
            try:
                loaded_data = json.load(uploaded_file)
                
                if st.button("Apply Uploaded Inputs"):
                    st.session_state.current_inputs = ScenarioInputs.from_dict(loaded_data)
                    st.success("✅ Loaded inputs from uploaded file")
                    st.rerun()
            except json.JSONDecodeError:
                st.error("Invalid JSON file")
    
    st.markdown("---")
    
    # Comparison export
    if st.session_state.comparison_scenarios:
        st.markdown("#### Export Comparison Data")
        
        comp_export = []
        for s in st.session_state.comparison_scenarios:
            comp_export.append({
                'scenario_name': s['name'],
                'gross_revenue': s['gross_revenue'],
                'noi': s['noi'],
                'contracts_per_week': s['contracts_per_week'],
                'leads_per_week': s['leads_per_week']
            })
        
        comp_df = pd.DataFrame(comp_export)
        comp_csv = comp_df.to_csv(index=False)
        
        st.download_button(
            label="📄 Download Comparison CSV",
            data=comp_csv,
            file_name=f"rei_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Sidebar - current scenario summary
with st.sidebar:
    st.markdown("### 📊 Current Scenario")
    st.markdown(f"**{inputs.name}**")
    
    st.markdown("---")
    
    st.metric("Gross Revenue", f"${outputs.revenue.gross_revenue/1e6:.2f}M")
    st.metric("NOI", f"${outputs.comp.noi/1e6:.2f}M")
    st.metric("Contracts/Week", f"{outputs.funnel.contracts_per_week:.1f}")
    st.metric("Leads/Week", f"{outputs.funnel.leads_per_week:.0f}")
    st.metric("Conversion", f"{outputs.funnel.lead_to_contract_rate*100:.1f}%")
    
    st.markdown("---")
    
    st.markdown("### 📋 In Comparison")
    if st.session_state.comparison_scenarios:
        for s in st.session_state.comparison_scenarios:
            st.markdown(f"• {s['name']}")
    else:
        st.caption("No scenarios in comparison")
