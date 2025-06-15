#!/usr/bin/env python3
"""
Test full contradiction processing with SCAR creation
"""

import sys
sys.path.append('.')

from backend.engines.proactive_contradiction_detector import ProactiveContradictionDetector
from backend.engines.contradiction_engine import ContradictionEngine
from backend.api.main import create_scar_from_tension
from backend.vault.vault_manager import VaultManager
from backend.vault.database import SessionLocal, GeoidDB, ScarDB
from backend.core.geoid import GeoidState
import json

def main():
    print('=== TESTING FULL CONTRADICTION PROCESSING ===')

    # Initialize components
    detector = ProactiveContradictionDetector()
    contradiction_engine = ContradictionEngine(tension_threshold=0.3)
    vault_manager = VaultManager()

    # Get initial SCAR count
    with SessionLocal() as db:
        initial_scar_count = db.query(ScarDB).count()
        print(f'Initial SCAR count: {initial_scar_count}')

    # Run scan to get tensions
    scan_results = detector.run_proactive_scan()
    tensions = scan_results['tensions_found'][:5]  # Process first 5 tensions

    print(f'\nProcessing {len(tensions)} tensions...')

    # Load geoids for processing
    with SessionLocal() as db:
        geoid_rows = db.query(GeoidDB).all()
        geoids_dict = {}
        for row in geoid_rows:
            try:
                geoid = GeoidState(
                    geoid_id=row.geoid_id,
                    semantic_state=row.semantic_state_json or {},
                    symbolic_state=row.symbolic_state or {},
                    embedding_vector=row.semantic_vector or [],
                    metadata=row.metadata_json or {}
                )
                geoids_dict[geoid.geoid_id] = geoid
            except:
                continue

    # Process tensions and create SCARs
    scars_created = 0
    for i, tension in enumerate(tensions):
        try:
            # Calculate pulse strength
            pulse_strength = contradiction_engine.calculate_pulse_strength(tension, geoids_dict)
            
            # Make decision
            decision = contradiction_engine.decide_collapse_or_surge(
                pulse_strength, {'semantic_cohesion': 0.5}, None
            )
            
            print(f'\nTension {i+1}: {tension.geoid_a} <-> {tension.geoid_b}')
            print(f'  Score: {tension.tension_score:.3f}')
            print(f'  Pulse strength: {pulse_strength:.3f}')
            print(f'  Decision: {decision}')
            
            # Create SCAR for all decisions (new logic)
            if decision in ['collapse', 'surge', 'buffer']:
                scar, vector = create_scar_from_tension(tension, geoids_dict, decision)
                vault_manager.insert_scar(scar, vector)
                scars_created += 1
                print(f'  SCAR created: {scar.scar_id}')
            
        except Exception as e:
            print(f'  Error processing tension: {e}')
            continue

    # Check final SCAR count
    with SessionLocal() as db:
        final_scar_count = db.query(ScarDB).count()
        print(f'\nFinal SCAR count: {final_scar_count}')
        print(f'SCARs created this run: {scars_created}')
        print(f'Total new SCARs: {final_scar_count - initial_scar_count}')

    # Check utilization improvement
    stats = detector.get_scan_statistics()
    print(f'\nUpdated utilization rate: {stats["utilization_rate"]:.3f} ({stats["utilization_rate"]*100:.1f}%)')

    print('\nCONTRADICTION PROCESSING COMPLETE!')

if __name__ == "__main__":
    main()