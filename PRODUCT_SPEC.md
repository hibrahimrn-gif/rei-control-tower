# REI Nationwide LLC - Dynamic View Dashboard
## Product Specification v1.0

---

## Architecture Decision

**Selected: Option A - Python + Streamlit Multipage App**

### Rationale:
1. **Speed to MVP**: Streamlit allows rapid prototyping with minimal boilerplate
2. **Native Data Handling**: Pandas integration for financial calculations
3. **Interactive Widgets**: Built-in sliders, inputs, and real-time updates
4. **Visualization**: Native chart support + Plotly integration
5. **Session State**: Easy scenario management without external database
6. **Single Codebase**: All Python, easier maintenance for your team

---

## Pages & Features

### Page 1: Overview (Home)
**Purpose**: Executive snapshot - "Control Tower" view

**Outputs**:
- KPI Cards: Gross Revenue, NOI, CEO Comp, Contracts/Week, Leads/Week
- High-level Funnel Visualization (Leads → Contracts → Outcomes)
- Critical Alerts Panel (bottlenecks, capacity warnings)
- Quick scenario selector

### Page 2: Pro Forma
**Purpose**: Full P&L with adjustable drivers

**Inputs**:
- Revenue Drivers (wholesale volume, avg fee, retained doors, memberships, listings)
- Commission Rates (president override, acq, dispo, membership)
- Marketing (weekly ad spend, CPL)
- Salaries (executive, staff)

**Outputs**:
- Revenue breakdown by line
- Expense breakdown by category
- NOI calculation
- Comp splits (Hamza, Clearroute)

### Page 3: Funnel & Lead Requirements
**Purpose**: Work backwards from outcomes to required lead volume

**Inputs**:
- Target outcomes (can pull from Pro Forma or override)
- Fallout rate
- Pipeline split percentages

**Outputs**:
- Contracts needed/year & /week
- Leads needed/year & /week
- Required Lead→Contract conversion rate
- Leads per contract ratio
- Weekly outcome targets by chute

### Page 4: Execution Plan
**Purpose**: Operational control tower

**Outputs**:
- Weekly Scoreboard (all targets in one view)
- Staffing Calculator with capacity inputs
- Bottleneck Alerts (color-coded)
- Recommended actions

**Staffing Inputs**:
- Closer capacity (leads/week, contracts/week)
- Underwriter capacity (underwrites/week)
- PM capacity (active rehabs)
- TC capacity (contracts/week)
- Dispo capacity (wholesales/week)
- DSCR Coordinator capacity (refis/week)
- Membership call metrics (close rate, show rate)

### Page 5: Sensitivity & Scenarios
**Purpose**: Stress testing and scenario planning

**Features**:
- Save/Load scenarios to JSON
- Side-by-side comparison (2+ scenarios)
- Sensitivity Tables:
  - CPL sensitivity (impact on leads, required conversion)
  - Fallout rate sensitivity
  - Conversion rate sensitivity
- Export to CSV/JSON

---

## Data Model & Formulas

### Core Revenue Calculations
```
wholesale_revenue = wholesale_volume × avg_wholesale_fee
internal_revenue = retained_doors × internal_acq_fee
membership_revenue = memberships × membership_price
listing_revenue = retail_listings × avg_retail_price × listing_commission_rate
gross_revenue = wholesale + internal + membership + listing + property_mgmt
```

### Core Expense Calculations
```
president_override = gross_revenue × 0.10
acq_commissions = (wholesale_revenue + internal_revenue) × 0.10
dispo_commissions = wholesale_revenue × 0.05
membership_commissions = membership_revenue × 0.10
marketing_spend = weekly_ad_spend × 52
total_expenses = president_override + commissions + marketing + salaries
```

### NOI & Comp Splits
```
noi = gross_revenue - total_expenses
hamza_draw = noi × 0.25
hamza_salary = 480000
hamza_total = hamza_draw + hamza_salary
clearroute_dividend = noi × 0.20
```

### Funnel Calculations
```
monetized_outcomes = wholesale_volume + retained_doors + retail_listings
contracts_needed = monetized_outcomes / (1 - fallout_rate)
contracts_per_week = contracts_needed / 52
leads_per_week = weekly_ad_spend / cpl
leads_per_year = leads_per_week × 52
lead_to_contract_rate = contracts_needed / leads_per_year
leads_per_contract = leads_per_year / contracts_needed
```

### Weekly Targets
```
internal_per_week = retained_doors / 52
wholesale_per_week = wholesale_volume / 52
retail_per_week = retail_listings / 52
fallout_per_week = contracts_per_week × fallout_rate
membership_per_week = memberships / 52
```

### Staffing Calculations
```
closers_needed_leads = leads_per_week / closer_lead_capacity
closers_needed_contracts = contracts_per_week / closer_contract_capacity
closers_needed = max(closers_needed_leads, closers_needed_contracts)

offers_per_week = contracts_per_week × offer_to_contract_ratio
underwriters_needed = offers_per_week / underwriter_capacity

active_rehabs = internal_per_week × (rehab_cycle_days / 7)
pms_needed = active_rehabs / pm_capacity

tcs_needed = contracts_per_week / tc_capacity
dispo_needed = wholesale_per_week / dispo_capacity
dscr_needed = internal_per_week / dscr_capacity

held_calls_needed = membership_per_week / close_rate
booked_calls_needed = held_calls_needed / show_rate
```

---

## Validation Rules

| Input | Validation |
|-------|------------|
| fallout_rate | 0.0 - 0.50 |
| cpl | > 0 |
| conversion_rate | 0.01 - 0.30 |
| commission_rates | 0.0 - 0.50 |
| volumes | >= 0, integer |
| capacities | > 0 |

---

## File Structure
```
rei-control-tower/
├── app.py                    # Main Streamlit app entry
├── requirements.txt          # Python dependencies
├── PRODUCT_SPEC.md          # This document
├── pages/
│   ├── 1_📊_Overview.py
│   ├── 2_💰_Pro_Forma.py
│   ├── 3_🎯_Funnel_Leads.py
│   ├── 4_⚙️_Execution_Plan.py
│   └── 5_📈_Scenarios.py
├── components/
│   ├── __init__.py
│   ├── calculations.py      # All formula logic
│   ├── visualizations.py    # Chart builders
│   └── utils.py             # Helpers, validation
├── data/
│   ├── default_scenario.json
│   └── scenarios/           # Saved scenarios
└── uploads/                 # For actual vs target CSVs
```

---

## Default Scenario: "2026 Base Plan"

All values per your pro forma - pre-loaded on app startup.

---

## Run Instructions (Preview)

```bash
cd rei-control-tower
pip install -r requirements.txt
streamlit run app.py
```

Access at: http://localhost:8501
