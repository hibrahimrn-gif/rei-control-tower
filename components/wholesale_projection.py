"""
Wholesale-Only 12-Month Projection Model
100% wholesaling (assignment fees) - no rentals, no rehabs, no slow money

Business Model Assumptions:
- CAC (Customer Acquisition Cost): Marketing spend per closed deal
- Assignment Fee: Revenue per closed wholesale deal
- Lead-to-Close Time: Average 24 days
- Lag Model: 20% close same month, 80% close next month
- Principal Payback: 100% marketing capital repaid before profit distributions
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import math


@dataclass
class WholesaleInputs:
    """All configurable inputs for the wholesale projection model"""
    # Core unit economics
    cac: float = 3500.0  # Cost per closed deal (marketing spend / deals)
    avg_assignment_fee: float = 20000.0  # Average revenue per closed deal
    lead_to_close_days: int = 24  # Average days from lead to close

    # Marketing funding ladder (monthly spend)
    marketing_ladder: List[float] = field(default_factory=lambda: [
        50000,    # Month 1
        300000,   # Month 2
        600000,   # Month 3
        900000,   # Month 4
        1200000,  # Month 5
        1200000,  # Month 6
        1200000,  # Month 7
        1200000,  # Month 8
        1200000,  # Month 9
        1200000,  # Month 10
        1200000,  # Month 11
        1200000,  # Month 12
    ])

    # Business days per month
    business_days_per_month: int = 22

    # Scenario modifiers
    cac_modifier: float = 1.0  # Multiply CAC by this (e.g., 1.25 for +25%)
    fee_modifier: float = 1.0  # Multiply fee by this (e.g., 0.85 for -15%)
    fallout_rate: float = 0.0  # Percentage of projected closes that fail (e.g., 0.10 for 10%)

    # Investor terms
    payback_days: int = 30  # Expected principal payback window

    # Pod system configuration
    pod_capacity: int = 50  # Files (deals) per pod
    pod_annual_cost: float = 50000.0  # Annual salary cost per pod
    buyers_added_daily: int = 300  # Total buyers added to list daily (nationwide)
    buyers_per_pod_daily: int = 100  # Buyers each pod must add daily

    # Scenario name
    scenario_name: str = "Base Case"


@dataclass
class MonthlyProjection:
    """Single month projection data"""
    month: int
    marketing_spend: float
    deals_generated_exact: float
    deals_generated_rounded: int
    deals_closed_exact: float
    deals_closed_rounded: int
    closings_per_day: float
    gross_revenue: float
    marketing_cost: float
    net_profit: float
    cumulative_net_profit: float
    principal_payback_due: float
    principal_remaining: float
    ending_cash: float
    # Pod system metrics
    pods_needed: int = 0
    pod_monthly_cost: float = 0.0
    buyers_added_monthly: int = 0
    buyer_coverage_ratio: float = 0.0  # Buyers available per deal


@dataclass
class ScenarioSummary:
    """12-month scenario totals"""
    scenario_name: str
    total_marketing_spend: float
    total_deals_generated: int
    total_deals_closed: int
    total_gross_revenue: float
    total_net_profit: float
    roi_multiple: float
    effective_cac: float
    effective_fee: float
    fallout_rate: float
    # Pod system totals
    max_pods_needed: int = 0
    total_pod_overhead: float = 0.0  # Annual pod costs (investor covers)
    total_investor_outlay: float = 0.0  # Marketing + Pod Overhead
    total_buyers_added: int = 0
    avg_buyer_coverage_ratio: float = 0.0


def calculate_monthly_projections(
    inputs: WholesaleInputs,
    use_lag_model: bool = True
) -> List[MonthlyProjection]:
    """
    Calculate 12-month projections with optional lag model.

    No-Lag Model: Deals close same month as generated
    Lagged Model: 20% close same month, 80% close next month (based on 24-day avg close)
    """
    effective_cac = inputs.cac * inputs.cac_modifier
    effective_fee = inputs.avg_assignment_fee * inputs.fee_modifier
    fallout_multiplier = 1.0 - inputs.fallout_rate

    projections = []
    cumulative_profit = 0.0
    cumulative_cash = 0.0
    principal_remaining = 0.0

    # Track deals generated for lag calculation
    deals_generated_history = [0.0]  # Month 0 = 0 deals

    for month in range(1, 13):
        month_idx = month - 1
        marketing_spend = inputs.marketing_ladder[month_idx]

        # Deals generated this month (before fallout)
        deals_generated_exact = marketing_spend / effective_cac
        deals_generated_history.append(deals_generated_exact)

        # Calculate deals closed based on model
        if use_lag_model:
            # Lagged model: 20% same month, 80% from previous month
            same_month = 0.20 * deals_generated_exact
            prev_month = 0.80 * deals_generated_history[month - 1] if month > 0 else 0
            deals_closed_exact = (same_month + prev_month) * fallout_multiplier
        else:
            # No-lag model: all deals close same month
            deals_closed_exact = deals_generated_exact * fallout_multiplier

        # Round to whole numbers for realistic projections
        deals_generated_rounded = round(deals_generated_exact)
        deals_closed_rounded = round(deals_closed_exact)

        # Financial calculations (use rounded for realism)
        gross_revenue = deals_closed_rounded * effective_fee
        closings_per_day = deals_closed_rounded / inputs.business_days_per_month

        # Net profit = Revenue - Marketing
        net_profit = gross_revenue - marketing_spend
        cumulative_profit += net_profit

        # Principal payback tracking
        # Marketing spend becomes principal due; repaid from revenue
        principal_remaining += marketing_spend  # Add new tranche

        # Pay back principal from gross revenue
        principal_payback = min(gross_revenue, principal_remaining)
        principal_remaining = max(0, principal_remaining - gross_revenue)

        # Ending cash = cumulative cash + revenue - principal payback
        # (we assume all revenue goes to principal first)
        ending_cash = cumulative_profit if principal_remaining == 0 else max(0, gross_revenue - marketing_spend)
        cumulative_cash = cumulative_profit  # Simplified: net profit accumulates

        # Pod system calculations
        pods_needed = math.ceil(deals_closed_rounded / inputs.pod_capacity) if deals_closed_rounded > 0 else 1
        pod_monthly_cost = pods_needed * (inputs.pod_annual_cost / 12)

        # Buyer capacity: nationwide adds 300+/day, but pods also add 100/day each
        # Total buyer acquisition = base nationwide + pod contribution
        buyers_added_monthly = inputs.buyers_added_daily * inputs.business_days_per_month
        # With pods active, each pod adds buyers too
        pod_buyer_contribution = pods_needed * inputs.buyers_per_pod_daily * inputs.business_days_per_month
        total_buyers_for_month = buyers_added_monthly + pod_buyer_contribution

        # Buyer coverage ratio: how many buyers available per deal needing disposition
        buyer_coverage_ratio = total_buyers_for_month / deals_closed_rounded if deals_closed_rounded > 0 else 0

        projections.append(MonthlyProjection(
            month=month,
            marketing_spend=marketing_spend,
            deals_generated_exact=deals_generated_exact,
            deals_generated_rounded=deals_generated_rounded,
            deals_closed_exact=deals_closed_exact,
            deals_closed_rounded=deals_closed_rounded,
            closings_per_day=closings_per_day,
            gross_revenue=gross_revenue,
            marketing_cost=marketing_spend,
            net_profit=net_profit,
            cumulative_net_profit=cumulative_profit,
            principal_payback_due=principal_payback,
            principal_remaining=principal_remaining,
            ending_cash=cumulative_profit,
            pods_needed=pods_needed,
            pod_monthly_cost=pod_monthly_cost,
            buyers_added_monthly=total_buyers_for_month,
            buyer_coverage_ratio=buyer_coverage_ratio
        ))

    return projections


def calculate_scenario_summary(
    projections: List[MonthlyProjection],
    inputs: WholesaleInputs
) -> ScenarioSummary:
    """Calculate 12-month totals for a scenario"""
    total_spend = sum(p.marketing_spend for p in projections)
    total_generated = sum(p.deals_generated_rounded for p in projections)
    total_closed = sum(p.deals_closed_rounded for p in projections)
    total_revenue = sum(p.gross_revenue for p in projections)
    total_profit = sum(p.net_profit for p in projections)

    roi = total_profit / total_spend if total_spend > 0 else 0

    # Pod system totals
    max_pods = max(p.pods_needed for p in projections)
    total_pod_overhead = sum(p.pod_monthly_cost for p in projections)
    total_buyers = sum(p.buyers_added_monthly for p in projections)
    avg_buyer_ratio = sum(p.buyer_coverage_ratio for p in projections) / len(projections) if projections else 0

    return ScenarioSummary(
        scenario_name=inputs.scenario_name,
        total_marketing_spend=total_spend,
        total_deals_generated=total_generated,
        total_deals_closed=total_closed,
        total_gross_revenue=total_revenue,
        total_net_profit=total_profit,
        roi_multiple=roi,
        effective_cac=inputs.cac * inputs.cac_modifier,
        effective_fee=inputs.avg_assignment_fee * inputs.fee_modifier,
        fallout_rate=inputs.fallout_rate,
        max_pods_needed=max_pods,
        total_pod_overhead=total_pod_overhead,
        total_investor_outlay=total_spend + total_pod_overhead,
        total_buyers_added=total_buyers,
        avg_buyer_coverage_ratio=avg_buyer_ratio
    )


def generate_scenario_comparison() -> Dict[str, Tuple[WholesaleInputs, List[MonthlyProjection], ScenarioSummary]]:
    """Generate all three scenarios: Base, Conservative, Aggressive"""
    scenarios = {}

    # Base Case
    base_inputs = WholesaleInputs(scenario_name="Base Case")
    base_projections = calculate_monthly_projections(base_inputs, use_lag_model=True)
    base_summary = calculate_scenario_summary(base_projections, base_inputs)
    scenarios["base"] = (base_inputs, base_projections, base_summary)

    # Conservative: CAC +25%, Fee -15%, 10% fallout
    conservative_inputs = WholesaleInputs(
        scenario_name="Conservative",
        cac_modifier=1.25,
        fee_modifier=0.85,
        fallout_rate=0.10
    )
    conservative_projections = calculate_monthly_projections(conservative_inputs, use_lag_model=True)
    conservative_summary = calculate_scenario_summary(conservative_projections, conservative_inputs)
    scenarios["conservative"] = (conservative_inputs, conservative_projections, conservative_summary)

    # Aggressive: CAC -10%, Fee +10%, 0% fallout
    aggressive_inputs = WholesaleInputs(
        scenario_name="Aggressive",
        cac_modifier=0.90,
        fee_modifier=1.10,
        fallout_rate=0.0
    )
    aggressive_projections = calculate_monthly_projections(aggressive_inputs, use_lag_model=True)
    aggressive_summary = calculate_scenario_summary(aggressive_projections, aggressive_inputs)
    scenarios["aggressive"] = (aggressive_inputs, aggressive_projections, aggressive_summary)

    return scenarios


def calculate_investor_distributions(
    total_net_profit: float,
    equity_percentages: List[float] = [0.10, 0.20, 0.30],
    distribution_percentages: List[float] = [0.0, 0.50, 1.00]
) -> Dict[str, Dict[str, float]]:
    """
    Calculate investor distributions based on equity stake and distribution policy.

    Formula: Investor Distribution = Net Profit * Equity % * Distribution %

    Args:
        total_net_profit: Total net profit after marketing payback
        equity_percentages: List of equity stakes to model (e.g., 10%, 20%, 30%)
        distribution_percentages: List of profit distribution rates (e.g., 0%, 50%, 100%)

    Returns:
        Dictionary with distribution matrix
    """
    distributions = {}

    for equity in equity_percentages:
        equity_key = f"{int(equity * 100)}%"
        distributions[equity_key] = {}

        for dist in distribution_percentages:
            dist_key = f"{int(dist * 100)}%"
            investor_amount = total_net_profit * equity * dist
            distributions[equity_key][dist_key] = investor_amount

    return distributions


def generate_csv_export(projections: List[MonthlyProjection], include_pods: bool = True) -> str:
    """Generate CSV string for Google Sheets export"""
    headers = [
        "Month",
        "Marketing Spend",
        "Deals Generated (Exact)",
        "Deals Generated (Rounded)",
        "Deals Closed (Exact)",
        "Deals Closed (Rounded)",
        "Closings/Day (22d)",
        "Gross Revenue",
        "Marketing Cost",
        "Net Profit",
        "Cumulative Net Profit",
        "Principal Payback",
        "Principal Remaining",
        "Ending Cash"
    ]

    if include_pods:
        headers.extend([
            "Pods Needed",
            "Pod Monthly Cost",
            "Buyers Added",
            "Buyer/Deal Ratio"
        ])

    lines = [",".join(headers)]

    for p in projections:
        row = [
            str(p.month),
            f"{p.marketing_spend:.0f}",
            f"{p.deals_generated_exact:.2f}",
            str(p.deals_generated_rounded),
            f"{p.deals_closed_exact:.2f}",
            str(p.deals_closed_rounded),
            f"{p.closings_per_day:.2f}",
            f"{p.gross_revenue:.0f}",
            f"{p.marketing_cost:.0f}",
            f"{p.net_profit:.0f}",
            f"{p.cumulative_net_profit:.0f}",
            f"{p.principal_payback_due:.0f}",
            f"{p.principal_remaining:.0f}",
            f"{p.ending_cash:.0f}"
        ]
        if include_pods:
            row.extend([
                str(p.pods_needed),
                f"{p.pod_monthly_cost:.0f}",
                str(p.buyers_added_monthly),
                f"{p.buyer_coverage_ratio:.1f}"
            ])
        lines.append(",".join(row))

    # Add totals row
    totals = [
        "TOTAL",
        f"{sum(p.marketing_spend for p in projections):.0f}",
        f"{sum(p.deals_generated_exact for p in projections):.2f}",
        str(sum(p.deals_generated_rounded for p in projections)),
        f"{sum(p.deals_closed_exact for p in projections):.2f}",
        str(sum(p.deals_closed_rounded for p in projections)),
        "N/A",
        f"{sum(p.gross_revenue for p in projections):.0f}",
        f"{sum(p.marketing_cost for p in projections):.0f}",
        f"{sum(p.net_profit for p in projections):.0f}",
        f"{projections[-1].cumulative_net_profit:.0f}",
        f"{sum(p.principal_payback_due for p in projections):.0f}",
        f"{projections[-1].principal_remaining:.0f}",
        f"{projections[-1].ending_cash:.0f}"
    ]
    if include_pods:
        totals.extend([
            f"MAX: {max(p.pods_needed for p in projections)}",
            f"{sum(p.pod_monthly_cost for p in projections):.0f}",
            str(sum(p.buyers_added_monthly for p in projections)),
            f"AVG: {sum(p.buyer_coverage_ratio for p in projections)/len(projections):.1f}"
        ])
    lines.append(",".join(totals))

    return "\n".join(lines)


def format_currency(value: float) -> str:
    """Format value as currency string"""
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"


def get_risk_analysis(with_pod_system: bool = True) -> List[Dict[str, str]]:
    """Return list of key risks and considerations"""
    if with_pod_system:
        return [
            {
                "category": "Dispo Bottleneck (MITIGATED)",
                "description": "Pod system + 300 buyers/day nationwide SOLVES dispo capacity. ~20+ buyers available per deal.",
                "mitigation": "✅ Pod system in place. Monitor buyer quality and deal-to-buyer match rate.",
                "status": "green"
            },
            {
                "category": "CAC Creep at Scale",
                "description": "$3,500 CAC benchmarked at low spend may increase at $1.2M/month due to audience saturation.",
                "mitigation": "Nationwide footprint diversifies risk. Monitor CAC by market; rotate creative weekly.",
                "status": "yellow"
            },
            {
                "category": "Cash Timing vs 30-Day Payback",
                "description": "Title delays, buyer financing issues can stretch actual close beyond 30 days.",
                "mitigation": "Build 15-day buffer into projections; negotiate flexible payback terms.",
                "status": "yellow"
            },
            {
                "category": "Market Saturation (MITIGATED)",
                "description": "Nationwide operation = no single market dependency. Seller inventory distributed.",
                "mitigation": "✅ Already nationwide. Monitor per-market CAC for early saturation signals.",
                "status": "green"
            },
            {
                "category": "Buyer Capacity (MITIGATED)",
                "description": "300+ buyers/day + pod buyer acquisition = 8,800+ new buyers/month at steady state.",
                "mitigation": "✅ Buyer pipeline exceeds deal flow by 20x+. Focus on buyer quality over quantity.",
                "status": "green"
            },
            {
                "category": "Pod Scaling Speed",
                "description": "Ramping from 1 pod to 7 pods in 6 months requires hiring pipeline.",
                "mitigation": "Start recruiting Month 1 for Month 3+ needs. Build bench of 2 pods ahead.",
                "status": "yellow"
            }
        ]
    else:
        return [
            {
                "category": "Dispo Bottleneck (Operational)",
                "description": "343 contracts/month = 16 deals/day. Requires massive buyers list and dispo team.",
                "mitigation": "Build buyer pipeline in parallel; consider JV partnerships for overflow.",
                "status": "red"
            },
            {
                "category": "CAC Creep at Scale",
                "description": "$3,500 CAC benchmarked at low spend may double at $1.2M/month due to audience saturation.",
                "mitigation": "Monitor CAC weekly; diversify channels; maintain creative refresh cadence.",
                "status": "red"
            },
            {
                "category": "Cash Timing vs 30-Day Payback",
                "description": "Title delays, buyer financing issues can stretch actual close beyond 30 days.",
                "mitigation": "Build 15-day buffer into projections; negotiate flexible payback terms.",
                "status": "yellow"
            },
            {
                "category": "Market Saturation",
                "description": "Aggressive spend in single market can exhaust seller inventory.",
                "mitigation": "Geographic expansion plan; multi-market launch by month 6.",
                "status": "red"
            },
            {
                "category": "Buyer Capacity",
                "description": "Wholesale volume assumes unlimited buyer demand at target spreads.",
                "mitigation": "Pre-qualify institutional buyers; develop retail investor network.",
                "status": "red"
            }
        ]


def calculate_pod_scaling_schedule(projections: List[MonthlyProjection]) -> List[Dict]:
    """Generate pod scaling schedule by month"""
    schedule = []
    prev_pods = 0

    for p in projections:
        delta = p.pods_needed - prev_pods
        schedule.append({
            "month": p.month,
            "deals_closed": p.deals_closed_rounded,
            "pods_needed": p.pods_needed,
            "pods_to_hire": max(0, delta),
            "monthly_pod_cost": p.pod_monthly_cost,
            "buyers_added": p.buyers_added_monthly,
            "buyer_per_deal_ratio": p.buyer_coverage_ratio
        })
        prev_pods = p.pods_needed

    return schedule
