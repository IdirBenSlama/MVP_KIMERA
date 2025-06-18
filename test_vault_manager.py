#!/usr/bin/env python3
"""Test vault manager functionality directly"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_vault_manager():
    """Test vault manager methods"""
    print("Testing UnderstandingVaultManager...")
    
    try:
        from backend.vault.understanding_vault_manager import UnderstandingVaultManager
        
        # Create instance
        vault_manager = UnderstandingVaultManager()
        print("✅ Created UnderstandingVaultManager instance")
        
        # Test get_all_geoids
        try:
            geoids = vault_manager.get_all_geoids()
            print(f"✅ get_all_geoids() returned {len(geoids)} geoids")
        except Exception as e:
            print(f"❌ get_all_geoids() failed: {e}")
        
        # Test get_total_scar_count
        try:
            count_a = vault_manager.get_total_scar_count("vault_a")
            count_b = vault_manager.get_total_scar_count("vault_b")
            print(f"✅ get_total_scar_count() - Vault A: {count_a}, Vault B: {count_b}")
        except Exception as e:
            print(f"❌ get_total_scar_count() failed: {e}")
        
        # Test get_understanding_metrics
        try:
            metrics = vault_manager.get_understanding_metrics()
            print(f"✅ get_understanding_metrics() returned metrics")
            print(f"   Components: {metrics['understanding_components']}")
        except Exception as e:
            print(f"❌ get_understanding_metrics() failed: {e}")
            
    except Exception as e:
        print(f"❌ Failed to import/create UnderstandingVaultManager: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vault_manager()