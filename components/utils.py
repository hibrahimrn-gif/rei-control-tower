"""
REI Nationwide LLC - Utilities Module
Validation, file I/O, and helper functions
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
from pathlib import Path


# Validation rules
VALIDATION_RULES = {
    'fallout_rate': (0.0, 0.50, 'Fallout rate must be 0-50%'),
    'cpl': (1.0, 500.0, 'CPL must be $1-$500'),
    'president_override_rate': (0.0, 0.50, 'President override must be 0-50%'),
    'acq_commission_rate': (0.0, 0.50, 'Acquisition commission must be 0-50%'),
    'dispo_commission_rate': (0.0, 0.50, 'Dispo commission must be 0-50%'),
    'membership_commission_rate': (0.0, 0.50, 'Membership commission must be 0-50%'),
    'listing_commission_rate': (0.0, 0.10, 'Listing commission must be 0-10%'),
    'hamza_noi_share': (0.0, 0.50, 'Owner share must be 0-50%'),
    'clearroute_noi_share': (0.0, 0.50, 'Partner share must be 0-50%'),
    'membership_close_rate': (0.05, 0.60, 'Close rate must be 5-60%'),
    'membership_show_rate': (0.30, 0.95, 'Show rate must be 30-95%'),
}

# Volume must be non-negative integers
VOLUME_FIELDS = [
    'wholesale_volume', 'retained_doors', 'memberships_sold', 'retail_listings'
]

# Dollar amounts must be positive
DOLLAR_FIELDS = [
    'avg_wholesale_fee', 'internal_acq_fee', 'membership_price', 'avg_retail_price',
    'weekly_ad_spend', 'executive_salaries', 'staff_salaries', 'hamza_salary',
    'property_mgmt_revenue'
]

# Capacity fields must be positive
CAPACITY_FIELDS = [
    'closer_lead_capacity', 'closer_contract_capacity', 'offer_to_contract_ratio',
    'underwriter_capacity', 'pm_capacity', 'tc_capacity', 'dispo_capacity', 'dscr_capacity'
]


def validate_input(field: str, value: float) -> Tuple[bool, Optional[str]]:
    """Validate a single input field"""
    
    # Check rate validations
    if field in VALIDATION_RULES:
        min_val, max_val, msg = VALIDATION_RULES[field]
        if value < min_val or value > max_val:
            return False, msg
    
    # Check volumes
    if field in VOLUME_FIELDS:
        if value < 0 or value != int(value):
            return False, f'{field} must be a non-negative integer'
    
    # Check dollar amounts
    if field in DOLLAR_FIELDS:
        if value < 0:
            return False, f'{field} must be non-negative'
    
    # Check capacities
    if field in CAPACITY_FIELDS:
        if value <= 0:
            return False, f'{field} must be positive'
    
    # Check pipeline split sums to ~1.0
    # (This is handled at the form level)
    
    return True, None


def validate_pipeline_split(internal: float, wholesale: float, 
                            retail: float, fallout: float) -> Tuple[bool, str]:
    """Validate that pipeline splits sum to 1.0"""
    total = internal + wholesale + retail + fallout
    if abs(total - 1.0) > 0.01:
        return False, f'Pipeline splits must sum to 100% (currently {total*100:.1f}%)'
    return True, ''


def get_data_dir() -> Path:
    """Get the data directory path"""
    return Path(__file__).parent.parent / 'data'


def get_scenarios_dir() -> Path:
    """Get the scenarios directory path"""
    scenarios_dir = get_data_dir() / 'scenarios'
    scenarios_dir.mkdir(parents=True, exist_ok=True)
    return scenarios_dir


def save_scenario(scenario_data: Dict, name: str = None) -> str:
    """Save a scenario to JSON file"""
    if name is None:
        name = scenario_data.get('name', 'Unnamed')
    
    # Sanitize filename
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    filepath = get_scenarios_dir() / filename
    
    with open(filepath, 'w') as f:
        json.dump(scenario_data, f, indent=2, default=str)
    
    return str(filepath)


def load_scenario(filepath: str) -> Optional[Dict]:
    """Load a scenario from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None


def list_saved_scenarios() -> List[Dict]:
    """List all saved scenarios with metadata"""
    scenarios = []
    scenarios_dir = get_scenarios_dir()
    
    for filepath in scenarios_dir.glob('*.json'):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                scenarios.append({
                    'filepath': str(filepath),
                    'filename': filepath.name,
                    'name': data.get('name', 'Unnamed'),
                    'modified': datetime.fromtimestamp(filepath.stat().st_mtime)
                })
        except:
            continue
    
    # Sort by modification date, newest first
    scenarios.sort(key=lambda x: x['modified'], reverse=True)
    return scenarios


