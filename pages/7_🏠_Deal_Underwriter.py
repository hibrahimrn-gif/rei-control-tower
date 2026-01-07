"""
REI Nationwide LLC - Deal Underwriter
Individual property underwriting calculator with routing recommendations
"""

import streamlit as st
import json
import sys
from pathlib import Path

# Add components to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="Deal Underwriter - REI Nationwide",
    page_icon="🏠",
    layout="wide"
)

# Load underwriting configuration
@st.cache_data
def load_underwriting_config():
    """Load underwriting configuration from JSON"""
    config_path = Path(__file__).parent.parent / "data" / "underwriting_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

config = load_underwriting_config()

# Custom CSS
st.markdown("""
<style>
    .deal-card {
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    .green-deal {
        background: linear-gradient(135deg, #065f46 0%, #064e3b 100%);
        border: 2px solid #10b981;
    }

    .yellow-deal {
        background: linear-gradient(135deg, #78350f 0%, #451a03 100%);
        border: 2px solid #f59e0b;
    }

    .red-deal {
        background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%);
        border: 2px solid #ef4444;
    }

    .score-badge {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .metric-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #374151;
    }

    .metric-label {
        color: #9ca3af;
        font-size: 0.9rem;
    }

    .metric-value {
        color: #e5e7eb;
        font-weight: 600;
    }

    .recommendation-box {
        background: #1e3a8a;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def calculate_underwriting(inputs: dict) -> dict:
    """
    Calculate all underwriting metrics based on inputs
    Returns dict with all calculated values and routing decision
    """
    # Extract inputs
    arv = inputs['arv']
    purchase_price = inputs['purchase_price']
    rehab_budget = inputs['rehab_budget']
    estimated_rent = inputs['estimated_rent']
    holding_months = inputs['holding_months']
    sqft = inputs.get('sqft', 1200)

    # 1. Purchase % ARV
    purchase_pct_arv = purchase_price / arv if arv > 0 else 0

    # 2. Holding Costs
    monthly_holding_rate = 0.01
    utilities_per_month = 150
    insurance_per_month = 100
    holding_costs = (purchase_price * monthly_holding_rate * holding_months) + \
                    ((utilities_per_month + insurance_per_month) * holding_months)

    # 3. Closing Costs
    closing_costs_buy = purchase_price * 0.03
    closing_costs_sell = arv * 0.01

    # 4. All-In Cost
    all_in_cost = purchase_price + rehab_budget + holding_costs + closing_costs_buy

    # 5. Gross Profit (if we sold at ARV)
    gross_profit = arv - all_in_cost - closing_costs_sell

    # 6. DSCR Calculation (simplified - assumes 80% LTV at 7% rate, 1.5% tax, $800/yr ins)
    # More accurate would pull from M Capital's actual loan terms
    loan_amount = all_in_cost * 0.80
    monthly_rate = 0.07 / 12
    n_payments = 360  # 30-year
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / \
                     ((1 + monthly_rate)**n_payments - 1) if loan_amount > 0 else 0

    annual_taxes = purchase_price * 0.015
    monthly_taxes = annual_taxes / 12
    monthly_insurance = 100

    piti = monthly_payment + monthly_taxes + monthly_insurance
    dscr = estimated_rent / piti if piti > 0 else 0

    # 7. Net Cashflow
    pm_fee_rate = 0.10
    pm_fee = estimated_rent * pm_fee_rate
    net_cashflow = estimated_rent - piti - pm_fee

    # 8. Wholesale Fee Potential
    wholesale_price = arv * 0.70
    wholesale_fee = wholesale_price - purchase_price - 5000  # $5k buffer

    # 9. Rehab $/sqft
    rehab_psf = rehab_budget / sqft if sqft > 0 else 0

    # 10. DECISION TREE LOGIC
    score = "RED"
    recommended_exit = "REJECT - Archive"
    reason = ""
    color_class = "red-deal"

    # GREEN: Route to Internal DSCR
    if purchase_pct_arv <= 0.45 and rehab_budget <= 20000 and net_cashflow >= 175:
        score = "GREEN"
        recommended_exit = "ROUTE TO INTERNAL DSCR"
        reason = "Perfect fit for M Capital model: Buy ≤45% ARV, Rehab ≤$20k, Strong cashflow"
        color_class = "green-deal"

    # YELLOW: Route to Wholesale
    elif purchase_pct_arv <= 0.60 and rehab_budget <= 30000 and wholesale_fee >= 25000:
        score = "YELLOW"
        recommended_exit = "ROUTE TO WHOLESALE"
        reason = f"Cannot hold, but strong wholesale potential: ${wholesale_fee:,.0f} assignment fee"
        color_class = "yellow-deal"

    # YELLOW: Route to Retail if low rehab and market-ready
    elif rehab_budget <= 5000 and purchase_pct_arv <= 0.70:
        score = "YELLOW"
        recommended_exit = "ROUTE TO RETAIL LISTING"
        reason = "Retail-ready property, list on MLS for 3% commission"
        color_class = "yellow-deal"

    # RED: Reject
    else:
        if rehab_budget > 30000:
            reason = f"Rehab too high: ${rehab_budget:,.0f} (max $20k for DSCR, $30k for wholesale)"
        elif purchase_pct_arv > 0.60:
            reason = f"Purchase price too high: {purchase_pct_arv*100:.1f}% ARV (max 45% for DSCR)"
        elif wholesale_fee < 25000:
            reason = f"Wholesale fee too low: ${wholesale_fee:,.0f} (min $30k target)"
        else:
            reason = "Does not meet minimum criteria for any exit strategy"

    return {
        'purchase_pct_arv': purchase_pct_arv,
        'all_in_cost': all_in_cost,
        'holding_costs': holding_costs,
        'closing_costs_buy': closing_costs_buy,
        'closing_costs_sell': closing_costs_sell,
        'gross_profit': gross_profit,
        'piti': piti,
        'dscr': dscr,
        'net_cashflow': net_cashflow,
        'wholesale_fee': wholesale_fee,
        'rehab_psf': rehab_psf,
        'score': score,
        'recommended_exit': recommended_exit,
        'reason': reason,
        'color_class': color_class,
        'loan_amount': loan_amount,
        'monthly_payment': monthly_payment
    }


def main():
    """Main underwriting calculator page"""

    st.title("🏠 Deal Underwriter")
    st.markdown("*Individual Property Underwriting Calculator with Routing Recommendations*")

    st.markdown("---")

    # Instructions
    with st.expander("ℹ️ How to Use This Calculator", expanded=False):
        st.markdown(f"""
        **Decision Tree Logic:**

        🟢 **GREEN (Route to Internal DSCR):**
        - Purchase ≤ 45% ARV
        - Rehab ≤ $20,000
        - Net cashflow ≥ $175/month
        - → Route to M Capital → Rehab → PM → Long-term hold

        🟡 **YELLOW (Route to Wholesale or Retail):**
        - Purchase 45-60% ARV OR Rehab $20k-30k
        - Wholesale fee potential ≥ $25k
        - → Assign to cash buyer OR list on MLS

        🔴 **RED (Reject/Archive):**
        - Rehab > $30k OR Purchase > 60% ARV
        - Poor wholesale fee potential
        - → Archive or refer to partners

        **Target Metrics:**
        - Internal DSCR: {config['business_model']['primary_strategies'][0]['target_volume']} doors/year
        - Wholesale: {config['business_model']['primary_strategies'][1]['target_volume']} deals/year @ ${config['business_model']['primary_strategies'][1]['fee_target']:,}/deal
        - Retail Listings: {config['business_model']['primary_strategies'][2]['target_volume']} listings/year
        """)

    # Two-column layout: Input form on left, results on right
    col_input, col_output = st.columns([1, 1])

    with col_input:
        st.markdown("### 📝 Property Information")

        # Basic inputs
        address = st.text_input(
            "Property Address",
            placeholder="123 Main St, City, State ZIP",
            help="Full property address"
        )

        col1, col2 = st.columns(2)

        with col1:
            arv = st.number_input(
                "ARV (After Repair Value)",
                min_value=0,
                value=180000,
                step=5000,
                format="%d",
                help="Estimated market value after repairs"
            )

            purchase_price = st.number_input(
                "Purchase Price",
                min_value=0,
                value=75000,
                step=1000,
                format="%d",
                help="Offer price to seller"
            )

            rehab_budget = st.number_input(
                "Rehab Budget",
                min_value=0,
                value=12000,
                step=1000,
                format="%d",
                help="Max $20k for M Capital DSCR model"
            )

        with col2:
            sqft = st.number_input(
                "Square Footage",
                min_value=0,
                value=1200,
                step=50,
                format="%d"
            )

            estimated_rent = st.number_input(
                "Est. Monthly Rent",
                min_value=0,
                value=1400,
                step=50,
                format="%d",
                help="Market rent after stabilization"
            )

            holding_months = st.number_input(
                "Holding Period (months)",
                min_value=0.5,
                max_value=12.0,
                value=2.0,
                step=0.5,
                help="Typical: 1.5-2 months for light rehab"
            )

        # Additional details
        st.markdown("### 🏡 Property Details")

        col3, col4, col5 = st.columns(3)

        with col3:
            bedrooms = st.number_input("Bedrooms", min_value=1, value=3, step=1)

        with col4:
            bathrooms = st.number_input("Bathrooms", min_value=1.0, value=2.0, step=0.5)

        with col5:
            condition = st.selectbox(
                "Condition",
                ["Retail Ready", "Light Cosmetic", "Heavy Rehab", "Gut Required"]
            )

        notes = st.text_area(
            "Additional Notes",
            placeholder="Seller motivation, unique features, issues found...",
            height=100
        )

        # Calculate button
        calculate_btn = st.button("🔍 Analyze Deal", type="primary", use_container_width=True)

    with col_output:
        st.markdown("### 📊 Underwriting Results")

        if calculate_btn or arv > 0:
            # Prepare inputs
            inputs = {
                'arv': arv,
                'purchase_price': purchase_price,
                'rehab_budget': rehab_budget,
                'estimated_rent': estimated_rent,
                'holding_months': holding_months,
                'sqft': sqft
            }

            # Calculate
            results = calculate_underwriting(inputs)

            # Display score badge
            score_colors = {
                'GREEN': '#10b981',
                'YELLOW': '#f59e0b',
                'RED': '#ef4444'
            }

            score_icons = {
                'GREEN': '🟢',
                'YELLOW': '🟡',
                'RED': '🔴'
            }

            st.markdown(f"""
            <div class="score-badge" style="background: {score_colors[results['score']]};">
                {score_icons[results['score']]} {results['score']} DEAL
            </div>
            """, unsafe_allow_html=True)

            # Recommendation box
            st.markdown(f"""
            <div class="recommendation-box">
                <h3 style="margin-top: 0; color: #60a5fa;">📌 Recommendation</h3>
                <p style="font-size: 1.1rem; font-weight: 600; color: #fff; margin: 0.5rem 0;">
                    {results['recommended_exit']}
                </p>
                <p style="color: #cbd5e1; margin: 0;">
                    {results['reason']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Key metrics
            st.markdown("#### 💰 Financial Breakdown")

            col_m1, col_m2, col_m3 = st.columns(3)

            with col_m1:
                pct_color = "#10b981" if results['purchase_pct_arv'] <= 0.45 else "#f59e0b" if results['purchase_pct_arv'] <= 0.60 else "#ef4444"
                st.metric(
                    "Purchase % ARV",
                    f"{results['purchase_pct_arv']*100:.1f}%",
                    delta="✅ Target: ≤45%" if results['purchase_pct_arv'] <= 0.45 else "⚠️ Over 45%"
                )

            with col_m2:
                st.metric(
                    "All-In Cost",
                    f"${results['all_in_cost']:,.0f}",
                    help="Purchase + Rehab + Holding + Closing"
                )

            with col_m3:
                rehab_color = "#10b981" if rehab_budget <= 20000 else "#f59e0b" if rehab_budget <= 30000 else "#ef4444"
                st.metric(
                    "Rehab $/sqft",
                    f"${results['rehab_psf']:.2f}",
                    delta="✅ Target: ≤$35" if results['rehab_psf'] <= 35 else "⚠️ High"
                )

            # Detailed metrics
            st.markdown("#### 📋 Detailed Calculations")

            st.markdown(f"""
            <div class="metric-row">
                <span class="metric-label">Purchase Price:</span>
                <span class="metric-value">${purchase_price:,.0f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Rehab Budget:</span>
                <span class="metric-value">${rehab_budget:,.0f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Holding Costs ({holding_months} months):</span>
                <span class="metric-value">${results['holding_costs']:,.0f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Closing Costs (Buy):</span>
                <span class="metric-value">${results['closing_costs_buy']:,.0f}</span>
            </div>
            <div class="metric-row" style="border-top: 2px solid #3b82f6; padding-top: 0.5rem;">
                <span class="metric-label"><strong>All-In Cost:</strong></span>
                <span class="metric-value"><strong>${results['all_in_cost']:,.0f}</strong></span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # DSCR Analysis (if applicable)
            if results['score'] == 'GREEN' or results['purchase_pct_arv'] <= 0.50:
                st.markdown("#### 🏦 DSCR Analysis (Long-Term Hold)")

                col_d1, col_d2 = st.columns(2)

                with col_d1:
                    dscr_color = "#10b981" if results['dscr'] >= 1.30 else "#f59e0b" if results['dscr'] >= 1.20 else "#ef4444"
                    st.metric(
                        "DSCR",
                        f"{results['dscr']:.2f}",
                        delta="✅ Target: ≥1.30" if results['dscr'] >= 1.30 else "⚠️ Low"
                    )

                with col_d2:
                    cashflow_color = "#10b981" if results['net_cashflow'] >= 175 else "#f59e0b" if results['net_cashflow'] >= 100 else "#ef4444"
                    st.metric(
                        "Net Cashflow/Month",
                        f"${results['net_cashflow']:,.0f}",
                        delta="✅ Target: ≥$175" if results['net_cashflow'] >= 175 else "⚠️ Low"
                    )

                st.markdown(f"""
                <div class="metric-row">
                    <span class="metric-label">Monthly Rent:</span>
                    <span class="metric-value">${estimated_rent:,.0f}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">PITI (Mortgage + Tax + Ins):</span>
                    <span class="metric-value">${results['piti']:,.0f}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Property Management (10%):</span>
                    <span class="metric-value">${estimated_rent * 0.10:,.0f}</span>
                </div>
                <div class="metric-row" style="border-top: 2px solid #3b82f6; padding-top: 0.5rem;">
                    <span class="metric-label"><strong>Net Cashflow:</strong></span>
                    <span class="metric-value"><strong>${results['net_cashflow']:,.0f}/month</strong></span>
                </div>
                """, unsafe_allow_html=True)

            # Wholesale Analysis
            st.markdown("---")
            st.markdown("#### 🤝 Wholesale Analysis")

            col_w1, col_w2 = st.columns(2)

            with col_w1:
                st.metric(
                    "Wholesale Price (70% ARV)",
                    f"${arv * 0.70:,.0f}"
                )

            with col_w2:
                wholesale_color = "#10b981" if results['wholesale_fee'] >= 30000 else "#f59e0b" if results['wholesale_fee'] >= 25000 else "#ef4444"
                st.metric(
                    "Potential Assignment Fee",
                    f"${results['wholesale_fee']:,.0f}",
                    delta="✅ Target: ≥$30k" if results['wholesale_fee'] >= 30000 else "⚠️ Below target"
                )

            # Gross profit if sold at ARV
            st.markdown("---")
            st.markdown("#### 💵 Gross Profit (If Sold at ARV)")

            st.metric(
                "Gross Profit",
                f"${results['gross_profit']:,.0f}",
                help="ARV - All-In Cost - Selling Costs"
            )

            roi_pct = (results['gross_profit'] / results['all_in_cost']) * 100 if results['all_in_cost'] > 0 else 0
            st.metric(
                "ROI %",
                f"{roi_pct:.1f}%"
            )

    # Save/Export section
    st.markdown("---")

    col_save1, col_save2, col_save3 = st.columns(3)

    with col_save1:
        if st.button("💾 Save to Session", use_container_width=True):
            st.success("✅ Deal saved to session state (feature pending)")

    with col_save2:
        if st.button("📄 Export to PDF", use_container_width=True):
            st.info("ℹ️ PDF export feature coming soon")

    with col_save3:
        if st.button("📧 Send to CRM", use_container_width=True):
            st.info("ℹ️ CRM integration (Left Main) coming soon")


if __name__ == "__main__":
    main()
