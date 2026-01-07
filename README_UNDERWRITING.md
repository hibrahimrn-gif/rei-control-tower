# REI Nationwide - Underwriting App System

## 🎯 Overview

Complete underwriting configuration and calculator for **REI Nationwide LLC's** high-velocity distressed property acquisition model.

**Business Model:** 300 DSCR doors + 300 wholesale deals + 100 retail listings per year

---

## 📦 What's Included

### 1. Configuration File
**`/data/underwriting_config.json`**

Comprehensive JSON configuration containing:
- ✅ Company profile & business model
- ✅ 4 primary exit strategies (DSCR, Wholesale, Retail, Membership)
- ✅ Deal criteria & purchase targets (45% ARV max for DSCR)
- ✅ Exit analysis decision tree (Green/Yellow/Red scoring)
- ✅ Underwriting parameters (rehab costs, capital costs, holding costs)
- ✅ Deal routing workflow (5-step process)
- ✅ Formulas for all calculations
- ✅ UI configuration for building forms
- ✅ Integration points (Left Main CRM, Leadzolo, APIs)

### 2. Documentation Guide
**`/UNDERWRITING_GUIDE.md`**

Complete usage guide with:
- ✅ Business model summary
- ✅ Deal routing decision tree (visual flowchart)
- ✅ Underwriting parameters & formulas
- ✅ Deal scoring system (Green/Yellow/Red definitions)
- ✅ 5-step underwriting workflow
- ✅ M Capital funding model details
- ✅ Sample underwriting outputs (3 example deals)
- ✅ Key metrics & targets
- ✅ Integration instructions

### 3. Interactive Calculator
**`/pages/7_🏠_Deal_Underwriter.py`**

Full Streamlit page with:
- ✅ Property input form (address, ARV, purchase price, rehab, rent, etc.)
- ✅ Real-time calculations
- ✅ Color-coded deal scoring (🟢 GREEN / 🟡 YELLOW / 🔴 RED)
- ✅ Routing recommendations
- ✅ DSCR analysis with cashflow projections
- ✅ Wholesale fee calculations
- ✅ ROI & gross profit displays
- ✅ Professional dark-theme UI

---

## 🚀 Quick Start

### Run the Dashboard

```bash
cd rei-control-tower
pip install -r requirements.txt
streamlit run app.py
```

Navigate to: **📊 Deal Underwriter** (Page 7)

---

## 🎨 Deal Scoring Logic

### 🟢 GREEN DEAL → Route to Internal DSCR

**Criteria:**
- Purchase ≤ 45% ARV
- Rehab ≤ $20,000
- Net cashflow ≥ $175/month
- DSCR ≥ 1.30

**Action:** Route to M Capital → Rehab → PM → Long-term hold

**Example:**
```
Property: 123 Oak St, Indianapolis
ARV: $180,000
Purchase: $75,000 (42% ARV) ✅
Rehab: $12,000 ✅
Rent: $1,400/month
DSCR: 1.47 ✅
Net Cashflow: $310/month ✅

SCORE: 🟢 GREEN - ROUTE TO INTERNAL DSCR
```

---

### 🟡 YELLOW DEAL → Route to Wholesale or Retail

**Criteria:**
- Purchase 45-60% ARV OR
- Rehab $20k-$30k
- Wholesale fee potential ≥ $25k
- No major structural issues

**Action:** Assign to cash buyer OR list on MLS

**Example:**
```
Property: 456 Elm Ave, Cleveland
ARV: $140,000
Purchase: $72,000 (51% ARV) ⚠️
Rehab: $25,000 ⚠️
Wholesale Fee: $26,000

SCORE: 🟡 YELLOW - ROUTE TO WHOLESALE
```

---

### 🔴 RED DEAL → Reject/Archive

**Criteria:**
- Rehab > $30k OR
- Purchase > 60% ARV
- Structural issues
- Timeline > 60 days
- Poor wholesale fee potential

**Action:** Archive or refer to partners

**Example:**
```
Property: 789 Maple Dr, Detroit
ARV: $95,000
Purchase: $55,000 (58% ARV) ❌
Rehab: $45,000 (foundation + roof) ❌
Timeline: 90+ days ❌

SCORE: 🔴 RED - REJECT
```

---

## 📊 Key Formulas

```javascript
// Purchase % ARV
purchase_pct_arv = purchase_price / arv

// All-In Cost
all_in_cost = purchase_price + rehab_budget + holding_costs + closing_costs

// Holding Costs
holding_costs = (purchase_price × 0.01 × months) + (utilities + insurance) × months

// DSCR
piti = mortgage_payment + (taxes/12) + (insurance/12)
dscr = monthly_rent / piti

// Net Cashflow
net_cashflow = monthly_rent - piti - (rent × pm_fee_rate)

// Wholesale Fee
wholesale_fee = (arv × 0.70) - purchase_price - buffer
```

---

## 🎯 Target Metrics

