"""
Sanctions Data Loader
---------------------
Loads and parses REAL sanctions data from official sources:
- EU Consolidated Sanctions List (CSV)
- OFAC SDN List (CSV)
- UN Security Council Sanctions List (XML)

This replaces the mock data with actual government sanctions lists.
"""

import logging
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Set
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SanctionsDataLoader:
    """
    Loads and parses sanctions data from multiple official sources.
    """
    
    def __init__(self, data_dir: str = "data/mock_external_data/sanctions"):
        """
        Initialize the sanctions data loader.
        
        Args:
            data_dir: Directory containing sanctions data files
        """
        self.data_dir = Path(data_dir)
        self.sanctions_data = {
            'entities': set(),  # Company names
            'individuals': set(),  # Person names
            'metadata': {}
        }
    
    def load_all_sanctions(self) -> Dict[str, Any]:
        """
        Load all sanctions lists.
        
        Returns:
            Dict with all sanctions data
        """
        logger.info("Loading sanctions data from all sources...")
        
        # Load EU sanctions
        eu_file = self.data_dir / "eu_sanctions.csv"
        if eu_file.exists():
            self._load_eu_sanctions(eu_file)
        else:
            logger.warning(f"EU sanctions file not found: {eu_file}")
        
        # Load OFAC sanctions
        ofac_file = self.data_dir / "ofac_sdn.csv"
        if ofac_file.exists():
            self._load_ofac_sanctions(ofac_file)
        else:
            logger.warning(f"OFAC sanctions file not found: {ofac_file}")
        
        # Load UN sanctions
        un_file = self.data_dir / "un_sanctions.xml"
        if un_file.exists():
            self._load_un_sanctions(un_file)
        else:
            logger.warning(f"UN sanctions file not found: {un_file}")
        
        # Convert sets to lists for JSON serialization
        result = {
            'entities': sorted(list(self.sanctions_data['entities'])),
            'individuals': sorted(list(self.sanctions_data['individuals'])),
            'total_entities': len(self.sanctions_data['entities']),
            'total_individuals': len(self.sanctions_data['individuals']),
            'sources': self.sanctions_data['metadata']
        }
        
        logger.info(f"Loaded {result['total_entities']} entities and {result['total_individuals']} individuals")
        
        return result
    
    def _load_eu_sanctions(self, file_path: Path):
        """Load EU sanctions from CSV."""
        try:
            logger.info(f"Loading EU sanctions from: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                # EU CSV format may vary - we'll try to handle it
                reader = csv.DictReader(f, delimiter=';')  # EU often uses semicolon
                
                count = 0
                for row in reader:
                    # Try to find name field (field names vary)
                    name = None
                    for key in row.keys():
                        if 'name' in key.lower():
                            name = row[key]
                            break
                    
                    if name and name.strip():
                        name_clean = name.strip().lower()
                        
                        # Determine if entity or individual (simple heuristic)
                        entity_type = row.get('Subject_Type', row.get('type', '')).lower()
                        
                        if 'enterprise' in entity_type or 'entity' in entity_type or 'ltd' in name_clean or 'inc' in name_clean:
                            self.sanctions_data['entities'].add(name_clean)
                        else:
                            self.sanctions_data['individuals'].add(name_clean)
                        
                        count += 1
                
                self.sanctions_data['metadata']['EU'] = {
                    'source': 'EU Consolidated Financial Sanctions',
                    'entries': count
                }
                
                logger.info(f"Loaded {count} EU sanctions entries")
        
        except Exception as e:
            logger.error(f"Failed to load EU sanctions: {e}")
    
    def _load_ofac_sanctions(self, file_path: Path):
        """Load OFAC sanctions from CSV."""
        try:
            logger.info(f"Loading OFAC sanctions from: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                count = 0
                for row in reader:
                    # OFAC CSV has 'name' field
                    name = row.get('name', '').strip()
                    sdn_type = row.get('type', row.get('SDN_Type', '')).lower()
                    
                    if name:
                        name_clean = name.lower()
                        
                        # Determine if entity or individual
                        if 'individual' in sdn_type:
                            self.sanctions_data['individuals'].add(name_clean)
                        else:
                            self.sanctions_data['entities'].add(name_clean)
                        
                        count += 1
                
                self.sanctions_data['metadata']['OFAC'] = {
                    'source': 'US Treasury OFAC SDN List',
                    'entries': count
                }
                
                logger.info(f"Loaded {count} OFAC sanctions entries")
        
        except Exception as e:
            logger.error(f"Failed to load OFAC sanctions: {e}")
    
    def _load_un_sanctions(self, file_path: Path):
        """Load UN sanctions from XML."""
        try:
            logger.info(f"Loading UN sanctions from: {file_path}")
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            count = 0
            
            # UN XML structure varies, but usually has INDIVIDUAL and ENTITY tags
            for individual in root.findall('.//INDIVIDUAL'):
                # Get first name and last name
                first_name = individual.findtext('.//FIRST_NAME', '').strip()
                second_name = individual.findtext('.//SECOND_NAME', '').strip()
                third_name = individual.findtext('.//THIRD_NAME', '').strip()
                
                name_parts = [first_name, second_name, third_name]
                full_name = ' '.join([n for n in name_parts if n]).lower()
                
                if full_name:
                    self.sanctions_data['individuals'].add(full_name)
                    count += 1
            
            for entity in root.findall('.//ENTITY'):
                # Get entity name
                name = entity.findtext('.//FIRST_NAME', '').strip()  # UN uses FIRST_NAME for entities too
                
                if name:
                    self.sanctions_data['entities'].add(name.lower())
                    count += 1
            
            self.sanctions_data['metadata']['UN'] = {
                'source': 'UN Security Council Consolidated List',
                'entries': count
            }
            
            logger.info(f"Loaded {count} UN sanctions entries")
        
        except Exception as e:
            logger.error(f"Failed to load UN sanctions: {e}")
    
    def save_to_json(self, output_file: str = "data/mock_external_data/sanctions/sanctions_combined.json"):
        """
        Save combined sanctions data to JSON file for fast loading.
        
        Args:
            output_file: Path to output JSON file
        """
        try:
            data = self.load_all_sanctions()
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved combined sanctions data to: {output_path}")
            logger.info(f"Total: {data['total_entities']} entities, {data['total_individuals']} individuals")
            
            return output_path
        
        except Exception as e:
            logger.error(f"Failed to save sanctions data: {e}")
            return None


def check_name_against_sanctions(
    name: str,
    sanctions_data: Dict[str, Any],
    threshold: float = 0.8
) -> Dict[str, Any]:
    """
    Check if a name appears in sanctions lists.
    
    Args:
        name: Name to check
        sanctions_data: Loaded sanctions data
        threshold: Similarity threshold (not used in exact match, for future enhancement)
    
    Returns:
        Dict with match results
    """
    name_lower = name.lower().strip()
    
    # Check exact matches in entities
    entity_match = name_lower in sanctions_data.get('entities', [])
    
    # Check exact matches in individuals
    individual_match = name_lower in sanctions_data.get('individuals', [])
    
    # Check partial matches (contains)
    entity_partial = [e for e in sanctions_data.get('entities', []) if name_lower in e or e in name_lower]
    individual_partial = [i for i in sanctions_data.get('individuals', []) if name_lower in i or i in name_lower]
    
    result = {
        'searched_name': name,
        'exact_match': entity_match or individual_match,
        'entity_exact_match': entity_match,
        'individual_exact_match': individual_match,
        'partial_matches': {
            'entities': entity_partial[:5],  # Top 5
            'individuals': individual_partial[:5]  # Top 5
        },
        'risk_level': 'blocked' if (entity_match or individual_match) else ('warning' if (entity_partial or individual_partial) else 'clear')
    }
    
    return result


# Test function
if __name__ == "__main__":
    print("=" * 80)
    print("LOADING REAL SANCTIONS DATA")
    print("=" * 80)
    
    # Initialize loader
    loader = SanctionsDataLoader()
    
    # Load all sanctions
    print("\n[STEP 1] Loading sanctions from all sources...")
    data = loader.load_all_sanctions()
    
    print(f"\n✅ Successfully loaded:")
    print(f"   - Total Entities: {data['total_entities']}")
    print(f"   - Total Individuals: {data['total_individuals']}")
    
    print(f"\n   Sources:")
    for source, info in data['sources'].items():
        print(f"   - {source}: {info['entries']} entries ({info['source']})")
    
    # Save to JSON
    print("\n[STEP 2] Saving combined data to JSON...")
    json_file = loader.save_to_json()
    
    if json_file:
        print(f"✅ Saved to: {json_file}")
    
    # Test check function
    print("\n[STEP 3] Testing name checks...")
    
    test_names = [
        "TechTextiles Ltd",
        "John Smith"
    ]
    
    for test_name in test_names:
        print(f"\n   Testing: {test_name}")
        result = check_name_against_sanctions(test_name, data)
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Exact Match: {result['exact_match']}")
        
        if result['partial_matches']['entities']:
            print(f"   Partial Entity Matches: {len(result['partial_matches']['entities'])}")
        if result['partial_matches']['individuals']:
            print(f"   Partial Individual Matches: {len(result['partial_matches']['individuals'])}")
    
    print("\n" + "=" * 80)
    print("SANCTIONS DATA LOADING COMPLETE")
    print("=" * 80)