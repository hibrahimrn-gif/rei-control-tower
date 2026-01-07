"""
REI Nationwide LLC - CRM Connector
Integration with Left Main (Salesforce) for deal tracking and pipeline management
"""

import requests
import json
from typing import Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
import os


@dataclass
class Deal:
    """Deal record for CRM"""
    id: Optional[str] = None
    address: str = ""
    arv: Optional[float] = None
    purchase_price: Optional[float] = None
    rehab_budget: Optional[float] = None
    estimated_rent: Optional[float] = None
    deal_score: Optional[str] = None  # GREEN, YELLOW, RED
    recommended_exit: Optional[str] = None
    lead_source: Optional[str] = None
    lead_id: Optional[str] = None
    stage: Optional[str] = None  # Lead, Offer, Under Contract, Closed, Dead
    assigned_closer: Optional[str] = None
    assigned_underwriter: Optional[str] = None
    created_date: Optional[str] = None
    updated_date: Optional[str] = None
    notes: Optional[str] = None

    # Calculated fields
    purchase_pct_arv: Optional[float] = None
    all_in_cost: Optional[float] = None
    dscr: Optional[float] = None
    net_cashflow: Optional[float] = None
    wholesale_fee: Optional[float] = None


class SalesforceConnector:
    """
    Connector for Salesforce (Left Main CRM)

    Setup:
    1. Create Connected App in Salesforce
    2. Get Consumer Key and Secret
    3. Set environment variables:
       - SALESFORCE_USERNAME
       - SALESFORCE_PASSWORD
       - SALESFORCE_SECURITY_TOKEN
       - SALESFORCE_CLIENT_ID
       - SALESFORCE_CLIENT_SECRET
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        security_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        instance_url: Optional[str] = None
    ):
        self.username = username or os.getenv('SALESFORCE_USERNAME')
        self.password = password or os.getenv('SALESFORCE_PASSWORD')
        self.security_token = security_token or os.getenv('SALESFORCE_SECURITY_TOKEN')
        self.client_id = client_id or os.getenv('SALESFORCE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SALESFORCE_CLIENT_SECRET')
        self.instance_url = instance_url or os.getenv('SALESFORCE_INSTANCE_URL', 'https://login.salesforce.com')

        self.access_token = None
        self.api_version = 'v59.0'

    def authenticate(self) -> Dict:
        """
        Authenticate with Salesforce using OAuth 2.0 Password Flow

        Returns:
            Dict with access_token and instance_url
        """
        if not all([self.username, self.password, self.security_token, self.client_id, self.client_secret]):
            return {
                'success': False,
                'error': 'Missing credentials',
                'message': 'Set SALESFORCE_* environment variables'
            }

        try:
            # OAuth 2.0 Password Flow
            # Real implementation:
            # auth_url = f"{self.instance_url}/services/oauth2/token"
            # response = requests.post(auth_url, data={
            #     'grant_type': 'password',
            #     'client_id': self.client_id,
            #     'client_secret': self.client_secret,
            #     'username': self.username,
            #     'password': self.password + self.security_token
            # })
            # result = response.json()
            # self.access_token = result['access_token']
            # self.instance_url = result['instance_url']

            # Mock implementation
            self.access_token = 'mock_access_token_12345'

            return {
                'success': True,
                'access_token': self.access_token,
                'instance_url': self.instance_url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_deal(self, deal: Deal) -> Dict:
        """
        Create a new deal (Opportunity) in Salesforce

        Args:
            deal: Deal object with property information

        Returns:
            Created deal with Salesforce ID
        """
        if not self.access_token:
            auth_result = self.authenticate()
            if not auth_result.get('success'):
                return auth_result

        try:
            # Map Deal object to Salesforce Opportunity fields
            # Assumes custom fields exist in Salesforce:
            # - Property_Address__c
            # - ARV__c
            # - Purchase_Price__c
            # - Rehab_Budget__c
            # - Estimated_Rent__c
            # - Deal_Score__c
            # - Recommended_Exit__c

            # Real implementation:
            # url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/Opportunity"
            # headers = {
            #     'Authorization': f'Bearer {self.access_token}',
            #     'Content-Type': 'application/json'
            # }
            # data = {
            #     'Name': f"Deal - {deal.address}",
            #     'Property_Address__c': deal.address,
            #     'ARV__c': deal.arv,
            #     'Purchase_Price__c': deal.purchase_price,
            #     'Rehab_Budget__c': deal.rehab_budget,
            #     'Estimated_Rent__c': deal.estimated_rent,
            #     'Deal_Score__c': deal.deal_score,
            #     'Recommended_Exit__c': deal.recommended_exit,
            #     'StageName': deal.stage or 'Lead',
            #     'CloseDate': (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
            # }
            # response = requests.post(url, headers=headers, json=data)
            # result = response.json()

            # Mock implementation
            deal.id = f"SF_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            deal.created_date = datetime.now().isoformat()

            return {
                'success': True,
                'data': {
                    'id': deal.id,
                    'deal': asdict(deal)
                },
                'message': f'Deal created in Salesforce: {deal.id}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def update_deal(self, deal_id: str, updates: Dict) -> Dict:
        """
        Update an existing deal in Salesforce

        Args:
            deal_id: Salesforce Opportunity ID
            updates: Dictionary of fields to update

        Returns:
            Success status
        """
        if not self.access_token:
            auth_result = self.authenticate()
            if not auth_result.get('success'):
                return auth_result

        try:
            # Real implementation:
            # url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/Opportunity/{deal_id}"
            # headers = {
            #     'Authorization': f'Bearer {self.access_token}',
            #     'Content-Type': 'application/json'
            # }
            # response = requests.patch(url, headers=headers, json=updates)

            # Mock implementation
            return {
                'success': True,
                'message': f'Deal {deal_id} updated successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_deal(self, deal_id: str) -> Dict:
        """
        Retrieve a deal from Salesforce

        Args:
            deal_id: Salesforce Opportunity ID

        Returns:
            Deal data
        """
        if not self.access_token:
            auth_result = self.authenticate()
            if not auth_result.get('success'):
                return auth_result

        try:
            # Real implementation:
            # url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/Opportunity/{deal_id}"
            # headers = {'Authorization': f'Bearer {self.access_token}'}
            # response = requests.get(url, headers=headers)
            # result = response.json()

            # Mock implementation
            return {
                'success': True,
                'data': {
                    'Id': deal_id,
                    'Name': 'Deal - 123 Oak St',
                    'Property_Address__c': '123 Oak St',
                    'ARV__c': 180000,
                    'Purchase_Price__c': 75000,
                    'Deal_Score__c': 'GREEN',
                    'StageName': 'Under Contract'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def query_deals(self, filters: Optional[Dict] = None, limit: int = 100) -> Dict:
        """
        Query deals from Salesforce

        Args:
            filters: Optional filters (e.g., {'Deal_Score__c': 'GREEN', 'StageName': 'Lead'})
            limit: Maximum number of records to return

        Returns:
            List of deals
        """
        if not self.access_token:
            auth_result = self.authenticate()
            if not auth_result.get('success'):
                return auth_result

        try:
            # Build SOQL query
            # soql = f"SELECT Id, Name, Property_Address__c, ARV__c, Purchase_Price__c, "
            # soql += f"Deal_Score__c, Recommended_Exit__c, StageName, CreatedDate "
            # soql += f"FROM Opportunity WHERE RecordType.Name = 'Real Estate Deal' "

            # if filters:
            #     conditions = [f"{k} = '{v}'" for k, v in filters.items()]
            #     soql += f"AND {' AND '.join(conditions)} "

            # soql += f"ORDER BY CreatedDate DESC LIMIT {limit}"

            # url = f"{self.instance_url}/services/data/{self.api_version}/query"
            # headers = {'Authorization': f'Bearer {self.access_token}'}
            # response = requests.get(url, headers=headers, params={'q': soql})
            # result = response.json()

            # Mock implementation
            return {
                'success': True,
                'data': {
                    'totalSize': 2,
                    'records': [
                        {
                            'Id': 'SF_001',
                            'Name': 'Deal - 123 Oak St',
                            'Property_Address__c': '123 Oak St',
                            'ARV__c': 180000,
                            'Purchase_Price__c': 75000,
                            'Deal_Score__c': 'GREEN',
                            'StageName': 'Under Contract'
                        },
                        {
                            'Id': 'SF_002',
                            'Name': 'Deal - 456 Elm Ave',
                            'Property_Address__c': '456 Elm Ave',
                            'ARV__c': 140000,
                            'Purchase_Price__c': 72000,
                            'Deal_Score__c': 'YELLOW',
                            'StageName': 'Offer'
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def add_note(self, deal_id: str, note: str) -> Dict:
        """
        Add a note to a deal in Salesforce

        Args:
            deal_id: Salesforce Opportunity ID
            note: Note text

        Returns:
            Success status
        """
        if not self.access_token:
            auth_result = self.authenticate()
            if not auth_result.get('success'):
                return auth_result

        try:
            # Real implementation would create a Note or ContentNote
            # Mock implementation
            return {
                'success': True,
                'message': f'Note added to deal {deal_id}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class LeftMainConnector(SalesforceConnector):
    """
    Specific connector for Left Main (built on Salesforce)
    Inherits from SalesforceConnector with Left Main specific customizations
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Left Main specific instance URL
        self.instance_url = os.getenv('LEFTMAIN_INSTANCE_URL', 'https://leftmain.my.salesforce.com')

    def sync_deal_from_underwriter(self, deal: Deal) -> Dict:
        """
        Sync deal from underwriting calculator to Left Main
        Creates or updates deal based on address
        """
        # Check if deal exists
        query_result = self.query_deals(filters={'Property_Address__c': deal.address})

        if query_result.get('success') and query_result['data']['totalSize'] > 0:
            # Update existing deal
            existing_deal_id = query_result['data']['records'][0]['Id']
            updates = {
                'ARV__c': deal.arv,
                'Purchase_Price__c': deal.purchase_price,
                'Rehab_Budget__c': deal.rehab_budget,
                'Deal_Score__c': deal.deal_score,
                'Recommended_Exit__c': deal.recommended_exit,
                'Last_Underwrite_Date__c': datetime.now().isoformat()
            }
            return self.update_deal(existing_deal_id, updates)
        else:
            # Create new deal
            return self.create_deal(deal)


# Convenience functions for Streamlit
def save_deal_to_crm(deal: Deal) -> Dict:
    """Save a deal to Left Main CRM"""
    connector = LeftMainConnector()
    return connector.sync_deal_from_underwriter(deal)


def get_deals_from_crm(filters: Optional[Dict] = None) -> List[Dict]:
    """Get deals from Left Main CRM"""
    connector = LeftMainConnector()
    result = connector.query_deals(filters=filters)

    if result.get('success'):
        return result['data']['records']
    else:
        return []
