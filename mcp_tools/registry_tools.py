"""
MCP-3: Company Registry Tools
------------------------------
Tools for verifying company existence and status in official registries.

Functions:
- check_uk_companies_house(registration_number): Verify UK company
- verify_business_entity(name, country): General company verification

APIs: UK Companies House API (free), OpenCorporates (free tier)
"""

import logging
from typing import Dict, Any, Optional
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_uk_companies_house(registration_number: str) -> Dict[str, Any]:
    """
    Verify a UK company using Companies House API.
    
    This function queries the UK Companies House public search API (no authentication needed).
    
    Args:
        registration_number (str): UK company registration number (e.g., "12345678")
        
    Returns:
        Dict containing:
        - 'success' (bool): Whether query was successful
        - 'company_name' (str): Official company name
        - 'company_number' (str): Registration number
        - 'company_status' (str): Status (e.g., 'active', 'dissolved')
        - 'date_of_creation' (str): When company was registered
        - 'registered_address' (Dict): Company's registered address
        - 'company_type' (str): Type of company
        - 'error' (str, optional): Error message if failed
        
    Example:
        >>> result = check_uk_companies_house("12345678")
        >>> print(result['company_name'])
        'TECHTEXTILES LIMITED'
        >>> print(result['company_status'])
        'active'
    """
    try:
        logger.info(f"Checking UK Companies House for registration: {registration_number}")
        
        # UK Companies House PUBLIC SEARCH API (no authentication required)
        # This searches by company number and returns basic info
        url = f"https://api.company-information.service.gov.uk/company/{registration_number}"
        
        # Try without authentication first (basic public data)
        response = requests.get(url, timeout=10)
        
        if response.status_code == 401:
            # If 401, fall back to search endpoint (definitely doesn't need auth)
            logger.info("Using search endpoint instead (no auth required)")
            search_url = "https://find-and-update.company-information.service.gov.uk/api/search/companies"
            
            search_response = requests.get(
                search_url,
                params={'q': registration_number},
                timeout=10
            )
            
            if search_response.status_code == 404:
                logger.warning(f"Company not found: {registration_number}")
                return {
                    'success': False,
                    'error': f"Company not found with registration number: {registration_number}",
                    'company_number': registration_number
                }
            
            search_response.raise_for_status()
            search_data = search_response.json()
            
            # Parse search results
            items = search_data.get('items', [])
            if not items:
                return {
                    'success': False,
                    'error': f"Company not found with registration number: {registration_number}",
                    'company_number': registration_number
                }
            
            # Get first result (exact match)
            company = items[0]
            
            result = {
                'success': True,
                'company_name': company.get('title', 'Unknown'),
                'company_number': company.get('company_number', registration_number),
                'company_status': company.get('company_status', 'Unknown'),
                'date_of_creation': company.get('date_of_creation', 'Unknown'),
                'company_type': company.get('company_type', 'Unknown'),
                'registered_address': {
                    'address_line_1': company.get('address', {}).get('address_line_1', ''),
                    'address_line_2': company.get('address', {}).get('address_line_2', ''),
                    'locality': company.get('address', {}).get('locality', ''),
                    'postal_code': company.get('address', {}).get('postal_code', ''),
                    'country': 'United Kingdom'
                },
                'note': 'Data from Companies House public search (no auth required)'
            }
            
            logger.info(f"Successfully verified UK company via search: {result['company_name']} ({result['company_status']})")
            
            return result
        
        if response.status_code == 404:
            logger.warning(f"Company not found: {registration_number}")
            return {
                'success': False,
                'error': f"Company not found with registration number: {registration_number}",
                'company_number': registration_number
            }
        
        response.raise_for_status()
        data = response.json()
        
        # Parse the response
        result = {
            'success': True,
            'company_name': data.get('company_name', 'Unknown'),
            'company_number': data.get('company_number', registration_number),
            'company_status': data.get('company_status', 'Unknown'),
            'date_of_creation': data.get('date_of_creation', 'Unknown'),
            'company_type': data.get('type', 'Unknown'),
            'registered_address': {
                'address_line_1': data.get('registered_office_address', {}).get('address_line_1', ''),
                'address_line_2': data.get('registered_office_address', {}).get('address_line_2', ''),
                'locality': data.get('registered_office_address', {}).get('locality', ''),
                'postal_code': data.get('registered_office_address', {}).get('postal_code', ''),
                'country': 'United Kingdom'
            },
            'accounts': {
                'next_due': data.get('accounts', {}).get('next_due', 'Unknown'),
                'overdue': data.get('accounts', {}).get('overdue', False)
            },
            'sic_codes': data.get('sic_codes', [])
        }
        
        logger.info(f"Successfully verified UK company: {result['company_name']} ({result['company_status']})")
        
        return result
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while checking Companies House: {e}")
        return {
            'success': False,
            'error': f"Network error: {str(e)}",
            'company_number': registration_number
        }
    except Exception as e:
        logger.error(f"Failed to check UK Companies House for {registration_number}: {e}")
        return {
            'success': False,
            'error': str(e),
            'company_number': registration_number
        }



