"""
REI Nationwide LLC - Deal Comparison Tool
Side-by-side comparison of multiple deals
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# Add components to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="Deal Comparison - REI Nationwide",
    page_icon="⚖️",
    layout="wide"
)


def calculate_deal_metrics(inputs: dict) -> dict:
    """Calculate all metrics for a deal"""
    arv = inputs.get('arv', 0)
    purchase_price = inputs.get('purchase_price', 0)
    rehab_budget = inputs.get('rehab_budget', 0)
    estimated_rent = inputs.get('estimated_rent', 0)
    holding_months = inputs.get('holding_months', 2.0)

    # Purchase % ARV
    purchase_pct_arv = purchase_price / arv if arv > 0 else 0

    # Holding costs
    holding_costs = (purchase_price * 0.01 * holding_months) + ((150 + 100) * holding_months)

    # Closing costs
    closing_costs_buy = purchase_price * 0.03

    # All-in cost
    all_in_cost = purchase_price + rehab_budget + holding_costs + closing_costs_buy

    # DSCR
    loan_amount = all_in_cost * 0.80
    monthly_rate = 0.07 / 12
    n_payments = 360
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / \
                     ((1 + monthly_rate)**n_payments - 1) if loan_amount > 0 else 0

    annual_taxes = purchase_price * 0.015
    monthly_taxes = annual_taxes / 12
    monthly_insurance = 100

    piti = monthly_payment + monthly_taxes + monthly_insurance
    dscr = estimated_rent / piti if piti > 0 else 0

    # Net cashflow
    pm_fee = estimated_rent * 0.10
    net_cashflow = estimated_rent - piti - pm_fee

    # Wholesale fee
    wholesale_fee = (arv * 0.70) - purchase_price - 5000

    # ROI
    annual_net_income = net_cashflow * 12
    roi_pct = (annual_net_income / all_in_cost) * 100 if all_in_cost > 0 else 0

    # Scoring
    if purchase_pct_arv <= 0.45 and rehab_budget <= 20000 and net_cashflow >= 175:
        deal_score = "GREEN"
        recommended_exit = "Internal DSCR"
    elif purchase_pct_arv <= 0.60 and rehab_budget <= 30000 and wholesale_fee >= 25000:
        deal_score = "YELLOW"
        recommended_exit = "Wholesale"
    else:
        deal_score = "RED"
        recommended_exit = "Reject"

    return {
        'purchase_pct_arv': purchase_pct_arv,
        'all_in_cost': all_in_cost,
        'holding_costs': holding_costs,
        'closing_costs_buy': closing_costs_buy,
        'dscr': dscr,
        'piti': piti,
        'net_cashflow': net_cashflow,
        'wholesale_fee': wholesale_fee,
        'roi_pct': roi_pct,
        'deal_score': deal_score,
        'recommended_exit': recommended_exit
    }


def create_comparison_chart(deals_data: list) -> go.Figure:
    """Create comparison bar chart"""
    metrics = ['Purchase % ARV', 'DSCR', 'Net Cashflow', 'Wholesale Fee']

    fig = go.Figure()

    for i, deal in enumerate(deals_data):
        name = deal['name']
        calc = deal['calculations']

        values = [
            calc['purchase_pct_arv'] * 100,  # Convert to percentage
            calc['dscr'],
            calc['net_cashflow'],
            calc['wholesale_fee'] / 1000  # Convert to thousands
        ]

        fig.add_trace(go.Bar(
            name=name,
            x=metrics,
            y=values,
            text=[f"{v:.1f}" for v in values],
            textposition='auto',
        ))

    fig.update_layout(
        title="Key Metrics Comparison",
        barmode='group',
        height=400,
        xaxis_title="Metric",
        yaxis_title="Value",
        template="plotly_white"
    )

    return fig


def main():
    """Main deal comparison page"""

    st.title("⚖️ Deal Comparison Tool")
    st.markdown("*Side-by-side comparison of multiple investment deals*")

    st.markdown("---")

    # Initialize session state for deals
    if 'comparison_deals' not in st.session_state:
        st.session_state.comparison_deals = []

    # Number of deals to compare
    st.markdown("### 📊 Select Number of Deals to Compare")

    num_deals = st.slider("Number of deals", min_value=2, max_value=5, value=2)

    st.markdown("---")

    # Input forms for each deal
    deals_data = []

    cols = st.columns(num_deals)

    for i in range(num_deals):
        with cols[i]:
            st.markdown(f"### Deal {i+1}")

            deal_name = st.text_input(
                "Deal Name",
                value=f"Deal {chr(65+i)}",  # A, B, C, etc.
                key=f"name_{i}"
            )

            address = st.text_input(
                "Address",
                placeholder="123 Main St",
                key=f"address_{i}"
            )

            arv = st.number_input(
                "ARV",
                min_value=0,
                value=180000,
                step=5000,
                key=f"arv_{i}"
            )

            purchase_price = st.number_input(
                "Purchase Price",
                min_value=0,
                value=75000,
                step=1000,
                key=f"purchase_{i}"
            )

            rehab_budget = st.number_input(
                "Rehab Budget",
                min_value=0,
                value=12000,
                step=1000,
                key=f"rehab_{i}"
            )

            estimated_rent = st.number_input(
                "Estimated Rent",
                min_value=0,
                value=1400,
                step=50,
                key=f"rent_{i}"
            )

            holding_months = st.number_input(
                "Holding Months",
                min_value=0.5,
                max_value=12.0,
                value=2.0,
                step=0.5,
                key=f"holding_{i}"
            )

            # Calculate metrics
            inputs = {
                'arv': arv,
                'purchase_price': purchase_price,
                'rehab_budget': rehab_budget,
                'estimated_rent': estimated_rent,
                'holding_months': holding_months
            }

            calculations = calculate_deal_metrics(inputs)

            deals_data.append({
                'name': deal_name,
                'address': address,
                'inputs': inputs,
                'calculations': calculations
            })

            # Display score
            score_colors = {
                'GREEN': '#10b981',
                'YELLOW': '#f59e0b',
                'RED': '#ef4444'
            }

            score = calculations['deal_score']
            color = score_colors.get(score, '#6b7280')

            st.markdown(f"""
            <div style="background: {color}; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: 700; margin-top: 10px;">
                {score}
            </div>
            """, unsafe_allow_html=True)

    # Comparison section
    st.markdown("---")
    st.markdown("### 📊 Comparison Results")

    # Create comparison table
    comparison_data = {
        'Metric': [
            'Address',
            'ARV',
            'Purchase Price',
            'Purchase % ARV',
            'Rehab Budget',
            'All-In Cost',
            'DSCR',
            'Net Cashflow/Month',
            'Wholesale Fee',
            'Annual ROI %',
            'Deal Score',
            'Recommended Exit'
        ]
    }

    for deal in deals_data:
        calc = deal['calculations']
        inputs = deal['inputs']

        comparison_data[deal['name']] = [
            deal['address'],
            f"${inputs['arv']:,.0f}",
            f"${inputs['purchase_price']:,.0f}",
            f"{calc['purchase_pct_arv']*100:.1f}%",
            f"${inputs['rehab_budget']:,.0f}",
            f"${calc['all_in_cost']:,.0f}",
            f"{calc['dscr']:.2f}",
            f"${calc['net_cashflow']:,.0f}",
            f"${calc['wholesale_fee']:,.0f}",
            f"{calc['roi_pct']:.1f}%",
            calc['deal_score'],
            calc['recommended_exit']
        ]

    df = pd.DataFrame(comparison_data)

    # Highlight best values
    def highlight_best(row):
        if row.name == 0:  # Address row
            return [''] * len(row)

        # Extract numeric values where possible
        try:
            values = []
            for val in row[1:]:  # Skip 'Metric' column
                if isinstance(val, str):
                    # Remove $ and , and %
                    clean_val = val.replace('$', '').replace(',', '').replace('%', '')
                    try:
                        values.append(float(clean_val))
                    except:
                        values.append(None)
                else:
                    values.append(val)

            # Find best value based on metric
            metric = row['Metric']

            if metric in ['Purchase % ARV', 'All-In Cost', 'Rehab Budget']:
                # Lower is better
                if all(v is not None for v in values):
                    best_idx = values.index(min(values))
                else:
                    best_idx = None
            elif metric in ['DSCR', 'Net Cashflow/Month', 'Wholesale Fee', 'Annual ROI %']:
                # Higher is better
                if all(v is not None for v in values):
                    best_idx = values.index(max(values))
                else:
                    best_idx = None
            else:
                best_idx = None

            # Apply highlighting
            styles = [''] * len(row)
            if best_idx is not None:
                styles[best_idx + 1] = 'background-color: rgba(16, 185, 129, 0.2); font-weight: 700'

            return styles

        except:
            return [''] * len(row)

    st.dataframe(
        df.style.apply(highlight_best, axis=1),
        hide_index=True,
        use_container_width=True
    )

    # Comparison chart
    st.markdown("---")
    st.markdown("### 📈 Visual Comparison")

    fig = create_comparison_chart(deals_data)
    st.plotly_chart(fig, use_container_width=True)

    # Winner recommendation
    st.markdown("---")
    st.markdown("### 🏆 Best Deal Recommendation")

    # Score priority: GREEN > YELLOW > RED
    green_deals = [d for d in deals_data if d['calculations']['deal_score'] == 'GREEN']

    if green_deals:
        # Among green deals, choose highest DSCR
        best_deal = max(green_deals, key=lambda x: x['calculations']['dscr'])
        st.success(f"✅ **Best Deal: {best_deal['name']}** ({best_deal['address']})")
        st.markdown(f"""
        **Reason:** 🟢 GREEN deal with highest DSCR ({best_deal['calculations']['dscr']:.2f})

        **Recommended Action:** Route to Internal DSCR → M Capital → Rehab → Long-term hold

        **Expected Outcome:** ${best_deal['calculations']['net_cashflow']:,.0f}/month net cashflow
        """)
    else:
        yellow_deals = [d for d in deals_data if d['calculations']['deal_score'] == 'YELLOW']
        if yellow_deals:
            # Among yellow deals, choose highest wholesale fee
            best_deal = max(yellow_deals, key=lambda x: x['calculations']['wholesale_fee'])
            st.warning(f"⚠️ **Best Deal: {best_deal['name']}** ({best_deal['address']})")
            st.markdown(f"""
            **Reason:** 🟡 YELLOW deal with highest wholesale fee (${best_deal['calculations']['wholesale_fee']:,.0f})

            **Recommended Action:** Route to Wholesale

            **Expected Outcome:** ${best_deal['calculations']['wholesale_fee']:,.0f} assignment fee
            """)
        else:
            st.error("❌ No viable deals found. All deals are RED (Reject).")

    # Export comparison
    st.markdown("---")
    st.markdown("### 💾 Export Comparison")

    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📄 Download Comparison (CSV)",
        data=csv_data,
        file_name=f"deal_comparison_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )


if __name__ == "__main__":
    main()
