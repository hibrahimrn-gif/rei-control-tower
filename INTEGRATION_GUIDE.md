# REI Nationwide - Integration Guide

## 🚀 Quick Start

All new features are now ready to use in your dashboard! Access them at:

- **Page 7:** 🏠 Deal Underwriter (Individual calculator)
- **Page 8:** 📊 Batch Upload (CSV batch processing)
- **Page 9:** ⚖️ Deal Comparison (Side-by-side comparison)

---

## 📋 New Features Overview

### 1. ✅ API Integrations

**File:** `/components/api_integrations.py`

**Supported APIs:**
- RealEstateAPI - Property details, comps, ARV estimates
- Zillow API - Zestimate, Rent Zestimate
- Rentometer API - Rent estimates

**Setup:**

```bash
# Set environment variables
export REALESTATE_API_KEY="your_api_key_here"
export ZILLOW_API_KEY="your_api_key_here"
export RENTOMETER_API_KEY="your_api_key_here"
```

**Usage:**

```python
from components.api_integrations import fetch_property_data

# Fetch comprehensive property data
property_data = fetch_property_data(
    address="123 Oak St, Indianapolis, IN 46201",
    sqft=1200
)

print(f"ARV: ${property_data.arv:,}")
print(f"Estimated Rent: ${property_data.estimated_rent:,}")
print(f"Source: {property_data.arv_source}")
```

**Features:**
- ✅ Auto-populate ARV from multiple sources
- ✅ Weighted average of estimates (high confidence sources prioritized)
- ✅ Rent estimates from Zillow + Rentometer
- ✅ Property details (sqft, beds, baths, year built)
- ✅ Comparable sales (comps) for ARV validation
- ✅ Confidence levels (high/medium/low)
- ✅ Graceful fallback if APIs unavailable (mock data for testing)

---

### 2. ✅ CRM Connector (Left Main / Salesforce)

**File:** `/components/crm_connector.py`

**Setup:**

```bash
# Set Salesforce credentials
export SALESFORCE_USERNAME="your_email@company.com"
export SALESFORCE_PASSWORD="your_password"
export SALESFORCE_SECURITY_TOKEN="your_security_token"
export SALESFORCE_CLIENT_ID="your_connected_app_client_id"
export SALESFORCE_CLIENT_SECRET="your_connected_app_secret"
export LEFTMAIN_INSTANCE_URL="https://leftmain.my.salesforce.com"
```

**Salesforce Setup Steps:**

1. **Create Connected App:**
   - Setup → Apps → App Manager → New Connected App
   - Enable OAuth Settings
   - Add OAuth Scopes: `full`, `refresh_token`, `offline_access`
   - Copy Consumer Key (Client ID) and Consumer Secret

2. **Get Security Token:**
   - Settings → My Personal Information → Reset Security Token
   - Token will be emailed to you

3. **Create Custom Fields** (if not already exists):
   - Property_Address__c (Text)
   - ARV__c (Currency)
   - Purchase_Price__c (Currency)
   - Rehab_Budget__c (Currency)
   - Estimated_Rent__c (Currency)
   - Deal_Score__c (Picklist: GREEN, YELLOW, RED)
   - Recommended_Exit__c (Text)

**Usage:**

```python
from components.crm_connector import Deal, save_deal_to_crm

# Create deal object
deal = Deal(
    address="123 Oak St",
    arv=180000,
    purchase_price=75000,
    rehab_budget=12000,
    estimated_rent=1400,
    deal_score="GREEN",
    recommended_exit="ROUTE TO INTERNAL DSCR"
)

# Save to CRM
result = save_deal_to_crm(deal)
print(result)  # {'success': True, 'data': {...}}
```

**Features:**
- ✅ Create deals in Salesforce
- ✅ Update existing deals
- ✅ Query deals by filters
- ✅ Add notes to deals
- ✅ Auto-sync from underwriting calculator
- ✅ Handles authentication (OAuth 2.0)

---

### 3. ✅ Batch Upload Feature (CSV)

**Page:** 📊 Batch Upload (Page 8)
**File:** `/components/batch_processor.py`

**How to Use:**

1. **Download CSV Template:**
   - Click "📄 Download CSV Template" button
   - Template includes sample data

2. **Fill in Your Deals:**
   - Required: address, arv, purchase_price, rehab_budget, estimated_rent
   - Optional: sqft, bedrooms, bathrooms, holding_months, notes

3. **Upload CSV:**
   - Click "Choose a CSV file"
   - Upload your completed file

4. **Review Results:**
   - Summary stats (Green/Yellow/Red counts)
   - Routing breakdown (DSCR/Wholesale/Retail/Reject)
   - Detailed results table (color-coded by score)

5. **Export Results:**
   - Export all results
   - Export only GREEN deals
   - Export only YELLOW deals

**Example CSV:**

```csv
address,arv,purchase_price,rehab_budget,estimated_rent,sqft
"123 Oak St, Indianapolis, IN",180000,75000,12000,1400,1200
"456 Elm Ave, Cleveland, OH",140000,72000,25000,1100,1100
"789 Maple Dr, Detroit, MI",95000,55000,45000,900,1050
```

