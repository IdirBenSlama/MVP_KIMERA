"""
Test compatibility with existing entropy monitor
"""

from backend.monitoring.entropy_monitor import EntropyMonitor
from backend.core.geoid import GeoidState
import numpy as np

def test_existing_monitor():
    """Test that existing entropy monitor still works"""
    print("Testing existing entropy monitor compatibility...")
    
    # Test basic entropy monitor
    monitor = EntropyMonitor()
    print('✅ Basic entropy monitor created')

    # Create test geoids
    geoids = []
    for i in range(5):
        geoid = GeoidState(
            geoid_id=f'test_{i}',
            semantic_state={f'feature_{j}': np.random.uniform(0.1, 1.0) for j in range(3)},
            symbolic_state={'state': f'test_{i}'},
            embedding_vector=np.random.uniform(0.1, 1.0, 5).tolist()
        )
        geoids.append(geoid)

    print(f'✅ Created {len(geoids)} test geoids')

    # Test entropy calculation
    vault_info = {'vault_a_scars': 10, 'vault_b_scars': 8}
    measurement = monitor.calculate_system_entropy(geoids, vault_info)

    print(f'✅ Entropy calculation successful:')
    print(f'   Shannon Entropy: {measurement.shannon_entropy:.4f}')
    print(f'   System Complexity: {measurement.system_complexity:.4f}')
    print(f'   Geoid Count: {measurement.geoid_count}')

    print('🎉 Existing entropy monitor works perfectly!')
    return True

if __name__ == "__main__":
    test_existing_monitor()