# REI Nationwide - Underwriting App Configuration Guide

## Overview

This guide explains how to use the `underwriting_config.json` configuration file to build deal analysis tools for REI Nationwide's high-velocity acquisition model.

---

## Business Model Summary

**REI Nationwide LLC** operates a "conveyor belt" model for distressed properties:

### Primary Exit Strategies (Priority Order):

1. **Internal DSCR Acquisition** (300 doors/year)
   - Buy ≤ 45% ARV
   - Light rehab ≤ $20k
   - Stabilize & refinance with M Capital
   - Target: $175/month net cashflow per door

2. **Wholesale Disposition** (300 deals/year)
   - Properties that don't fit internal model
   - Minimum $30k assignment fee
   - Quick turn to cash buyers

3. **Retail Listing** (100 listings/year)
   - Retail-ready properties or high seller net requirements
   - 3% commission on ~$250k average listing

4. **Membership DFY** (150 clients/year)
   - Done-for-you service for investor clients
   - $15k price point

---

## Deal Routing Decision Tree

```
┌─────────────────────────────────────┐
│   Lead Intake (PPC/Marketing)       │
│   Target: 178 leads/week @ $100 CPL │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Initial Screen (Closer)           │
│   Quick ARV check                   │
└──────────────┬──────────────────────┘
               │
               ▼
       ┌───────┴───────┐
       │               │
       ▼               ▼
   Purchase ≤ 45% ARV?    Purchase > 45% ARV?
   Rehab ≤ $20k?          OR Rehab > $20k?
       │                   │
       │                   │
       ▼                   ▼
   🟢 GREEN DEAL       🟡 YELLOW DEAL
   Route to DSCR       Route to Wholesale
       │                   │
       │                   ▼
       │               Can wholesale
       │               for $30k+ fee?
       │                   │
       │              ┌────┴────┐
       │              │         │
       │              ▼         ▼
       │            YES        NO
       │             │          │
       │             ▼          ▼
       │         Wholesale   🔴 RED DEAL
       │                     REJECT/Archive
       │
       ▼
   Full Underwrite
   M Capital package
   PM assignment
   45-day cycle
```

---

## Underwriting Parameters

### Purchase Price Targets

| Exit Strategy | Max Purchase % ARV | Max Rehab | Timeline |
|---------------|-------------------|-----------|----------|
| **DSCR Internal** | **45%** | **$20k** | 45 days |
| Wholesale | 55-70% | Any | 15 days |
| Retail Listing | Any | Retail ready | 30 days |

### Rehab Cost Tiers

| Tier | $/sqft | Typical Total | Scope | Status |
|------|--------|---------------|-------|--------|
| **Light Refresh** | $5-15 | $3k-10k | Paint, clean, minor repairs | ✅ ACCEPTABLE |
| **Cosmetic** | $15-35 | $10k-20k | Flooring, kitchen/bath, paint | ✅ ACCEPTABLE |
| **Gut Rehab** | $50-100 | $30k+ | Full renovation | 🔴 REJECT |

### Financial Calculations

```javascript
// Purchase % ARV
purchase_pct_arv = purchase_price / arv

// All-In Cost
all_in_cost = purchase_price
            + rehab_budget
            + holding_costs
            + closing_costs_buy

// Holding Costs (per month)
holding_costs = (purchase_price × 0.01 × months_held)
              + (utilities + insurance) × months_held

// Closing Costs
closing_costs_buy = purchase_price × 0.03  // 3%
closing_costs_sell = arv × 0.01             // 1%

// DSCR Calculation
piti = mortgage_payment + (taxes/12) + (insurance/12)
dscr = monthly_rent / piti

// Net Cashflow
net_cashflow = monthly_rent - piti - (rent × pm_fee_rate)

// Wholesale Fee Calculation
wholesale_fee = (arv × 0.70) - purchase_price - buffer
```

---

## Deal Scoring System

### 🟢 GREEN DEAL (Route to Internal DSCR)