**Features:**
- ✅ Process 50+ deals at once
- ✅ Automatic scoring (Green/Yellow/Red)
- ✅ Validation with error messages
- ✅ Routing recommendations
- ✅ Full calculations (DSCR, cashflow, wholesale fees)
- ✅ Export filtered results
- ✅ Color-coded visualization

---

### 4. ✅ PDF Export Functionality

**File:** `/components/pdf_export.py`

**Setup (Optional):**

PDF export works with HTML by default. For true PDF generation, install:

**Option A: WeasyPrint** (Recommended)

```bash
# macOS
brew install cairo pango gdk-pixbuf libffi
pip install weasyprint

# Ubuntu/Debian
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
pip install weasyprint

# Windows
# Download GTK3 runtime from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
pip install weasyprint
```

**Option B: pdfkit** (Alternative)

```bash
# Install wkhtmltopdf binary
# macOS:
brew install wkhtmltopdf

# Ubuntu/Debian:
sudo apt-get install wkhtmltopdf

# Windows:
# Download from https://wkhtmltopdf.org/downloads.html

# Install Python package
pip install pdfkit
```

**Usage:**

```python
from components.pdf_export import generate_pdf_underwriting_package

# Deal data
deal_data = {
    'address': '123 Oak St',
    'arv': 180000,
    'purchase_price': 75000,
    'rehab_budget': 12000,
    'estimated_rent': 1400,
    'sqft': 1200,
    'bedrooms': 3,
    'bathrooms': 2.0,
    'deal_score': 'GREEN',
    'recommended_exit': 'ROUTE TO INTERNAL DSCR',
    # ... all calculations
}

# Generate PDF (or HTML)
pdf_buffer = generate_pdf_underwriting_package(deal_data, method='html')

# Download in Streamlit
st.download_button(
    label="📄 Download PDF",
    data=pdf_buffer,
    file_name="underwriting_package.pdf",
    mime="application/pdf"
)
```

**Features:**
- ✅ Professional PDF layout
- ✅ Company branding
- ✅ Color-coded deal scores
- ✅ Complete financial breakdown
- ✅ DSCR analysis
- ✅ Wholesale analysis
- ✅ Recommendations box
- ✅ Disclaimers
- ✅ Works with or without PDF libraries (HTML fallback)

---

### 5. ✅ Deal Comparison Tool

**Page:** ⚖️ Deal Comparison (Page 9)

**How to Use:**

1. **Select Number of Deals:**
   - Use slider to choose 2-5 deals to compare

2. **Enter Deal Details:**
   - Each deal has its own input form
   - Enter: Name, Address, ARV, Purchase, Rehab, Rent

3. **Review Comparison:**
   - Side-by-side metrics table
   - Best values highlighted in green
   - Visual comparison chart
   - Winner recommendation

4. **Export Comparison:**
   - Download comparison table as CSV

**Features:**
- ✅ Compare up to 5 deals side-by-side
- ✅ Auto-highlight best metrics
- ✅ Visual bar charts
- ✅ Winner recommendation (prioritizes GREEN deals, then highest DSCR)
- ✅ Export comparison table
- ✅ Real-time calculations

**Metrics Compared:**
- Purchase % ARV (lower is better)
- All-In Cost (lower is better)
- DSCR (higher is better)
- Net Cashflow (higher is better)
- Wholesale Fee (higher is better)
- Annual ROI % (higher is better)
- Deal Score & Recommendation

---

## 🔌 Integration Roadmap

### Phase 1: ✅ Complete
- [x] API integration framework
- [x] CRM connector
- [x] Batch upload
- [x] PDF export
- [x] Deal comparison

### Phase 2: 🚧 Next Steps

**1. Activate Real APIs:**

```bash
# Get API keys from:
# - RealEstateAPI: https://www.realestateapi.com/
# - Zillow: https://www.zillow.com/howto/api/APIOverview.htm
# - Rentometer: https://www.rentometer.com/api

# Set environment variables
export REALESTATE_API_KEY="xxx"
export ZILLOW_API_KEY="xxx"
export RENTOMETER_API_KEY="xxx"
```

**2. Connect to Left Main CRM:**

```bash
# Follow Salesforce setup steps above
# Test connection:
python -c "from components.crm_connector import LeftMainConnector; c = LeftMainConnector(); print(c.authenticate())"
```

**3. Add to Underwriting Page:**

Update `/pages/7_🏠_Deal_Underwriter.py` to add:

```python
# Add "Auto-Populate from API" button
if st.button("🔍 Auto-Populate from APIs"):
    with st.spinner("Fetching property data..."):
        data = fetch_property_data(address, sqft)
        st.session_state.arv = data.arv
        st.session_state.estimated_rent = data.estimated_rent

# Add "Save to CRM" functionality
if st.button("📧 Save to CRM"):
    deal = Deal(
        address=address,
        arv=arv,
        # ...
    )
    result = save_deal_to_crm(deal)
    if result['success']:
        st.success("✅ Saved to Left Main!")
```

