# Wholesale-Only 12-Month Projection Model

## Executive Summary

This model projects a 12-month wholesale-only operation (100% assignment fees) with investor-funded marketing capital. Overhead is covered separately for equity; this model focuses purely on marketing → deals → cash flow → principal payback.

---

## 1. Base Case: 12-Month Projection (Lagged Model)

### Assumptions

| Parameter | Value |
|-----------|-------|
| CAC (Cost per Closed Deal) | $3,500 |
| Avg Assignment Fee | $20,000 |
| Lead-to-Close Time | 24 days |
| Lag Model | 20% close same month; 80% close next month |
| Principal Payback | 100% marketing capital repaid from revenue before profit |
| Business Days/Month | 22 |
| Fallout Rate | 0% (Base Case) |
| **Pod System** | |
| Files per Pod | 50 |
| Pod Annual Cost | $50,000 |
| Buyers Added/Day (nationwide) | 300+ |
| Buyers per Pod/Day | 100 |

### Monthly Projection Table

| Month | Marketing Spend | Deals Gen. | Deals Closed | Closings/Day | Gross Revenue | Principal Payback | Net Profit | Cumulative Profit |
|-------|-----------------|------------|--------------|--------------|---------------|-------------------|------------|-------------------|
| 1 | $50,000 | 14 | 3 | 0.1 | $60,000 | $50,000 | $10,000 | $10,000 |
| 2 | $300,000 | 86 | 29 | 1.3 | $580,000 | $300,000 | $280,000 | $290,000 |
| 3 | $600,000 | 171 | 103 | 4.7 | $2,060,000 | $600,000 | $1,460,000 | $1,750,000 |
| 4 | $900,000 | 257 | 189 | 8.6 | $3,780,000 | $900,000 | $2,880,000 | $4,630,000 |
| 5 | $1,200,000 | 343 | 274 | 12.5 | $5,480,000 | $1,200,000 | $4,280,000 | $8,910,000 |
| 6 | $1,200,000 | 343 | 343 | 15.6 | $6,860,000 | $1,200,000 | $5,660,000 | $14,570,000 |
| 7 | $1,200,000 | 343 | 343 | 15.6 | $6,860,000 | $1,200,000 | $5,660,000 | $20,230,000 |
| 8 | $1,200,000 | 343 | 343 | 15.6 | $6,860,000 | $1,200,000 | $5,660,000 | $25,890,000 |
| 9 | $1,200,000 | 343 | 343 | 15.6 | $6,860,000 | $1,200,000 | $5,660,000 | $31,550,000 |
| 10 | $1,200,000 | 343 | 343 | 15.6 | $6,860,000 | $1,200,000 | $5,660,000 | $37,210,000 |
| 11 | $1,200,000 | 343 | 343 | 15.6 | $6,860,000 | $1,200,000 | $5,660,000 | $42,870,000 |
| 12 | $1,200,000 | 343 | 343 | 15.6 | $6,860,000 | $1,200,000 | $5,660,000 | $48,530,000 |
| **TOTAL** | **$11,450,000** | **3,272** | **2,999** | **N/A** | **$59,980,000** | **$11,450,000** | **$48,530,000** | **$48,530,000** |

### Calculation Notes

**Deals Generated (Exact Values):**
- Month 1: 14.29 → rounded to 14
- Month 2: 85.71 → rounded to 86
- Month 3: 171.43 → rounded to 171
- Month 4: 257.14 → rounded to 257
- Months 5-12: 342.86 → rounded to 343

**Lagged Deals Closed Formula:**
```
Deals Closed(m) = 0.20 × Deals Generated(m) + 0.80 × Deals Generated(m-1)
```

---

## 2. CSV Data Block (Base Case - Lagged)

Copy and paste directly into Google Sheets:

```csv
Month,Marketing Spend,Deals Generated (Exact),Deals Generated (Rounded),Deals Closed (Exact),Deals Closed (Rounded),Closings/Day (22d),Gross Revenue,Marketing Cost,Net Profit,Cumulative Net Profit,Principal Payback,Principal Remaining,Ending Cash
1,50000,14.29,14,2.86,3,0.14,60000,50000,10000,10000,50000,0,10000
2,300000,85.71,86,28.57,29,1.32,580000,300000,280000,290000,300000,0,290000
3,600000,171.43,171,102.86,103,4.68,2060000,600000,1460000,1750000,600000,0,1750000
4,900000,257.14,257,188.57,189,8.59,3780000,900000,2880000,4630000,900000,0,4630000
5,1200000,342.86,343,274.29,274,12.45,5480000,1200000,4280000,8910000,1200000,0,8910000
6,1200000,342.86,343,342.86,343,15.59,6860000,1200000,5660000,14570000,1200000,0,14570000
7,1200000,342.86,343,342.86,343,15.59,6860000,1200000,5660000,20230000,1200000,0,20230000
8,1200000,342.86,343,342.86,343,15.59,6860000,1200000,5660000,25890000,1200000,0,25890000
9,1200000,342.86,343,342.86,343,15.59,6860000,1200000,5660000,31550000,1200000,0,31550000
10,1200000,342.86,343,342.86,343,15.59,6860000,1200000,5660000,37210000,1200000,0,37210000
11,1200000,342.86,343,342.86,343,15.59,6860000,1200000,5660000,42870000,1200000,0,42870000
12,1200000,342.86,343,342.86,343,15.59,6860000,1200000,5660000,48530000,1200000,0,48530000
TOTAL,11450000,3271.43,3272,2998.57,2999,N/A,59980000,11450000,48530000,48530000,11450000,0,48530000
```

---

## 3. Scenario Analysis (12-Month Totals)

### Scenario Definitions

| Scenario | CAC | Assignment Fee | Fallout |
|----------|-----|----------------|---------|
| **Base** | $3,500 | $20,000 | 0% |
| **Conservative** | $4,375 (+25%) | $17,000 (-15%) | 10% |
| **Aggressive** | $3,150 (-10%) | $22,000 (+10%) | 0% |

### Comparison Table

| Metric (12-Month Total) | Conservative | Base Case | Aggressive |
|-------------------------|--------------|-----------|------------|
| Total Spend | $11,450,000 | $11,450,000 | $11,450,000 |
| Deals Generated | 2,617 | 3,272 | 3,635 |
| Deals Closed (incl. fallout) | 2,159 | 2,999 | 3,332 |
| Total Revenue | $36,703,000 | $59,980,000 | $73,304,000 |
| Net Profit (After Payback) | $25,253,000 | $48,530,000 | $61,854,000 |
| ROI (Profit / Spend) | **2.2x** | **4.2x** | **5.4x** |

---

## 4. Investor Equity Return Model

### A) Formulas (Using Variables)

Since overhead is covered for equity, the investor's cash return comes from Net Profit.

**Variables:**
- `N` = Net Profit After Marketing (from projection table)
- `E` = Investor Equity % (ownership stake)
- `D` = Profit Distribution % (how much profit is distributed vs. retained)

**Formula:**
```
Investor Distribution = N × E × D
```

**Example Calculation:**
- N = $48,530,000 (Base Case Net Profit)
- E = 20% (Investor owns 20%)
- D = 50% (Half of profit distributed)

```
Investor Distribution = $48,530,000 × 0.20 × 0.50 = $4,853,000
```

### B) Investor Cash Distribution Grid

Based on **$48,530,000 Net Profit** (Base Case):

| Equity Stake | Distribute 0% (Reinvest) | Distribute 50% (Split) | Distribute 100% (Max Cash) |
|--------------|--------------------------|------------------------|---------------------------|
| **10%** | $0 | $2,426,500 | $4,853,000 |
| **20%** | $0 | $4,853,000 | $9,706,000 |
| **30%** | $0 | $7,279,500 | $14,559,000 |

**Reading the table:**
- Row = Investor's equity stake
- Column = How much profit is distributed vs. reinvested
- Cell = Total cash paid to investor over 12 months

---

## 5. Pod System Scaling Schedule

The pod system provides scalable operational capacity with 50 files per pod and $50K annual cost per pod.

### Pod Scaling by Month

| Month | Deals Closed | Pods Needed | Pods to Hire | Monthly Pod Cost | Buyers Added | Buyers/Deal |
|-------|--------------|-------------|--------------|------------------|--------------|-------------|
| 1 | 3 | 1 | 1 | $4,167 | 8,800 | 2,933x |
| 2 | 29 | 1 | - | $4,167 | 8,800 | 303x |
| 3 | 103 | 3 | 2 | $12,500 | 13,200 | 128x |
| 4 | 189 | 4 | 1 | $16,667 | 15,400 | 81x |
| 5 | 274 | 6 | 2 | $25,000 | 19,800 | 72x |
| 6 | 343 | 7 | 1 | $29,167 | 22,000 | 64x |
| 7-12 | 343 | 7 | - | $29,167 | 22,000 | 64x |
| **TOTAL** | **2,999** | **MAX: 7** | **7 hires** | **$291,667** | **230,600** | **AVG: 77x** |