**Criteria:**
- ✅ Purchase ≤ 45% ARV
- ✅ Rehab ≤ $20k
- ✅ 45-day turn possible
- ✅ Net rent ≥ $175/month
- ✅ DSCR ≥ 1.30

**Action:** Route to M Capital → Rehab → PM → Long-term hold

---

### 🟡 YELLOW DEAL (Route to Wholesale or Retail)

**Criteria:**
- Purchase 45-55% ARV OR
- Rehab $20k-$30k
- Can wholesale for $30k+ fee
- No major structural issues

**Action:**
- If wholesale buyer exists → Assign contract
- If retail-ready → MLS listing

---

### 🔴 RED DEAL (Reject/Archive)

**Criteria:**
- ❌ Rehab > $30k
- ❌ Structural issues (foundation, roof, mold)
- ❌ Timeline > 60 days
- ❌ Buy > 55% ARV with no wholesale market

**Action:** Archive or refer to partners

---

## Underwriting Workflow (5 Steps)

### Step 1: Lead Intake
- **Responsible:** Closer
- **Input:** Lead from PPC/Leadzolo
- **Output:** Basic property info (address, condition, seller asking price)

### Step 2: Initial Screen
- **Responsible:** Closer
- **Tools:** Zillow, Redfin, RealEstateAPI
- **Quick Check:** Does it fit 45% ARV model?
- **Decision:** If NO → Skip to wholesale routing

### Step 3: Full Underwrite
- **Responsible:** Underwriter
- **Tasks:**
  - Detailed comp analysis (3+ comps within 0.5mi)
  - Rehab walkthrough & bid
  - Rent validation (Rentometer, PM feedback)
  - DSCR calculation
- **Output:** Underwriting package with Green/Yellow/Red score

### Step 4: Offer Presentation
- **Responsible:** Closer
- **Output:** Signed purchase agreement OR counter OR rejection
- **Target:** 4:1 offer-to-contract ratio

### Step 5: Contract to Close
- **Responsible:** TC (Transaction Coordinator)
- **Routing:**
  - **Green DSCR:** → M Capital funding → Rehab contractor → PM
  - **Yellow Wholesale:** → Dispo agent → Buyer blast
  - **Yellow Retail:** → Listing agent → MLS prep

---

## M Capital Funding Model

| Parameter | Value |
|-----------|-------|
| **Funding Coverage** | 100% of Purchase + Rehab |
| **Max Rehab** | $20,000 |
| **Deal Cycle** | 45 days |
| **Cost Structure** | Flat fee (~15% per deal, ~$13,500 avg) |
| **Annual ROI Target** | 100% (2x in 12 months) |
| **Volume Target** | 300 doors/year |

**Example:**
- Purchase: $100k
- Rehab: $15k
- M Capital funds: $115k (100%)
- M Capital fee: $17,250 (15%)
- Timeline: 45 days
- Exit: DSCR refi into long-term rental

---

## Integration Points

### CRM: Left Main (Salesforce)
- Lead tracking
- Pipeline management
- Contract status

### Marketing: Leadzolo PPC
- Weekly spend: $34,400
- Target CPL: $100
- Target leads/week: 178

### Property Data APIs
- **RealEstateAPI:** Comps, property details
- **Zillow API:** ARV estimates, rent estimates
- **Rentometer:** Rent validation
- **PropStream:** Market analysis, comps

### Hosting
- **Current:** Python/Streamlit
- **Future Option:** React/Next.js on Vercel/Netlify

---

## Sample Underwriting Outputs

### Example 1: Green DSCR Deal ✅

**Property:** 123 Oak Street, Indianapolis, IN
**ARV:** $180,000
**Purchase Price:** $75,000 (42% ARV) ✅
**Rehab Budget:** $12,000 (cosmetic) ✅
**Sqft:** 1,200
**Est. Rent:** $1,400/month