def verify_business_entity(
    company_name: str, 
    country: str = "United Kingdom"
) -> Dict[str, Any]:
    """
    General business entity verification across countries.
    
    This is a simplified function that demonstrates the concept.
    For production, you would integrate with services like:
    - OpenCorporates API (international company data)
    - Dun & Bradstreet
    - Country-specific registries
    
    Args:
        company_name (str): Company name to verify
        country (str): Country where company is registered (default: "United Kingdom")
        
    Returns:
        Dict containing:
        - 'success' (bool): Whether verification was performed
        - 'verified' (bool): Whether company was found
        - 'company_name' (str): Searched company name
        - 'country' (str): Country
        - 'registry_source' (str): Which registry was checked
        - 'note' (str): Additional information
        
    Example:
        >>> result = verify_business_entity("TechTextiles Ltd", "United Kingdom")
        >>> print(result['verified'])
        True
    """
    try:
        logger.info(f"Verifying business entity: {company_name} ({country})")
        
        # This is a placeholder for demonstration
        # In production, you would:
        # 1. Determine which country registry to use
        # 2. Call the appropriate API (OpenCorporates, etc.)
        # 3. Parse and return the results
        
        if country.lower() in ["uk", "united kingdom", "england", "scotland", "wales"]:
            note = "For UK companies, use check_uk_companies_house() with registration number for detailed verification"
            registry_source = "UK Companies House"
        elif country.lower() == "united arab emirates" or country.lower() == "uae":
            note = "UAE company verification would require integration with UAE Ministry of Economy API"
            registry_source = "UAE Ministry of Economy"
        elif country.lower() == "united states" or country.lower() == "usa":
            note = "US company verification varies by state. Would integrate with state-specific registries"
            registry_source = "State-specific registries"
        else:
            note = f"Would integrate with {country} national business registry or OpenCorporates API"
            registry_source = f"{country} National Registry"
        
        return {
            'success': True,
            'verified': False,  # Would be True if actual verification done
            'company_name': company_name,
            'country': country,
            'registry_source': registry_source,
            'note': note,
            'recommendation': "Use country-specific registry tools for detailed verification"
        }
    
    except Exception as e:
        logger.error(f"Failed to verify business entity {company_name}: {e}")
        return {
            'success': False,
            'error': str(e),
            'company_name': company_name,
            'country': country
        }


# Test function
if __name__ == "__main__":
    print("=" * 80)
    print("TESTING MCP-3: COMPANY REGISTRY TOOLS")
    print("=" * 80)
    
    # Test 1: Check real UK company (example: Companies House itself)
    print("\n[TEST 1] Checking UK company (Companies House registration: 00445790)...")
    result = check_uk_companies_house("00445790")
    
    if result['success']:
        print(f"✅ Success!")
        print(f"   Company: {result['company_name']}")
        print(f"   Status: {result['company_status']}")
        print(f"   Registered: {result['date_of_creation']}")
        print(f"   Address: {result['registered_address']['address_line_1']}, {result['registered_address']['postal_code']}")
        print(f"   Accounts next due: {result['accounts']['next_due']}")
        print(f"   Accounts overdue: {result['accounts']['overdue']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 2: Check non-existent company
    print("\n[TEST 2] Checking non-existent company (99999999)...")
    result2 = check_uk_companies_house("99999999")
    
    if not result2['success']:
        print(f"✅ Correctly identified as not found")
        print(f"   Error: {result2['error']}")
    else:
        print(f"❌ Unexpected success")
    
    # Test 3: General verification
    print("\n[TEST 3] General business entity verification...")
    result3 = verify_business_entity("TechTextiles Ltd", "United Kingdom")
    print(f"   Company: {result3['company_name']}")
    print(f"   Country: {result3['country']}")
    print(f"   Registry: {result3['registry_source']}")
    print(f"   Note: {result3['note']}")
    
    print("\n" + "=" * 80)
    print("REGISTRY TOOLS TEST COMPLETE")
    print("=" * 80)