def delete_scenario(filepath: str) -> bool:
    """Delete a saved scenario"""
    try:
        os.remove(filepath)
        return True
    except:
        return False


def export_to_csv(data: Dict, filepath: str) -> str:
    """Export scenario data to CSV"""
    df = pd.DataFrame([data])
    df.to_csv(filepath, index=False)
    return filepath


def export_to_json(data: Dict, filepath: str) -> str:
    """Export scenario data to JSON"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    return filepath


def load_actuals_csv(filepath: str) -> Optional[pd.DataFrame]:
    """Load actual performance data from CSV"""
    try:
        df = pd.read_csv(filepath)
        return df
    except:
        return None


def parse_actuals(df: pd.DataFrame) -> Dict:
    """Parse actuals DataFrame into expected format"""
    result = {
        'leads_by_week': {},
        'contracts_by_week': {},
        'outcomes_by_week': {}
    }
    
    # Expected columns: week, leads, contracts, internal, wholesale, retail
    if 'week' in df.columns:
        for _, row in df.iterrows():
            week = str(row.get('week', ''))
            result['leads_by_week'][week] = row.get('leads', 0)
            result['contracts_by_week'][week] = row.get('contracts', 0)
            result['outcomes_by_week'][week] = {
                'internal': row.get('internal', 0),
                'wholesale': row.get('wholesale', 0),
                'retail': row.get('retail', 0)
            }
    
    return result


def create_default_scenario() -> Dict:
    """Create the default 2026 Base Plan scenario"""
    return {
        'name': '2026 Base Plan',
        
        # Revenue Drivers
        'wholesale_volume': 300,
        'avg_wholesale_fee': 30000.0,
        'retained_doors': 300,
        'internal_acq_fee': 30000.0,
        'memberships_sold': 150,
        'membership_price': 15000.0,
        'retail_listings': 100,
        'avg_retail_price': 250000.0,
        'listing_commission_rate': 0.03,
        'property_mgmt_revenue': 540000.0,
        
        # Marketing
        'weekly_ad_spend': 34400.0,
        'cpl': 100.0,
        
        # Commission Rates
        'president_override_rate': 0.10,
        'acq_commission_rate': 0.10,
        'dispo_commission_rate': 0.05,
        'membership_commission_rate': 0.10,
        
        # Salaries
        'executive_salaries': 990000.0,
        'staff_salaries': 698000.0,
        'hamza_salary': 480000.0,
        
        # Comp Structure
        'hamza_noi_share': 0.25,
        'clearroute_noi_share': 0.20,
        
        # Pipeline Split
        'internal_split': 0.30,
        'wholesale_split': 0.30,
        'retail_split': 0.20,
        'fallout_rate': 0.20,
        
        # Staffing Capacities
        'closer_lead_capacity': 85.0,
        'closer_contract_capacity': 4.0,
        'offer_to_contract_ratio': 4.0,
        'underwriter_capacity': 40.0,
        'rehab_cycle_days': 45,
        'pm_capacity': 10.0,
        'tc_capacity': 10.0,
        'dispo_capacity': 6.0,
        'dscr_capacity': 6.0,
        'membership_close_rate': 0.25,
        'membership_show_rate': 0.70,
    }


def format_large_number(value: float, prefix: str = '$') -> str:
    """Format large numbers for display"""
    if value >= 1_000_000:
        return f"{prefix}{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{prefix}{value/1_000:.1f}K"
    else:
        return f"{prefix}{value:.0f}"


def calculate_weekly_from_annual(annual_value: float) -> float:
    """Convert annual value to weekly"""
    return annual_value / 52


def calculate_annual_from_weekly(weekly_value: float) -> float:
    """Convert weekly value to annual"""
    return weekly_value * 52


def generate_sample_actuals_template() -> pd.DataFrame:
    """Generate a sample CSV template for actuals upload"""
    weeks = [f"2026-W{i:02d}" for i in range(1, 13)]
    
    return pd.DataFrame({
        'week': weeks,
        'leads': [0] * 12,
        'contracts': [0] * 12,
        'internal': [0] * 12,
        'wholesale': [0] * 12,
        'retail': [0] * 12
    })
