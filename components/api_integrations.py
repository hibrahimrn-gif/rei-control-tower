"""
REI Nationwide LLC - API Integrations
Connectors for RealEstateAPI, Zillow, Rentometer, and other data sources
"""

import requests
import json
from typing import Dict, Optional, List
from dataclasses import dataclass
import os


@dataclass
class PropertyData:
    """Property data from external APIs"""
    address: str
    arv: Optional[float] = None
    arv_source: Optional[str] = None
    arv_confidence: Optional[str] = None
    estimated_rent: Optional[float] = None
    rent_source: Optional[str] = None
    sqft: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    year_built: Optional[int] = None
    property_type: Optional[str] = None
    comps: Optional[List[Dict]] = None
    last_sale_price: Optional[float] = None
    last_sale_date: Optional[str] = None
    tax_assessed_value: Optional[float] = None
    errors: Optional[List[str]] = None


class RealEstateAPIConnector:
    """
    Connector for RealEstateAPI.com
    Used for: Property details, comps, ARV estimates
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('REALESTATE_API_KEY')
        self.base_url = "https://api.realestateapi.com/v2"

    def get_property_details(self, address: str) -> Dict:
        """
        Get property details by address

        Returns:
            - Property characteristics (sqft, beds, baths, year built)
            - Last sale info
            - Tax assessment
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'API key not configured',
                'message': 'Set REALESTATE_API_KEY environment variable'
            }

        try:
            # Mock implementation - replace with actual API call
            # Real implementation would be:
            # response = requests.get(
            #     f"{self.base_url}/property",
            #     params={'address': address},
            #     headers={'Authorization': f'Bearer {self.api_key}'}
            # )
            # return response.json()

            # Mock response for demonstration
            return {
                'success': True,
                'data': {
                    'address': address,
                    'sqft': 1200,
                    'bedrooms': 3,
                    'bathrooms': 2.0,
                    'year_built': 1985,
                    'property_type': 'Single Family',
                    'last_sale_price': 85000,
                    'last_sale_date': '2020-03-15',
                    'tax_assessed_value': 120000
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_comps(self, address: str, radius_miles: float = 0.5, max_results: int = 10) -> Dict:
        """
        Get comparable sales (comps) for ARV calculation

        Args:
            address: Property address
            radius_miles: Search radius in miles
            max_results: Maximum number of comps to return

        Returns:
            List of comparable properties with sale prices
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'API key not configured'
            }

        try:
            # Mock implementation
            return {
                'success': True,
                'data': {
                    'comps': [
                        {
                            'address': '125 Oak St',
                            'sale_price': 185000,
                            'sale_date': '2025-12-01',
                            'sqft': 1250,
                            'bedrooms': 3,
                            'bathrooms': 2,
                            'distance_miles': 0.2,
                            'price_per_sqft': 148
                        },
                        {
                            'address': '127 Oak St',
                            'sale_price': 175000,
                            'sale_date': '2025-11-15',
                            'sqft': 1180,
                            'bedrooms': 3,
                            'bathrooms': 2,
                            'distance_miles': 0.3,
                            'price_per_sqft': 148
                        },
                        {
                            'address': '456 Maple Ave',
                            'sale_price': 190000,
                            'sale_date': '2025-10-20',
                            'sqft': 1300,
                            'bedrooms': 3,
                            'bathrooms': 2.5,
                            'distance_miles': 0.4,
                            'price_per_sqft': 146
                        }
                    ],
                    'median_sale_price': 185000,
                    'median_price_per_sqft': 148
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def estimate_arv(self, address: str, sqft: int, condition: str = 'average') -> Dict:
        """
        Estimate After Repair Value (ARV)

        Args:
            address: Property address
            sqft: Square footage
            condition: Property condition after repairs (poor/average/good/excellent)

        Returns:
            ARV estimate with confidence level
        """
        comps_result = self.get_comps(address)

        if not comps_result.get('success'):
            return comps_result

        try:
            comps = comps_result['data']['comps']
            median_psf = comps_result['data']['median_price_per_sqft']

            # Adjust for condition
            condition_multipliers = {
                'poor': 0.85,
                'average': 1.0,
                'good': 1.08,
                'excellent': 1.15
            }

            multiplier = condition_multipliers.get(condition, 1.0)
            estimated_arv = sqft * median_psf * multiplier

            # Determine confidence based on number of comps and recency
            if len(comps) >= 5:
                confidence = 'high'
            elif len(comps) >= 3:
                confidence = 'medium'
            else:
                confidence = 'low'

            return {
                'success': True,
                'data': {
                    'arv': round(estimated_arv, -2),  # Round to nearest $100
                    'arv_low': round(estimated_arv * 0.92, -2),
                    'arv_high': round(estimated_arv * 1.08, -2),
                    'confidence': confidence,
                    'median_price_per_sqft': median_psf,
                    'num_comps_used': len(comps),
                    'source': 'RealEstateAPI'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class ZillowAPIConnector:
    """
    Connector for Zillow API (or Zillow scraper)
    Used for: Zestimate (ARV), Rent Zestimate
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ZILLOW_API_KEY')
        self.base_url = "https://api.zillow.com/v1"

    def get_zestimate(self, address: str) -> Dict:
        """
        Get Zillow's Zestimate (ARV estimate)

        Returns:
            Zestimate value and range
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'API key not configured',
                'message': 'Set ZILLOW_API_KEY environment variable'
            }

        try:
            # Mock implementation
            return {
                'success': True,
                'data': {
                    'zestimate': 182000,
                    'zestimate_low': 175000,
                    'zestimate_high': 190000,
                    'valuation_range': 15000,
                    'last_updated': '2026-01-07',
                    'source': 'Zillow Zestimate'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_rent_zestimate(self, address: str) -> Dict:
        """
        Get Zillow's Rent Zestimate

        Returns:
            Estimated monthly rent
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'API key not configured'
            }

        try:
            # Mock implementation
            return {
                'success': True,
                'data': {
                    'rent_zestimate': 1425,
                    'rent_low': 1350,
                    'rent_high': 1500,
                    'last_updated': '2026-01-07',
                    'source': 'Zillow Rent Zestimate'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class RentometerAPIConnector:
    """
    Connector for Rentometer API
    Used for: Rent estimates, rent comparisons
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('RENTOMETER_API_KEY')
        self.base_url = "https://api.rentometer.com/v1"

    def get_rent_estimate(self, address: str, bedrooms: int, bathrooms: float) -> Dict:
        """
        Get rent estimate from Rentometer

        Returns:
            Median rent for similar properties in the area
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'API key not configured',
                'message': 'Set RENTOMETER_API_KEY environment variable'
            }

        try:
            # Mock implementation
            return {
                'success': True,
                'data': {
                    'median_rent': 1400,
                    'rent_25th_percentile': 1250,
                    'rent_75th_percentile': 1550,
                    'percentile': 52,  # This property would be in 52nd percentile
                    'sample_size': 47,  # Number of comparable rentals
                    'source': 'Rentometer'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class PropertyDataAggregator:
    """
    Aggregates data from multiple APIs to provide best estimate
    """

    def __init__(
        self,
        realestate_api_key: Optional[str] = None,
        zillow_api_key: Optional[str] = None,
        rentometer_api_key: Optional[str] = None
    ):
        self.realestate = RealEstateAPIConnector(realestate_api_key)
        self.zillow = ZillowAPIConnector(zillow_api_key)
        self.rentometer = RentometerAPIConnector(rentometer_api_key)

    def get_comprehensive_data(
        self,
        address: str,
        sqft: Optional[int] = None,
        bedrooms: Optional[int] = None,
        bathrooms: Optional[float] = None
    ) -> PropertyData:
        """
        Get comprehensive property data from all available sources

        Returns:
            PropertyData object with aggregated information
        """
        errors = []

        # Get property details from RealEstateAPI
        property_details = self.realestate.get_property_details(address)

        if property_details.get('success'):
            data = property_details['data']
            sqft = sqft or data.get('sqft')
            bedrooms = bedrooms or data.get('bedrooms')
            bathrooms = bathrooms or data.get('bathrooms')
        else:
            errors.append(f"RealEstateAPI: {property_details.get('error')}")

        # Get ARV estimates from multiple sources
        arv_estimates = []

        # RealEstateAPI ARV
        if sqft:
            arv_result = self.realestate.estimate_arv(address, sqft)
            if arv_result.get('success'):
                arv_estimates.append({
                    'value': arv_result['data']['arv'],
                    'source': 'RealEstateAPI',
                    'confidence': arv_result['data']['confidence']
                })

        # Zillow Zestimate
        zestimate = self.zillow.get_zestimate(address)
        if zestimate.get('success'):
            arv_estimates.append({
                'value': zestimate['data']['zestimate'],
                'source': 'Zillow',
                'confidence': 'medium'
            })
        else:
            errors.append(f"Zillow: {zestimate.get('error')}")

        # Calculate weighted average ARV (prefer high confidence sources)
        if arv_estimates:
            weights = {'high': 1.0, 'medium': 0.7, 'low': 0.4}
            total_weight = sum(weights.get(est['confidence'], 0.5) for est in arv_estimates)
            weighted_arv = sum(
                est['value'] * weights.get(est['confidence'], 0.5)
                for est in arv_estimates
            ) / total_weight

            arv = round(weighted_arv, -2)
            arv_source = ', '.join([est['source'] for est in arv_estimates])
            arv_confidence = arv_estimates[0]['confidence'] if len(arv_estimates) == 1 else 'medium'
        else:
            arv = None
            arv_source = None
            arv_confidence = None

        # Get rent estimates
        rent_estimates = []

        # Zillow Rent Zestimate
        rent_zestimate = self.zillow.get_rent_zestimate(address)
        if rent_zestimate.get('success'):
            rent_estimates.append({
                'value': rent_zestimate['data']['rent_zestimate'],
                'source': 'Zillow Rent Zestimate'
            })

        # Rentometer
        if bedrooms and bathrooms:
            rentometer_result = self.rentometer.get_rent_estimate(address, bedrooms, bathrooms)
            if rentometer_result.get('success'):
                rent_estimates.append({
                    'value': rentometer_result['data']['median_rent'],
                    'source': 'Rentometer'
                })
            else:
                errors.append(f"Rentometer: {rentometer_result.get('error')}")

        # Calculate average rent
        if rent_estimates:
            estimated_rent = round(sum(est['value'] for est in rent_estimates) / len(rent_estimates), 0)
            rent_source = ', '.join([est['source'] for est in rent_estimates])
        else:
            estimated_rent = None
            rent_source = None

        # Get comps
        comps_result = self.realestate.get_comps(address)
        comps = comps_result['data']['comps'] if comps_result.get('success') else None

        return PropertyData(
            address=address,
            arv=arv,
            arv_source=arv_source,
            arv_confidence=arv_confidence,
            estimated_rent=estimated_rent,
            rent_source=rent_source,
            sqft=sqft,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            year_built=property_details['data'].get('year_built') if property_details.get('success') else None,
            property_type=property_details['data'].get('property_type') if property_details.get('success') else None,
            comps=comps,
            last_sale_price=property_details['data'].get('last_sale_price') if property_details.get('success') else None,
            last_sale_date=property_details['data'].get('last_sale_date') if property_details.get('success') else None,
            tax_assessed_value=property_details['data'].get('tax_assessed_value') if property_details.get('success') else None,
            errors=errors if errors else None
        )


# Convenience function for Streamlit
def fetch_property_data(address: str, sqft: Optional[int] = None) -> PropertyData:
    """
    Convenience function to fetch property data
    Uses environment variables for API keys
    """
    aggregator = PropertyDataAggregator()
    return aggregator.get_comprehensive_data(address, sqft=sqft)
