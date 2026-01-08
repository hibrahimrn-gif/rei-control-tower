"""
REI Nationwide LLC - Wholesale-Only 12-Month Projection Model
100% Wholesaling Strategy - No Rentals, No Rehabs, No Slow Money

CFO/FP&A Dashboard with:
- 12-month cash flow projections
- Investor tranche payback tracking
- Scenario analysis (Base, Conservative, Aggressive)
- Investor equity distribution modeling
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add components to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.wholesale_projection import (
    WholesaleInputs,
    calculate_monthly_projections,
    calculate_scenario_summary,
    generate_scenario_comparison,
    calculate_investor_distributions,
    generate_csv_export,
    format_currency,
    get_risk_analysis,
    calculate_pod_scaling_schedule
)

st.set_page_config(
    page_title="Wholesale Projection Model",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .big-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4ade80;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #2d4a6f;
    }
    .risk-card {
        background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%);
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .formula-box {
        background: #1e293b;
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.title("📈 Wholesale-Only 12-Month Projection Model")
    st.markdown("*CFO Dashboard: Cash Flow, Investor Payback, Scenario Analysis*")

    st.markdown("---")

    # Sidebar for inputs
    with st.sidebar:
        st.header("Model Inputs")

        st.subheader("Unit Economics")
        cac = st.number_input("CAC ($/deal)", value=3500, step=100, format="%d")
        avg_fee = st.number_input("Avg Assignment Fee ($)", value=20000, step=1000, format="%d")
        lead_to_close = st.number_input("Lead-to-Close (days)", value=24, step=1, format="%d")

        st.subheader("Monthly Marketing Ladder")
        m1 = st.number_input("Month 1", value=50000, step=10000, format="%d")
        m2 = st.number_input("Month 2", value=300000, step=10000, format="%d")
        m3 = st.number_input("Month 3", value=600000, step=10000, format="%d")
        m4 = st.number_input("Month 4", value=900000, step=10000, format="%d")
        m5_12 = st.number_input("Months 5-12 (each)", value=1200000, step=50000, format="%d")

        marketing_ladder = [m1, m2, m3, m4] + [m5_12] * 8

        st.subheader("Model Settings")
        use_lag = st.checkbox("Use Lagged Model (24-day close)", value=True)
        business_days = st.number_input("Business Days/Month", value=22, step=1)

        st.subheader("Pod System")
        pod_capacity = st.number_input("Files per Pod", value=50, step=5, format="%d")
        pod_annual_cost = st.number_input("Pod Annual Cost ($)", value=50000, step=5000, format="%d")
        buyers_daily = st.number_input("Buyers Added/Day (nationwide)", value=300, step=25, format="%d")
        buyers_per_pod = st.number_input("Buyers/Pod/Day", value=100, step=10, format="%d")

    # Create custom inputs
    custom_inputs = WholesaleInputs(
        cac=cac,
        avg_assignment_fee=avg_fee,
        lead_to_close_days=lead_to_close,
        marketing_ladder=marketing_ladder,
        business_days_per_month=business_days,
        pod_capacity=pod_capacity,
        pod_annual_cost=pod_annual_cost,
        buyers_added_daily=buyers_daily,
        buyers_per_pod_daily=buyers_per_pod,
        scenario_name="Custom"
    )

    # Generate all scenarios
    scenarios = generate_scenario_comparison()

    # Override base with custom inputs
    custom_projections = calculate_monthly_projections(custom_inputs, use_lag_model=use_lag)
    custom_summary = calculate_scenario_summary(custom_projections, custom_inputs)

    # ==================== SECTION 1: KEY METRICS ====================
    st.header("1. Key Metrics (12-Month Totals)")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Marketing Spend",
            format_currency(custom_summary.total_marketing_spend),
            help="Total capital deployed across 12 months"
        )

    with col2:
        st.metric(
            "Total Deals Closed",
            f"{custom_summary.total_deals_closed:,}",
            help="Rounded deal count (lagged model)"
        )

    with col3:
        st.metric(
            "Gross Revenue",
            format_currency(custom_summary.total_gross_revenue),
            help="Total assignment fees collected"
        )

    with col4:
        st.metric(
            "Net Profit",
            format_currency(custom_summary.total_net_profit),
            help="Revenue minus marketing spend"
        )

    with col5:
        st.metric(
            "ROI Multiple",
            f"{custom_summary.roi_multiple:.1f}x",
            help="Net Profit / Marketing Spend"
        )

    # Pod System Metrics Row
    st.markdown("###")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)

    with col_p1:
        st.metric(
            "Max Pods Needed",
            f"{custom_summary.max_pods_needed}",
            help="Peak pod count at steady state"
        )

    with col_p2:
        st.metric(
            "Pod Overhead (12mo)",
            format_currency(custom_summary.total_pod_overhead),
            help="Total pod costs (investor covers)"
        )

    with col_p3:
        st.metric(
            "Total Investor Outlay",
            format_currency(custom_summary.total_investor_outlay),
            help="Marketing + Pod Overhead"
        )

    with col_p4:
        st.metric(
            "Avg Buyers/Deal",
            f"{custom_summary.avg_buyer_coverage_ratio:.0f}x",
            help="Buyer pipeline coverage ratio"
        )

    st.markdown("---")

    # ==================== SECTION 2: 12-MONTH TABLE ====================
    st.header("2. Base Case: 12-Month Projection (Lagged Model)")

    # Model assumptions box
    st.info(f"""
    **Assumptions:**
    - CAC: ${cac:,} | Avg Fee: ${avg_fee:,}
    - Lag: 20% of deals close in the month generated; 80% close in the following month
    - Principal Payback: 100% of marketing capital is repaid from Gross Revenue before profit distribution
    - Rounding: Deals are rounded to the nearest whole number for financial calculations
    """)

    # Create DataFrame for display
    df_data = []
    for p in custom_projections:
        df_data.append({
            "Month": p.month,
            "Marketing Spend": f"${p.marketing_spend:,.0f}",
            "Deals Closed": p.deals_closed_rounded,
            "Closings/Day": f"{p.closings_per_day:.1f}",
            "Gross Revenue": f"${p.gross_revenue:,.0f}",
            "Net Profit": f"${p.net_profit:,.0f}",
            "Cumulative Profit": f"${p.cumulative_net_profit:,.0f}",
            "Pods": p.pods_needed,
            "Buyers Added": f"{p.buyers_added_monthly:,}",
            "Buyers/Deal": f"{p.buyer_coverage_ratio:.0f}x"
        })

    # Add totals row
    df_data.append({
        "Month": "TOTAL",
        "Marketing Spend": format_currency(sum(p.marketing_spend for p in custom_projections)),
        "Deals Closed": sum(p.deals_closed_rounded for p in custom_projections),
        "Closings/Day": "N/A",
        "Gross Revenue": format_currency(sum(p.gross_revenue for p in custom_projections)),
        "Net Profit": format_currency(sum(p.net_profit for p in custom_projections)),
        "Cumulative Profit": format_currency(custom_projections[-1].cumulative_net_profit),
        "Pods": f"MAX: {custom_summary.max_pods_needed}",
        "Buyers Added": f"{custom_summary.total_buyers_added:,}",
        "Buyers/Deal": f"AVG: {custom_summary.avg_buyer_coverage_ratio:.0f}x"
    })

    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Visualization: Monthly profit chart
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Monthly Net Profit", "Cumulative Cash Position"),
        vertical_spacing=0.15
    )

    months = [p.month for p in custom_projections]
    net_profits = [p.net_profit for p in custom_projections]
    cumulative = [p.cumulative_net_profit for p in custom_projections]
    marketing = [p.marketing_spend for p in custom_projections]

    # Monthly Net Profit bars
    fig.add_trace(
        go.Bar(
            x=months,
            y=net_profits,
            name="Net Profit",
            marker_color="#4ade80"
        ),
        row=1, col=1
    )

    # Marketing spend line
    fig.add_trace(
        go.Scatter(
            x=months,
            y=marketing,
            name="Marketing Spend",
            mode="lines+markers",
            line=dict(color="#ef4444", dash="dash")
        ),
        row=1, col=1
    )

    # Cumulative cash
    fig.add_trace(
        go.Scatter(
            x=months,
            y=cumulative,
            name="Cumulative Cash",
            fill="tozeroy",
            fillcolor="rgba(59, 130, 246, 0.3)",
            line=dict(color="#3b82f6", width=3)
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        template="plotly_dark"
    )
    fig.update_xaxes(title_text="Month", row=2, col=1)
    fig.update_yaxes(title_text="$", tickformat=",.0f")

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== SECTION 3: CSV EXPORT ====================
    st.header("3. CSV Export (Google Sheets Ready)")

    csv_content = generate_csv_export(custom_projections)

    st.code(csv_content, language="csv")

    st.download_button(
        label="Download CSV",
        data=csv_content,
        file_name="wholesale_projection_base_case.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # ==================== SECTION 4: SCENARIO COMPARISON ====================
    st.header("4. Scenario Analysis (12-Month Totals)")

    st.markdown("""
    | Scenario | CAC | Assignment Fee | Fallout |
    |----------|-----|----------------|---------|
    | **Base** | $3,500 | $20,000 | 0% |
    | **Conservative** | $4,375 (+25%) | $17,000 (-15%) | 10% |
    | **Aggressive** | $3,150 (-10%) | $22,000 (+10%) | 0% |
    """)

    # Build comparison table
    comparison_data = []
    for key in ["conservative", "base", "aggressive"]:
        _, _, summary = scenarios[key]
        comparison_data.append({
            "Scenario": summary.scenario_name,
            "Total Spend": format_currency(summary.total_marketing_spend),
            "Deals Generated": f"{summary.total_deals_generated:,}",
            "Deals Closed": f"{summary.total_deals_closed:,}",
            "Total Revenue": format_currency(summary.total_gross_revenue),
            "Net Profit": format_currency(summary.total_net_profit),
            "ROI": f"{summary.roi_multiple:.1f}x"
        })

    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # Scenario comparison chart
    scenario_names = [d["Scenario"] for d in comparison_data]
    scenario_profits = [scenarios[k][2].total_net_profit for k in ["conservative", "base", "aggressive"]]
    scenario_revenues = [scenarios[k][2].total_gross_revenue for k in ["conservative", "base", "aggressive"]]

    fig_compare = go.Figure()

    fig_compare.add_trace(go.Bar(
        name="Gross Revenue",
        x=scenario_names,
        y=scenario_revenues,
        marker_color="#3b82f6"
    ))

    fig_compare.add_trace(go.Bar(
        name="Net Profit",
        x=scenario_names,
        y=scenario_profits,
        marker_color="#4ade80"
    ))

    fig_compare.update_layout(
        barmode="group",
        title="Scenario Comparison: Revenue vs Profit",
        yaxis_title="$ Amount",
        yaxis_tickformat=",.0f",
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(fig_compare, use_container_width=True)

    st.markdown("---")

    # ==================== SECTION 5: INVESTOR EQUITY MODEL ====================
    st.header("5. Investor Equity Return Model")

    st.markdown("""
    **Context:** Investor covers overhead for 12 months in exchange for equity.
    Their cash return comes from a share of Net Profit (post-principal payback).
    """)

    # Formula box
    st.markdown("""
    <div class="formula-box">
    <strong>Investor Distribution Formula:</strong><br><br>
    <code>Investor Distribution = Net Profit * Equity % (E) * Distribution % (D)</code><br><br>
    Where:<br>
    - <strong>Net Profit (N)</strong> = Total profit after marketing capital payback<br>
    - <strong>Equity % (E)</strong> = Investor's ownership stake (e.g., 10%, 20%, 30%)<br>
    - <strong>Distribution % (D)</strong> = Portion of profit distributed vs. reinvested (0%, 50%, 100%)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("###")

    # Calculate distribution matrix
    net_profit = custom_summary.total_net_profit
    distributions = calculate_investor_distributions(net_profit)

    st.subheader(f"Distribution Matrix (Based on ${net_profit:,.0f} Net Profit)")

    # Create matrix table
    matrix_data = []
    for equity_pct in ["10%", "20%", "30%"]:
        row = {"Equity Stake": equity_pct}
        for dist_pct in ["0%", "50%", "100%"]:
            amount = distributions[equity_pct][dist_pct]
            row[f"Distribute {dist_pct}"] = format_currency(amount)
        matrix_data.append(row)

    matrix_df = pd.DataFrame(matrix_data)
    st.dataframe(matrix_df, use_container_width=True, hide_index=True)

    st.caption("""
    **Reading the table:**
    - Row = Investor's equity stake
    - Column = How much profit is distributed (vs. reinvested)
    - Cell = Cash paid to investor over 12 months
    """)

    st.markdown("---")

    # ==================== SECTION 6: POD SCALING SCHEDULE ====================
    st.header("6. Pod System Scaling Schedule")

    pod_schedule = calculate_pod_scaling_schedule(custom_projections)

    pod_df_data = []
    for ps in pod_schedule:
        pod_df_data.append({
            "Month": ps["month"],
            "Deals Closed": ps["deals_closed"],
            "Pods Needed": ps["pods_needed"],
            "Pods to Hire": ps["pods_to_hire"] if ps["pods_to_hire"] > 0 else "-",
            "Monthly Pod Cost": f"${ps['monthly_pod_cost']:,.0f}",
            "Buyers Added": f"{ps['buyers_added']:,}",
            "Buyer/Deal": f"{ps['buyer_per_deal_ratio']:.0f}x"
        })

    pod_df = pd.DataFrame(pod_df_data)
    st.dataframe(pod_df, use_container_width=True, hide_index=True)

    # Pod scaling visualization
    fig_pods = go.Figure()

    fig_pods.add_trace(go.Bar(
        x=[p["month"] for p in pod_schedule],
        y=[p["pods_needed"] for p in pod_schedule],
        name="Pods Needed",
        marker_color="#3b82f6"
    ))

    fig_pods.add_trace(go.Scatter(
        x=[p["month"] for p in pod_schedule],
        y=[p["deals_closed"] for p in pod_schedule],
        name="Deals Closed",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="#4ade80", width=3)
    ))

    fig_pods.update_layout(
        title="Pod Scaling vs Deal Volume",
        xaxis_title="Month",
        yaxis=dict(title="Pods", side="left"),
        yaxis2=dict(title="Deals", side="right", overlaying="y"),
        template="plotly_dark",
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )

    st.plotly_chart(fig_pods, use_container_width=True)

    st.markdown("---")

    # ==================== SECTION 7: RISK ANALYSIS ====================
    st.header("7. CFO Risk Analysis & Key Takeaways")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Key Takeaways")

        st.success(f"""
        **Cash Efficiency**: Model is self-liquidating from Month 1.
        Revenue (${custom_projections[0].gross_revenue:,}) covers principal (${custom_projections[0].marketing_spend:,}) immediately.
        """)

        st.info(f"""
        **Volume at Scale**: By Month 6, you're closing **{custom_projections[5].deals_closed_rounded} deals/month**.
        That's **{custom_projections[5].closings_per_day:.1f} closings per business day** with **{custom_projections[5].pods_needed} pods**.
        """)

        st.success(f"""
        **Buyer Pipeline**: {custom_summary.avg_buyer_coverage_ratio:.0f}x buyer coverage.
        300+ buyers/day nationwide = **{custom_summary.total_buyers_added:,} total buyers** over 12 months.
        """)

        st.success(f"""
        **Profitability**: {custom_summary.roi_multiple:.1f}x ROI on marketing spend.
        ${custom_summary.total_net_profit/1e6:.1f}M net profit on ${custom_summary.total_marketing_spend/1e6:.1f}M deployed.
        """)

    with col_right:
        st.subheader("Risk Status (with Pod System)")

        risks = get_risk_analysis(with_pod_system=True)

        for risk in risks:
            status = risk.get('status', 'yellow')
            if status == 'green':
                icon = '✅'
                card_style = 'background: linear-gradient(135deg, #14532d 0%, #052e16 100%); border-left: 4px solid #22c55e;'
            elif status == 'yellow':
                icon = '⚠️'
                card_style = 'background: linear-gradient(135deg, #78350f 0%, #451a03 100%); border-left: 4px solid #f59e0b;'
            else:
                icon = '🔴'
                card_style = 'background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); border-left: 4px solid #ef4444;'

            st.markdown(f"""
            <div style="{card_style} padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;">
                <strong>{icon} {risk['category']}</strong><br>
                <span style="font-size: 0.9em;">{risk['description']}</span><br>
                <em style="color: #94a3b8; font-size: 0.85em;">{risk['mitigation']}</em>
            </div>
            """, unsafe_allow_html=True)

    # Updated operational summary
    st.success(f"""
    **Operational Summary (Pod System Active):**

    At steady state (Months 6-12):
    - **{custom_projections[5].deals_closed_rounded} deals/month** handled by **{custom_projections[5].pods_needed} pods** (50 files each)
    - **{custom_projections[5].buyers_added_monthly:,} buyers added/month** = {custom_projections[5].buyer_coverage_ratio:.0f}x coverage per deal
    - Pod overhead: **${custom_projections[5].pod_monthly_cost:,.0f}/month** (investor covers)
    - Total investor commitment: **${custom_summary.total_investor_outlay/1e6:.1f}M** (marketing + pods)

    ✅ **Dispo bottleneck SOLVED** with pod system + nationwide buyer acquisition.
    """)

    st.markdown("---")

    # ==================== SECTION 8: NO-LAG COMPARISON ====================
    st.header("8. Model Comparison: Lagged vs No-Lag")

    no_lag_projections = calculate_monthly_projections(custom_inputs, use_lag_model=False)
    no_lag_summary = calculate_scenario_summary(no_lag_projections, custom_inputs)

    comparison_models = pd.DataFrame([
        {
            "Model": "No-Lag (Optimistic)",
            "Total Deals Closed": no_lag_summary.total_deals_closed,
            "Total Revenue": format_currency(no_lag_summary.total_gross_revenue),
            "Net Profit": format_currency(no_lag_summary.total_net_profit),
            "ROI": f"{no_lag_summary.roi_multiple:.1f}x"
        },
        {
            "Model": "Lagged (Realistic)",
            "Total Deals Closed": custom_summary.total_deals_closed,
            "Total Revenue": format_currency(custom_summary.total_gross_revenue),
            "Net Profit": format_currency(custom_summary.total_net_profit),
            "ROI": f"{custom_summary.roi_multiple:.1f}x"
        }
    ])

    st.dataframe(comparison_models, use_container_width=True, hide_index=True)

    st.caption("""
    **Note:** The lagged model accounts for the 24-day average close time by assuming
    20% of deals close same-month and 80% roll to the following month. This creates
    a more realistic cash flow projection, especially in the ramp-up months.
    """)


if __name__ == "__main__":
    main()
