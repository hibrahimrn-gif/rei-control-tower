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
    get_risk_analysis
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

    # Create custom inputs
    custom_inputs = WholesaleInputs(
        cac=cac,
        avg_assignment_fee=avg_fee,
        lead_to_close_days=lead_to_close,
        marketing_ladder=marketing_ladder,
        business_days_per_month=business_days,
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
            "Deals Gen.": p.deals_generated_rounded,
            "Deals Closed": p.deals_closed_rounded,
            "Closings/Day": f"{p.closings_per_day:.1f}",
            "Gross Revenue": f"${p.gross_revenue:,.0f}",
            "Principal Payback": f"${p.principal_payback_due:,.0f}",
            "Net Profit": f"${p.net_profit:,.0f}",
            "Cumulative Profit": f"${p.cumulative_net_profit:,.0f}"
        })

    # Add totals row
    df_data.append({
        "Month": "TOTAL",
        "Marketing Spend": format_currency(sum(p.marketing_spend for p in custom_projections)),
        "Deals Gen.": sum(p.deals_generated_rounded for p in custom_projections),
        "Deals Closed": sum(p.deals_closed_rounded for p in custom_projections),
        "Closings/Day": "N/A",
        "Gross Revenue": format_currency(sum(p.gross_revenue for p in custom_projections)),
        "Principal Payback": format_currency(sum(p.principal_payback_due for p in custom_projections)),
        "Net Profit": format_currency(sum(p.net_profit for p in custom_projections)),
        "Cumulative Profit": format_currency(custom_projections[-1].cumulative_net_profit)
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

    # ==================== SECTION 6: RISK ANALYSIS ====================
    st.header("6. CFO Risk Analysis & Key Takeaways")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Key Takeaways")

        st.success(f"""
        **Cash Efficiency**: Model is self-liquidating from Month 1.
        Revenue (${custom_projections[0].gross_revenue:,}) covers principal (${custom_projections[0].marketing_spend:,}) immediately.
        """)

        st.info(f"""
        **Volume at Scale**: By Month 6, you're closing **{custom_projections[5].deals_closed_rounded} deals/month**.
        That's **{custom_projections[5].closings_per_day:.1f} closings per business day**.
        This is factory-scale wholesaling.
        """)

        st.success(f"""
        **Profitability**: {custom_summary.roi_multiple:.1f}x ROI on marketing spend.
        ${custom_summary.total_net_profit/1e6:.1f}M net profit on ${custom_summary.total_marketing_spend/1e6:.1f}M deployed.
        """)

    with col_right:
        st.subheader("Critical Risks")

        risks = get_risk_analysis()

        for risk in risks[:3]:  # Top 3 risks
            st.markdown(f"""
            <div class="risk-card">
                <strong>🔴 {risk['category']}</strong><br>
                {risk['description']}<br>
                <em style="color: #94a3b8;">Mitigation: {risk['mitigation']}</em>
            </div>
            """, unsafe_allow_html=True)

    # Operational capacity warning
    st.warning(f"""
    **Operational Reality Check:**

    At steady state (Months 6-12), you need:
    - **{custom_projections[5].deals_closed_rounded} closed deals/month** = {custom_projections[5].closings_per_day:.1f}/day
    - This requires a **massive dispo operation** (selling {custom_projections[5].deals_closed_rounded} contracts/month)
    - Typical dispo rep handles 20-30 deals/month = **{max(1, round(custom_projections[5].deals_closed_rounded / 25))} dispo reps needed**
    - Buyer list must absorb {custom_projections[5].deals_closed_rounded * 12:,} deals/year

    The math works. The physics is the challenge.
    """)

    st.markdown("---")

    # ==================== SECTION 7: NO-LAG COMPARISON ====================
    st.header("7. Model Comparison: Lagged vs No-Lag")

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