### Phase 3: 🔮 Future Enhancements

- [ ] Webhook integration (auto-import leads from PPC)
- [ ] Email notifications for new deals
- [ ] Mobile app (React Native)
- [ ] Portfolio performance tracking
- [ ] Predictive analytics (ML model for deal scoring)
- [ ] Integration with property management software
- [ ] Automated comps refresh (daily)
- [ ] Deal pipeline Kanban board

---

## 📁 File Structure (Updated)

```
rei-control-tower/
├── app.py                          # Main app
├── requirements.txt                # Dependencies (updated)
├── PRODUCT_SPEC.md                 # Dashboard spec
├── UNDERWRITING_GUIDE.md           # Underwriting docs
├── README_UNDERWRITING.md          # Underwriting quick start
├── INTEGRATION_GUIDE.md            # ⭐ This file
│
├── pages/
│   ├── 1_📊_Overview.py
│   ├── 2_💰_Pro_Forma.py
│   ├── 3_🎯_Funnel_Leads.py
│   ├── 4_⚙️_Execution_Plan.py
│   ├── 5_📈_Scenarios.py
│   ├── 6_💰_Investor_Capital.py
│   ├── 7_🏠_Deal_Underwriter.py    # Individual calculator
│   ├── 8_📊_Batch_Upload.py        # ⭐ NEW: Batch CSV upload
│   └── 9_⚖️_Deal_Comparison.py     # ⭐ NEW: Deal comparison
│
├── components/
│   ├── __init__.py
│   ├── calculations.py
│   ├── visualizations.py
│   ├── utils.py
│   ├── api_integrations.py         # ⭐ NEW: API connectors
│   ├── crm_connector.py            # ⭐ NEW: Salesforce/Left Main
│   ├── batch_processor.py          # ⭐ NEW: CSV batch processing
│   └── pdf_export.py               # ⭐ NEW: PDF generation
│
└── data/
    ├── default_scenario.json
    └── underwriting_config.json
```

---

## 🧪 Testing

### Test API Integration (Mock Mode):

```python
from components.api_integrations import fetch_property_data

# Works without API keys (returns mock data)
data = fetch_property_data("123 Test St")
print(f"ARV: ${data.arv:,}")  # Should return ~$182,000 (mock)
```

### Test CRM Connector (Mock Mode):

```python
from components.crm_connector import Deal, save_deal_to_crm

deal = Deal(address="123 Test St", arv=180000, deal_score="GREEN")
result = save_deal_to_crm(deal)
print(result)  # Should return mock success
```

### Test Batch Upload:

1. Navigate to Page 8 (Batch Upload)
2. Download template
3. Upload template (as-is, with sample data)
4. Verify 2 deals are processed (1 GREEN, 1 YELLOW)

### Test PDF Export:

```python
from components.pdf_export import generate_pdf_underwriting_package

deal_data = {
    'address': '123 Test St',
    'arv': 180000,
    'purchase_price': 75000,
    'rehab_budget': 12000,
    'deal_score': 'GREEN',
    # ... minimal required fields
}

# Generate HTML (no dependencies required)
buffer = generate_pdf_underwriting_package(deal_data, method='html')
print("PDF generated successfully!")
```

### Test Deal Comparison:

1. Navigate to Page 9 (Deal Comparison)
2. Keep default values for Deal A and Deal B
3. Click through comparison table and chart
4. Verify "Best Deal" recommendation shows Deal A (GREEN)

---

## 🐛 Troubleshooting

### API Integration Issues:

**"API key not configured"**
- Solution: Set environment variables or pass API keys to connectors

**Getting mock data instead of real data**
- Solution: This is expected when API keys are not configured. Set keys to enable real APIs.

### CRM Connection Issues:

**"Missing credentials"**
- Solution: Ensure all 5 Salesforce env vars are set (username, password, token, client_id, client_secret)

**"Invalid username, password, security token"**
- Solution: Reset security token in Salesforce, verify password is correct

### Batch Upload Issues:

**"Invalid CSV format"**
- Solution: Ensure CSV has required columns: address, arv, purchase_price, rehab_budget, estimated_rent

**Validation errors**
- Solution: Check that numeric fields are > 0, address is not empty

### PDF Export Issues:

**"WeasyPrint/pdfkit not installed"**
- Solution: Install dependencies or use method='html' to export HTML instead

**WeasyPrint system dependencies missing**
- Solution: Follow installation instructions for your OS (see PDF Export setup above)

---

## 📞 Support

- **Dashboard Issues:** See `/PRODUCT_SPEC.md`
- **Underwriting Questions:** See `/UNDERWRITING_GUIDE.md`
- **API Setup:** See this file (INTEGRATION_GUIDE.md)

---

**Version:** 1.0
**Last Updated:** January 7, 2026
**Maintained By:** REI Nationwide LLC
