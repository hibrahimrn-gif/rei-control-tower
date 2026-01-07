"""
REI Nationwide LLC - Dynamic View Calculations Engine
All formulas are documented and unit-safe (annual vs weekly conversions explicit)
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
import json


@dataclass
class ScenarioInputs:
    """All adjustable inputs for a scenario"""
    # Scenario metadata
    name: str = "2026 Base Plan"
    
    # Revenue Drivers (annual volumes)
    wholesale_volume: int = 300
    avg_wholesale_fee: float = 30000.0
    retained_doors: int = 300
    internal_acq_fee: float = 30000.0
    memberships_sold: int = 150
    membership_price: float = 15000.0
    retail_listings: int = 100
    avg_retail_price: float = 250000.0
    listing_commission_rate: float = 0.03
    property_mgmt_revenue: float = 540000.0
    
    # Marketing
    weekly_ad_spend: float = 34400.0
    cpl: float = 100.0
    
    # Commission Rates
    president_override_rate: float = 0.10
    acq_commission_rate: float = 0.10
    dispo_commission_rate: float = 0.05
    membership_commission_rate: float = 0.10
    
    # Salaries (annual)
    executive_salaries: float = 990000.0  # Hamza + Jacqui + Melissa
    staff_salaries: float = 698000.0
    hamza_salary: float = 480000.0
    
    # Comp Structure
    hamza_noi_share: float = 0.25
    clearroute_noi_share: float = 0.20
    
    # Pipeline Split (must sum to 1.0)
    internal_split: float = 0.30
    wholesale_split: float = 0.30
    retail_split: float = 0.20
    fallout_rate: float = 0.20
    
    # Staffing Capacities
    closer_lead_capacity: float = 85.0  # leads/week/closer
    closer_contract_capacity: float = 4.0  # contracts/week/closer
    offer_to_contract_ratio: float = 4.0  # offers per contract
    underwriter_capacity: float = 40.0  # underwrites/week
    rehab_cycle_days: int = 45
    pm_capacity: float = 10.0  # active rehabs per PM
    tc_capacity: float = 10.0  # contracts/week per TC
    dispo_capacity: float = 6.0  # wholesale/week per dispo
    dscr_capacity: float = 6.0  # refis/week per coordinator
    membership_close_rate: float = 0.25
    membership_show_rate: float = 0.70
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'ScenarioInputs':
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class RevenueOutputs:
    """All revenue calculations"""
    wholesale_revenue: float = 0.0
    internal_revenue: float = 0.0
    membership_revenue: float = 0.0
    listing_revenue: float = 0.0
    property_mgmt_revenue: float = 0.0
    gross_revenue: float = 0.0


@dataclass
class ExpenseOutputs:
    """All expense calculations"""
    president_override: float = 0.0
    acq_commissions: float = 0.0
    dispo_commissions: float = 0.0
    membership_commissions: float = 0.0
    marketing_spend: float = 0.0
    executive_salaries: float = 0.0
    staff_salaries: float = 0.0
    total_expenses: float = 0.0


@dataclass
class CompOutputs:
    """Compensation and profit splits"""
    noi: float = 0.0
    hamza_draw: float = 0.0
    hamza_salary: float = 0.0
    hamza_total_comp: float = 0.0
    clearroute_dividend: float = 0.0


@dataclass
class FunnelOutputs:
    """Lead funnel calculations"""
    monetized_outcomes: int = 0
    contracts_needed_annual: float = 0.0
    contracts_per_week: float = 0.0
    leads_per_week: float = 0.0
    leads_per_year: float = 0.0
    lead_to_contract_rate: float = 0.0
    leads_per_contract: float = 0.0
    
    # Weekly targets by chute
    internal_per_week: float = 0.0
    wholesale_per_week: float = 0.0
    retail_per_week: float = 0.0
    fallout_per_week: float = 0.0
    membership_per_week: float = 0.0


@dataclass
class StaffingOutputs:
    """Staffing requirements"""
    closers_needed: float = 0.0
    closers_by_leads: float = 0.0
    closers_by_contracts: float = 0.0
    offers_per_week: float = 0.0
    underwriters_needed: float = 0.0
    active_rehabs: float = 0.0
    pms_needed: float = 0.0
    tcs_needed: float = 0.0
    dispo_needed: float = 0.0
    dscr_coordinators_needed: float = 0.0
    held_calls_needed: float = 0.0
    booked_calls_needed: float = 0.0


@dataclass
class Alert:
    """Bottleneck alert"""
    severity: str  # 'warning', 'critical'
    category: str
    message: str
    recommendation: str


@dataclass 
class ScenarioOutputs:
    """All computed outputs for a scenario"""
    revenue: RevenueOutputs = field(default_factory=RevenueOutputs)
    expenses: ExpenseOutputs = field(default_factory=ExpenseOutputs)
    comp: CompOutputs = field(default_factory=CompOutputs)
    funnel: FunnelOutputs = field(default_factory=FunnelOutputs)
    staffing: StaffingOutputs = field(default_factory=StaffingOutputs)
    alerts: List[Alert] = field(default_factory=list)


def calculate_revenue(inputs: ScenarioInputs) -> RevenueOutputs:
    """Calculate all revenue lines"""
    wholesale = inputs.wholesale_volume * inputs.avg_wholesale_fee
    internal = inputs.retained_doors * inputs.internal_acq_fee
    membership = inputs.memberships_sold * inputs.membership_price
    listing = inputs.retail_listings * inputs.avg_retail_price * inputs.listing_commission_rate
    prop_mgmt = inputs.property_mgmt_revenue
    
    return RevenueOutputs(
        wholesale_revenue=wholesale,
        internal_revenue=internal,
        membership_revenue=membership,
        listing_revenue=listing,
        property_mgmt_revenue=prop_mgmt,
        gross_revenue=wholesale + internal + membership + listing + prop_mgmt
    )


def calculate_expenses(inputs: ScenarioInputs, revenue: RevenueOutputs) -> ExpenseOutputs:
    """Calculate all expenses"""
    president_override = revenue.gross_revenue * inputs.president_override_rate
    acq_comm = (revenue.wholesale_revenue + revenue.internal_revenue) * inputs.acq_commission_rate
    dispo_comm = revenue.wholesale_revenue * inputs.dispo_commission_rate
    membership_comm = revenue.membership_revenue * inputs.membership_commission_rate
    marketing = inputs.weekly_ad_spend * 52
    
    total = (president_override + acq_comm + dispo_comm + membership_comm + 
             marketing + inputs.executive_salaries + inputs.staff_salaries)
    
    return ExpenseOutputs(
        president_override=president_override,
        acq_commissions=acq_comm,
        dispo_commissions=dispo_comm,
        membership_commissions=membership_comm,
        marketing_spend=marketing,
        executive_salaries=inputs.executive_salaries,
        staff_salaries=inputs.staff_salaries,
        total_expenses=total
    )


def calculate_comp(inputs: ScenarioInputs, revenue: RevenueOutputs, 
                   expenses: ExpenseOutputs) -> CompOutputs:
    """Calculate NOI and compensation splits"""
    noi = revenue.gross_revenue - expenses.total_expenses
    hamza_draw = noi * inputs.hamza_noi_share
    clearroute = noi * inputs.clearroute_noi_share
    
    return CompOutputs(
        noi=noi,
        hamza_draw=hamza_draw,
        hamza_salary=inputs.hamza_salary,
        hamza_total_comp=hamza_draw + inputs.hamza_salary,
        clearroute_dividend=clearroute
    )


def calculate_funnel(inputs: ScenarioInputs) -> FunnelOutputs:
    """Calculate lead funnel requirements - working backwards from outcomes"""
    # Monetized outcomes (deals that close to one of three exit chutes)
    monetized = inputs.wholesale_volume + inputs.retained_doors + inputs.retail_listings
    
    # Contracts needed accounting for fallout
    contracts_annual = monetized / (1 - inputs.fallout_rate) if inputs.fallout_rate < 1 else 0
    contracts_weekly = contracts_annual / 52
    
    # Lead calculations
    leads_weekly = inputs.weekly_ad_spend / inputs.cpl if inputs.cpl > 0 else 0
    leads_annual = leads_weekly * 52
    
    # Conversion metrics
    lead_to_contract = contracts_annual / leads_annual if leads_annual > 0 else 0
    leads_per_contract = leads_annual / contracts_annual if contracts_annual > 0 else 0
    
    # Weekly targets by chute
    internal_wk = inputs.retained_doors / 52
    wholesale_wk = inputs.wholesale_volume / 52
    retail_wk = inputs.retail_listings / 52
    fallout_wk = contracts_weekly * inputs.fallout_rate
    membership_wk = inputs.memberships_sold / 52
    
    return FunnelOutputs(
        monetized_outcomes=monetized,
        contracts_needed_annual=contracts_annual,
        contracts_per_week=contracts_weekly,
        leads_per_week=leads_weekly,
        leads_per_year=leads_annual,
        lead_to_contract_rate=lead_to_contract,
        leads_per_contract=leads_per_contract,
        internal_per_week=internal_wk,
        wholesale_per_week=wholesale_wk,
        retail_per_week=retail_wk,
        fallout_per_week=fallout_wk,
        membership_per_week=membership_wk
    )


def calculate_staffing(inputs: ScenarioInputs, funnel: FunnelOutputs) -> StaffingOutputs:
    """Calculate staffing requirements based on weekly targets and capacities"""
    # Closers - need enough for both lead handling AND contract closing
    closers_leads = funnel.leads_per_week / inputs.closer_lead_capacity if inputs.closer_lead_capacity > 0 else 0
    closers_contracts = funnel.contracts_per_week / inputs.closer_contract_capacity if inputs.closer_contract_capacity > 0 else 0
    closers_needed = max(closers_leads, closers_contracts)
    
    # Underwriters
    offers_weekly = funnel.contracts_per_week * inputs.offer_to_contract_ratio
    underwriters = offers_weekly / inputs.underwriter_capacity if inputs.underwriter_capacity > 0 else 0
    
    # Project Managers (based on active rehab pipeline)
    active_rehabs = funnel.internal_per_week * (inputs.rehab_cycle_days / 7)
    pms = active_rehabs / inputs.pm_capacity if inputs.pm_capacity > 0 else 0
    
    # Transaction Coordinators
    tcs = funnel.contracts_per_week / inputs.tc_capacity if inputs.tc_capacity > 0 else 0
    
    # Dispo team
    dispo = funnel.wholesale_per_week / inputs.dispo_capacity if inputs.dispo_capacity > 0 else 0
    
    # DSCR Coordinator
    dscr = funnel.internal_per_week / inputs.dscr_capacity if inputs.dscr_capacity > 0 else 0
    
    # Membership sales calls
    held_calls = funnel.membership_per_week / inputs.membership_close_rate if inputs.membership_close_rate > 0 else 0
    booked_calls = held_calls / inputs.membership_show_rate if inputs.membership_show_rate > 0 else 0
    
    return StaffingOutputs(
        closers_needed=closers_needed,
        closers_by_leads=closers_leads,
        closers_by_contracts=closers_contracts,
        offers_per_week=offers_weekly,
        underwriters_needed=underwriters,
        active_rehabs=active_rehabs,
        pms_needed=pms,
        tcs_needed=tcs,
        dispo_needed=dispo,
        dscr_coordinators_needed=dscr,
        held_calls_needed=held_calls,
        booked_calls_needed=booked_calls
    )


def generate_alerts(inputs: ScenarioInputs, funnel: FunnelOutputs, 
                    staffing: StaffingOutputs) -> List[Alert]:
    """Generate bottleneck and capacity alerts"""
    alerts = []
    
    # Closer capacity check
    if staffing.closers_needed > staffing.closers_by_leads:
        alerts.append(Alert(
            severity='warning',
            category='Closers',
            message=f'Contracts/week ({funnel.contracts_per_week:.1f}) driving closer need over lead volume',
            recommendation='Focus on contract velocity or add closers'
        ))
    
    # High conversion requirement check
    if funnel.lead_to_contract_rate > 0.08:
        alerts.append(Alert(
            severity='critical',
            category='Conversion',
            message=f'Required conversion rate {funnel.lead_to_contract_rate*100:.1f}% is aggressive',
            recommendation='Increase ad spend or lower targets to reach <8% required conversion'
        ))
    elif funnel.lead_to_contract_rate > 0.06:
        alerts.append(Alert(
            severity='warning',
            category='Conversion',
            message=f'Required conversion rate {funnel.lead_to_contract_rate*100:.1f}% is challenging',
            recommendation='Monitor closely; consider increasing lead volume buffer'
        ))
    
    # CPL sensitivity check
    if inputs.cpl > 120:
        alerts.append(Alert(
            severity='warning',
            category='Marketing',
            message=f'CPL ${inputs.cpl:.0f} is above target range',
            recommendation='Optimize ad creative/targeting or increase conversion to compensate'
        ))
    
    # Underwriting capacity
    if staffing.offers_per_week > inputs.underwriter_capacity * 2:
        alerts.append(Alert(
            severity='critical',
            category='Underwriting',
            message=f'{staffing.offers_per_week:.0f} offers/week exceeds 2-underwriter capacity',
            recommendation='Add underwriting capacity or improve offer-to-contract ratio'
        ))
    
    # PM capacity for rehabs
    if staffing.pms_needed > 3:
        alerts.append(Alert(
            severity='warning',
            category='Project Management',
            message=f'{staffing.active_rehabs:.0f} concurrent rehabs requires {staffing.pms_needed:.1f} PMs',
            recommendation='Ensure PM capacity or extend rehab cycles'
        ))
    
    # Fallout rate check
    if inputs.fallout_rate > 0.25:
        alerts.append(Alert(
            severity='warning',
            category='Pipeline',
            message=f'Fallout rate {inputs.fallout_rate*100:.0f}% is high',
            recommendation='Review qualifying criteria or disposition strategy'
        ))
    
    return alerts


def run_full_calculation(inputs: ScenarioInputs) -> ScenarioOutputs:
    """Run all calculations and return complete outputs"""
    revenue = calculate_revenue(inputs)
    expenses = calculate_expenses(inputs, revenue)
    comp = calculate_comp(inputs, revenue, expenses)
    funnel = calculate_funnel(inputs)
    staffing = calculate_staffing(inputs, funnel)
    alerts = generate_alerts(inputs, funnel, staffing)
    
    return ScenarioOutputs(
        revenue=revenue,
        expenses=expenses,
        comp=comp,
        funnel=funnel,
        staffing=staffing,
        alerts=alerts
    )


def generate_sensitivity_cpl(inputs: ScenarioInputs, 
                              cpl_values: List[float] = [80, 100, 120, 150, 200]) -> List[Dict]:
    """Generate CPL sensitivity table"""
    results = []
    base_inputs = ScenarioInputs(**inputs.to_dict())
    
    for cpl in cpl_values:
        base_inputs.cpl = cpl
        funnel = calculate_funnel(base_inputs)
        results.append({
            'CPL': f'${cpl:.0f}',
            'Leads/Week': f'{funnel.leads_per_week:.0f}',
            'Leads/Year': f'{funnel.leads_per_year:.0f}',
            'Lead→Contract': f'{funnel.lead_to_contract_rate*100:.1f}%',
            'Leads/Contract': f'{funnel.leads_per_contract:.1f}'
        })
    
    return results


def generate_sensitivity_fallout(inputs: ScenarioInputs,
                                  fallout_values: List[float] = [0.10, 0.15, 0.20, 0.25, 0.30]) -> List[Dict]:
    """Generate fallout rate sensitivity table"""
    results = []
    base_inputs = ScenarioInputs(**inputs.to_dict())
    
    for fallout in fallout_values:
        base_inputs.fallout_rate = fallout
        funnel = calculate_funnel(base_inputs)
        results.append({
            'Fallout Rate': f'{fallout*100:.0f}%',
            'Contracts/Year': f'{funnel.contracts_needed_annual:.0f}',
            'Contracts/Week': f'{funnel.contracts_per_week:.1f}',
            'Leads/Contract': f'{funnel.leads_per_contract:.1f}',
            'Lead→Contract': f'{funnel.lead_to_contract_rate*100:.1f}%'
        })
    
    return results


def generate_sensitivity_conversion(inputs: ScenarioInputs,
                                     conversion_values: List[float] = [0.03, 0.04, 0.05, 0.06, 0.07, 0.08]) -> List[Dict]:
    """Generate conversion sensitivity - shows required leads/spend for each conversion rate"""
    results = []
    base_inputs = ScenarioInputs(**inputs.to_dict())
    funnel = calculate_funnel(base_inputs)
    contracts_needed = funnel.contracts_needed_annual
    
    for conv in conversion_values:
        leads_needed = contracts_needed / conv if conv > 0 else 0
        leads_weekly = leads_needed / 52
        spend_weekly = leads_weekly * base_inputs.cpl
        spend_annual = spend_weekly * 52
        
        results.append({
            'Conversion': f'{conv*100:.0f}%',
            'Leads/Week Needed': f'{leads_weekly:.0f}',
            'Leads/Year Needed': f'{leads_needed:.0f}',
            'Weekly Spend': f'${spend_weekly:,.0f}',
            'Annual Spend': f'${spend_annual:,.0f}'
        })
    
    return results


def scenario_to_export(inputs: ScenarioInputs, outputs: ScenarioOutputs) -> Dict:
    """Prepare scenario for CSV/JSON export"""
    return {
        # Inputs
        'scenario_name': inputs.name,
        'wholesale_volume': inputs.wholesale_volume,
        'avg_wholesale_fee': inputs.avg_wholesale_fee,
        'retained_doors': inputs.retained_doors,
        'internal_acq_fee': inputs.internal_acq_fee,
        'memberships_sold': inputs.memberships_sold,
        'membership_price': inputs.membership_price,
        'retail_listings': inputs.retail_listings,
        'weekly_ad_spend': inputs.weekly_ad_spend,
        'cpl': inputs.cpl,
        'fallout_rate': inputs.fallout_rate,
        
        # Key Outputs
        'gross_revenue': outputs.revenue.gross_revenue,
        'total_expenses': outputs.expenses.total_expenses,
        'noi': outputs.comp.noi,
        'hamza_total_comp': outputs.comp.hamza_total_comp,
        'clearroute_dividend': outputs.comp.clearroute_dividend,
        'contracts_per_week': outputs.funnel.contracts_per_week,
        'leads_per_week': outputs.funnel.leads_per_week,
        'lead_to_contract_rate': outputs.funnel.lead_to_contract_rate,
        'closers_needed': outputs.staffing.closers_needed,
        'underwriters_needed': outputs.staffing.underwriters_needed,
        'pms_needed': outputs.staffing.pms_needed
    }