### Pod System Economics

| Metric | Value |
|--------|-------|
| Total Pod Overhead (12mo) | $291,667 |
| Marketing Capital | $11,450,000 |
| **Total Investor Outlay** | **$11,741,667** |
| Buyer Pipeline (12mo) | 230,600 buyers |
| Buyer Coverage Ratio | 77x (avg buyers per deal) |

---

## 6. CFO Summary: Key Takeaways & Risk Analysis

### Key Takeaways

1. **Cash Efficiency:** The model is self-liquidating from Month 1. Revenue ($60K) covers principal ($50K) immediately. You never carry a marketing "debt" balance in the Base Case.

2. **Volume Implication:** By Month 6, you are closing **343 deals/month** with **7 pods** (50 files each). This is "factory scale" wholesaling with a scalable operational model.

3. **Buyer Pipeline:** 300+ buyers/day nationwide = **22,000+ buyers/month** at steady state. With 343 deals/month, you have **64x buyer coverage** per deal. Dispo is NOT a bottleneck.

4. **Profitability:** The model yields **$48.5M in net profit** on **$11.74M total investor outlay** (marketing + pods). This is **4.1x ROI** on total capital.

5. **Principal Payback:** 100% of marketing capital is repaid within the same month closings occur. The 30-day payback expectation is met every month in the Base Case.

### Risk Analysis (with Pod System)

| Risk Category | Status | Description | Mitigation |
|---------------|--------|-------------|------------|
| **Dispo Bottleneck** | ✅ MITIGATED | Pod system + 300 buyers/day nationwide SOLVES dispo capacity. 64x buyer coverage per deal. | Monitor buyer quality and deal-to-buyer match rate. |
| **Market Saturation** | ✅ MITIGATED | Nationwide operation = no single market dependency. Seller inventory distributed. | Monitor per-market CAC for early saturation signals. |
| **Buyer Capacity** | ✅ MITIGATED | 300+ buyers/day + pod buyer acquisition = 22,000+ new buyers/month at steady state. | Focus on buyer quality over quantity. |
| **CAC Creep at Scale** | ⚠️ MONITOR | $3,500 CAC benchmarked at low spend may increase at $1.2M/month due to audience saturation. | Nationwide footprint diversifies risk. Monitor CAC by market; rotate creative weekly. |
| **Cash Timing** | ⚠️ MONITOR | Title delays, buyer financing issues can stretch actual close beyond 30 days. | Build 15-day buffer into projections; negotiate flexible payback terms. |
| **Pod Scaling Speed** | ⚠️ MONITOR | Ramping from 1 pod to 7 pods in 6 months requires hiring pipeline. | Start recruiting Month 1 for Month 3+ needs. Build bench of 2 pods ahead. |

### Operational Reality Check (with Pod System)

At steady state (Months 6-12):
- **343 deals/month** handled by **7 pods** (50 files each)
- **22,000 buyers added/month** = 64x coverage per deal
- Pod overhead: **$29,167/month** (investor covers)
- Total investor commitment: **$11.74M** (marketing + pods)

✅ **Dispo bottleneck SOLVED** with pod system + nationwide buyer acquisition.

**The math works. The physics now works too.**

---

## 7. Model Comparison: Lagged vs No-Lag

| Model | Total Deals Closed | Total Revenue | Net Profit | ROI |
|-------|-------------------|---------------|------------|-----|
| **No-Lag (Optimistic)** | 3,272 | $65,440,000 | $53,990,000 | 4.7x |
| **Lagged (Realistic)** | 2,999 | $59,980,000 | $48,530,000 | 4.2x |

**Note:** The lagged model accounts for the 24-day average close time by assuming 20% of deals close same-month and 80% roll to the following month. This creates a more realistic cash flow projection, especially in ramp-up months.

---

## Appendix: Marketing Ladder Input

| Month | Marketing Spend |
|-------|-----------------|
| 1 | $50,000 |
| 2 | $300,000 |
| 3 | $600,000 |
| 4 | $900,000 |
| 5 | $1,200,000 |
| 6 | $1,200,000 |
| 7 | $1,200,000 |
| 8 | $1,200,000 |
| 9 | $1,200,000 |
| 10 | $1,200,000 |
| 11 | $1,200,000 |
| 12 | $1,200,000 |
| **TOTAL** | **$11,450,000** |

---

*Model generated for REI Nationwide LLC - January 2026*
