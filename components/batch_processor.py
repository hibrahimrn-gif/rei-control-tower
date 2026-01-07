"""
REI Nationwide LLC - Batch Deal Processor
Upload and process multiple deals via CSV
"""

import pandas as pd
import io
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import json


@dataclass
class BatchDealResult:
    """Result for a single deal in batch processing"""
    row_number: int
    address: str
    arv: Optional[float]
    purchase_price: Optional[float]
    rehab_budget: Optional[float]
    estimated_rent: Optional[float]

    # Calculated fields
    purchase_pct_arv: Optional[float] = None
    all_in_cost: Optional[float] = None
    dscr: Optional[float] = None
    net_cashflow: Optional[float] = None
    wholesale_fee: Optional[float] = None

    # Scoring
    deal_score: Optional[str] = None  # GREEN, YELLOW, RED
    recommended_exit: Optional[str] = None
    score_reason: Optional[str] = None

    # Validation
    is_valid: bool = True
    validation_errors: Optional[List[str]] = None


def validate_csv_format(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate CSV has required columns

    Required columns:
    - address
    - arv
    - purchase_price
    - rehab_budget
    - estimated_rent

    Optional columns:
    - sqft
    - bedrooms
    - bathrooms
    - holding_months
    - notes

    Returns:
        (is_valid, error_messages)
    """
    required_columns = ['address', 'arv', 'purchase_price', 'rehab_budget', 'estimated_rent']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        return False, [f"Missing required columns: {', '.join(missing_columns)}"]

    return True, []


def calculate_underwriting_for_row(row: pd.Series, row_number: int) -> BatchDealResult:
    """
    Calculate underwriting metrics for a single row from CSV

    Args:
        row: Pandas Series with deal data
        row_number: Row number in CSV (for tracking)

    Returns:
        BatchDealResult with all calculations
    """
    validation_errors = []

    # Extract basic fields
    address = str(row.get('address', ''))
    arv = float(row.get('arv', 0))
    purchase_price = float(row.get('purchase_price', 0))
    rehab_budget = float(row.get('rehab_budget', 0))
    estimated_rent = float(row.get('estimated_rent', 0))
    sqft = int(row.get('sqft', 1200)) if 'sqft' in row else 1200
    holding_months = float(row.get('holding_months', 2.0)) if 'holding_months' in row else 2.0

    # Validate inputs
    if not address or address == 'nan':
        validation_errors.append("Address is required")
    if arv <= 0:
        validation_errors.append("ARV must be greater than 0")
    if purchase_price <= 0:
        validation_errors.append("Purchase price must be greater than 0")
    if rehab_budget < 0:
        validation_errors.append("Rehab budget cannot be negative")
    if estimated_rent <= 0:
        validation_errors.append("Estimated rent must be greater than 0")

    if validation_errors:
        return BatchDealResult(
            row_number=row_number,
            address=address,
            arv=arv,
            purchase_price=purchase_price,
            rehab_budget=rehab_budget,
            estimated_rent=estimated_rent,
            is_valid=False,
            validation_errors=validation_errors
        )

    # Calculate metrics (same logic as Deal_Underwriter.py)
    purchase_pct_arv = purchase_price / arv if arv > 0 else 0

    # Holding costs
    monthly_holding_rate = 0.01
    utilities_per_month = 150
    insurance_per_month = 100
    holding_costs = (purchase_price * monthly_holding_rate * holding_months) + \
                    ((utilities_per_month + insurance_per_month) * holding_months)

    # Closing costs
    closing_costs_buy = purchase_price * 0.03
    closing_costs_sell = arv * 0.01

    # All-in cost
    all_in_cost = purchase_price + rehab_budget + holding_costs + closing_costs_buy

    # DSCR calculation
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
    pm_fee_rate = 0.10
    pm_fee = estimated_rent * pm_fee_rate
    net_cashflow = estimated_rent - piti - pm_fee

    # Wholesale fee
    wholesale_price = arv * 0.70
    wholesale_fee = wholesale_price - purchase_price - 5000

    # Scoring logic
    deal_score = "RED"
    recommended_exit = "REJECT - Archive"
    score_reason = ""

    # GREEN: Route to Internal DSCR
    if purchase_pct_arv <= 0.45 and rehab_budget <= 20000 and net_cashflow >= 175:
        deal_score = "GREEN"
        recommended_exit = "ROUTE TO INTERNAL DSCR"
        score_reason = "Perfect fit for M Capital model"

    # YELLOW: Route to Wholesale
    elif purchase_pct_arv <= 0.60 and rehab_budget <= 30000 and wholesale_fee >= 25000:
        deal_score = "YELLOW"
        recommended_exit = "ROUTE TO WHOLESALE"
        score_reason = f"Wholesale potential: ${wholesale_fee:,.0f} fee"

    # YELLOW: Route to Retail
    elif rehab_budget <= 5000 and purchase_pct_arv <= 0.70:
        deal_score = "YELLOW"
        recommended_exit = "ROUTE TO RETAIL LISTING"
        score_reason = "Retail-ready property"

    # RED: Reject
    else:
        if rehab_budget > 30000:
            score_reason = f"Rehab too high: ${rehab_budget:,.0f}"
        elif purchase_pct_arv > 0.60:
            score_reason = f"Purchase price too high: {purchase_pct_arv*100:.1f}% ARV"
        elif wholesale_fee < 25000:
            score_reason = f"Wholesale fee too low: ${wholesale_fee:,.0f}"
        else:
            score_reason = "Does not meet minimum criteria"

    return BatchDealResult(
        row_number=row_number,
        address=address,
        arv=arv,
        purchase_price=purchase_price,
        rehab_budget=rehab_budget,
        estimated_rent=estimated_rent,
        purchase_pct_arv=purchase_pct_arv,
        all_in_cost=all_in_cost,
        dscr=dscr,
        net_cashflow=net_cashflow,
        wholesale_fee=wholesale_fee,
        deal_score=deal_score,
        recommended_exit=recommended_exit,
        score_reason=score_reason,
        is_valid=True,
        validation_errors=None
    )


def process_batch_csv(csv_file) -> Tuple[List[BatchDealResult], pd.DataFrame]:
    """
    Process batch CSV file and return results

    Args:
        csv_file: Uploaded CSV file (Streamlit UploadedFile)

    Returns:
        (list_of_results, summary_dataframe)
    """
    # Read CSV
    df = pd.read_csv(csv_file)

    # Validate format
    is_valid, errors = validate_csv_format(df)
    if not is_valid:
        raise ValueError(f"Invalid CSV format: {', '.join(errors)}")

    # Process each row
    results = []
    for idx, row in df.iterrows():
        result = calculate_underwriting_for_row(row, idx + 2)  # +2 because row 1 is header
        results.append(result)

    # Create summary DataFrame
    summary_data = []
    for result in results:
        summary_data.append({
            'Row': result.row_number,
            'Address': result.address,
            'ARV': f"${result.arv:,.0f}" if result.arv else "N/A",
            'Purchase': f"${result.purchase_price:,.0f}" if result.purchase_price else "N/A",
            'Purchase % ARV': f"{result.purchase_pct_arv*100:.1f}%" if result.purchase_pct_arv else "N/A",
            'Rehab': f"${result.rehab_budget:,.0f}" if result.rehab_budget else "N/A",
            'DSCR': f"{result.dscr:.2f}" if result.dscr else "N/A",
            'Net Cashflow': f"${result.net_cashflow:,.0f}" if result.net_cashflow else "N/A",
            'Wholesale Fee': f"${result.wholesale_fee:,.0f}" if result.wholesale_fee else "N/A",
            'Score': result.deal_score,
            'Recommendation': result.recommended_exit,
            'Valid': '✅' if result.is_valid else '❌',
            'Errors': ', '.join(result.validation_errors) if result.validation_errors else ''
        })

    summary_df = pd.DataFrame(summary_data)

    return results, summary_df


def get_batch_summary_stats(results: List[BatchDealResult]) -> Dict:
    """
    Get summary statistics for batch processing results

    Returns:
        Dict with counts by score, valid/invalid, etc.
    """
    total_deals = len(results)
    valid_deals = sum(1 for r in results if r.is_valid)
    invalid_deals = total_deals - valid_deals

    green_deals = sum(1 for r in results if r.deal_score == 'GREEN')
    yellow_deals = sum(1 for r in results if r.deal_score == 'YELLOW')
    red_deals = sum(1 for r in results if r.deal_score == 'RED')

    dscr_routes = sum(1 for r in results if 'DSCR' in (r.recommended_exit or ''))
    wholesale_routes = sum(1 for r in results if 'WHOLESALE' in (r.recommended_exit or ''))
    retail_routes = sum(1 for r in results if 'RETAIL' in (r.recommended_exit or ''))
    reject_routes = sum(1 for r in results if 'REJECT' in (r.recommended_exit or ''))

    # Calculate averages for valid deals
    valid_results = [r for r in results if r.is_valid]

    avg_arv = sum(r.arv for r in valid_results if r.arv) / len(valid_results) if valid_results else 0
    avg_purchase_pct = sum(r.purchase_pct_arv for r in valid_results if r.purchase_pct_arv) / len(valid_results) if valid_results else 0
    avg_dscr = sum(r.dscr for r in valid_results if r.dscr) / len([r for r in valid_results if r.dscr]) if valid_results else 0

    return {
        'total_deals': total_deals,
        'valid_deals': valid_deals,
        'invalid_deals': invalid_deals,
        'green_deals': green_deals,
        'yellow_deals': yellow_deals,
        'red_deals': red_deals,
        'dscr_routes': dscr_routes,
        'wholesale_routes': wholesale_routes,
        'retail_routes': retail_routes,
        'reject_routes': reject_routes,
        'avg_arv': avg_arv,
        'avg_purchase_pct': avg_purchase_pct,
        'avg_dscr': avg_dscr
    }


def export_batch_results_to_csv(results: List[BatchDealResult]) -> str:
    """
    Export batch results to CSV string

    Returns:
        CSV string ready for download
    """
    data = []
    for result in results:
        data.append({
            'Row Number': result.row_number,
            'Address': result.address,
            'ARV': result.arv,
            'Purchase Price': result.purchase_price,
            'Rehab Budget': result.rehab_budget,
            'Estimated Rent': result.estimated_rent,
            'Purchase % ARV': result.purchase_pct_arv,
            'All-In Cost': result.all_in_cost,
            'DSCR': result.dscr,
            'Net Cashflow': result.net_cashflow,
            'Wholesale Fee': result.wholesale_fee,
            'Deal Score': result.deal_score,
            'Recommended Exit': result.recommended_exit,
            'Score Reason': result.score_reason,
            'Valid': result.is_valid,
            'Validation Errors': ', '.join(result.validation_errors) if result.validation_errors else ''
        })

    df = pd.DataFrame(data)
    return df.to_csv(index=False)


def create_csv_template() -> str:
    """
    Create a CSV template for batch upload

    Returns:
        CSV template string with headers and sample data
    """
    template_data = {
        'address': ['123 Oak St, Indianapolis, IN 46201', '456 Elm Ave, Cleveland, OH 44101'],
        'arv': [180000, 140000],
        'purchase_price': [75000, 72000],
        'rehab_budget': [12000, 25000],
        'estimated_rent': [1400, 1100],
        'sqft': [1200, 1100],
        'bedrooms': [3, 3],
        'bathrooms': [2.0, 2.0],
        'holding_months': [2.0, 2.0],
        'notes': ['Light cosmetic rehab', 'Heavy rehab required']
    }

    df = pd.DataFrame(template_data)
    return df.to_csv(index=False)