| Metric | Annual Target | Weekly Target |
|--------|---------------|---------------|
| **Internal DSCR Doors** | 300 | 5.8 |
| **Wholesale Deals** | 300 | 5.8 |
| **Retail Listings** | 100 | 1.9 |
| **Contracts Signed** | 900 | 17.3 |
| **Leads Required** | ~9,000 | 178 @ $100 CPL |
| **Lead→Contract Rate** | 5-6% | - |

---

## 🔗 Integration Roadmap

### Phase 1: ✅ Complete
- [x] Configuration file created
- [x] Documentation written
- [x] Interactive calculator built
- [x] Deal scoring logic implemented

### Phase 2: 🚧 Pending
- [ ] Connect RealEstateAPI for automated ARV/comps
- [ ] Integrate Zillow/Rentometer APIs for rent estimates
- [ ] Connect to Left Main (Salesforce) CRM
- [ ] PDF export for underwriting packages
- [ ] Save deals to database (SQLite or cloud)

### Phase 3: 🔮 Future
- [ ] Side-by-side deal comparison tool
- [ ] Batch upload via CSV
- [ ] Mobile-responsive PWA version
- [ ] Email/SMS notifications for new deals
- [ ] Portfolio performance tracking

---

## 📁 File Structure

```
rei-control-tower/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Python dependencies
├── PRODUCT_SPEC.md                 # Dashboard spec
├── UNDERWRITING_GUIDE.md           # ⭐ Underwriting documentation
├── README_UNDERWRITING.md          # ⭐ This file
│
├── pages/
│   ├── 1_📊_Overview.py            # Control tower home
│   ├── 2_💰_Pro_Forma.py           # P&L modeling
│   ├── 3_🎯_Funnel_Leads.py        # Lead requirements
│   ├── 4_⚙️_Execution_Plan.py     # Staffing & bottlenecks
│   ├── 5_📈_Scenarios.py           # Scenario planning
│   ├── 6_💰_Investor_Capital.py    # M Capital ROI tracking
│   └── 7_🏠_Deal_Underwriter.py    # ⭐ NEW: Individual deal calculator
│
├── components/
│   ├── calculations.py             # Core formulas
│   ├── visualizations.py           # Charts
│   └── utils.py                    # Helpers
│
└── data/
    ├── default_scenario.json       # Base plan 2026
    └── underwriting_config.json    # ⭐ Underwriting configuration
```

---

## 💡 Usage Examples

### Example 1: Analyze a New Deal

1. Navigate to **📊 Deal Underwriter** (Page 7)
2. Enter property details:
   - ARV: $180,000
   - Purchase Price: $75,000
   - Rehab Budget: $12,000
   - Est. Rent: $1,400/month
3. Click **🔍 Analyze Deal**
4. Review score & routing recommendation
5. If 🟢 GREEN: Route to M Capital → Rehab → PM
6. If 🟡 YELLOW: Route to Wholesale or Retail
7. If 🔴 RED: Archive or pass

### Example 2: Batch Analysis (Future)

1. Export CSV template
2. Fill in 50 properties
3. Upload CSV
4. Get instant Green/Yellow/Red scores
5. Auto-route to appropriate chutes

### Example 3: API Integration (Future)

```python
# Auto-populate ARV from RealEstateAPI
response = requests.get(f"https://api.realestate.com/arv?address={address}")
arv = response.json()['arv']

# Auto-populate rent from Rentometer
rent_response = requests.get(f"https://api.rentometer.com/estimate?address={address}")
estimated_rent = rent_response.json()['median_rent']
```

---

## 🎓 Business Model Context

### REI Nationwide "Conveyor Belt" Model

**Philosophy:** High-velocity distressed property pipeline with clear exit routing

**Exits:**
1. **Internal DSCR (Priority 1):** Buy ≤45% ARV, light rehab, hold for cashflow
2. **Wholesale (Priority 2):** Cannot hold? Assign for $30k fee
3. **Retail Listing (Priority 3):** Retail-ready? List on MLS
4. **Membership DFY:** Sell turnkey service to investor clients

**Capital Partner:** M Capital
- 100% funding (Purchase + Rehab)
- Max $20k rehab budget
- 45-day deal cycle
- Target: 100% annual ROI (2x in 12 months)

**Lead Flow:** ~178 leads/week @ $100 CPL → 18 contracts/week → 14 closed deals/week

**Staffing:** Closers, Underwriters, PMs, TCs, Dispo Agents, DSCR Coordinators

---

## 📞 Support & Feedback

- **Dashboard Issues:** See `/PRODUCT_SPEC.md`
- **Underwriting Questions:** See `/UNDERWRITING_GUIDE.md`
- **API Integrations:** See `config['integrations']` in `/data/underwriting_config.json`

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0** | 2026-01-07 | Initial underwriting system created |

---

**Built for:** REI Nationwide LLC
**Maintained By:** Internal Dev Team
**Last Updated:** January 7, 2026