**Calculations:**
- All-in cost: $75k + $12k + $2.5k (holding) + $2.3k (closing) = **$91,800**
- PITI: $950/month (loan + tax + ins)
- DSCR: $1,400 / $950 = **1.47** ✅
- Net Cashflow: $1,400 - $950 - $140 (PM) = **$310/month** ✅

**Score:** 🟢 **GREEN - Route to Internal DSCR**

---

### Example 2: Yellow Wholesale Deal

**Property:** 456 Elm Avenue, Cleveland, OH
**ARV:** $140,000
**Purchase Price:** $72,000 (51% ARV) ⚠️
**Rehab Budget:** $25,000 ⚠️
**Sqft:** 1,100

**Calculations:**
- Too high % ARV for M Capital model
- Rehab exceeds $20k threshold
- Wholesale fee potential: ($140k × 0.70) - $72k = **$26,000**

**Score:** 🟡 **YELLOW - Route to Wholesale** (fee below $30k target, negotiate down or pass)

---

### Example 3: Red Reject Deal ❌

**Property:** 789 Maple Drive, Detroit, MI
**ARV:** $95,000
**Purchase Price:** $55,000 (58% ARV) ❌
**Rehab Budget:** $45,000 (foundation + roof) ❌
**Timeline:** 90+ days ❌

**Score:** 🔴 **RED - REJECT**
**Reason:** Structural issues, rehab too high, buy % too high, no wholesale market

---

## Key Metrics & Targets

| Metric | Target | Current Status |
|--------|--------|----------------|
| **Contracts/Week** | 18 | Track in dashboard |
| **Leads/Week** | 178 @ $100 CPL | Track in dashboard |
| **Lead→Contract Rate** | 5-6% | Track in dashboard |
| **Internal DSCR Doors/Year** | 300 | Track in dashboard |
| **Wholesale Deals/Year** | 300 | Track in dashboard |
| **Avg Wholesale Fee** | $30,000 | Track in dashboard |
| **Retail Listings/Year** | 100 | Track in dashboard |
| **Fallout Rate** | 20% | Track in dashboard |

---

## Building the Underwriting App

### Recommended UI Components

1. **Deal Input Form**
   - Address, ARV, Purchase Price, Rehab Budget
   - Sqft, Beds, Baths, Condition dropdown
   - Estimated rent, holding period

2. **Real-Time Calculations Display**
   - Purchase % ARV (color-coded)
   - All-in cost breakdown
   - DSCR calculation
   - Net cashflow projection
   - Wholesale fee potential

3. **Deal Score Badge**
   - Large, color-coded: 🟢 GREEN / 🟡 YELLOW / 🔴 RED
   - Recommended exit strategy

4. **Routing Recommendation**
   - "Route to Internal DSCR" with checklist
   - "Route to Wholesale - Expected fee: $XX,XXX"
   - "REJECT - Reason: [...]"

5. **Export/Save Options**
   - Save to CRM (Left Main integration)
   - Export PDF underwriting package
   - Save to scenario comparison

### Integration with Existing Dashboard

The underwriting app should integrate with the existing **REI Control Tower** pages:

- **Page 2 (Pro Forma):** Uses aggregate deal targets (300 DSCR, 300 wholesale)
- **Page 3 (Funnel):** Feeds contract volume requirements
- **Page 4 (Execution Plan):** Staffing needs based on deal flow
- **NEW Page 7:** **Deal Underwriter** (individual deal calculator)

---

## Next Steps

1. ✅ Configuration created (`underwriting_config.json`)
2. ⬜ Build Streamlit underwriting calculator page
3. ⬜ Integrate RealEstateAPI for automated ARV/comps
4. ⬜ Connect to Left Main CRM for deal tracking
5. ⬜ Add export to PDF underwriting package
6. ⬜ Build deal comparison view (side-by-side analysis)

---

**Version:** 1.0
**Last Updated:** January 7, 2026
**Maintained By:** REI Nationwide LLC
